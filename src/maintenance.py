#!/usr/bin/env python3
import os
import glob
import time

from config_utils import CONFIG, AIM_ROOT
RAW_DIR = CONFIG['paths'].get('archive_raw_dir', os.path.join(AIM_ROOT, "archive/raw"))
INDEX_DIR = CONFIG['paths'].get('archive_index_dir', os.path.join(AIM_ROOT, "archive/index"))

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
