#!/usr/bin/env python3
import sys
import json
import os
import re

# Add src to path so we can import reasoning_utils
hook_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(hook_dir)
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from reasoning_utils import generate_reasoning, AIM_ROOT

# --- CONFIGURATION (Load from core/CONFIG.json) ---
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

ALLOWED_ROOT = CONFIG['settings'].get('allowed_root', '/home/kingb')

def get_current_momentum():
    """Reads the latest Context Pulse to understand the agent's intent."""
    continuity_dir = CONFIG['paths']['continuity_dir']
    pattern = os.path.join(continuity_dir, "202[0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9][0-9][0-9].md")
    import glob
    pulses = glob.glob(pattern)
    if not pulses: return "No active momentum found."
    pulses.sort(reverse=True)
    try:
        with open(pulses[0], 'r') as f:
            return f.read()
    except: return "Error reading momentum."

def audit_intent(command, args, momentum):
    """Level 2 Intent Verification using AI."""
    prompt = f"""
You are the A.I.M. Safety Sentinel. Your job is to verify if a tool command aligns with the user's current project momentum.

CURRENT MOMENTUM (Context Pulse):
{momentum}

PENDING COMMAND:
Tool: {command}
Args: {json.dumps(args)}

Is this command consistent with the current technical arc? 
If it is destructive (rm, delete, replace) and unrelated to the momentum, flag it as 'unsafe'.
Otherwise, flag it as 'safe'.

Output ONLY a JSON object:
{{
  "decision": "safe" | "unsafe",
  "reason": "short explanation"
}}
"""
    try:
        response_text = generate_reasoning(prompt, system_instruction="You are a strict security auditor. Minimize false positives but block clearly stray destructive actions.")
        # Extract JSON from potential markdown blocks
        clean_json = re.sub(r"```json\n|\n```", "", response_text).strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"decision": "safe", "reason": f"Audit failed, defaulting to safe: {str(e)}"}

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            print(json.dumps({"decision": "proceed"}))
            return

        data = json.loads(input_data)
        command = data.get('command')
        args = data.get('args', {})

        # --- LEVEL 1: PATH PROTECTION (Hard Guardrail) ---
        
        # 1a. Check explicit path arguments
        target_path = args.get('file_path') or args.get('dir_path') or args.get('path')
        
        # 1b. Loophole Fix: Scan shell command strings for hidden paths
        shell_cmd = args.get('command', '')
        if command == 'run_shell_command' and shell_cmd:
            # Look for any /home/... paths in the command string
            # We use a broad pattern to catch as much as possible
            paths_in_cmd = re.findall(r'/home/[a-zA-Z0-9._/-]+', shell_cmd)
            for p in paths_in_cmd:
                # Standardize the path
                abs_p = os.path.abspath(os.path.expanduser(p.strip()))
                if abs_p.startswith('/home/') and not abs_p.startswith(ALLOWED_ROOT):
                    print(json.dumps({
                        "decision": "stop",
                        "message": f"VIOLATION: Shell command string contains unauthorized path: {abs_p}"
                    }))
                    return

        if target_path:
            abs_path = os.path.abspath(os.path.expanduser(target_path))
            if not abs_path.startswith(ALLOWED_ROOT):
                print(json.dumps({
                    "decision": "stop",
                    "message": f"VIOLATION: Attempted access outside allowed root: {abs_path}"
                }))
                return

        # --- LEVEL 2: INTENT PROTECTION (AI Guardrail) ---
        # Only audit state-altering commands and only if AI auditing is enabled
        sentinel_mode = CONFIG['settings'].get('sentinel_mode', 'full') # full or path-only
        
        if sentinel_mode == 'full' and command in ['replace', 'write_file', 'run_shell_command']:
            momentum = get_current_momentum()
            audit = audit_intent(command, args, momentum)
            
            if audit.get('decision') == 'unsafe':
                print(json.dumps({
                    "decision": "stop",
                    "message": f"SAFETY ALERT: {audit.get('reason')}"
                }))
                return

        # Default: Proceed
        print(json.dumps({"decision": "proceed"}))

    except Exception as e:
        # On error, we proceed but log to stderr
        sys.stderr.write(f"Sentinel Error: {str(e)}\n")
        print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
