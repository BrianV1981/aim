#!/home/kingb/aim/venv/bin/python3
import os
import json
import sys
import re
import glob
import keyring
from google import genai

# --- CONFIGURATION (Load from core/CONFIG.json) ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        config_path = os.path.join(current, "core/CONFIG.json")
        if os.path.exists(config_path):
            return current
        current = os.path.dirname(current)
    return "/home/kingb/aim"

AIM_ROOT = find_aim_root(os.getcwd())
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

ALLOWED_ROOT = CONFIG['settings']['allowed_root']
CONTINUITY_DIR = CONFIG['paths']['continuity_dir']
MODEL = CONFIG['models'].get('sentinel', 'gemini-flash-latest')

DANGER_PATTERNS = [
    r"rm\s+-rf\s+/",         # Delete root
    r"rm\s+-rf\s+\*",         # Delete all in current dir (high risk)
    r"mkfs",                  # Format disk
    r"dd\s+if=",              # Low-level disk write
    r"> /dev/",               # Writing to device files
    r"chmod\s+-R\s+777",      # Dangerous permissions
    r"chown\s+-R",             # Dangerous ownership changes
    r":\(\){ :\|:& };:"      # Fork bomb
]

MUTATION_KEYWORDS = [
    "rm ", "mv ", "cp ", "chmod ", "chown ", ">", "wget ", "curl ", "git push", "git commit"
]

def is_statically_dangerous(command):
    """Checks the command string against known dangerous patterns."""
    for pattern in DANGER_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return f"Danger Pattern Detected: '{pattern}'"
    return None

def get_latest_pulse():
    """Finds the most recent context pulse to define the current intent."""
    pattern = os.path.join(CONTINUITY_DIR, "202[0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9][0-9][0-9].md")
    pulses = glob.glob(pattern)
    if not pulses: return "No active pulse."
    pulses.sort(reverse=True)
    try:
        with open(pulses[0], 'r') as f:
            return f.read()
    except:
        return "Failed to read pulse."

def semantic_intent_check(command, cwd):
    """Uses LLM to verify if the command aligns with the current mental model."""
    api_key = keyring.get_password("aim-system", "google-api-key")
    if not api_key:
        return True, "No API key found for semantic check."
    
    try:
        client = genai.Client(api_key=api_key)
        pulse_text = get_latest_pulse()
        
        prompt = f"""You are the A.I.M. Safety Sentinel (Semantic Intent Guardrail).
Your job is to evaluate if a shell command proposed by the AI agent is safe and aligns with the current project intent.

CURRENT MENTAL MODEL (Intent):
{pulse_text}

PROPOSED COMMAND:
`{command}`

EXECUTION DIRECTORY:
`{cwd}`

ALLOWED ROOT DIRECTORY:
`{ALLOWED_ROOT}`

EVALUATION RULES:
1. If the command operates outside the ALLOWED ROOT DIRECTORY and is destructive (e.g. rm), ABORT.
2. If the command contradicts the CURRENT MENTAL MODEL or seems like a dangerous "YOLO hallucination" (e.g., deleting project files arbitrarily, pushing to production without intent), ABORT.
3. If it's a standard development command or aligns with the current tasks in the Mental Model, PROCEED.

REPLY FORMAT:
You MUST reply with exactly one of these two formats:
PROCEED
or
ABORT: [Provide a concise, 1-sentence reason why]
"""
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        
        result = response.text.strip()
        if result.startswith("ABORT"):
            reason = result.split(":", 1)[1].strip() if ":" in result else "Semantic guardrail denied execution."
            return False, reason
        else:
            return True, "Approved by Semantic Sentinel."
            
    except Exception as e:
        # If API fails, default to allowing if static checks pass to not brick the agent
        return True, f"Semantic check failed due to API error: {e}"

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            print(json.dumps({}))
            return

        data = json.loads(input_data)
        
        args = data.get('arguments', {})
        cmd = args.get('command', '')
        cwd = data.get('dir_path', os.getcwd())

        # 1. Static Pattern Check (Level 0)
        static_reason = is_statically_dangerous(cmd)
        if static_reason:
            print(json.dumps({
                "decision": "abort",
                "message": f"SAFETY SENTINEL ALERT: Command blocked for security reasons. {static_reason}"
            }))
            return

        # 2. Path Check (Level 1)
        abs_cwd = os.path.abspath(os.path.expanduser(cwd))
        if "rm " in cmd and not abs_cwd.startswith(ALLOWED_ROOT):
            print(json.dumps({
                "decision": "abort",
                "message": f"SAFETY SENTINEL ALERT: Shell deletion blocked outside of authorized workspace: {ALLOWED_ROOT}"
            }))
            return

        # 3. Semantic Intent Check (Level 2)
        needs_semantic_check = any(kw in cmd for kw in MUTATION_KEYWORDS)
        
        if needs_semantic_check:
            is_safe, reason = semantic_intent_check(cmd, abs_cwd)
            if not is_safe:
                print(json.dumps({
                    "decision": "abort",
                    "message": f"SEMANTIC SENTINEL ALERT: Command contradicts architectural intent. {reason}"
                }))
                return

        # Proceed
        print(json.dumps({"decision": "proceed"}))

    except Exception as e:
        print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
