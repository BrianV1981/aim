#!/usr/bin/env python3
import os
import json
import glob
import subprocess
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
src_dir = os.path.join(aim_root, 'src')
if src_dir not in sys.path: sys.path.append(src_dir)
import shutil
import re
from datetime import datetime

# --- CONFIG ---
from config_utils import CONFIG, AIM_ROOT
from memory_utils import commit_proposal
VENV_PYTHON = os.path.join(AIM_ROOT, "venv/bin/python3")
TMP_CHATS_DIR = CONFIG['paths'].get('tmp_chats_dir')
SUMMARIZER_PATH = os.path.join(AIM_ROOT, "hooks/tier1_hourly_summarizer.py")
DISTILLER_PATH = os.path.join(AIM_ROOT, "src/handoff_pulse_generator.py")
PROPOSAL_DIR = os.path.join(AIM_ROOT, "memory/proposals")
MEMORY_PATH = os.path.join(AIM_ROOT, "core/MEMORY.md")

def rebuild():
    print("--- A.I.M. METHODICAL MEMORY REBUILDER ---")
    
    # 1. Clean Slate
    print("Cleaning existing logs and pulses...")
    for d in [os.path.join(AIM_ROOT, "memory"), os.path.join(AIM_ROOT, "continuity")]:
        for f in glob.glob(os.path.join(d, "*.md")): os.remove(f)
    
    # 2. Gather Transcripts
    transcripts = glob.glob(os.path.join(TMP_CHATS_DIR, "session-*.json"))
    
    stamped_files = []
    for t in transcripts:
        try:
            with open(t, 'r') as f:
                data = json.load(f)
                ts = data['messages'][0]['timestamp'] if data.get('messages') else '0000'
                stamped_files.append((t, ts))
        except: pass
    
    stamped_files.sort(key=lambda x: x[1]) # Chronological
    print(f"Found {len(stamped_files)} sessions to process.")
    
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, 'w') as f: f.write("# MEMORY.md (REBUILD IN PROGRESS)\n")

    for i, (t_path, _) in enumerate(stamped_files):
        session_name = os.path.basename(t_path)
        print(f"[{i+1}/{len(stamped_files)}] Processing: {session_name}")
        
        try:
            with open(t_path, 'r') as f:
                data = json.load(f)
            
            # Extract date for distiller
            session_date = None
            for msg in data.get('messages', []):
                if 'timestamp' in msg:
                    try:
                        session_date = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00')).strftime("%Y-%m-%d")
                        break
                    except: pass
            
            if not session_date: session_date = datetime.now().strftime("%Y-%m-%d")

            payload = {
                "session_id": data.get('sessionId'),
                "session_history": data.get('messages', []),
                "skip_distill": True
            }
            
            # A. SUMMARIZE
            print("   -> Summarizing...")
            subprocess.run([VENV_PYTHON, SUMMARIZER_PATH], input=json.dumps(payload), text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # B. DISTILL
            print(f"   -> Distilling (Date: {session_date})...")
            subprocess.run([VENV_PYTHON, DISTILLER_PATH, session_date], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # C. COMMIT
            print(f"   -> Committing proposal...")
            if commit_proposal(AIM_ROOT):
                print("   [OK] Memory updated.")
            else:
                print("   [SKIP] No proposal committed.")
                
        except Exception as e:
            print(f"   [ERROR] Turn {i+1}: {e}")

    print("\n[SUCCESS] Methodical rebuild complete.")

if __name__ == "__main__":
    rebuild()
