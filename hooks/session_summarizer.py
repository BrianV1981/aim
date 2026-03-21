#!/usr/bin/env python3
import sys
import json
import os
import shutil
import glob
import subprocess
import time
import re
from datetime import datetime

# --- DYNAMIC ROOT DISCOVERY ---
def find_aim_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
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
    if not history: return "No activity detected."
    notes = []
    for msg in history:
        m_type = msg.get('role') or msg.get('type')
        if m_type == 'user':
            content = msg.get('content', [])
            text = " ".join([c.get('text', '') for c in content if 'text' in c]) if isinstance(content, list) else content
            if text: notes.append(f"- [USER] {str(text)[:300]}...")
        elif m_type in ['gemini', 'model']:
            body = msg.get('content', '')
            if body and len(body) < 500:
                notes.append(f"- [A.I.M.] {body.strip()}")
            tool_calls = msg.get('toolCalls') or msg.get('tool_calls') or []
            for call in tool_calls:
                name = call.get('name') or call.get('function', {}).get('name')
                args = call.get('args') or call.get('function', {}).get('arguments')
                notes.append(f"- [ACTION] {name} -> {json.dumps(args)[:200]}...")
    return "\n".join(notes) if notes else "Technical trace complete."

def find_raw_history(session_id):
    if not session_id: return []
    for d in [ARCHIVE_RAW_DIR, TMP_CHATS_DIR]:
        if not d or not os.path.exists(d): continue
        pattern = os.path.join(d, f"*{session_id}*.json")
        matches = glob.glob(pattern)
        if matches:
            source = max(matches, key=os.path.getmtime)
            try:
                with open(source, 'r') as f:
                    data = json.load(f)
                    return data.get('messages') or data.get('session_history') or []
            except: pass
    return []

def get_last_processed_index(log_path, session_id):
    """Bulletproof: Simple string search if regex fails."""
    if not os.path.exists(log_path): return 0
    try:
        with open(log_path, 'r') as f:
            content = f.read()
        
        # Split by session ID to find the relevant block
        if session_id in content:
            # Find the LAST occurrence of Last Index after the session_id
            parts = content.split(session_id)
            last_segment = parts[-1]
            idx_matches = re.findall(r"Last Index:\s*[`']?(\d+)[`']?", last_segment)
            if idx_matches:
                return int(idx_matches[-1])
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
        
        if not history:
            history = find_raw_history(session_id)

        today = datetime.now().strftime("%Y-%m-%d")
        os.makedirs(DAILY_LOG_DIR, exist_ok=True)
        log_path = os.path.join(DAILY_LOG_DIR, f"{today}.md")
        
        last_index = get_last_processed_index(log_path, session_id)
        new_history = history[last_index:]
        
        if new_history:
            sys.stderr.write(f"[DEBUG] Scrivener: Appending {len(new_history)} turns starting from index {last_index}\n")
            with open(log_path, "a") as f:
                f.write(f"\n\n## Session Log: {datetime.now().strftime('%H:%M:%S')}\n")
                f.write(f"Session ID: `{session_id}`\n")
                f.write(f"Last Index: `{len(history)}`\n")
                f.write("\nScrivener Notes (Technical Trace):\n")
                f.write(get_scrivener_notes(new_history))
                f.write("\n---\n")

        if not skip_distill:
            distiller_path = os.path.join(SRC_DIR, "distiller.py")
            venv_python = os.path.join(AIM_ROOT, "venv/bin/python3")
            if os.path.exists(distiller_path):
                subprocess.run([venv_python, distiller_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(json.dumps({"decision": "proceed"}))
    except Exception as e:
        sys.stderr.write(f"[SCRIVENER ERROR] {e}\n")
        print(json.dumps({"decision": "proceed"}))
    finally:
        release_lock()

if __name__ == "__main__":
    main()
