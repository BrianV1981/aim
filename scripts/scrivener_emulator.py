#!/usr/bin/env python3
import os
import json
import sys
import glob
from datetime import datetime

# --- CONFIG BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

from config_utils import CONFIG, AIM_ROOT

CHATS_DIR = CONFIG['paths'].get('tmp_chats_dir')
MEMORY_DIR = CONFIG['paths'].get('memory_dir')

def get_scrivener_notes(history):
    """NON-AI: Determinstically extracts the technical essence from messages."""
    if not history: return "No activity recorded."
    
    notes = []
    for msg in history:
        m_type = msg.get('type')
        ts = msg.get('timestamp', 'Unknown Time')
        if m_type == 'user':
            text = " ".join([c.get('text', '') for c in msg.get('content', []) if 'text' in c])
            if text: notes.append(f"[{ts}] [USER] {text[:500]}...")
        elif m_type == 'gemini':
            content = msg.get('content', '')
            if content and len(content) < 500:
                notes.append(f"[{ts}] [A.I.M.] {content.strip()}")
            
            for call in msg.get('toolCalls', []):
                notes.append(f"[{ts}] [ACTION] {call.get('name')} -> {json.dumps(call.get('args'))[:300]}...")
    
    return "\n".join(notes) if notes else "No activity recorded."

def get_last_processed_index(session_id):
    """Transitioned from brittle Markdown parsing to dedicated JSON state."""
    STATE_FILE = os.path.join(AIM_ROOT, "archive/scrivener_state.json")
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                return state.get(session_id, 0)
        except: pass
    return 0

def update_last_processed_index(session_id, index):
    """Updates the high-fidelity JSON state file."""
    STATE_FILE = os.path.join(AIM_ROOT, "archive/scrivener_state.json")
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
        sys.stderr.write(f"[EMULATOR] State write error: {e}\n")

def emulate_scrivener(target_date=None, ignore_temporal=False):
    date_str = target_date or datetime.now().strftime("%Y-%m-%d")
    print(f"--- A.I.M. SCRIVENER EMULATOR (High-Fidelity): {date_str} ---")
    
    pattern = os.path.join(CHATS_DIR, f"session-{date_str}*.json")
    transcripts = glob.glob(pattern)
    transcripts.sort()
    
    if not transcripts:
        print(f"No transcripts found for {date_str} in {CHATS_DIR}")
        return

    log_path = os.path.join(MEMORY_DIR, f"{date_str}.md")
    full_log_content = ""
    
    for t_path in transcripts:
        print(f"Processing: {os.path.basename(t_path)}")
        try:
            with open(t_path, 'r') as f:
                data = json.load(f)
            
            history = data.get('messages', [])
            session_id = data.get('sessionId')
            
            # Use High-Fidelity Logic
            last_index = get_last_processed_index(session_id)
            
            if last_index >= len(history):
                continue

            # Temporal Filtering
            new_history = []
            for i in range(last_index, len(history)):
                msg = history[i]
                ts = msg.get('timestamp', '')
                if ignore_temporal or not ts or ts.startswith(date_str):
                    new_history.append(msg)
            
            if new_history:
                final_block = f"\n## Session Log: {date_str}\nSession ID: `{session_id}`\n"
                final_block += f"Last Index: `{len(history)}`\n"
                final_block += "\n### Scrivener Notes (Deterministic Trace):\n"
                final_block += get_scrivener_notes(new_history)
                final_block += "\n---\n"
                full_log_content += final_block
            
            update_last_processed_index(session_id, len(history))
            
        except Exception as e:
            print(f"Error processing {t_path}: {e}")

    if full_log_content:
        with open(log_path, 'a') as f:
            f.write(full_log_content)
        print(f"[SUCCESS] High-fidelity log updated: {log_path}")
    else:
        print("[SKIP] No new messages to log.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    emulate_scrivener(target)
