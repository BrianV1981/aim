#!/usr/bin/env python3
import os
import json
import glob
import subprocess
import sys
import time
import re
from datetime import datetime

# --- CONFIG ---
hook_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(hook_dir)
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

from reasoning_utils import generate_reasoning, AIM_ROOT

VENV_PYTHON = os.path.join(AIM_ROOT, "venv/bin/python3")
from config_utils import CONFIG
from memory_utils import commit_proposal
CHATS_DIR = CONFIG['paths'].get('tmp_chats_dir')
SUMMARIZER_PATH = os.path.join(AIM_ROOT, "hooks/tier1_hourly_summarizer.py")
DISTILLER_PATH = os.path.join(AIM_ROOT, "src/handoff_pulse_generator.py")
MEMORY_PATH = os.path.join(AIM_ROOT, "core/MEMORY.md")
PROPOSAL_DIR = os.path.join(AIM_ROOT, "memory/proposals")

def restore():
    print("\n--- A.I.M. DEEP FORENSIC RESTORATION ---")
    
    # 1. Purge Corrupted Files
    print("Purging corrupted logs and resetting core memory...")
    for f in glob.glob(os.path.join(AIM_ROOT, "memory/*.md")): os.remove(f)
    for f in glob.glob(os.path.join(PROPOSAL_DIR, "*.md")): os.remove(f)
    with open(MEMORY_PATH, 'w') as f:
        f.write("# A.I.M. CORE MEMORY (RECONSTRUCTION IN PROGRESS)\n")

    # 2. Identify and Sort Transcripts (OLDEST FIRST)
    transcripts = glob.glob(os.path.join(CHATS_DIR, "session-*.json"))
    
    # High-fidelity sorting: extract internal timestamp
    stamped_files = []
    for t in transcripts:
        try:
            with open(t, 'r') as f:
                data = json.load(f)
                ts = data['messages'][0]['timestamp'] if data.get('messages') else '0000'
                stamped_files.append((t, ts))
        except: pass
    
    stamped_files.sort(key=lambda x: x[1]) # Chronological
    
    print(f"Ready to process {len(stamped_files)} sessions chronologically with rate-limit protection.")

    for i, (t_path, _) in enumerate(stamped_files):
        session_name = os.path.basename(t_path)
        print(f"\n[{i+1}/{len(stamped_files)}] RESTORING: {session_name}")
        
        try:
            with open(t_path, 'r') as f:
                data = json.load(f)
            
            # Extract date for this specific turn
            session_date = datetime.now().strftime("%Y-%m-%d")
            if data.get('messages') and 'timestamp' in data['messages'][0]:
                session_date = data['messages'][0]['timestamp'].split('T')[0]

            payload = {
                "session_id": data.get('sessionId'),
                "session_history": data.get('messages', []),
                "skip_distill": True
            }
            
            # A. SUMMARIZE (Write to Narrative Log)
            print("   -> Generating Narrative Log Entry...")
            proc = subprocess.Popen([VENV_PYTHON, SUMMARIZER_PATH], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            proc.communicate(input=json.dumps(payload))
            
            # B. DISTILL (Create Memory Proposal)
            print(f"   -> Extracting Durable Truths (Date: {session_date})...")
            subprocess.run([VENV_PYTHON, DISTILLER_PATH, session_date], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # C. COMMIT (Apply to Memory.md immediately)
            print(f"   -> Committing Architectural Update...")
            commit_proposal(AIM_ROOT)
            
            # D. RATE LIMIT PROTECTION
            if i < len(stamped_files) - 1:
                print("   -> Respecting API Quotas (Waiting 60s)...")
                time.sleep(60)
                
        except Exception as e:
            print(f"   [ERROR] Turn {i+1} failed: {e}")

    print("\n[SUCCESS] Total Memory Restoration Complete.")

if __name__ == "__main__":
    restore()
