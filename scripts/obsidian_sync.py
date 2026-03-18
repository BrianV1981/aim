#!/home/kingb/aim/venv/bin/python3
import os
import shutil
import glob

# --- CONFIGURATION ---
SOURCE_DIR = "/home/kingb/aim/memory"
VAULT_TARGET = "/home/kingb/OperationsCenterVault/AIM_LOGS"

def sync():
    if not os.path.exists(VAULT_TARGET):
        try:
            os.makedirs(VAULT_TARGET, exist_ok=True)
            print(f"Created A.I.M. export folder in vault: {VAULT_TARGET}")
        except Exception as e:
            print(f"Error creating vault folder: {e}")
            return

    # Sync only .md files
    md_files = glob.glob(os.path.join(SOURCE_DIR, "*.md"))
    
    synced_count = 0
    for src in md_files:
        filename = os.path.basename(src)
        # Skip temporary distillation proposals if they are messy
        if "PROPOSAL" in filename:
            continue
            
        dest = os.path.join(VAULT_TARGET, filename)
        try:
            # Only copy if the file is different or newer
            if not os.path.exists(dest) or os.path.getmtime(src) > os.path.getmtime(dest):
                shutil.copy2(src, dest)
                synced_count += 1
        except Exception as e:
            print(f"Failed to sync {filename}: {e}")

    if synced_count > 0:
        print(f"Synced {synced_count} A.I.M. notes to Obsidian Vault.")

if __name__ == "__main__":
    sync()
