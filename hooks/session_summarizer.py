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
    """Dynamically discovers the A.I.M. root directory."""
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core", "CONFIG.json")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
sys.path.append(os.path.join(AIM_ROOT, "src"))
sys.path.append(os.path.join(AIM_ROOT, "scripts"))

try:
    from reasoning_utils import generate_reasoning
except ImportError:
    generate_reasoning = None

try:
    from extract_signal import extract_signal, skeleton_to_markdown
except ImportError:
    extract_signal = None

CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
MEMORY_PATH = os.path.join(AIM_ROOT, "core/MEMORY.md")
if not os.path.exists(CONFIG_PATH):
    sys.exit(0)

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

ARCHIVE_RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")
STATE_FILE = os.path.join(AIM_ROOT, "archive/scrivener_state.json")
DAILY_LOG_DIR = os.path.join(AIM_ROOT, "memory/hourly") # Stage 1 output
LOCK_FILE = os.path.join(AIM_ROOT, ".aim.lock")

# --- AI NARRATOR PROMPT ---
NARRATOR_SYSTEM = """You are a Memory Proposer. Your goal is to analyze a delta of project activity and propose updates for the Durable Memory (MEMORY.md).

### INPUTS
1. **Signal Skeleton:** A noise-reduced transcript of recent activity.
2. **Current Memory:** The existing state of durable memory.

### CONSTRAINTS
- You must output a structured report identifying what to ADD, REMOVE, or CONTRADICT.
- Prioritize DELETION of stale facts over simple concatenation.
- Identify contradictory instructions or logic shifts.

### OUTPUT SCHEMA
1. **Rationale:** Brief summary of the activity delta.
2. **Proposed Adds:** New facts, milestones, or rules to record.
3. **Proposed Removes:** Outdated or redundant facts to purge.
4. **Contradictions:** Any existing rules in MEMORY.md that were violated or superseded.
"""

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
    
    # Load Current Memory for context
    memory_content = ""
    if os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH, 'r') as f:
                memory_content = f.read()
        except: pass

    combined_input = f"### SIGNAL SKELETON\n{skeleton_str}\n\n### CURRENT MEMORY\n{memory_content}"

    # BASE CASE 1: Small enough to process
    if size_kb <= 4000:
        return generate_reasoning(combined_input, system_instruction=NARRATOR_SYSTEM, brain_type="tier1")
    
    # BASE CASE 2: Cannot subdivide a single turn
    if len(skeleton_json) <= 1:
        # Truncate the single turn to fit if possible, or just process it
        truncated = combined_input[:1000000] # 1MB limit for single turn processing
        return generate_reasoning(truncated + "... [TRUNCATED]", system_instruction=NARRATOR_SYSTEM, brain_type="tier1")

    # Recursive Windowing
    sys.stderr.write(f"[SCRIVENER] Sectioning large session ({size_kb:.1f}KB) at level {level}...\n")
    mid = len(skeleton_json) // 2
    part1 = skeleton_json[:mid]
    part2 = skeleton_json[mid:]
    
    narrative1 = recursive_narrate(part1, level + 1)
    narrative2 = recursive_narrate(part2, level + 1)
    
    return f"{narrative1}\n\n{narrative2}"

def process_local_transcript(transcript_path, is_light_mode=False):
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

        # --- THE ZERO-TOKEN NOISE REDUCTION PIPELINE ---
        try:
            skeleton = extract_signal(temp_path)
            
            # PHASE 41: ZERO-TOKEN MARKDOWN EXPORT
            # Save a human-readable markdown version for Obsidian sync
            md_content = skeleton_to_markdown(skeleton, session_id)
            md_dir = os.path.join(AIM_ROOT, "archive/history")
            os.makedirs(md_dir, exist_ok=True)
            today_str = datetime.now().strftime("%Y-%m-%d")
            md_filename = f"{today_str}_{session_id[:8]}.md"
            md_path = os.path.join(md_dir, md_filename)
            
            # We append to the file so it builds up sequentially as the session progresses
            with open(md_path, "a", encoding="utf-8") as md_file:
                md_file.write(md_content)

            # If we are in Lightweight Mode, we just save the clean skeleton and skip the LLM reasoning
            if is_light_mode:
                os.makedirs(DAILY_LOG_DIR, exist_ok=True)
                today_str = datetime.now().strftime("%Y-%m-%d")
                log_path = os.path.join(DAILY_LOG_DIR, f"{today_str}_{datetime.now().strftime('%H')}_light.json")

                # Append to the daily JSON log file for searchability without LLM distillation
                with open(log_path, "a") as f:
                    f.write(json.dumps(skeleton) + "\n")

                update_state(session_id, len(history))
                return True

            # --- DEEP BRAIN MODE (LLM DISTILLATION) ---
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
            else:
                narrative = recursive_narrate(skeleton)

            # PHASE 32: Graceful Suspension on Capacity Lockout
            if "[ERROR: CAPACITY_LOCKOUT]" in narrative:
                sys.stderr.write(f"\n[SCRIBE SUSPENDED] Google servers are out of capacity for the selected model. Pausing summarization for {session_id[:8]} to prevent silent degradation.\n")
                return False

            if not narrative or "Google API Error" in narrative or "Exception" in narrative:
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

def main(args):
    is_light_mode = "--light" in args
    
    # FOCUS: Only process the LATEST transcript to stop spamming
    transcripts = glob.glob(os.path.join(ARCHIVE_RAW_DIR, "*.json"))
    if not transcripts:
        print(json.dumps({"decision": "proceed", "updated": 0}))
        return

    latest_transcript = max(transcripts, key=os.path.getmtime)
    updated = 1 if process_local_transcript(latest_transcript, is_light_mode) else 0
    
    # Also trigger history scribe for full session mirroring
    try:
        subprocess.run([sys.executable, os.path.join(AIM_ROOT, "src", "history_scribe.py")], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

    print(json.dumps({"decision": "proceed", "updated": updated}))

if __name__ == "__main__":
    main(sys.argv)
