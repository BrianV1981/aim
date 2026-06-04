#!/usr/bin/env python3
import os
import shutil
import glob
import json
import sys

# --- CONFIG BOOTSTRAP ---
def find_aim_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

if not os.path.exists(CONFIG_PATH):
    sys.exit(0)

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

TMP_CHATS_DIR = CONFIG['paths'].get('tmp_chats_dir')
ARCHIVE_RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")

def mirror_transcripts():
    """Ultra-fast mirroring of global transcripts to local archive."""
    if not os.path.exists(TMP_CHATS_DIR): return
    os.makedirs(ARCHIVE_RAW_DIR, exist_ok=True)
    
    # Mirror all JSON transcripts
    transcripts = glob.glob(os.path.join(TMP_CHATS_DIR, "*.json"))
    count = 0
    for t in transcripts:
        filename = os.path.basename(t)
        dest = os.path.join(ARCHIVE_RAW_DIR, filename)
        
        # Only copy if new or updated
        if not os.path.exists(dest) or os.path.getmtime(t) > os.path.getmtime(dest):
            shutil.copy2(t, dest)
            count += 1
            
    if count > 0:
        sys.stderr.write(f"[PORTER] Mirrored {count} transcripts to local archive.\n")

if __name__ == "__main__":
    mirror_transcripts()
