#!/usr/bin/env python3
import os
import sys
import glob
import subprocess
import json

def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        if os.path.exists(os.path.join(current, "setup.sh")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
ARCHIVE_RAW = os.path.join(AIM_ROOT, "archive", "raw")
CONTINUITY_DIR = os.path.join(AIM_ROOT, "continuity")
LAST_SESSION_CLEAN = os.path.join(CONTINUITY_DIR, "LAST_SESSION_FLIGHT_RECORDER.md")

# Load Config
try:
    with open(os.path.join(AIM_ROOT, "core/CONFIG.json"), 'r') as f:
        CONFIG = json.load(f)
except Exception:
    CONFIG = {}

def main():
    print("--- A.I.M. CRASH RECOVERY PROTOCOL ---")
    
    # 1. Find all JSON files in archive/raw
    json_files = glob.glob(os.path.join(ARCHIVE_RAW, "session-*.json"))
    if not json_files:
        print("[ERROR] No session files found in archive/raw.")
        sys.exit(1)
        
    # Sort by modification time, newest first
    json_files.sort(key=os.path.getmtime, reverse=True)
    recent_files = json_files[:5]
    
    print("\\n[?] Select the session that crashed (or 'q' to quit and verify via /resume):")
    from datetime import datetime
    for i, jf in enumerate(recent_files):
        size_bytes = os.path.getsize(jf)
        size_mb = size_bytes / (1024 * 1024)
        mtime = os.path.getmtime(jf)
        time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        # Quick and dirty turn estimation without full JSON parsing (since it might be corrupt)
        turns = 0
        try:
            with open(jf, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                turns = content.count('"role":')
        except Exception:
            pass
            
        print(f"  [{i+1}] {os.path.basename(jf)} | Size: {size_mb:.2f} MB | Est. Turns: {turns} | Last Modified: {time_str}")
        
    print("  [q] Quit (Exit without recovery)")
    
    target_json = None
    while True:
        choice = input("\\nEnter selection [1-{len} or q]: ".format(len=len(recent_files))).strip().lower()
        if choice == 'q':
            print("Exiting crash recovery. No files were modified.")
            sys.exit(0)
        
        if choice.isdigit() and 1 <= int(choice) <= len(recent_files):
            target_json = recent_files[int(choice) - 1]
            break
        print("Invalid choice. Try again.")
        
    print(f"\n[1/5] Identified crashed session: {os.path.basename(target_json)}")
    
    # 2. Extract signal and format to markdown
    print(f"[2/5] Purging noise and extracting signal to {LAST_SESSION_CLEAN}...")
    try:
        sys.path.insert(0, os.path.join(AIM_ROOT, "scripts"))
        from extract_signal import extract_signal, skeleton_to_markdown
        skeleton = extract_signal(target_json)
        session_id = os.path.basename(target_json).replace('.json', '')
        md_content = skeleton_to_markdown(skeleton, session_id)
        
        # Truncate to config limit lines
        tail_lines = CONFIG.get('settings', {}).get('handoff_context_lines', 0)
        md_lines = md_content.splitlines()
        
        if tail_lines > 0 and len(md_lines) > tail_lines:
            truncated_lines = md_lines[-tail_lines:]
        else:
            truncated_lines = md_lines
        
        os.makedirs(CONTINUITY_DIR, exist_ok=True)
        with open(LAST_SESSION_CLEAN, 'w', encoding='utf-8') as f:
            if tail_lines > 0:
                f.write(f"# A.I.M. Clean Session Transcript (Rolling Delta)\n*This is a noise-reduced flight recorder showing only the last {tail_lines} lines.*\n\n")
            else:
                f.write("# A.I.M. Clean Session Transcript (Full History)\n*This is a noise-reduced flight recorder showing the entire session.*\n\n")
            f.write('\n'.join(truncated_lines) + '\n')
    except Exception as e:
        print(f"[ERROR] Signal extraction failed: {e}")
        sys.exit(1)
        
    # 3. Generate Handoff Pulse
    print("[3/5] Generating autonomic handoff pulse...")
    venv_python = os.path.join(AIM_ROOT, "venv", "bin", "python3")
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    try:
        subprocess.run(
            [venv_python, os.path.join(AIM_ROOT, "src", "handoff_pulse_generator.py")],
            cwd=AIM_ROOT, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Handoff pulse generation failed: {e}")
        sys.exit(1)
        
    # 4. Sync Issue Tracker
    print("[4/5] Synchronizing the issue tracker...")
    try:
        subprocess.run(
            [venv_python, os.path.join(AIM_ROOT, "scripts", "sync_issue_tracker.py")],
            cwd=AIM_ROOT, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Issue tracker sync failed: {e}")
        sys.exit(1)

    print("\n[SUCCESS] Crash recovery sequence complete.")
    print("The environment is stabilized and the next agent can safely wake up.")

if __name__ == "__main__":
    main()