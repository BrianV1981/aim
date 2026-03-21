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
# --- ADD SRC TO PATH FOR FORENSIC UTILS ---
sys.path.append(os.path.join(AIM_ROOT, "src"))
try:
    from forensic_utils import ForensicDB
except ImportError:
    ForensicDB = None

CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

if not os.path.exists(CONFIG_PATH):
    sys.exit(0)

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

ARCHIVE_RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")
STATE_FILE = os.path.join(AIM_ROOT, "archive/scrivener_state.json")
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

def prune_archive_raw():
    """Prunes archive/raw/ of transcripts older than 24 hours."""
    try:
        now = time.time()
        count = 0
        for f in glob.glob(os.path.join(ARCHIVE_RAW_DIR, "*.json")):
            if now - os.path.getmtime(f) > 86400: # 24 hours
                os.remove(f)
                count += 1
        if count > 0:
            sys.stderr.write(f"[SCRIVENER] Pruned {count} old transcripts from archive/raw/\n")
    except Exception as e:
        sys.stderr.write(f"[SCRIVENER] Pruning error: {e}\n")

def get_scrivener_notes(history):
    if not history: return "No technical actions detected."
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
                notes.append(f"- [A.I.M.] {str(body).strip()}")
            tool_calls = msg.get('toolCalls') or msg.get('tool_calls') or []
            for call in tool_calls:
                name = call.get('name') or call.get('function', {}).get('name')
                args = call.get('args') or call.get('function', {}).get('arguments')
                notes.append(f"- [ACTION] {name} -> {json.dumps(args)[:200]}...")
    return "\n".join(notes) if notes else "Technical trace complete."

def get_last_processed_index(session_id):
    """
    High-Fidelity State Lookup:
    Transitioned from brittle Markdown parsing to dedicated JSON state.
    """
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                return state.get(session_id, 0)
        except Exception as e:
            sys.stderr.write(f"[SCRIVENER] State read error: {e}\n")
    return 0

def update_last_processed_index(session_id, index):
    """Updates the high-fidelity JSON state file."""
    state = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
        except: pass
    
    state[session_id] = index
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        sys.stderr.write(f"[SCRIVENER] State write error: {e}\n")

def process_local_transcript(transcript_path, ignore_temporal=False):
    """Processes a single local transcript into the daily log with Temporal Filtering."""
    try:
        with open(transcript_path, 'r') as f:
            data = json.load(f)
        
        session_id = data.get('sessionId') or data.get('session_id')
        history = data.get('messages', [])
        if not session_id or not history: return False

        today_str = datetime.now().strftime("%Y-%m-%d")
        os.makedirs(DAILY_LOG_DIR, exist_ok=True)
        log_path = os.path.join(DAILY_LOG_DIR, f"{today_str}.md")
        
        last_index = get_last_processed_index(session_id)
        
        if last_index >= len(history):
            return False

        # Temporal Filtering: Only process messages from today (unless overridden)
        new_history = []
        for i in range(last_index, len(history)):
            msg = history[i]
            ts = msg.get('timestamp', '')
            # Strictly ignore if ts mismatch today AND not overridden
            if ignore_temporal or not ts or ts.startswith(today_str):
                new_history.append(msg)
        
        if new_history:
            sys.stderr.write(f"[SCRIVENER] Appending {len(new_history)} turns for {session_id[:8]}...\n")
            with open(log_path, "a") as f:
                f.write(f"\n\n## Session Log: {datetime.now().strftime('%H:%M:%S')}\n")
                f.write(f"Session ID: `{session_id}`\n")
                f.write(f"Last Index: `{len(history)}`\n") # Still log the total index for reference
                f.write("\nScrivener Notes (Technical Trace):\n")
                f.write(get_scrivener_notes(new_history))
                f.write("\n---\n")
        
        # Always update index to current length to avoid re-processing old turns
        update_last_processed_index(session_id, len(history))
        return True if new_history else False

    except Exception as e:
        sys.stderr.write(f"[SCRIVENER ERROR] {transcript_path}: {e}\n")
    return False

def main():
    try:
        input_data = sys.stdin.read()
        if not acquire_lock(): sys.exit(0)

        # Cleanup Routine: Keep the processing pool lean
        prune_archive_raw()

        # Check for flags in input data
        ignore_temporal = False
        skip_distill = True
        try:
            if input_data:
                data = json.loads(input_data)
                ignore_temporal = data.get('ignore_temporal', False)
                skip_distill = data.get('skip_distill', False)
        except: pass

        # In the new PORTER-PROCESSOR model, we loop through ALL local raw transcripts
        # This ensures multi-agent compatibility.
        transcripts = glob.glob(os.path.join(ARCHIVE_RAW_DIR, "*.json"))
        updated_count = 0
        for t_path in transcripts:
            if process_local_transcript(t_path, ignore_temporal=ignore_temporal):
                updated_count += 1

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
