#!/usr/bin/env python3
import os
import sys
import subprocess

def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh")): return current
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
        
        # Log any hook errors to stderr so the operator can debug, but the core OS doesn't crash
        if process.stderr:
            sys.stderr.write(f"\n[A.I.M. HOOK DIAGNOSTIC] {hook_script_name} stderr:\n{process.stderr}\n")
            
        if process.returncode != 0:
            sys.stderr.write(f"[A.I.M. HOOK DIAGNOSTIC] {hook_script_name} failed with exit code {process.returncode}.\n")
            print("{}")
            return
            
        # Ensure the stdout is actually valid JSON before piping it to the Gemini CLI
        if process.stdout:
            import json
            try:
                # We just parse it to guarantee it won't crash the upstream CLI
                json.loads(process.stdout)
                print(process.stdout, end="")
            except json.JSONDecodeError:
                sys.stderr.write(f"[A.I.M. HOOK DIAGNOSTIC] {hook_script_name} returned invalid JSON. Masking output.\n")
                print("{}")
        else:
            print("{}")
            
    except Exception as e:
        sys.stderr.write(f"\n[A.I.M. HOOK DIAGNOSTIC] Core Router Exception executing {hook_script_name}: {e}\n")
        print("{}")

if __name__ == "__main__":
    main()