#!/usr/bin/env python3
import os
import json
import sys
import subprocess
import re

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
    ALLOWED_ROOT = CONFIG['settings'].get('allowed_root', aim_root)
except ImportError:
    ALLOWED_ROOT = aim_root

def is_path_safe(path, allowed_root):
    if not path: return True
    try:
        abs_path = os.path.abspath(os.path.expanduser(path))
        # Ensure it starts with allowed_root and doesn't escape via symlinks (optional check)
        return abs_path.startswith(allowed_root)
    except:
        return False

def scan_command_for_paths(command, allowed_root, current_dir):
    # This is a naive check for absolute paths or directory escapes in commands
    # 1. Look for absolute paths
    abs_paths = re.findall(r'/(?:[\w.-]+/)*[\w.-]*', command)
    for p in abs_paths:
        if not is_path_safe(p, allowed_root):
            return False, p
    
    # 2. Look for relative escapes
    if '..' in command:
        # Extract potential path strings containing '..'
        rel_paths = re.findall(r'(?:\.\./)+[\w.-]*', command)
        for p in rel_paths:
            resolved = os.path.normpath(os.path.join(current_dir, p))
            if not resolved.startswith(allowed_root):
                return False, resolved

    return True, None

def main():
    try:
        if not input_data:
            print(json.dumps({"decision": "proceed"}))
            return

        data = json.loads(input_data)
        tool = data.get('tool')
        args = data.get('arguments', {})
        cwd = data.get('dir_path', os.getcwd())
        
        # 1. Check direct path arguments
        target_path = args.get('file_path') or args.get('dir_path') or args.get('path')
        if target_path:
            if not is_path_safe(target_path, ALLOWED_ROOT):
                print(json.dumps({
                    "decision": "abort",
                    "message": f"SURGICAL LOCKDOWN: Unauthorized path '{target_path}'"
                }))
                return

        # 2. Check current working directory for execution
        if cwd:
            if not is_path_safe(cwd, ALLOWED_ROOT):
                print(json.dumps({
                    "decision": "abort",
                    "message": f"SURGICAL LOCKDOWN: Unauthorized execution directory '{cwd}'"
                }))
                return

        # 3. Special handling for shell commands (Deep Scan)
        if tool == "run_shell_command":
            command_str = args.get('command', '')
            safe, suspicious_path = scan_command_for_paths(command_str, ALLOWED_ROOT, cwd)
            if not safe:
                print(json.dumps({
                    "decision": "abort",
                    "message": f"SURGICAL LOCKDOWN: Suspicious path in command '{suspicious_path}'"
                }))
                return

        print(json.dumps({"decision": "proceed"}))
    except Exception as e:
        # In a "Hard-lock" mode, we might want to fail-closed, but for now, we'll allow on internal errors.
        # print(json.dumps({"decision": "abort", "message": f"GUARDRAIL ERROR: {str(e)}"}))
        print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
