#!/usr/bin/env python3
import os
import sys
import glob
import subprocess
import time
from datetime import datetime

def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh")): return current
        if os.path.exists(os.path.join(current, "setup.sh")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
CHATS_DIR = os.path.expanduser("~/.gemini/tmp/aim/chats/")
ARCHIVE_HISTORY = os.path.join(AIM_ROOT, "archive", "history")
CONTINUITY_DIR = os.path.join(AIM_ROOT, "continuity")
LAST_SESSION_CLEAN = os.path.join(CONTINUITY_DIR, "LAST_SESSION_FLIGHT_RECORDER.md")

def main():
    print("--- A.I.M. CRASH RECOVERY PROTOCOL ---")
    
    # 1. Find all JSONL files in ~/.gemini/tmp/aim/chats/
    if not os.path.exists(CHATS_DIR):
        print(f"[ERROR] Chats directory not found: {CHATS_DIR}")
        sys.exit(1)
        
    json_files = glob.glob(os.path.join(CHATS_DIR, "session-*.jsonl"))
    if not json_files:
        print(f"[ERROR] No session files found in {CHATS_DIR}.")
        sys.exit(1)
        
    # Sort by modification time, newest first
    json_files.sort(key=os.path.getmtime, reverse=True)
    recent_files = json_files[:5]
    
    print("\n[?] Select the session that crashed (or 'q' to quit):")
    for i, jf in enumerate(recent_files):
        size_bytes = os.path.getsize(jf)
        size_mb = size_bytes / (1024 * 1024)
        mtime = os.path.getmtime(jf)
        time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"  [{i+1}] {os.path.basename(jf)} | Size: {size_mb:.2f} MB | Last Modified: {time_str}")
        
    print("  [q] Quit (Exit without recovery)")
    
    target_json = None
    while True:
        choice = input(f"\nEnter selection [1-{len(recent_files)} or q]: ").strip().lower()
        if choice == 'q':
            print("Exiting crash recovery. No files were modified.")
            sys.exit(0)
        
        if choice.isdigit() and 1 <= int(choice) <= len(recent_files):
            target_json = recent_files[int(choice) - 1]
            break
        print("Invalid choice. Try again.")
        
    print(f"\n[1/4] Identified crashed session: {os.path.basename(target_json)}")
    
    # 2. Extract signal and format to markdown
    print(f"[2/4] Purging noise and extracting signal to {LAST_SESSION_CLEAN}...")
    try:
        sys.path.insert(0, os.path.join(AIM_ROOT, ".aim_core"))
        from extract_signal import extract_signal, skeleton_to_markdown
        skeleton = extract_signal(target_json)
        session_id = os.path.basename(target_json).replace('.jsonl', '')
        md_content = skeleton_to_markdown(skeleton, session_id)
        
        os.makedirs(CONTINUITY_DIR, exist_ok=True)
        with open(LAST_SESSION_CLEAN, 'w', encoding='utf-8') as f:
            f.write(md_content)
    except Exception as e:
        print(f"[ERROR] Signal extraction failed: {e}")
        sys.exit(1)

    # 3. Save to archive/history/
    timestamp = datetime.fromtimestamp(os.path.getmtime(target_json)).strftime('%Y-%m-%d_%H%M')
    archive_filename = f"{timestamp}_{session_id}.md"
    archive_filepath = os.path.join(ARCHIVE_HISTORY, archive_filename)
    print(f"[3/4] Archiving flight recorder to {archive_filepath}...")
    try:
        os.makedirs(ARCHIVE_HISTORY, exist_ok=True)
        with open(archive_filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
    except Exception as e:
        print(f"[ERROR] Archiving failed: {e}")
        sys.exit(1)
        
    # 4. Trigger Subconscious Scribe (session_summarizer.py)
    print("[4/4] Triggering Subconscious Scribe to ingest into memory-wiki...")
    venv_python = os.path.join(AIM_ROOT, "venv", "bin", "python3")
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    try:
        subprocess.Popen(
            [venv_python, os.path.join(AIM_ROOT, "hooks", "session_summarizer.py"), "--reincarnate", archive_filepath, "--bg"],
            cwd=AIM_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
    except Exception as e:
        print(f"[ERROR] Failed to trigger subconscious scribe: {e}")
        sys.exit(1)

    print("\n[SUCCESS] Crash recovery sequence complete.")
    print("The long-term memory extraction is running in the background.")
    print("You may now resume your task or start a new agent.")

if __name__ == "__main__":
    main()
