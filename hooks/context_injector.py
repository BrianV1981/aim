#!/usr/bin/env python3
import os
import json
import glob
import sys
import subprocess
import math
from datetime import datetime

# --- VENV BOOTSTRAP ---
hook_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(hook_dir)
venv_python = os.path.join(aim_root, "venv/bin/python3")

if os.path.exists(venv_python) and sys.executable != venv_python:
    try:
        process = subprocess.run([venv_python] + sys.argv, input=sys.stdin.read(), text=True, capture_output=True)
        print(process.stdout)
        sys.exit(process.returncode)
    except Exception: pass

# --- LOGIC ---
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

try:
    from config_utils import CONFIG, AIM_ROOT
    from forensic_utils import get_embedding, ForensicDB
except ImportError:
    print(json.dumps({}))
    sys.exit(0)

def get_specialist_pointer(cwd):
    """Detects if this folder requires a specialized sub-agent."""
    pointer_path = os.path.join(cwd, "SPECIALIST.md")
    if os.path.exists(pointer_path):
        try:
            with open(pointer_path, 'r') as f:
                return f.read()
        except: pass
    return None

def main():
    try:
        cwd = os.getcwd()
        injection_parts = []
        
        # 1. SPECIALIST POINTER (New Architecture)
        specialist_info = get_specialist_pointer(cwd)
        if specialist_info:
            injection_parts.append(f"## 🤖 SPECIALIST DIRECTIVE DETECTED\n{specialist_info}")

        # 2. Add other context (Git Delta, Pulse, etc.) here if needed
        # ...

        if not injection_parts:
            print(json.dumps({}))
            return

        final_injection = "\n--- [A.I.M. CONTEXT FLYWHEEL] ---\n"
        final_injection += "\n\n---\n\n".join(injection_parts)
        final_injection += "\n\n--- [END INJECTION] ---\n"
        
        print(json.dumps({"content": final_injection}))

    except Exception:
        print(json.dumps({}))

if __name__ == "__main__":
    main()
