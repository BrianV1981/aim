#!/home/kingb/aim/venv/bin/python3
import os
import re
import glob

# --- CONFIGURATION ---
BASE_DIR = "/home/kingb/aim"
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive/raw")

# --- SCRUBBING PATTERNS ---
SCRUB_MAP = {
    r"AIza[0-9A-Za-z-_]{35}": "[GOOGLE_API_KEY_SCRUBBED]",
    r"/home/[a-z0-9_-]+/": "[HOME_DIR_SCRUBBED]/",
    r"sk-[a-zA-Z0-9]{48}": "[OPENAI_KEY_SCRUBBED]",
    r"([0-9]{1,3}\.){3}[0-9]{1,3}": "[IP_SCRUBBED]",
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}": "[SESSION_ID_SCRUBBED]",
    r"kingb": "[USER_SCRUBBED]",
    r"J\.A\.R\.V\.I\.S\.?": "A.I.M."
}


def scrub_files():
    if not os.path.exists(ARCHIVE_DIR):
        return

    files = glob.glob(os.path.join(ARCHIVE_DIR, "*.json"))
    
    for file_path in files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            scrubbed_content = content
            for pattern, replacement in SCRUB_MAP.items():
                scrubbed_content = re.sub(pattern, replacement, scrubbed_content)

            if scrubbed_content != content:
                with open(file_path, 'w') as f:
                    f.write(scrubbed_content)
                print(f"Scrubbed: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"Error scrubbing {file_path}: {e}")

if __name__ == "__main__":
    print("--- A.I.M. Privacy Hardening: Scrubbing Archive ---")
    scrub_files()
    print("Scrubbing complete.")
