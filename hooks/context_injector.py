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
    from forensic_utils import get_embedding, ForensicDB
except ImportError:
    print(json.dumps({}))
    sys.exit(0)

def check_self_healing_sync(aim_root, venv_python):
    """Additive safety feature: Synchronizes manual edits with Engram DB."""
    try:
        db = ForensicDB()
        targets = [
            os.path.join(aim_root, "GEMINI.md"),
            os.path.join(aim_root, "docs/*.md"),
            os.path.join(aim_root, "core/*.md")
        ]
        needs_sync = False
        for pattern in targets:
            for file_path in glob.glob(pattern):
                filename = os.path.basename(file_path)
                session_id = f"foundation-{filename}"
                stored_mtime = db.get_session_mtime(session_id)
                current_mtime = os.path.getmtime(file_path)
                if current_mtime > stored_mtime:
                    needs_sync = True
                    break
            if needs_sync: break
        db.close()
        if needs_sync:
            subprocess.Popen([venv_python, os.path.join(aim_root, "src/bootstrap_brain.py")], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

def get_latest_pulse():
    continuity_dir = CONFIG['paths'].get('continuity_dir')
    if not continuity_dir: return None
    pulses = glob.glob(os.path.join(continuity_dir, "*.md"))
    if not pulses: return None
    pulses.sort(reverse=True)
    try:
        with open(pulses[0], 'r') as f: return f.read()
    except: return None

def main():
    try:
        # 1. Trigger Self-Healing Sync (Background)
        check_self_healing_sync(aim_root, venv_python)

        # 2. Parse Hook Input
        if not input_data:
            print(json.dumps({}))
            return
        
        data = json.loads(input_data)
        history = data.get('messages', []) or data.get('session_history', [])
        
        # --- PHASE 17: ONE-TIME BOOTLOADING ---
        # We only inject the Pulse if this is the start of the session
        if len(history) > 2:
            # We already have a conversation going; skip injection to save tokens.
            print(json.dumps({}))
            return

        injection_parts = []
        
        # Add Latest Pulse for Onboarding
        pulse = get_latest_pulse()
        if pulse:
            injection_parts.append(f"## 🔋 PROJECT MOMENTUM (LATEST PULSE)\n{pulse}")

        if not injection_parts:
            print(json.dumps({}))
            return

        final_injection = "\n--- [A.I.M. SESSION ONBOARDING] ---\n"
        final_injection += "\n\n---\n\n".join(injection_parts)
        final_injection += "\n\n--- [END ONBOARDING] ---\n"
        
        print(json.dumps({"content": final_injection}))

    except Exception:
        print(json.dumps({}))

if __name__ == "__main__":
    main()
