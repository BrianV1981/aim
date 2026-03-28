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
sys.path.append(os.path.join(AIM_ROOT, "src"))
sys.path.append(os.path.join(AIM_ROOT, "scripts"))

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
DAILY_LOG_DIR = os.path.join(AIM_ROOT, "memory/hourly") # Stage 1 output
LOCK_FILE = os.path.join(AIM_ROOT, ".aim.lock")

# --- AI NARRATOR PROMPT ---
NARRATOR_SYSTEM = "You are a Surgical Technical Scribe. Convert this Signal Skeleton into a concise, 3-5 sentence technical history. Focus ONLY on logic shifts, bug fixes, and file paths. ZERO FLUFF."

def get_state(session_id):
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                val = state.get(session_id, {})
                if isinstance(val, dict):
                    return val.get('last_narrated_turn', 0)
        except: pass
    return 0

def update_state(session_id, last_narrated_turn):
    state = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
        except: pass
    
    current = state.get(session_id, {})
    current["last_narrated_turn"] = last_narrated_turn
    state[session_id] = current
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def recursive_narrate(skeleton_json, level=0):
    """
    Subdivides large sessions into sections.
    Threshold: 4MB (approx 4000KB) to handle 16MB files in 4 sections.
    """
    skeleton_str = json.dumps(skeleton_json, indent=2)
    size_kb = len(skeleton_str.encode('utf-8')) / 1024
    
    # BASE CASE 1: Small enough to process
    if size_kb <= 4000:
        return generate_reasoning(skeleton_str, system_instruction=NARRATOR_SYSTEM, brain_type="tier1")
    
    # BASE CASE 2: Cannot subdivide a single turn
    if len(skeleton_json) <= 1:
        # Truncate the single turn to fit if possible, or just process it
        truncated = skeleton_str[:1000000] # 1MB limit for single turn processing
        return generate_reasoning(truncated + "... [TRUNCATED]", system_instruction=NARRATOR_SYSTEM, brain_type="tier1")

    # Recursive Windowing
    sys.stderr.write(f"[SCRIVENER] Sectioning large session ({size_kb:.1f}KB) at level {level}...\n")
    mid = len(skeleton_json) // 2
    part1 = skeleton_json[:mid]
    part2 = skeleton_json[mid:]
    
    narrative1 = recursive_narrate(part1, level + 1)
    narrative2 = recursive_narrate(part2, level + 1)
    
    return f"{narrative1}\n\n{narrative2}"

def process_local_transcript(transcript_path):
    try:
        with open(transcript_path, 'r') as f:
            data = json.load(f)
        
        session_id = data.get('sessionId') or data.get('session_id')
        history = data.get('messages', []) or data.get('session_history', [])
        if not session_id or not history:
            return False

        last_narrated = get_state(session_id)
        if last_narrated >= len(history):
            return False

        # DELTA EXTRACTION: Only process turns since last_narrated
        new_history = history[last_narrated:]
        if not new_history:
            return False

        # Prepare temporary JSON for signal extraction
        temp_path = transcript_path + ".tmp"
        with open(temp_path, 'w') as tf:
            json.dump({"messages": new_history}, tf)
        
        try:
            skeleton = extract_signal(temp_path)

            # PHASE 39: THE EUREKA PROTOCOL (Hindsight Pruning Heuristic)
            total_tokens = sum(msg.get('tokens', {}).get('total', 0) for msg in skeleton if 'tokens' in msg)
            action_count = sum(len(msg.get('actions', [])) for msg in skeleton if 'actions' in msg)

            # If the agent spent a massive amount of tokens but executed very few final actions,
            # it likely hit a 'Eureka' moment after long thrashing. We compress it to save space.
            if total_tokens > 20000 and action_count > 0 and action_count < 3:
                sys.stderr.write(f"\n[EUREKA PROTOCOL] Detected high-thrash resolution ({total_tokens} tokens / {action_count} actions). Hindsight Pruning engaged.\n")
                synthetic_prompt = f"The agent spent {total_tokens} tokens investigating an issue, but only executed {action_count} actions to fix it. Review this skeleton and output ONLY the final 'Eureka' solution (the exact fix) in 2 sentences. Discard the dead-end debugging steps.\n\nSKELETON:\n{json.dumps(skeleton[-10:], indent=2)}"
                narrative = generate_reasoning(synthetic_prompt, system_instruction="You are the Eureka Protocol. Output only the final fix.", brain_type="tier1")
                narrative = f"### [EUREKA SYNTHESIS]\n{narrative}"

                # In a full implementation, we would rewrite the native session.json here to permanently prune the context window.
            else:
                narrative = recursive_narrate(skeleton)

            # PHASE 32: Graceful Suspension on Capacity Lockout            if "[ERROR: CAPACITY_LOCKOUT]" in narrative:
                sys.stderr.write(f"\n[SCRIBE SUSPENDED] Google servers are out of capacity for the selected model. Pausing summarization for {session_id[:8]} to prevent silent degradation.\n")
                return False

            if "Google API Error" in narrative or "Exception" in narrative:
                return False

            os.makedirs(DAILY_LOG_DIR, exist_ok=True)
            today_str = datetime.now().strftime("%Y-%m-%d")
            log_path = os.path.join(DAILY_LOG_DIR, f"{today_str}_{datetime.now().strftime('%H')}.md")
            
            with open(log_path, "a") as f:
                f.write(f"\n\n## Surgical Delta: {datetime.now().strftime('%H:%M:%S')}\n")
                f.write(f"Session: `{session_id[:8]}` | Turns: `{last_narrated}` to `{len(history)}`\n\n")
                f.write(narrative)
                f.write("\n---\n")
                
            update_state(session_id, len(history))
            time.sleep(2.0) # Rate limit protection
            return True
            
        finally:
            if os.path.exists(temp_path): os.remove(temp_path)

    except Exception as e:
        sys.stderr.write(f"[SCRIVENER FATAL] {e}\n")
    return False

def main():
    # FOCUS: Only process the LATEST transcript to stop spamming
    transcripts = glob.glob(os.path.join(ARCHIVE_RAW_DIR, "*.json"))
    if not transcripts:
        print(json.dumps({"decision": "proceed", "updated": 0}))
        return

    latest_transcript = max(transcripts, key=os.path.getmtime)
    updated = 1 if process_local_transcript(latest_transcript) else 0
    
    print(json.dumps({"decision": "proceed", "updated": updated}))

if __name__ == "__main__":
    main()
