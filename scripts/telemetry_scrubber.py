#!/usr/bin/env python3
import os
import re
import glob
import getpass
import keyring
import sys

# --- DYNAMIC CONFIGURATION ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        config_path = os.path.join(current, "core/CONFIG.json")
        if os.path.exists(config_path):
            return current
        current = os.path.dirname(current)
    return "/home/kingb/aim"

AIM_ROOT = find_aim_root(os.getcwd())
ARCHIVE_DIR = os.path.join(AIM_ROOT, "archive/raw")

# --- DYNAMIC SCRUBBING PATTERNS ---
def get_scrub_map():
    user = getpass.getuser()
    scrub_map = {
        r"AIza[0-9A-Za-z-_]{35}": "[GOOGLE_API_KEY_SCRUBBED]",
        rf"/home/{user}/": "[HOME_DIR_SCRUBBED]/",
        r"sk-[a-zA-Z0-9]{48}": "[OPENAI_KEY_SCRUBBED]",
        r"([0-9]{1,3}\.){3}[0-9]{1,3}": "[IP_SCRUBBED]",
        rf"\b{user}\b": "[USER_SCRUBBED]",
        r"J\.A\.R\.V\.I\.S\.?": "A.I.M."
    }
    
    # Ingest keys from keyring if available
    google_key = keyring.get_password("aim-system", "google-api-key")
    if google_key:
        scrub_map[re.escape(google_key)] = "[GOOGLE_API_KEY_SCRUBBED]"
        
    embedding_key = keyring.get_password("aim-system", "embedding-api-key")
    if embedding_key:
        scrub_map[re.escape(embedding_key)] = "[EMBEDDING_API_KEY_SCRUBBED]"
        
    return scrub_map

def scrub_files():
    if not os.path.exists(ARCHIVE_DIR):
        return

    files = glob.glob(os.path.join(ARCHIVE_DIR, "*.json"))
    scrub_map = get_scrub_map()
    
    for file_path in files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            scrubbed_content = content
            for pattern, replacement in scrub_map.items():
                # Note: We use flags=re.IGNORECASE for the username but maybe not for keys
                if "[USER_SCRUBBED]" in replacement:
                    scrubbed_content = re.sub(pattern, replacement, scrubbed_content, flags=re.IGNORECASE)
                else:
                    scrubbed_content = re.sub(pattern, replacement, scrubbed_content)

            if scrubbed_content != content:
                with open(file_path, 'w') as f:
                    f.write(scrubbed_content)
                # print(f"Scrubbed: {os.path.basename(file_path)}")
        except Exception as e:
            sys.stderr.write(f"Error scrubbing {file_path}: {e}\n")

if __name__ == "__main__":
    # print("--- A.I.M. Privacy Hardening: Scrubbing Archive ---")
    scrub_files()
    # print("Scrubbing complete.")
