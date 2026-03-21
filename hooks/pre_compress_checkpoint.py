#!/usr/bin/env python3
import os
import json
import sys
import subprocess

# --- VENV BOOTSTRAP ---
hook_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(hook_dir)
venv_python = os.path.join(aim_root, "venv/bin/python3")

# PreCompress provides the FULL session history in stdin
input_data = sys.stdin.read()

if os.path.exists(venv_python) and sys.executable != venv_python:
    try:
        process = subprocess.run([venv_python] + sys.argv, input=input_data, text=True, capture_output=True)
        print(process.stdout)
        sys.exit(process.returncode)
    except Exception: pass

# --- LOGIC ---
SUMMARIZER_PATH = os.path.join(hook_dir, "session_summarizer.py")

def main():
    try:
        if not input_data:
            print(json.dumps({"decision": "proceed"}))
            return

        # We trigger the summarizer IMMEDIATELY before the CLI prunes the history
        # We set skip_distill=True because we don't want a full pulse yet, just the archival
        data = json.loads(input_data)
        data['skip_distill'] = True
        
        sys.stderr.write("[SHIELD] Pre-Compression Checkpoint Triggered. Archiving history...\n")
        
        subprocess.run(
            [venv_python, SUMMARIZER_PATH],
            input=json.dumps(data),
            text=True,
            capture_output=True
        )

        # Tell the CLI to proceed with its compression
        print(json.dumps({"decision": "proceed"}))

    except Exception:
        print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
