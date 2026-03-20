#!/usr/bin/env python3
import os
import json
import subprocess
import glob
import sys
from datetime import datetime

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

TMP_CHATS_DIR = CONFIG['paths']['tmp_chats_dir']
SUMMARIZER_PATH = os.path.join(CONFIG['paths']['hooks_dir'], "session_summarizer.py")
VENV_PYTHON = os.path.join(AIM_ROOT, "venv/bin/python3")

def back_populate():
    """Scans the tmp folder for session JSONs and runs the summarizer on them."""
    transcripts = glob.glob(os.path.join(TMP_CHATS_DIR, "session-*.json"))
    transcripts.sort() # Sort chronologically by filename
    
    print(f"A.I.M. Back-Populator: Found {len(transcripts)} session files in tmp.")
    
    for transcript_path in transcripts:
        print(f"Processing: {os.path.basename(transcript_path)}...")
        try:
            with open(transcript_path, 'r') as f:
                data = json.load(f)
            
            # Summarizer expects 'messages' or 'session_history'
            # It also handles raw transcript extraction if sessionId is present
            
            payload = {
                "session_id": data.get('sessionId'),
                "session_history": data.get('messages', []),
                "skip_distill": True # We don't want to generate pulses for old stuff yet
            }
            
            # Run the summarizer via subprocess
            process = subprocess.Popen(
                [VENV_PYTHON, SUMMARIZER_PATH],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=json.dumps(payload))
            
            if stderr:
                # sys.stderr.write(f"  Info: {stderr.strip()}\n")
                pass
            
            print(f"  Result: {stdout.strip()}")
                
        except Exception as e:
            print(f"  Failed to process {transcript_path}: {e}")

if __name__ == "__main__":
    back_populate()
