#!/usr/bin/env python3
import sys
import json
import os
import shutil
import glob
import subprocess
from datetime import datetime

# DEBUG: Prove the hook was called
with open("/tmp/aim_hook.log", "a") as f:
    f.write(f"HOOK CALLED: {datetime.now().isoformat()}\n")

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
                # Avoid long prompts: keep first 300 chars
                display_text = content.strip().replace('\n', ' ')
                if len(display_text) > 300:
                    display_text = display_text[:300] + "..."
                summary.append(f"### Brian: {display_text}")
        
        # 2. A.I.M. (Model)
        elif role in ['model', 'gemini']:
            # Thoughts (Forensic Gold)
            thoughts = turn.get('thoughts', [])
            for thought in thoughts:
                if isinstance(thought, dict):
                    subject = thought.get('subject', 'Thinking')
                    desc = thought.get('description', '')
                    if desc:
                        # Keep it concise
                        if len(desc) > 200:
                            desc = desc[:200] + "..."
                        summary.append(f"> *Thought ({subject}):* {desc}")

            # Tool Calls
            # Live hooks send 'tool_calls' with 'function'/'arguments'
            # Transcripts send 'toolCalls' with 'name'/'args'
            calls = turn.get('tool_calls') or turn.get('toolCalls') or []
            for call in calls:
                # Resolve name
                name = call.get('name')
                if not name and 'function' in call:
                    name = call['function'].get('name')
                
                # Resolve args
                args = call.get('args') or {}
                if not args and 'function' in call:
                    args = call['function'].get('arguments', {})
                
                # Format action
                target = args.get('file_path') or args.get('dir_path') or args.get('path') or args.get('command')
                if target:
                    summary.append(f"**A.I.M.:** `{name}` on `{target}`")
                else:
                    summary.append(f"**A.I.M.:** `{name}`")

            # Final Content (if any)
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
    # We look for the newest file matching the session_id
    pattern = os.path.join(TMP_CHATS_DIR, f"*{session_id}*.json")
    matches = glob.glob(pattern)
    
    if not matches:
        # Try substring match
        pattern = os.path.join(TMP_CHATS_DIR, f"*{session_id[:8]}*.json")
        matches = glob.glob(pattern)
        
    if matches:
        # Pick newest
        source = max(matches, key=os.path.getmtime)
        os.makedirs(ARCHIVE_RAW_DIR, exist_ok=True)
        destination = os.path.join(ARCHIVE_RAW_DIR, os.path.basename(source))
        shutil.copy2(source, destination)
        return destination
    return None

def trigger_distillation():
    distiller_path = os.path.join(SRC_DIR, "distiller.py")
    if os.path.exists(distiller_path):
        try:
            subprocess.Popen([sys.executable, distiller_path], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        
        if not session_id and history:
            # Try to extract session_id from transcript if we are back-populating
            # (Though back-populator should pass it)
            pass

        # 1. Archive
        archived_path = archive_transcript(session_id)
        
        # 2. Daily Log
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

        # 3. Distillation
        trigger_distillation()

        print(json.dumps({"decision": "proceed"}))
    except Exception as e:
        sys.stderr.write(f"Error in session_summarizer.py: {str(e)}\n")
        print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
