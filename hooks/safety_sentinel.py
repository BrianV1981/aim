#!/usr/bin/env python3
import os
import json
import sys
import re

# --- CONFIGURATION ---
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

ALLOWED_ROOT = "/home/kingb"

def is_dangerous(command):
    """Checks the command string against known dangerous patterns."""
    for pattern in DANGER_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return f"Danger Pattern Detected: '{pattern}'"
    return None

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            print(json.dumps({}))
            return

        data = json.loads(input_data)
        
        # BeforeTool payload for run_shell_command contains 'command' in args
        args = data.get('arguments', {})
        cmd = args.get('command', '')
        cwd = data.get('dir_path', os.getcwd())

        # 1. Pattern Check
        reason = is_dangerous(cmd)
        if reason:
            error_msg = f"SAFETY SENTINEL ALERT: Command blocked for security reasons. {reason}"
            print(json.dumps({
                "decision": "abort",
                "message": error_msg
            }))
            return

        # 2. Path Check (Ensuring we stay in A.I.M. territory for sensitive commands)
        # We allow reading anywhere in /home/kingb, but restrict certain shell operations.
        if "rm " in cmd and not cwd.startswith(ALLOWED_ROOT):
            error_msg = f"SAFETY SENTINEL ALERT: Shell deletion blocked outside of authorized workspace: {ALLOWED_ROOT}"
            print(json.dumps({
                "decision": "abort",
                "message": error_msg
            }))
            return

        # If everything looks good, proceed
        print(json.dumps({"decision": "proceed"}))

    except Exception as e:
        # Default to safe mode: proceed if we can't parse
        print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
