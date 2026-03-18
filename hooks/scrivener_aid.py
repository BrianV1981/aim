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
    return "/home/kingb/aim"

AIM_ROOT = find_aim_root(os.getcwd())
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

CHECKPOINT_FILE = os.path.join(CONFIG['paths']['tmp_chats_dir'], "../last_scrivener_pulse")
INTERVAL_SECONDS = CONFIG['settings']['scrivener_interval_minutes'] * 60
SUMMARIZER_PATH = os.path.join(CONFIG['paths']['hooks_dir'], "session_summarizer.py")

def trigger_checkpoint(input_data):
    """Silently runs the summarizer hook during the session."""
    if os.path.exists(SUMMARIZER_PATH):
        try:
            # We pass the same input data (session_id, history) to the summarizer
            subprocess.Popen([sys.executable, SUMMARIZER_PATH], 
                             stdin=subprocess.PIPE,
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL,
                             text=True).communicate(input=input_data)
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
        
        # 2. Check the last checkpoint time
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

        # 3. If interval exceeded, trigger silent checkpoint
        if now - last_pulse > INTERVAL_SECONDS:
            with open(CHECKPOINT_FILE, "w") as f:
                f.write(str(now))
            
            # --- PILLAR B: ROLLING INTERIM BACKUP ---
            backup_path = os.path.join(AIM_ROOT, "continuity/INTERIM_BACKUP.json")
            try:
                # We save the raw history to a dedicated recovery file
                with open(backup_path, 'w') as bf:
                    bf.write(input_data)
            except: pass
            # ----------------------------------------

            # RUN THE SUMMARY & DISTILLATION LOOP
            trigger_checkpoint(input_data)
                
            reminder = "\n\n[SCRIVENER'S AID: Active Checkpoint Performed. Your current progress has been distilled into the Daily Log and Context Pulse. Continue.]\n"
            print(json.dumps({
                "message": reminder
            }))
        else:
            print(json.dumps({}))

    except Exception:
        # Silently proceed on error to avoid breaking the CLI tool loop
        print(json.dumps({}))

if __name__ == "__main__":
    main()
