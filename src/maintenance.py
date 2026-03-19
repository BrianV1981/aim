#!/usr/bin/env python3
import os
import glob
import time

def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        config_path = os.path.join(current, "core/CONFIG.json")
        if os.path.exists(config_path):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root(os.getcwd())
RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")
INDEX_DIR = os.path.join(AIM_ROOT, "archive/index")

def clean_archive(days=30):
    """
    Optional cleanup for very old session logs to prevent index bloat.
    (Currently conservative - just identifies files)
    """
    now = time.time()
    cutoff = now - (days * 86400)
    
    raw_files = glob.glob(os.path.join(RAW_DIR, "*.json"))
    for f in raw_files:
        if os.path.getmtime(f) < cutoff:
            # print(f"Found old session: {os.path.basename(f)}")
            pass

if __name__ == "__main__":
    clean_archive()
