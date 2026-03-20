#!/usr/bin/env python3
import sys
import json
import os
import shutil
import glob
import subprocess
import time
from datetime import datetime

# --- CONFIG BOOTSTRAP ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root(os.getcwd())
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

if not os.path.exists(CONFIG_PATH):
    sys.exit(0)

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

TMP_CHATS_DIR = CONFIG['paths'].get('tmp_chats_dir')
ARCHIVE_RAW_DIR = CONFIG['paths'].get('archive_raw_dir')
DAILY_LOG_DIR = CONFIG['paths'].get('memory_dir')
SRC_DIR = CONFIG['paths'].get('src_dir')
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
    """NON-AI: Extracts technical essence deterministically."""
    if not history: return "No new activity recorded."
    
    notes = []
    for msg in history:
        m_type = msg.get('type')
        if m_type == 'user':
            content = msg.get('content', [])
            text = " ".join([c.get('text', '') for c in content if 'text' in c])
            if text: notes.append(f"- [USER] {text[:300]}...")
        elif m_type == 'gemini':
            # Log model's own statements if concise
            body = msg.get('content', '')
            if body and len(body) < 500:
                notes.append(f"- [A.I.M.] {body.strip()}")
            # Log all tool actions
            for call in msg.get('toolCalls', []):
                notes.append(f"- [ACTION] {call.get('name')} -> {json.dumps(call.get('args'))[:200]}...")
    
    return "\n".join(notes) if notes else "No new activity recorded."

def find_raw_history(session_id):
    """Deep search for the transcript JSON on disk if hook payload is empty."""
    if not session_id or not TMP_CHATS_DIR: return []
    
    # Priority 1: Check existing archive
    pattern = os.path.join(ARCHIVE_RAW_DIR, f"*{session_id}*.json")
    matches = glob.glob(pattern)
    
    # Priority 2: Check global tmp folder
    if not matches:
        pattern = os.path.join(TMP_CHATS_DIR, f"*{session_id}*.json")
        matches = glob.glob(pattern)
        
    if matches:
        # Get newest match
        source = max(matches, key=os.path.getmtime)
        try:
            with open(source, 'r') as f:
                data = json.load(f)
                return data.get('messages') or data.get('session_history') or []
        except: pass
    return []

def get_last_processed_index(log_path, session_id):
    """Stateful tracking: find where we left off in this log file."""
    if not os.path.exists(log_path): return 0
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
            for i in range(len(lines)-1, -1, -1):
                if f"Session ID: `{session_id}`" in lines[i]:
                    # Search nearby lines for the last index marker
                    for j in range(i, min(i+10, len(lines))):
                        if "Last Index: `" in lines[j]:
                            return int(lines[j].split("`")[1])
    except: pass
    return 0

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data: sys.exit(0)
        if not acquire_lock(): sys.exit(0)

        data = json.loads(input_data)
        session_id = data.get('session_id') or data.get('sessionId')
        history = data.get('session_history') or data.get('messages') or []
        skip_distill = data.get('skip_distill', False)
        
        # If history is missing from hook (common in AfterTool), go find it on disk
        if not history:
            history = find_raw_history(session_id)

        today = datetime.now().strftime("%Y-%m-%d")
        os.makedirs(DAILY_LOG_DIR, exist_ok=True)
        log_path = os.path.join(DAILY_LOG_DIR, f"{today}.md")
        
        last_index = get_last_processed_index(log_path, session_id)
        # We only log messages that haven't been written to THIS log file yet
        new_history = history[last_index:]
        
        if new_history:
            with open(log_path, "a") as f:
                f.write(f"\n\n## Session Log: {datetime.now().strftime('%H:%M:%S')}\n")
                f.write(f"Session ID: `{session_id}`\n")
                f.write(f"Last Index: `{len(history)}`\n")
                f.write("\nScrivener Notes (Technical Trace):\n")
                f.write(get_scrivener_notes(new_history))
                f.write("\n---\n")

        # Distillation (The AI Part) only runs on SessionEnd (when skip_distill is False)
        if not skip_distill:
            distiller_path = os.path.join(SRC_DIR, "distiller.py")
            venv_python = os.path.join(AIM_ROOT, "venv/bin/python3")
            if os.path.exists(distiller_path):
                subprocess.run([venv_python, distiller_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(json.dumps({"decision": "proceed"}))
    except Exception:
        print(json.dumps({"decision": "proceed"}))
    finally:
        release_lock()

if __name__ == "__main__":
    main()
