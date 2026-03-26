#!/usr/bin/env python3
import os
import sys
import subprocess

def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        if os.path.exists(os.path.join(current, "setup.sh")): return current
        current = os.path.dirname(current)
    return None

def main():
    if len(sys.argv) < 2:
        print("{}")
        sys.exit(0)

    hook_script_name = sys.argv[1]
    aim_root = find_aim_root()

    if not aim_root:
        # Not inside an A.I.M. workspace, fail silently
        print("{}")
        sys.exit(0)

    venv_python = os.path.join(aim_root, "venv", "bin", "python3")
    script_path = os.path.join(aim_root, "hooks", hook_script_name)

    if not os.path.exists(script_path):
        print("{}")
        sys.exit(0)
    
    # Read stdin
    input_data = ""
    import select
    if select.select([sys.stdin], [], [], 0.0)[0]:
        input_data = sys.stdin.read()

    cmd = [venv_python, script_path]
    
    try:
        process = subprocess.run(cmd, input=input_data, text=True, capture_output=True)
        # Print the hook's stdout back to Gemini CLI
        if process.stdout:
            print(process.stdout, end="")
        else:
            print("{}")
    except Exception:
        print("{}")

if __name__ == "__main__":
    main()