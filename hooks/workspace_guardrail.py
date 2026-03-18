#!/usr/bin/env python3
import os
import json
import sys

# --- CONFIGURATION ---
ALLOWED_ROOT = "/home/kingb"

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            print(json.dumps({}))
            return

        data = json.loads(input_data)
        args = data.get('arguments', {})
        cwd = data.get('dir_path', os.getcwd())
        
        # 1. Check for target path in arguments
        target_path = args.get('file_path') or args.get('dir_path') or args.get('path')
        
        if target_path:
            # Resolve to absolute path
            if not os.path.isabs(target_path):
                target_path = os.path.join(cwd, target_path)
            
            abs_target = os.path.abspath(os.path.expanduser(target_path))
            
            if not abs_target.startswith(ALLOWED_ROOT):
                error_msg = f"WORKSPACE GUARDRAIL ALERT: Operation blocked. Path '{abs_target}' is outside the authorized root: {ALLOWED_ROOT}"
                print(json.dumps({
                    "decision": "abort",
                    "message": error_msg
                }))
                return

        # 2. Check the command-level dir_path (for tools like run_shell_command)
        if cwd:
            abs_cwd = os.path.abspath(os.path.expanduser(cwd))
            if not abs_cwd.startswith(ALLOWED_ROOT):
                error_msg = f"WORKSPACE GUARDRAIL ALERT: Operation blocked. Execution directory '{abs_cwd}' is outside the authorized root: {ALLOWED_ROOT}"
                print(json.dumps({
                    "decision": "abort",
                    "message": error_msg
                }))
                return

        # If everything looks good, proceed
        print(json.dumps({"decision": "proceed"}))

    except Exception:
        # Default to safe mode: proceed if we can't parse
        print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
