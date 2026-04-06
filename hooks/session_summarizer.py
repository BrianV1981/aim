#!/usr/bin/env python3
import sys
import json
import os
import glob
import re
from datetime import datetime

# --- DYNAMIC ROOT DISCOVERY ---
def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core", "CONFIG.json")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
sys.path.append(os.path.join(AIM_ROOT, "src"))

try:
    from reasoning_utils import generate_reasoning
except ImportError:
    generate_reasoning = None

CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
MEMORY_PATH = os.path.join(AIM_ROOT, "core/MEMORY.md")
GEMINI_PATH = os.path.join(AIM_ROOT, "GEMINI.md")

if not os.path.exists(CONFIG_PATH):
    sys.exit(0)

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

# --- SINGLE-SHOT COMPILER PROMPT ---
COMPILER_SYSTEM = """You are the Sovereign Memory Compiler. Your goal is to analyze a session transcript and immediately update the project's permanent memory and rule files.

### INPUTS
1. **Session Transcript:** A noise-reduced record of recent activity.
2. **Current `core/MEMORY.md`:** The existing state of durable memory.
3. **Current `GEMINI.md`:** The existing absolute rules and agentic guardrails.

### CONSTRAINTS
- **Recency Bias Guard:** Do NOT add temporary debugging steps or rabbit-holes. ONLY update `core/MEMORY.md` if a permanent architectural state changed.
- **Rule of Law Guard:** ONLY update `GEMINI.md` if a catastrophic workflow failure occurred that requires a new absolute physical constraint. Do NOT add stylistic preferences.
- **Compression:** If you add a new fact, attempt to consolidate or remove an outdated one.
- **Timestamping:** Any NEW architectural facts or rules you add MUST include a timestamp in the format `(Added: YYYY-MM-DD)` at the end of the bullet point or sentence.

### OUTPUT SCHEMA
You MUST output the entirety of both files. Do NOT use omission placeholders like "..." or "rest of code". Rewriting the entire file is required so that new information is woven elegantly into the correct existing sections (rather than just appended to the bottom).
Your final output MUST follow this exact structure:

### core/MEMORY.md
```markdown
[FULL UPDATED CONTENT OF core/MEMORY.md]
```

### GEMINI.md
```markdown
[FULL UPDATED CONTENT OF GEMINI.md]
```
"""

def extract_file_content(full_text, filename):
    """Extracts the markdown block following a specific filename header."""
    pattern = rf"### {re.escape(filename)}\s*```(?:markdown|md)?\n(.*?)```"
    match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def atomic_write(file_path, content):
    temp_path = f"{file_path}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, file_path)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def process_transcript(md_path):
    if not generate_reasoning:
        print("[ERROR] reasoning_utils not available.")
        return False
        
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
            
        memory_content = ""
        if os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, 'r', encoding='utf-8') as f:
                memory_content = f.read()
                
        gemini_content = ""
        if os.path.exists(GEMINI_PATH):
            with open(GEMINI_PATH, 'r', encoding='utf-8') as f:
                gemini_content = f.read()

        combined_input = f"### SESSION TRANSCRIPT\n{transcript}\n\n### CURRENT core/MEMORY.md\n{memory_content}\n\n### CURRENT GEMINI.md\n{gemini_content}"

        print(f"[COMPILER] Distilling Single-Shot Memory from: {os.path.basename(md_path)}")
        # We temporarily continue using 'tier1' model config from the TUI until Phase 2 updates it
        compiled_output = generate_reasoning(combined_input, system_instruction=COMPILER_SYSTEM, brain_type="tier1")

        if not compiled_output or "[ERROR" in compiled_output:
            print("[ERROR] LLM generation failed or returned an error.")
            return False

        new_memory = extract_file_content(compiled_output, "core/MEMORY.md")
        new_gemini = extract_file_content(compiled_output, "GEMINI.md")

        if new_memory and len(new_memory) > 50:
            atomic_write(MEMORY_PATH, new_memory)
            print("[SUCCESS] MEMORY.md securely updated.")
            
        if new_gemini and len(new_gemini) > 50:
            atomic_write(GEMINI_PATH, new_gemini)
            print("[SUCCESS] GEMINI.md securely updated.")

        return True

    except Exception as e:
        print(f"[FATAL] Single-Shot Compiler Error: {e}")
        return False

def main(args):
    is_light_mode = "--light" in args
    
    if is_light_mode:
        print(json.dumps({"decision": "skip", "reason": "light_mode_active"}))
        return

    # Check cognitive mode for offloading
    cognitive_mode = CONFIG.get('settings', {}).get('cognitive_mode', 'monolithic')
    if cognitive_mode == 'frontline':
        print(json.dumps({"decision": "skip", "reason": "frontline_mode_offloads_compute"}))
        return

    # Accept direct MD path or find the latest in archive/history
    md_path = None
    for arg in args[1:]:
        if arg.endswith('.md') and os.path.exists(arg):
            md_path = arg
            break
            
    if not md_path:
        history_dir = os.path.join(AIM_ROOT, "archive/history")
        if os.path.exists(history_dir):
            transcripts = glob.glob(os.path.join(history_dir, "*.md"))
            if transcripts:
                md_path = max(transcripts, key=os.path.getmtime)
                
    if not md_path:
        print(json.dumps({"decision": "skip", "reason": "no_transcript_found"}))
        return

    updated = 1 if process_transcript(md_path) else 0
    print(json.dumps({"decision": "proceed", "updated": updated}))

if __name__ == "__main__":
    main(sys.argv)
