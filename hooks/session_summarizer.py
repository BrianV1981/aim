#!/home/kingb/aim/venv/bin/python3
import sys
import json
import os
import shutil
import glob
import subprocess
from datetime import datetime

# --- CONFIGURATION (Load from core/CONFIG.json) ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        config_path = os.path.join(current, "core/CONFIG.json")
        if os.path.exists(config_path):
            return current
        current = os.path.dirname(current)
    return "/home/kingb/aim"

AIM_ROOT = find_aim_root(os.getcwd())
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

ARCHIVE_RAW_DIR = CONFIG['paths']['archive_raw_dir']
DAILY_LOG_DIR = CONFIG['paths']['memory_dir']
SRC_DIR = CONFIG['paths']['src_dir']
TMP_CHATS_DIR = CONFIG['paths']['tmp_chats_dir']

def summarize_session(history):
    """
    Highly-forensic summary extraction for A.I.M. Daily Logs.
    Handles both live hook payloads and archived transcript schemas.
    """
    summary = []
    if not history:
        return "*(No history captured in this turn)*"

    for turn in history:
        # Normalize role/type
        role = turn.get('role') or turn.get('type')
        
        # 1. Brian (User)
        if role == 'user':
            content = turn.get('content', '')
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and 'text' in part:
                        text_parts.append(part['text'])
                    elif isinstance(part, str):
                        text_parts.append(part)
                content = " ".join(text_parts)
            
            if content.strip():
                display_text = content.strip().replace('\n', ' ')
                if len(display_text) > 300:
                    display_text = display_text[:300] + "..."
                summary.append(f"### Brian: {display_text}")
        
        # 2. A.I.M. (Model)
        elif role in ['model', 'gemini']:
            # Thoughts
            thoughts = turn.get('thoughts', [])
            for thought in thoughts:
                if isinstance(thought, dict):
                    desc = thought.get('description', '')
                    if desc:
                        if len(desc) > 200: desc = desc[:200] + "..."
                        summary.append(f"> *Thought:* {desc}")

            # Tool Calls
            calls = turn.get('tool_calls') or turn.get('toolCalls') or []
            for call in calls:
                name = call.get('name') or (call.get('function', {}).get('name') if 'function' in call else None)
                args = call.get('args') or (call.get('function', {}).get('arguments', {}) if 'function' in call else {})
                
                target = args.get('file_path') or args.get('dir_path') or args.get('path') or args.get('command')
                if target:
                    summary.append(f"**A.I.M.:** `{name}` on `{target}`")
                else:
                    summary.append(f"**A.I.M.:** `{name}`")

            # Content
            content = turn.get('content', '')
            if isinstance(content, list):
                text_parts = [p.get('text', '') for p in content if isinstance(p, dict) and 'text' in p]
                content = " ".join(text_parts)
            
            if content and content.strip():
                display_text = content.strip().replace('\n', ' ')
                if len(display_text) > 300:
                    display_text = display_text[:300] + "..."
                summary.append(f"**A.I.M. Result:** {display_text}")

    return "\n".join(summary)

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
    venv_python = os.path.join(AIM_ROOT, "venv/bin/python3")
    
    # 1. Trigger Indexer (Real-time Forensic Update)
    if os.path.exists(indexer_path):
        try:
            # Run indexer in background - it doesn't need to block the pulse
            subprocess.Popen([venv_python, indexer_path], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass

    # 2. Trigger Distiller (Pulse Generation)
    if os.path.exists(distiller_path):
        try:
            # BLOCKING CALL: Ensure the distiller finishes before we exit the hook
            subprocess.run([venv_python, distiller_path], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL,
                           check=False)
            return True
        except Exception:
            return False
    return False

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data: sys.exit(0)
        
        data = json.loads(input_data)
        session_id = data.get('session_id') or data.get('sessionId')
        history = data.get('session_history') or data.get('messages') or []
        
        # 1. Archive
        archived_path = archive_transcript(session_id)
        
        # 2. Forensic History Recovery
        # If history is empty (often true on exit hooks), read the archived transcript
        if not history and archived_path:
            try:
                with open(archived_path, 'r') as f:
                    t_data = json.load(f)
                    history = t_data.get('messages', [])
            except: pass

        # 3. Daily Log
        today = datetime.now().strftime("%Y-%m-%d")
        os.makedirs(DAILY_LOG_DIR, exist_ok=True)
        log_path = os.path.join(DAILY_LOG_DIR, f"{today}.md")
        
        with open(log_path, "a") as f:
            f.write(f"\n\n## Session Log: {datetime.now().strftime('%H:%M:%S')}\n")
            f.write(f"Session ID: `{session_id}`\n")
            if archived_path:
                f.write(f"Archive: `aim/archive/raw/{os.path.basename(archived_path)}` (Forensic Saved)\n")
            f.write("\nKey Actions:\n")
            f.write(summarize_session(history))
            f.write("\n---\n")

        # 4. Distillation (Pulse Generation)
        trigger_distillation()

        print(json.dumps({"decision": "proceed"}))
    except Exception as e:
        sys.stderr.write(f"Error in session_summarizer.py: {str(e)}\n")
        print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
