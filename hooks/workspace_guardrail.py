#!/usr/bin/env python3
import os
import json
import sys
import subprocess

# --- VENV BOOTSTRAP ---
hook_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(hook_dir)
venv_python = os.path.join(aim_root, "venv/bin/python3")

input_data = sys.stdin.read()

if os.path.exists(venv_python) and sys.executable != venv_python:
    try:
        process = subprocess.run([venv_python] + sys.argv, input=input_data, text=True, capture_output=True)
        print(process.stdout)
        sys.exit(process.returncode)
    except Exception:
        pass

# --- LOGIC ---
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

try:
    from config_utils import CONFIG
    ALLOWED_ROOT = CONFIG['settings'].get('allowed_root', os.path.expanduser("~"))
except ImportError:
    ALLOWED_ROOT = os.path.expanduser("~")

def main():
    try:
        if not input_data:
            print(json.dumps({}))
            return

        data = json.loads(input_data)
        args = data.get('arguments', {})
        cwd = data.get('dir_path', os.getcwd())
        
        target_path = args.get('file_path') or args.get('dir_path') or args.get('path')
        
        if target_path:
            abs_target = os.path.abspath(os.path.expanduser(target_path))
            if not abs_target.startswith(ALLOWED_ROOT):
                print(json.dumps({
                    "decision": "abort",
                    "message": f"WORKSPACE GUARDRAIL ALERT: Unauthorized path '{abs_target}'"
                }))
                return

        if cwd:
            abs_cwd = os.path.abspath(os.path.expanduser(cwd))
            if not abs_cwd.startswith(ALLOWED_ROOT):
                print(json.dumps({
                    "decision": "abort",
                    "message": f"WORKSPACE GUARDRAIL ALERT: Unauthorized execution directory '{abs_cwd}'"
                }))
                return

        print(json.dumps({"decision": "proceed"}))
    except Exception:
        print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
