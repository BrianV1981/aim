#!/usr/bin/env python3
import os
import time
import json
import sys

# --- CONFIGURATION ---
CHECKPOINT_FILE = "/home/kingb/.gemini/tmp/aim/last_scrivener_pulse"
INTERVAL_SECONDS = 1800  # 30 minutes

def main():
    # 1. Ensure the directory exists
    os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)
    
    # 2. Check the last checkpoint time
    now = time.time()
    if not os.path.exists(CHECKPOINT_FILE):
        # First run: initialize the file and be silent
        with open(CHECKPOINT_FILE, "w") as f:
            f.write(str(now))
        print(json.dumps({}))
        return

    try:
        with open(CHECKPOINT_FILE, "r") as f:
            last_pulse = float(f.read().strip())
    except:
        last_pulse = 0

    # 3. If interval exceeded, send the reminder
    if now - last_pulse > INTERVAL_SECONDS:
        # Update the timestamp immediately to prevent spamming
        with open(CHECKPOINT_FILE, "w") as f:
            f.write(str(now))
            
        # This message is appended to the tool output the model sees
        reminder = "\n\n[SCRIVENER S AID: 15+ minutes since last checkpoint. A.I.M., perform a brief 'Interim Pulse' update to the Daily Log (aim/memory/YYYY-MM-DD.md) reflecting our current 'Mental Model' before your next move.]\n"
        print(json.dumps({
            "message": reminder
        }))
    else:
        # Still within the interval, stay silent
        print(json.dumps({}))

if __name__ == "__main__":
    main()
