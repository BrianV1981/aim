#!/home/kingb/aim/venv/bin/python3
import sys
import json
import os
import shutil
import glob
import subprocess
from datetime import datetime

# Add src to path so we can import reasoning_utils
hook_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(hook_dir)
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from reasoning_utils import generate_reasoning, AIM_ROOT

# --- CONFIGURATION (Load from core/CONFIG.json) ---
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

TMP_CHATS_DIR = CONFIG['paths']['tmp_chats_dir']
ARCHIVE_RAW_DIR = CONFIG['paths']['archive_raw_dir']
DAILY_LOG_DIR = CONFIG['paths']['memory_dir']
SRC_DIR = CONFIG['paths']['src_dir']

def summarize_session(history):
    """Generates a high-signal summary of the turn."""
    if not history: return "No new activity recorded."
    
    # We only summarize the delta to keep it snappy
    prompt = f"""
Distill these recent session messages into a concise bulleted list of:
- Intent: (What was the user trying to do?)
- Actions: (What specific changes or tools were run?)
- Outcome: (Success/Failure and current project state)

Be blunt. No filler.

RECENT MESSAGES:
{json.dumps(history[-10:], indent=2)}
"""
    system_instr = "You are the A.I.M. Session Summarizer. Distill technical activity into high-fidelity bullet points."
    
    try:
        summary = generate_reasoning(prompt, system_instruction=system_instr)
        return summary
    except Exception as e:
        return f"Summary failed: {str(e)}"

def archive_transcript(session_id):
    if not session_id: return None
    pattern = os.path.join(TMP_CHATS_DIR, f"*{session_id}*.json")
    matches = glob.glob(pattern)
    if not matches:
        pattern = os.path.join(TMP_CHATS_DIR, f"*{session_id[:8]}*.json")
        matches = glob.glob(pattern)
    if matches:
        source = max(matches, key=os.path.getmtime)
        os.makedirs(ARCHIVE_RAW_DIR, exist_ok=True)
        destination = os.path.join(ARCHIVE_RAW_DIR, os.path.basename(source))
        shutil.copy2(source, destination)
        return destination
    return None

def trigger_distillation():
    distiller_path = os.path.join(SRC_DIR, "distiller.py")
    indexer_path = os.path.join(SRC_DIR, "indexer.py")
    scrubber_path = os.path.join(AIM_ROOT, "scripts/telemetry_scrubber.py")
    venv_python = os.path.join(AIM_ROOT, "venv/bin/python3")
    
    # 1. Trigger Scrubber (Privacy Hardening)
    if os.path.exists(scrubber_path):
        try:
            subprocess.run([venv_python, scrubber_path], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass

    # 2. Trigger Indexer (Real-time Forensic Update)
    if os.path.exists(indexer_path):
        try:
            subprocess.run([venv_python, indexer_path], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass

    # 3. Trigger Distiller (Pulse Generation)
    if os.path.exists(distiller_path):
        try:
            subprocess.run([venv_python, distiller_path], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           check=False)
            return True
        except Exception:
            return False
    return False

def get_last_processed_index(log_path, session_id):
    if not os.path.exists(log_path): return 0
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
            for i in range(len(lines)-1, -1, -1):
                if f"Session ID: `{session_id}`" in lines[i]:
                    for j in range(i, min(i+10, len(lines))):
                        if "Last Index: `" in lines[j]:
                            return int(lines[j].split("`")[1])
    except: pass
    return 0

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data: sys.exit(0)
        
        data = json.loads(input_data)
        session_id = data.get('session_id') or data.get('sessionId')
        history = data.get('session_history') or data.get('messages') or []
        
        # Check if we should skip distillation (e.g. called from scrivener periodic task)
        skip_distill = data.get('skip_distill', False)
        
        # 1. Archive
        archived_path = archive_transcript(session_id)
        
        # 2. Forensic History Recovery
        if not history and archived_path:
            try:
                with open(archived_path, 'r') as f:
                    t_data = json.load(f)
                    history = t_data.get('messages', [])
            except: pass

        # 3. Daily Log (Stateful)
        today = datetime.now().strftime("%Y-%m-%d")
        os.makedirs(DAILY_LOG_DIR, exist_ok=True)
        log_path = os.path.join(DAILY_LOG_DIR, f"{today}.md")
        
        last_index = get_last_processed_index(log_path, session_id)
        new_history = history[last_index:]
        
        if not new_history:
            trigger_distillation()
            sys.exit(0)

        with open(log_path, "a") as f:
            f.write(f"\n\n## Session Log: {datetime.now().strftime('%H:%M:%S')}\n")
            f.write(f"Session ID: `{session_id}`\n")
            f.write(f"Last Index: `{len(history)}`\n")
            if archived_path:
                f.write(f"Archive: `aim/archive/raw/{os.path.basename(archived_path)}` (Forensic Saved)\n")
            f.write("\nKey Actions:\n")
            f.write(summarize_session(new_history))
            f.write("\n---\n")

        # 4. Distillation (Pulse Generation)
        if not skip_distill:
            trigger_distillation()

        print(json.dumps({"decision": "proceed"}))
    except Exception as e:
        sys.stderr.write(f"Error in session_summarizer.py: {str(e)}\n")
        print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
