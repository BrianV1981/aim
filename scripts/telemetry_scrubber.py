#!/home/kingb/aim/venv/bin/python3
import os
import re
import json

# --- CONFIGURATION (Load from core/CONFIG.json) ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        config_path = os.path.join(current, "core/CONFIG.json")
        if os.path.exists(config_path):
            return current
        current = os.path.dirname(current)
    return "/home/kingb/aim"

AIM_ROOT = find_aim_root(os.getcwd())
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

LOG_PATH = os.path.expanduser("~/.gemini/telemetry.log") # Default location

# --- SCRUBBING PATTERNS ---
SCRUB_MAP = {
    r"AIza[0-9A-Za-z-_]{35}": "[GOOGLE_API_KEY_SCRUBBED]",
    r"/home/[a-z0-9_-]+/": "[HOME_DIR_SCRUBBED]/",
    r"sk-[a-zA-Z0-9]{48}": "[OPENAI_KEY_SCRUBBED]",
    r"([0-9]{1,3}\.){3}[0-9]{1,3}": "[IP_SCRUBBED]"
}

def scrub_logs():
    if not os.path.exists(LOG_PATH):
        print(f"No telemetry log found at {LOG_PATH}. Skipping scrubbing.")
        return

    print(f"--- A.I.M. Telemetry Scrubber: Cleaning {LOG_PATH} ---")
    
    try:
        with open(LOG_PATH, 'r') as f:
            content = f.read()

        scrubbed_content = content
        for pattern, replacement in SCRUB_MAP.items():
            scrubbed_content = re.sub(pattern, replacement, scrubbed_content)

        if scrubbed_content != content:
            with open(LOG_PATH, 'w') as f:
                f.write(scrubbed_content)
            print("Successfully scrubbed sensitive data from logs.")
        else:
            print("No sensitive data detected in logs.")

    except Exception as e:
        print(f"Error during log scrubbing: {e}")

if __name__ == "__main__":
    scrub_logs()
