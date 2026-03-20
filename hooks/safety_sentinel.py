#!/usr/bin/env python3
import sys
import json
import os
import subprocess
import re

# --- VENV BOOTSTRAP ---
hook_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(hook_dir)
venv_python = os.path.join(aim_root, "venv/bin/python3")

# NOTE: BeforeTool provides tool call JSON in stdin
input_data = sys.stdin.read()

if os.path.exists(venv_python) and sys.executable != venv_python:
    try:
        process = subprocess.run([venv_python] + sys.argv, input=input_data, text=True, capture_output=True)
        print(process.stdout)
        sys.exit(process.returncode)
    except Exception: pass

# --- LOGIC ---
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

try:
    from config_utils import CONFIG, AIM_ROOT
    from reasoning_utils import generate_reasoning
except ImportError:
    print(json.dumps({"decision": "proceed"}))
    sys.exit(0)

ALLOWED_ROOT = CONFIG.get('settings', {}).get('allowed_root', os.path.expanduser("~"))

def get_current_momentum():
    continuity_dir = CONFIG.get('paths', {}).get('continuity_dir')
    if not continuity_dir: return "No momentum found."
    import glob
    pattern = os.path.join(continuity_dir, "202[0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9][0-9][0-9].md")
    pulses = glob.glob(pattern)
    if not pulses: return "No active momentum found."
    pulses.sort(reverse=True)
    try:
        with open(pulses[0], 'r') as f: return f.read()
    except: return "Error reading momentum."

def audit_intent(command, args, momentum):
    prompt = f"""
You are the A.I.M. Safety Sentinel. Verify if this command aligns with project momentum.
MOMENTUM: {momentum}
COMMAND: {command} ({json.dumps(args)})
Output ONLY JSON: {{"decision": "safe"|"unsafe", "reason": "..."}}
"""
    try:
        resp = generate_reasoning(prompt, brain_type="sentinel")
        clean = re.sub(r"```json\n|\n```", "", resp).strip()
        return json.loads(clean)
    except: return {"decision": "safe", "reason": "Audit failed."}

def main():
    try:
        if not input_data:
            print(json.dumps({"decision": "proceed"}))
            return
        data = json.loads(input_data)
        command = data.get('command')
        args = data.get('arguments', {}) # BeforeTool uses 'arguments'

        # Path Check
        target = args.get('file_path') or args.get('dir_path') or args.get('path')
        if target:
            abs_target = os.path.abspath(os.path.expanduser(target))
            if not abs_target.startswith(ALLOWED_ROOT):
                print(json.dumps({"decision": "abort", "message": f"GUARDRAIL: Unauthorized path {abs_target}"}))
                return

        # Intent Check
        mode = CONFIG.get('settings', {}).get('sentinel_mode', 'full')
        if mode == 'full' and command in ['replace', 'write_file', 'run_shell_command']:
            audit = audit_intent(command, args, get_current_momentum())
            if audit.get('decision') == 'unsafe':
                print(json.dumps({"decision": "abort", "message": f"SENTINEL: {audit.get('reason')}"}))
                return

        print(json.dumps({"decision": "proceed"}))
    except Exception: print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
