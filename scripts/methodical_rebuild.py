#!/usr/bin/env python3
import os
import json
import glob
import subprocess
import sys
import shutil
import re
from datetime import datetime

# --- CONFIG ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root(os.getcwd())
VENV_PYTHON = os.path.join(AIM_ROOT, "venv/bin/python3")
TMP_CHATS_DIR = "/home/kingb/.gemini/tmp/aim/chats"
SUMMARIZER_PATH = os.path.join(AIM_ROOT, "hooks/session_summarizer.py")
DISTILLER_PATH = os.path.join(AIM_ROOT, "src/distiller.py")
PROPOSAL_DIR = os.path.join(AIM_ROOT, "memory/proposals")
MEMORY_PATH = os.path.join(AIM_ROOT, "core/MEMORY.md")

def commit_proposal(proposal_path):
    if not os.path.exists(proposal_path): return False
    try:
        with open(proposal_path, 'r') as f:
            content = f.read()
        if "### 3. MEMORY DELTA" not in content: return False
        delta_part = content.split("### 3. MEMORY DELTA")[1].strip()
        delta = re.sub(r"^```(markdown|md)?\n", "", delta_part)
        delta = re.sub(r"\n```$", "", delta).strip()
        with open(MEMORY_PATH, 'w') as f:
            f.write(delta)
        # Archive
        archive_dir = os.path.join(AIM_ROOT, "memory/archive")
        os.makedirs(archive_dir, exist_ok=True)
        os.rename(proposal_path, os.path.join(archive_dir, os.path.basename(proposal_path)))
        return True
    except Exception as e:
        print(f"      Commit Error: {e}")
        return False

def rebuild():
    print("--- A.I.M. METHODICAL MEMORY REBUILDER ---")
    
    # 1. Clean Slate
    print("Cleaning existing logs and pulses...")
    for d in [os.path.join(AIM_ROOT, "memory"), os.path.join(AIM_ROOT, "continuity")]:
        for f in glob.glob(os.path.join(d, "*.md")): os.remove(f)
    
    # 2. Gather Transcripts
    transcripts = glob.glob(os.path.join(TMP_CHATS_DIR, "session-*.json"))
    transcripts.sort()
    print(f"Found {len(transcripts)} sessions to process.")
    
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, 'w') as f: f.write("# MEMORY.md (REBUILD IN PROGRESS)\n")

    for i, t_path in enumerate(transcripts):
        session_name = os.path.basename(t_path)
        print(f"[{i+1}/{len(transcripts)}] Processing: {session_name}")
        
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
            proc = subprocess.Popen([VENV_PYTHON, SUMMARIZER_PATH], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            proc.communicate(input=json.dumps(payload))
            
            # B. DISTILL
            print(f"   -> Distilling (Date: {session_date})...")
            subprocess.run([VENV_PYTHON, DISTILLER_PATH, session_date], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # C. COMMIT
            proposals = glob.glob(os.path.join(PROPOSAL_DIR, "PROPOSAL_*.md"))
            if proposals:
                proposals.sort(reverse=True)
                latest = proposals[0]
                print(f"   -> Committing proposal: {os.path.basename(latest)}")
                if commit_proposal(latest):
                    print("   [OK] Memory updated.")
                else:
                    print("   [SKIP] Invalid delta.")
            else:
                print("   [SKIP] No proposal.")
                
        except Exception as e:
            print(f"   [ERROR] Turn {i+1}: {e}")

    print("\n[SUCCESS] Methodical rebuild complete.")

if __name__ == "__main__":
    rebuild()
