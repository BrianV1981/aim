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

    # Primary: OpenCode export directory (post-bridge) + Gemini CLI hidden cache (backward compat)
    tmp_dir = os.path.expanduser("~/.gemini/tmp")
    dest_dir = Path(args.dest)
    dest_dir.mkdir(parents=True, exist_ok=True)

    opencode_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "archive", "raw")

    print(f"--- A.I.M. BENCHMARK RECOVERY PROTOCOL ---")
    print(f"Searching session caches (OpenCode exports + Gemini CLI fallback)...")
    print(f"OpenCode path: {opencode_dir}")
    print(f"Gemini path:   {tmp_dir}/**/chats/*.json\n")

    # Gather files from both sources
    current_time = time.time()
    cutoff_time = current_time - (args.hours * 3600)
    files = []

    # Source 1: OpenCode export directory
    if os.path.exists(opencode_dir):
        opencode_files = glob.glob(os.path.join(opencode_dir, "*.json"))
        for f in opencode_files:
            if os.path.getmtime(f) > cutoff_time:
                files.append(f)

    # Source 2: Gemini CLI hidden temp cache (backward compat)
    if os.path.exists(tmp_dir):
        search_pattern = os.path.join(tmp_dir, "**", "chats", "*.json")
        gemini_files = glob.glob(search_pattern, recursive=True)
        for f in gemini_files:
            if os.path.getmtime(f) > cutoff_time and f not in files:
                files.append(f)
    
    # Sort by newest first
    files.sort(key=os.path.getmtime, reverse=True)

    if not files:
        print(f"No benchmark logs found from the last {args.hours} hours.")
        return

    print(f"Found {len(files)} recent session logs across all isolated environments:")
    for i, f in enumerate(files):
        mod_time = time.ctime(os.path.getmtime(f))
        size_kb = os.path.getsize(f) / 1024
        # Extract environment name from path (handles both gemini tmp and opencode archive layouts)
        path_parts = Path(f).parts
        if '.gemini' in path_parts:
            env_name = path_parts[-3] if len(path_parts) >= 3 else 'unknown'
        else:
            env_name = 'opencode'
        print(f" [{i+1}] {env_name} | {mod_time} | {size_kb:.1f} KB")
        print(f"     Path: {f}")

    print("\n-------------------------------------------")
    if args.auto_copy:
        for f in files:
            path_parts = Path(f).parts
            if '.gemini' in path_parts:
                env_name = path_parts[-3] if len(path_parts) >= 3 else 'unknown'
            else:
                env_name = 'opencode'
            session_id = Path(f).stem
            new_name = f"{env_name}_{session_id}.json"
            dest_path = dest_dir / new_name
            shutil.copy2(f, dest_path)
            print(f"Copied to: {dest_path}")
    else:
        choice = input(f"\nDo you want to copy these {len(files)} files to '{args.dest}/'? (y/n): ")
        if choice.lower() == 'y':
            for f in files:
                path_parts = Path(f).parts
                if '.gemini' in path_parts:
                    env_name = path_parts[-3] if len(path_parts) >= 3 else 'unknown'
                else:
                    env_name = 'opencode'
                session_id = Path(f).stem
                new_name = f"{env_name}_{session_id}.json"
                dest_path = dest_dir / new_name
                shutil.copy2(f, dest_path)
                print(f"Copied to: {dest_path}")
        else:
            print("Recovery aborted. The files remain safe in the hidden cache.")

if __name__ == "__main__":
    main()
