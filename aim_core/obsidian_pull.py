#!/usr/bin/env python3
import os
import shutil
import glob
import json
import subprocess
import sys
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

def pull_path(vault_src, aim_dest, extensions=["*.md"]):
    """Surgical pull of newer files from the vault back to the A.I.M. workspace."""
    if not os.path.exists(vault_src): return 0
    
    pulled_count = 0
    if os.path.isdir(vault_src):
        os.makedirs(aim_dest, exist_ok=True)
        for ext in extensions:
            files = glob.glob(os.path.join(vault_src, ext))
            for f in files:
                filename = os.path.basename(f)
                dest_f = os.path.join(aim_dest, filename)
                # Pull if it doesn't exist in A.I.M. workspace, or if the vault version is newer
                if not os.path.exists(dest_f) or os.path.getmtime(f) > os.path.getmtime(dest_f):
                    shutil.copy2(f, dest_f)
                    print(f"  [PULLED] {filename}")
                    pulled_count += 1
    else:
        # Single file pull
        os.makedirs(os.path.dirname(aim_dest), exist_ok=True)
        if not os.path.exists(aim_dest) or os.path.getmtime(vault_src) > os.path.getmtime(aim_dest):
            shutil.copy2(vault_src, aim_dest)
            print(f"  [PULLED] {os.path.basename(vault_src)}")
            pulled_count += 1
            
    return pulled_count

def full_vault_pull():
    vault_root = load_vault_path()
    if not vault_root:
        print("[ERROR] Obsidian vault path not configured in core/CONFIG.json.")
        return

    print(f"--- A.I.M. Obsidian Vault Ingest (Pull): {datetime.now().strftime('%H:%M:%S')} ---")
    
    total_pulled = 0
    
    # 1. Narrative Logs (memory/*.md)
    # The workspace expects flat files in memory/, but Obsidian might have them in the root. 
    # Aligning with obsidian_sync.py logic which drops memory/ files in the vault root.
    total_pulled += pull_path(vault_root, os.path.join(AIM_ROOT, "memory"))
    
    # 2. Durable Core (core/*.md)
    total_pulled += pull_path(os.path.join(vault_root, "core"), os.path.join(AIM_ROOT, "core"))
    
    # 3. Transient Pulse (continuity/*.md)
    total_pulled += pull_path(os.path.join(vault_root, "continuity"), os.path.join(AIM_ROOT, "continuity"))
    
    # 4. Momentum Documentation (docs/*.md)
    total_pulled += pull_path(os.path.join(vault_root, "docs"), os.path.join(AIM_ROOT, "docs"))

    if total_pulled > 0:
        print(f"\n[SUCCESS] Transport layer pulled {total_pulled} updated files from Obsidian Vault.")
        print("[TRIGGER] Re-indexing A.I.M. Engram DB...")
        
        # Fire the existing indexing engine (bootstrap_brain.py) to ingest changes into the vector database
        try:
            script_path = os.path.join(AIM_ROOT, "src", "bootstrap_brain.py")
            venv_python = os.path.join(AIM_ROOT, "venv", "bin", "python3")
            python_exec = venv_python if os.path.exists(venv_python) else sys.executable
            
            subprocess.run([python_exec, script_path], check=True)
            print("\n[SUCCESS] Obsidian edits successfully ingested into the Engram DB.")
        except Exception as e:
            print(f"\n[ERROR] Failed to trigger Engram DB indexing: {e}")
    else:
        print("\n[INFO] No new changes detected in the Obsidian Vault. Workspace is up-to-date.")

if __name__ == "__main__":
    full_vault_pull()
