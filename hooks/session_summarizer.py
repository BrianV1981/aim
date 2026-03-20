#!/usr/bin/env python3
import sys
import json
import os
import shutil
import glob
import subprocess
import time
from datetime import datetime

# --- CONFIG ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root(os.getcwd())
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

TMP_CHATS_DIR = CONFIG['paths']['tmp_chats_dir']
ARCHIVE_RAW_DIR = CONFIG['paths']['archive_raw_dir']
DAILY_LOG_DIR = CONFIG['paths']['memory_dir']
SRC_DIR = CONFIG['paths']['src_dir']
LOCK_FILE = os.path.join(AIM_ROOT, ".aim.lock")

def acquire_lock(timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except FileExistsError:
            time.sleep(0.5)
    return False

def release_lock():
    if os.path.exists(LOCK_FILE):
        try: os.remove(LOCK_FILE)
        except: pass

def get_scrivener_notes(history):
    """NON-AI: Determinstically extracts the technical essence from messages."""
    if not history: return "No new activity."
    
    notes = []
    for msg in history:
        m_type = msg.get('type')
        if m_type == 'user':
            text = " ".join([c.get('text', '') for c in msg.get('content', []) if 'text' in c])
            notes.append(f"- [USER] {text[:300]}...")
        elif m_type == 'gemini':
            for call in msg.get('toolCalls', []):
                notes.append(f"- [ACTION] Executed {call.get('name')} with {json.dumps(call.get('args'))[:200]}...")
    
    return "\n".join(notes)

def archive_transcript(session_id):
    if not session_id or not TMP_CHATS_DIR: return None
    pattern = os.path.join(TMP_CHATS_DIR, f"*{session_id}*.json")
    matches = glob.glob(pattern)
    if matches:
        source = max(matches, key=os.path.getmtime)
        os.makedirs(ARCHIVE_RAW_DIR, exist_ok=True)
        destination = os.path.join(ARCHIVE_RAW_DIR, os.path.basename(source))
        shutil.copy2(source, destination)
        return destination
    return None

def trigger_distillation():
    """AI Part: Distillation stays AI-powered."""
    distiller_path = os.path.join(SRC_DIR, "distiller.py")
    venv_python = os.path.join(AIM_ROOT, "venv/bin/python3")
    if os.path.exists(distiller_path):
        subprocess.run([venv_python, distiller_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    return False

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data: sys.exit(0)
        if not acquire_lock(): sys.exit(0)

        data = json.loads(input_data)
        session_id = data.get('session_id') or data.get('sessionId')
        history = data.get('session_history') or data.get('messages') or []
        skip_distill = data.get('skip_distill', False)
        
        archived_path = archive_transcript(session_id)
        
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(DAILY_LOG_DIR, f"{today}.md")
        
        with open(log_path, "a") as f:
            f.write(f"\n\n## Session Log: {datetime.now().strftime('%H:%M:%S')}\n")
            f.write(f"Session ID: `{session_id}`\n")
            if archived_path:
                f.write(f"Archive: `archive/raw/{os.path.basename(archived_path)}` (Forensic Saved)\n")
            f.write("\nScrivener Notes (Raw History):\n")
            f.write(get_scrivener_notes(history))
            f.write("\n---\n")

        if not skip_distill:
            trigger_distillation()

        print(json.dumps({"decision": "proceed"}))
    except Exception as e:
        print(json.dumps({"decision": "proceed"}))
    finally:
        release_lock()

if __name__ == "__main__":
    main()
