#!/usr/bin/env python3
import os
import shutil
import glob
import json
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
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

def load_vault_path():
    if not os.path.exists(CONFIG_PATH): return None
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            return config['settings'].get('obsidian_vault_path')
    except: return None

def sync_path(src, dest):
    """Surgical sync of a single file or directory."""
    if not os.path.exists(src): return
    
    if os.path.isdir(src):
        os.makedirs(dest, exist_ok=True)
        # We only sync .md files from directories to keep the vault clean
        files = glob.glob(os.path.join(src, "*.md"))
        for f in files:
            filename = os.path.basename(f)
            dest_f = os.path.join(dest, filename)
            if not os.path.exists(dest_f) or os.path.getmtime(f) > os.path.getmtime(dest_f):
                shutil.copy2(f, dest_f)
    else:
        # Single file sync
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if not os.path.exists(dest) or os.path.getmtime(src) > os.path.getmtime(dest):
            shutil.copy2(src, dest)

def full_vault_sync():
    vault_root = load_vault_path()
    if not vault_root:
        # print("Obsidian sync skipped: No vault path configured.")
        return

    print(f"--- A.I.M. Obsidian Vault Sync: {datetime.now().strftime('%H:%M:%S')} ---")
    print(f"Target: {vault_root}")
    
    # 1. Narrative Logs (memory/*.md)
    sync_path(os.path.join(AIM_ROOT, "memory"), vault_root)
    
    # 2. Durable Core (core/*.md)
    sync_path(os.path.join(AIM_ROOT, "core"), os.path.join(vault_root, "core"))
    
    # 3. Transient Pulse (continuity/*.md)
    sync_path(os.path.join(AIM_ROOT, "continuity"), os.path.join(vault_root, "continuity"))
    
    # 4. Momentum Documentation (docs/*.md)
    sync_path(os.path.join(AIM_ROOT, "docs"), os.path.join(vault_root, "docs"))

    print("[SUCCESS] Vault mirrored.")

if __name__ == "__main__":
    full_vault_sync()
