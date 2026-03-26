#!/usr/bin/env python3
import os
import glob
import time
import shutil
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="A.I.M. Benchmark JSON Recovery Protocol")
    parser.add_argument("--dest", type=str, default="docs/benchmarks/raw_logs", help="Destination folder for recovered logs")
    parser.add_argument("--hours", type=int, default=24, help="How many hours back to search")
    parser.add_argument("--auto-copy", action="store_true", help="Automatically copy found files without prompting")
    args = parser.parse_args()

    # The hidden directory where Gemini CLI stores session logs for isolated sub-environments
    tmp_dir = os.path.expanduser("~/.gemini/tmp")
    dest_dir = Path(args.dest)
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"--- A.I.M. BENCHMARK RECOVERY PROTOCOL ---")
    print(f"Searching hidden Gemini CLI temporary environment caches...")
    print(f"Path: {tmp_dir}/**/chats/*.json\n")

    if not os.path.exists(tmp_dir):
        print(f"Error: Could not find the global Gemini CLI tmp directory at {tmp_dir}")
        return

    # Find all json files in the chats subdirectories
    search_pattern = os.path.join(tmp_dir, "**", "chats", "*.json")
    files = glob.glob(search_pattern, recursive=True)

    # Filter by time
    current_time = time.time()
    cutoff_time = current_time - (args.hours * 3600)
    recent_files = [f for f in files if os.path.getmtime(f) > cutoff_time]
    
    # Sort by newest first
    recent_files.sort(key=os.path.getmtime, reverse=True)

    if not recent_files:
        print(f"No benchmark logs found from the last {args.hours} hours.")
        return

    print(f"Found {len(recent_files)} recent session logs across all isolated environments:")
    for i, f in enumerate(recent_files):
        mod_time = time.ctime(os.path.getmtime(f))
        size_kb = os.path.getsize(f) / 1024
        # Extract the environment name (e.g., 'django-matrix-pro' from '~/.gemini/tmp/django-matrix-pro/chats/...')
        env_name = Path(f).parts[-3] 
        print(f" [{i+1}] {env_name} | {mod_time} | {size_kb:.1f} KB")
        print(f"     Path: {f}")

    print("\n-------------------------------------------")
    if args.auto_copy:
        for f in recent_files:
            env_name = Path(f).parts[-3]
            session_id = Path(f).stem
            new_name = f"{env_name}_{session_id}.json"
            dest_path = dest_dir / new_name
            shutil.copy2(f, dest_path)
            print(f"Copied to: {dest_path}")
    else:
        choice = input(f"\nDo you want to copy these {len(recent_files)} files to '{args.dest}/'? (y/n): ")
        if choice.lower() == 'y':
            for f in recent_files:
                env_name = Path(f).parts[-3]
                session_id = Path(f).stem
                new_name = f"{env_name}_{session_id}.json"
                dest_path = dest_dir / new_name
                shutil.copy2(f, dest_path)
                print(f"Copied to: {dest_path}")
        else:
            print("Recovery aborted. The files remain safe in the hidden cache.")

if __name__ == "__main__":
    main()
