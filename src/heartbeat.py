#!/usr/bin/env python3
import os
import sqlite3
import glob
import time
from datetime import datetime

def find_aim_root():
    current = os.path.dirname(os.path.abspath(__file__))
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()

def print_status(component, status, message=""):
    color = "\033[92m" if status == "PASS" else ("\033[93m" if status == "WARN" else "\033[91m")
    reset = "\033[0m"
    print(f"[{color}{status}{reset}] {component:<25} {message}")

def check_db():
    db_path = os.path.join(AIM_ROOT, "archive/engram.db")
    if not os.path.exists(db_path):
        print_status("Engram DB", "FAIL", "Database file is missing.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM fragments")
        f_count = c.fetchone()[0]
        c.execute("SELECT count(*) FROM sessions")
        s_count = c.fetchone()[0]
        conn.close()
        print_status("Engram DB", "PASS", f"Healthy ({f_count} fragments across {s_count} sessions)")
    except Exception as e:
        print_status("Engram DB", "FAIL", f"Corruption detected: {e}")

def check_failsafe():
    tail_path = os.path.join(AIM_ROOT, "continuity/FALLBACK_TAIL.md")
    if not os.path.exists(tail_path):
        print_status("Failsafe Hook", "FAIL", "FALLBACK_TAIL.md is missing. Hooks may be broken.")
        return
    
    mtime = os.path.getmtime(tail_path)
    age_hours = (time.time() - mtime) / 3600
    
    if age_hours > 24:
        print_status("Failsafe Hook", "WARN", f"Stale snapshot ({age_hours:.1f} hours old). Are you working?")
    else:
        print_status("Failsafe Hook", "PASS", f"Active (Updated {age_hours:.1f} hours ago)")

def check_memory_pipeline():
    memory_dir = os.path.join(AIM_ROOT, "memory")
    
    # Check Hourly (Tier 1)
    hourly_files = glob.glob(os.path.join(memory_dir, "hourly/*.md"))
    # Check Daily (Tier 2)
    daily_files = glob.glob(os.path.join(memory_dir, "daily/*.md"))
    
    all_logs = hourly_files + daily_files
    if not all_logs:
        print_status("Memory Pipeline", "WARN", "No hourly or daily logs found. Is the agent talking?")
        return
        
    latest_log = max(all_logs, key=os.path.getmtime)
    age_hours = (time.time() - os.path.getmtime(latest_log)) / 3600
    
    if age_hours > 48:
        print_status("Memory Pipeline", "WARN", f"Pipeline may be stalled. Last log was {age_hours:.1f} hours ago.")
    else:
        print_status("Memory Pipeline", "PASS", f"Logs cascading normally. Newest log: {os.path.basename(latest_log)}")

def check_sync():
    sync_dir = os.path.join(AIM_ROOT, "archive/sync")
    jsonl_files = glob.glob(os.path.join(sync_dir, "*.jsonl"))
    if not jsonl_files:
        print_status("Sovereign Sync", "WARN", f"No JSONL chunks found. Run '{os.path.basename(AIM_ROOT)} push' to protect DB.")
        return
        
    print_status("Sovereign Sync", "PASS", f"{len(jsonl_files)} chunks ready for GitOps.")

def main():
    print("\n--- A.I.M. SYSTEM HEALTH CHECK ---")
    check_db()
    check_failsafe()
    check_memory_pipeline()
    check_sync()
    print("-" * 34 + "\n")

if __name__ == "__main__":
    main()
