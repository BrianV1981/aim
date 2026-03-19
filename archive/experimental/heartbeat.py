#!/usr/bin/env python3
# --- STATUS: DECOMMISSIONED / ON HOLD (Token Burn Risk) ---
# This script was developed for high-frequency distillation but is 
# currently inactive to prevent unnecessary API costs.
# Use hooks/scrivener_aid.py for reactive 30-minute distillation.
# -----------------------------------------------------------
import os
import json
import subprocess
import sys
import keyring
import glob
from datetime import datetime
from google import genai

# --- CONFIGURATION (Load from core/CONFIG.json) ---
BASE_DIR = "/home/kingb/aim"
CONFIG_PATH = os.path.join(BASE_DIR, "core/CONFIG.json")
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

# Retrieve API key from local keyring
API_KEY = keyring.get_password("aim-system", "google-api-key")
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    print("ERROR: GOOGLE_API_KEY not found in keyring.", file=sys.stderr)
    sys.exit(1)

MODEL = CONFIG['models'].get('heartbeat', 'gemini-1.5-flash-8b')
HEARTBEAT_MD = os.path.join(BASE_DIR, "core/HEARTBEAT.md")
DAILY_LOG_DIR = CONFIG['paths']['memory_dir']
ARCHIVE_RAW_DIR = CONFIG['paths']['archive_raw_dir']

def get_git_status():
    """Checks for uncommitted changes."""
    try:
        status = subprocess.check_output(["git", "status", "--short"], cwd=BASE_DIR).decode().strip()
        return status if status else "CLEAN"
    except:
        return "ERROR"

def get_index_health():
    """Checks for unindexed raw files."""
    raw_files = glob.glob(os.path.join(ARCHIVE_RAW_DIR, "*.json"))
    indexed_files = glob.glob(os.path.join(CONFIG['paths']['archive_index_dir'], "*.fragments.json"))
    
    unindexed_count = 0
    for rf in raw_files:
        if not os.path.exists(rf.replace(".json", ".fragments.json").replace(ARCHIVE_RAW_DIR, CONFIG['paths']['archive_index_dir'])):
            unindexed_count += 1
    
    return "HEALTHY" if unindexed_count == 0 else f"{unindexed_count} FILES PENDING INDEXING"

def perform_distillation():
    """Distills ONLY the new entries from the daily log."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(DAILY_LOG_DIR, f"{today}.md")
    
    if not os.path.exists(log_path):
        return "No daily log found for today."

    # 1. Read Daily Log
    with open(log_path, 'r') as f:
        full_log = f.read()

    # 2. Check for the last processed session in HEARTBEAT.md to find our diff
    # Simple strategy: find the last session ID mentioned in the log and the heartbeat
    # For now, let's just send the last 100 lines of the daily log to keep it token-efficient.
    log_lines = full_log.splitlines()
    recent_log = "\n".join(log_lines[-100:])

    prompt = f"""
Distill these recent session logs into a one-sentence summary of current progress and a one-sentence summary of the next task.
Be extremely concise. Use Brian's preferred "Direct & Blunt" tone.

LOG:
{recent_log}
"""
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"Distillation Error: {str(e)}"

def update_heartbeat():
    git_status = get_git_status()
    index_health = get_index_health()
    distillation = perform_distillation()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Construct the new Pulse Log entry
    new_pulse = f"""
## 🕒 Heartbeat Update: {timestamp}
- **Git Status:** {git_status}
- **Index Health:** {index_health}
- **Keyring Active:** YES
- **Current Momentum:** {distillation}
"""

    # Update core/HEARTBEAT.md
    with open(HEARTBEAT_MD, 'r') as f:
        content = f.read()

    # We append the pulse to the end, or replace the last one.
    # To keep HEARTBEAT.md lean, let's just keep the last 5 pulses.
    if "## 📜 Pulse Log" in content:
        header, history = content.split("## 📜 Pulse Log")
        
        # Parse existing pulses (very simple split)
        pulses = history.split("## 🕒 Heartbeat Update:")[1:]
        pulses = [p.strip() for p in pulses]
        
        # Add the new one at the top
        pulses.insert(0, new_pulse.replace("## 🕒 Heartbeat Update: ", "").strip())
        
        # Keep only top 5
        pulses = pulses[:5]
        
        new_history = "\n\n## 📜 Pulse Log\n"
        for p in pulses:
            new_history += f"\n## 🕒 Heartbeat Update: {p}\n"
        
        with open(HEARTBEAT_MD, 'w') as f:
            f.write(header + new_history)
    else:
        # Fallback if the file structure is different
        with open(HEARTBEAT_MD, 'a') as f:
            f.write(new_pulse)

if __name__ == "__main__":
    print(f"--- A.I.M. Heartbeat Protocol (Sovereign SDK: {MODEL}) ---")
    update_heartbeat()
    print("Heartbeat synchronized.")
