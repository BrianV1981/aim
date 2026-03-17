#!/usr/bin/env python3
import sys
import json
import os
import shutil
import glob
from datetime import datetime

# --- CONFIGURATION ---
TMP_CHATS_DIR = "/home/kingb/.gemini/tmp/kingb/chats"
ARCHIVE_RAW_DIR = "/home/kingb/aim/archive/raw"
DAILY_LOG_DIR = "/home/kingb/memory"

def summarize_session(history):
    """Generates a brief summary for the daily log."""
    summary = []
    for turn in history:
        if turn.get('role') == 'user':
            content = turn.get('content', '')
            if isinstance(content, list):
                content = content[0].get('text', '') if content else ''
            summary.append(f"### Brian: {content[:100]}...")
        elif turn.get('role') == 'model':
            calls = turn.get('tool_calls', [])
            if calls:
                tool_names = [call.get('function', {}).get('name') for call in calls]
                summary.append(f"**A.I.M.:** Executed tools: {', '.join(tool_names)}")
    return "\n".join(summary)

def archive_transcript(session_id):
    """Locates the JSON transcript in tmp and copies it to the archive."""
    if not session_id:
        return None
    
    # Search for the session file in the tmp directory
    # Format: session-YYYY-MM-DDTHH-mm-SS-ID.json
    pattern = os.path.join(TMP_CHATS_DIR, f"session-*{session_id[:8]}*.json")
    matches = glob.glob(pattern)
    
    if not matches:
        # Try finding by session_id inside files if the filename doesn't match perfectly
        for f in glob.glob(os.path.join(TMP_CHATS_DIR, "*.json")):
            try:
                with open(f, 'r') as j:
                    data = json.load(j)
                    if data.get('sessionId') == session_id:
                        matches = [f]
                        break
            except:
                continue

    if matches:
        source = matches[0]
        dest_filename = os.path.basename(source)
        destination = os.path.join(ARCHIVE_RAW_DIR, dest_filename)
        shutil.copy2(source, destination)
        return destination
    return None

def main():
    try:
        # 1. Read input from Gemini CLI
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)

        data = json.loads(input_data)
        session_id = data.get('session_id')
        history = data.get('session_history', [])
        
        # 2. Archive Raw Transcript
        archived_path = archive_transcript(session_id)
        
        # 3. Create/Append to Daily Log
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = os.path.join(DAILY_LOG_DIR, f"{today}.md")
        
        with open(log_path, "a") as f:
            f.write(f"\n\n## Session Log: {datetime.now().strftime('%H:%M:%S')}\n")
            f.write(f"Session ID: `{session_id}`\n")
            if archived_path:
                f.write(f"Archive: `aim/archive/raw/{os.path.basename(archived_path)}` (Forensic Saved)\n")
            else:
                f.write("Status: Session ended (Forensic Search Pending)\n")
            
            f.write("\nKey Actions:\n")
            f.write(summarize_session(history))
            f.write("\n---\n")

        # 4. Return success
        print(json.dumps({"decision": "proceed"}))

    except Exception as e:
        sys.stderr.write(f"Error in session_summarizer.py: {str(e)}\n")
        print(json.dumps({"decision": "proceed"}))

if __name__ == "__main__":
    main()
