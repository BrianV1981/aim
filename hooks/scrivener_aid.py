#!/usr/bin/env python3
import os
import time
import json
import sys
import subprocess

# --- CONFIGURATION (Load from core/CONFIG.json) ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        config_path = os.path.join(current, "core/CONFIG.json")
        if os.path.exists(config_path):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root(os.getcwd())
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

CHECKPOINT_FILE = os.path.join(CONFIG['paths']['tmp_chats_dir'], "../last_scrivener_pulse")
INTERVAL_SECONDS = CONFIG['settings']['scrivener_interval_minutes'] * 60
SUMMARIZER_PATH = os.path.join(CONFIG['paths']['hooks_dir'], "session_summarizer.py")
VENV_PYTHON = os.path.join(AIM_ROOT, "venv/bin/python3")

def trigger_checkpoint(input_data):
    """Silently runs the summarizer hook during the session."""
    if os.path.exists(SUMMARIZER_PATH):
        try:
            data = json.loads(input_data)
            data['skip_distill'] = True
            modified_input = json.dumps(data)

            subprocess.Popen([VENV_PYTHON, SUMMARIZER_PATH], 
                             stdin=subprocess.PIPE,
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL,
                             text=True).communicate(input=modified_input)
            return True
        except Exception:
            return False
    return False

def main():
    try:
        # 1. Read input from Gemini CLI
        input_data = sys.stdin.read()
        if not input_data:
            print(json.dumps({}))
            return
        
        # --- PILLAR B: ROLLING INTERIM BACKUP (Every Turn) ---
        # This is a zero-token local write. We do this on every tool call
        # to ensure crash recovery is always up-to-the-second.
        backup_path = os.path.join(AIM_ROOT, "continuity/INTERIM_BACKUP.json")
        try:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            with open(backup_path, 'w') as bf:
                bf.write(input_data)
        except: pass
        # -----------------------------------------------------

        # 2. Check the last checkpoint time for AI-based summary
        os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)
        now = time.time()
        
        if not os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, "w") as f:
                f.write(str(now))
            print(json.dumps({}))
            return

        try:
            with open(CHECKPOINT_FILE, "r") as f:
                last_pulse = float(f.read().strip())
        except:
            last_pulse = 0

        # 3. If interval exceeded, trigger expensive summary checkpoint
        if now - last_pulse > INTERVAL_SECONDS:
            with open(CHECKPOINT_FILE, "w") as f:
                f.write(str(now))
            
            trigger_checkpoint(input_data)
                
            reminder = "\n\n[SCRIVENER'S AID: Active Checkpoint Performed. Your progress has been incrementalized.]\n"
            print(json.dumps({
                "message": reminder
            }))
        else:
            # Just return empty, but we've already saved the interim backup!
            print(json.dumps({}))

    except Exception:
        print(json.dumps({}))

if __name__ == "__main__":
    main()
