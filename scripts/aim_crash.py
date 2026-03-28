#!/usr/bin/env python3
import os
import sys
import glob
import subprocess

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
LAST_SESSION_CLEAN = os.path.join(CONTINUITY_DIR, "LAST_SESSION_CLEAN.md")

def main():
    print("--- A.I.M. CRASH RECOVERY PROTOCOL ---")
    
    # 1. Find all JSON files in archive/raw
    json_files = glob.glob(os.path.join(ARCHIVE_RAW, "session-*.json"))
    if not json_files:
        print("[ERROR] No session files found in archive/raw.")
        sys.exit(1)
        
    # Sort by modification time, newest first
    json_files.sort(key=os.path.getmtime, reverse=True)
    
    # Identify crashed session: the second most recent file, 
    # since the first most recent is the current active session.
    if len(json_files) < 2:
        target_json = json_files[0]
    else:
        target_json = json_files[1]
        
    print(f"[1/5] Identified crashed session: {os.path.basename(target_json)}")
    
    # 2. Extract signal and format to markdown
    print(f"[2/5] Purging noise and extracting signal to {LAST_SESSION_CLEAN}...")
    try:
        sys.path.insert(0, os.path.join(AIM_ROOT, "scripts"))
        from extract_signal import extract_signal, skeleton_to_markdown
        skeleton = extract_signal(target_json)
        session_id = os.path.basename(target_json).replace('.json', '')
        md_content = skeleton_to_markdown(skeleton, session_id)
        
        # Truncate to last 2000 lines
        md_lines = md_content.splitlines()
        truncated_lines = md_lines[-2000:] if len(md_lines) > 2000 else md_lines
        
        os.makedirs(CONTINUITY_DIR, exist_ok=True)
        with open(LAST_SESSION_CLEAN, 'w', encoding='utf-8') as f:
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
        
    # 5. Copy ISSUE_TRACKER.md to root
    print("[5/5] Elevating ISSUE_TRACKER.md to workspace root...")
    try:
        import shutil
        src_tracker = os.path.join(CONTINUITY_DIR, "ISSUE_TRACKER.md")
        dst_tracker = os.path.join(AIM_ROOT, "ISSUE_TRACKER.md")
        if os.path.exists(src_tracker):
            shutil.copy2(src_tracker, dst_tracker)
    except Exception as e:
        print(f"[ERROR] Failed to copy issue tracker: {e}")
        sys.exit(1)

    print("\n[SUCCESS] Crash recovery sequence complete.")
    print("The environment is stabilized and the next agent can safely wake up.")

if __name__ == "__main__":
    main()