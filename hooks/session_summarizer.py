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
DAILY_LOG_DIR = "/home/kingb/aim/memory"

def summarize_session(history):
    """Generates a higher-resolution summary for the daily log."""
    summary = []
    for turn in history:
        if turn.get('role') == 'user':
            content = turn.get('content', '')
            if isinstance(content, list):
                text_parts = [part.get('text', '') for part in content if part.get('text')]
                content = " ".join(text_parts)
            summary.append(f"### Brian: {content[:500]}...")
        elif turn.get('role') == 'model':
            calls = turn.get('tool_calls', [])
            if calls:
                for call in calls:
                    fn = call.get('function', {})
                    name = fn.get('name')
                    if name:
                        args = fn.get('arguments', {})
                        # Try to find a file path in common tool arguments
                        target = args.get('file_path') or args.get('dir_path') or args.get('path')
                        if target:
                            summary.append(f"**A.I.M.:** `{name}` on `{target}`")
                        else:
                            summary.append(f"**A.I.M.:** `{name}`")
    return "\n".join(summary)

def archive_transcript(session_id):
    """Locates the JSON transcript in tmp and copies it to the archive."""
    if not session_id:
        return None
    
    # Priority 1: Direct match with session ID in the filename (most common)
    pattern = os.path.join(TMP_CHATS_DIR, f"session-*{session_id[:8]}*.json")
    matches = glob.glob(pattern)
    
    # Priority 2: Full session ID match in filename
    if not matches:
        pattern = os.path.join(TMP_CHATS_DIR, f"*{session_id}*.json")
        matches = glob.glob(pattern)

    # Priority 3: Deep search (if filename-based search fails)
    if not matches:
        all_jsons = glob.glob(os.path.join(TMP_CHATS_DIR, "*.json"))
        # Sort by mtime to check newest files first
        all_jsons.sort(key=os.path.getmtime, reverse=True)
        
        for f in all_jsons:
            try:
                # We only peek at the start of the file for the sessionId to be efficient
                with open(f, 'r') as j:
                    # Session JSONs usually have sessionId in the first few lines
                    peek = j.read(1024)
                    if session_id in peek:
                        matches = [f]
                        break
            except:
                continue

    if matches:
        source = matches[0]
        dest_filename = os.path.basename(source)
        destination = os.path.join(ARCHIVE_RAW_DIR, dest_filename)
        # Ensure we don't overwrite with an older version if the file somehow exists
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
        os.makedirs(DAILY_LOG_DIR, exist_ok=True)
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
