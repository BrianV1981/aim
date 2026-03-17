#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime

# --- CONFIGURATION ---
AIM_ROOT = "/home/kingb/aim"
INDEXER_PATH = os.path.join(AIM_ROOT, "src/indexer.py")
RETRIEVER_PATH = os.path.join(AIM_ROOT, "src/retriever.py")
MEMORY_MD = os.path.join(AIM_ROOT, "core/MEMORY.md")
DAILY_LOG_DIR = "/home/kingb/memory"

def run_indexer():
    """Runs the A.I.M. Indexer to process any new raw transcripts."""
    print("--- Running A.I.M. Session Indexer ---")
    try:
        result = subprocess.run(["python3", INDEXER_PATH], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Indexer Errors: {result.stderr}", file=sys.stderr)
    except Exception as e:
        print(f"Failed to run indexer: {e}", file=sys.stderr)

def check_daily_logs():
    """Checks the most recent daily log for pending distillation."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(DAILY_LOG_DIR, f"{today}.md")
    
    if os.path.exists(log_path):
        print(f"--- Daily Log Detected: {today}.md ---")
        print("Ready for manual or model-assisted distillation into core/MEMORY.md.")
    else:
        print("--- No Daily Log Found for Today ---")

def main():
    print(f"--- A.I.M. Maintenance Mode: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    # 1. Index all pending transcripts
    run_indexer()
    
    # 2. Check logs
    check_daily_logs()
    
    print("--- Maintenance Complete ---")

if __name__ == "__main__":
    main()
