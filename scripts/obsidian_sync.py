#!/usr/bin/env python3
import os
import shutil
import glob
from datetime import datetime

def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        config_path = os.path.join(current, "core/CONFIG.json")
        if os.path.exists(config_path):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root(os.getcwd())
SOURCE_DIR = os.path.join(AIM_ROOT, "memory")
# Note: DEST_DIR should ideally be in CONFIG.json, but for now we keep the user's likely path
DEST_DIR = "/home/kingb/OperationsCenterVault/AIM_LOGS/"

def sync_logs():
    if not os.path.exists(DEST_DIR):
        try:
            os.makedirs(DEST_DIR, exist_ok=True)
        except:
            return # Silent fail if vault doesn't exist

    # Sync daily logs (*.md in memory/)
    logs = glob.glob(os.path.join(SOURCE_DIR, "202[0-9]-[0-9][0-9]-[0-9][0-9].md"))
    for log in logs:
        filename = os.path.basename(log)
        dest_path = os.path.join(DEST_DIR, filename)
        
        # Only copy if different or doesn't exist
        if not os.path.exists(dest_path) or os.path.getmtime(log) > os.path.getmtime(dest_path):
            shutil.copy2(log, dest_path)

if __name__ == "__main__":
    sync_logs()
