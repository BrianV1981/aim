#!/usr/bin/env python3
import os
import time
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
    except Exception: pass

# --- LOGIC ---
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

try:
    from config_utils import CONFIG, AIM_ROOT
except ImportError:
    print(json.dumps({}))
    sys.exit(0)

CHECKPOINT_FILE = os.path.join(CONFIG['paths']['tmp_chats_dir'], "../last_scrivener_pulse")
INTERVAL_SECONDS = CONFIG['settings'].get('scrivener_interval_minutes', 30) * 60
SUMMARIZER_PATH = os.path.join(CONFIG['paths']['hooks_dir'], "session_summarizer.py")

def trigger_checkpoint(data_string):
    """Silently runs the summarizer hook during the session."""
    if os.path.exists(SUMMARIZER_PATH):
        try:
            data = json.loads(data_string)
            data['skip_distill'] = True
            modified_input = json.dumps(data)

            # --- TRUE BACKGROUND EXECUTION ---
            # We use subprocess.Popen without communicate() to truly detach
            subprocess.Popen(
                [venv_python, SUMMARIZER_PATH], 
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                text=True,
                start_new_session=True 
            ).stdin.write(modified_input)
            return True
        except Exception: return False
    return False

def main():
    try:
        if not input_data:
            print(json.dumps({}))
            return
        
        # 1. PILLAR B: ROLLING INTERIM BACKUP
        backup_path = os.path.join(AIM_ROOT, "continuity/INTERIM_BACKUP.json")
        try:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            with open(backup_path, 'w') as bf:
                bf.write(input_data)
            
            # PHASE 17: Mirror global transcripts to local archive
            porter_path = os.path.join(AIM_ROOT, "scripts/session_porter.py")
            if os.path.exists(porter_path):
                subprocess.run([venv_python, porter_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass

        # 2. PERIODIC CHECKPOINT
        try:
            os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)
            now = time.time()
            
            if not os.path.exists(CHECKPOINT_FILE):
                with open(CHECKPOINT_FILE, "w") as f: f.write(str(now))
                print(json.dumps({}))
                return

            with open(CHECKPOINT_FILE, "r") as f:
                last_pulse = float(f.read().strip())

            if now - last_pulse > INTERVAL_SECONDS:
                with open(CHECKPOINT_FILE, "w") as f: f.write(str(now))
                trigger_checkpoint(input_data)
                # Note: We don't print a message here to keep shell output clean in YOLO mode
                print(json.dumps({}))
            else:
                print(json.dumps({}))
        except:
            print(json.dumps({}))

    except Exception: 
        print(json.dumps({}))

if __name__ == "__main__":
    main()
