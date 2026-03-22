#!/usr/bin/env python3
import sys
import json
import os
import shutil
import glob
import subprocess
import time
import re
import select
from datetime import datetime

# --- DYNAMIC ROOT DISCOVERY ---
def find_aim_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
# --- ADD SRC AND SCRIPTS TO PATH ---
sys.path.append(os.path.join(AIM_ROOT, "src"))
sys.path.append(os.path.join(AIM_ROOT, "scripts"))

try:
    from forensic_utils import ForensicDB
except ImportError:
    ForensicDB = None

try:
    from reasoning_utils import generate_reasoning
except ImportError:
    generate_reasoning = None

try:
    from extract_signal import extract_signal
except ImportError:
    extract_signal = None

CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

if not os.path.exists(CONFIG_PATH):
    sys.exit(0)

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

ARCHIVE_RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")
STATE_FILE = os.path.join(AIM_ROOT, "archive/scrivener_state.json")
HOURLY_LOG_DIR = os.path.join(CONFIG['paths'].get('memory_dir'), "hourly")
SRC_DIR = CONFIG['paths'].get('src_dir')
LOCK_FILE = os.path.join(AIM_ROOT, ".aim.lock")

# --- AI NARRATOR PROMPT ---
NARRATOR_SYSTEM = "You are a Surgical Technical Scribe. Convert this Signal Skeleton into a concise, 3-5 sentence technical history. Focus ONLY on logic shifts, bug fixes, and file paths. ZERO FLUFF. Target context: Handoff for the next agent."

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

def get_state(session_id):
    """Returns (last_indexed_turn, last_narrated_turn)"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                val = state.get(session_id, 0)
                if isinstance(val, dict):
                    return val.get('last_indexed_turn', 0), val.get('last_narrated_turn', 0)
                else:
                    # Migration: Old format was just an integer (last_indexed)
                    return val, 0
        except: pass
    return 0, 0

def update_state(session_id, last_indexed_turn=None, last_narrated_turn=None):
    state = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
        except: pass
    
    current = state.get(session_id, {})
    if not isinstance(current, dict):
        current = {"last_indexed_turn": current, "last_narrated_turn": 0}
    
    if last_indexed_turn is not None:
        current["last_indexed_turn"] = last_indexed_turn
    if last_narrated_turn is not None:
        current["last_narrated_turn"] = last_narrated_turn
        
    state[session_id] = current
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        sys.stderr.write(f"[SCRIVENER] State write error: {e}\n")

def recursive_narrate(skeleton_json, level=0):
    """Subdivides if the skeleton exceeds 250KB for efficiency."""
    skeleton_str = json.dumps(skeleton_json, indent=2)
    size_kb = len(skeleton_str.encode('utf-8')) / 1024
    
    if size_kb <= 250:
        return generate_reasoning(skeleton_str, system_instruction=NARRATOR_SYSTEM)
    
    # Recursive Windowing
    sys.stderr.write(f"[SCRIVENER] Skeleton too large ({size_kb:.1f}KB) at level {level}, subdividing...\n")
    mid = len(skeleton_json) // 2
    part1 = skeleton_json[:mid]
    part2 = skeleton_json[mid:]
    
    narrative1 = recursive_narrate(part1, level + 1)
    narrative2 = recursive_narrate(part2, level + 1)
    
    return f"{narrative1}\n\n{narrative2}"

def process_local_transcript(transcript_path, ignore_temporal=False):
    """Processes a single local transcript into the hourly log."""
    try:
        with open(transcript_path, 'r') as f:
            data = json.load(f)
        
        session_id = data.get('sessionId') or data.get('session_id')
        history = data.get('messages', []) or data.get('session_history', [])
        if not session_id or not history:
            return False

        today_str = datetime.now().strftime("%Y-%m-%d")
        hour_str = datetime.now().strftime("%H")
        os.makedirs(HOURLY_LOG_DIR, exist_ok=True)
        log_path = os.path.join(HOURLY_LOG_DIR, f"{today_str}_{hour_str}.md")
        
        last_indexed, last_narrated = get_state(session_id)
        
        if last_narrated >= len(history):
            return False

        # Signal Extraction for NEW turns only
        new_history = []
        for i in range(last_narrated, len(history)):
            msg = history[i]
            ts = msg.get('timestamp', '')
            if ignore_temporal or not ts or ts.startswith(today_str):
                new_history.append(msg)
        
        if not new_history:
            update_state(session_id, last_indexed_turn=len(history), last_narrated_turn=len(history))
            return False

        # Prepare a temporary JSON for extract_signal
        temp_session = { "messages": new_history }
        temp_path = transcript_path + ".tmp"
        with open(temp_path, 'w') as tf:
            json.dump(temp_session, tf)
        
        try:
            skeleton = extract_signal(temp_path)
            if isinstance(skeleton, str) and skeleton.startswith("Extraction Error"):
                sys.stderr.write(f"[SCRIVENER] Signal extraction error: {skeleton}\n")
                return False
                
            narrative = recursive_narrate(skeleton)
            
            sys.stderr.write(f"[SCRIVENER] Narrating {len(new_history)} turns for {session_id[:8]}...\n")
            with open(log_path, "a") as f:
                f.write(f"\n\n## Surgical Narrative: {datetime.now().strftime('%H:%M:%S')}\n")
                f.write(f"Session ID: `{session_id}` | Turns: `{last_narrated}` to `{len(history)}`\n")
                f.write(f"\n{narrative}\n")
                f.write("\n---\n")
                
            update_state(session_id, last_indexed_turn=len(history), last_narrated_turn=len(history))
            return True
            
        finally:
            if os.path.exists(temp_path): os.remove(temp_path)

    except Exception as e:
        sys.stderr.write(f"[SCRIVENER ERROR] {transcript_path}: {e}\n")
    return False

def main():
    try:
        input_data = ""
        if select.select([sys.stdin], [], [], 0.1)[0]:
            input_data = sys.stdin.read()
        
        if not acquire_lock(): sys.exit(0)

        prune_archive_raw()

        ignore_temporal = False
        try:
            if input_data:
                data = json.loads(input_data)
                ignore_temporal = data.get('ignore_temporal', False)
        except: pass

        transcripts = glob.glob(os.path.join(ARCHIVE_RAW_DIR, "*.json"))
        updated_count = 0
        today_file_str = datetime.now().strftime("%Y-%m-%d")
        
        for t_path in transcripts:
            fname = os.path.basename(t_path)
            if today_file_str not in fname: continue
            
            if process_local_transcript(t_path, ignore_temporal=ignore_temporal):
                updated_count += 1

        print(json.dumps({"decision": "proceed", "updated": updated_count}))
    except Exception as e:
        sys.stderr.write(f"[SCRIVENER FATAL] {e}\n")
        print(json.dumps({"decision": "proceed"}))
    finally:
        release_lock()

if __name__ == "__main__":
    main()
