#!/usr/bin/env python3
import os
import time
import json
import shutil
import subprocess
from datetime import datetime

# --- A.I.M. Decoupled Brain Daemon ---
# Designed to run 24/7 on a secondary "Brain" machine.
# Uses a shared file system (Obsidian Sync / Syncthing) as a Zero-API transport layer.

# Configurable paths (can be set via environment variables)
VAULT_ROOT = os.environ.get("AIM_VAULT_ROOT", os.path.expanduser("~/Vault"))
INBOX_DIR = os.path.join(VAULT_ROOT, "AIM_Inbox")
ENGRAM_DIR = os.path.join(VAULT_ROOT, ".engrams")
PROCESSED_DIR = os.path.join(VAULT_ROOT, "AIM_Processed")

# Polling interval in seconds
POLL_INTERVAL = 10

def setup_directories():
    """Ensure the necessary transport layer directories exist."""
    for d in [INBOX_DIR, ENGRAM_DIR, PROCESSED_DIR]:
        os.makedirs(d, exist_ok=True)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] A.I.M. Brain Daemon Initialized.")
    print(f"  Watching: {INBOX_DIR}")
    print(f"  Output:   {ENGRAM_DIR}")

def run_memory_pipeline(session_file):
    """
    Executes the 5-Tier Memory Pipeline (Scribe -> Proposer -> Refiner -> Consolidator -> Archivist).
    In a full production setup, this would invoke the specific tier scripts.
    For the Transport Layer MVP, we will simulate the pipeline parsing and engram generation.
    """
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🧠 SIGNAL DETECTED: {os.path.basename(session_file)}")
    
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
            
        # Simulate processing time
        print("  -> Engaging Tier 1 (Scribe): Extracting narratives...")
        time.sleep(1)
        print("  -> Engaging Tier 2 (Proposer): Identifying memory deltas...")
        time.sleep(1)
        
        # Generate an Engram artifact
        session_id = session_data.get('sessionId', 'unknown_session')
        engram_filename = f"engram_{session_id}_{int(time.time())}.md"
        engram_path = os.path.join(ENGRAM_DIR, engram_filename)
        
        # In reality, this content comes from the LLM via reasoning_utils
        engram_content = f"""---
id: {session_id}
type: engram
date: {datetime.now().strftime('%Y-%m-%d')}
---
# Decoupled Engram Synthesis
*This memory was processed asynchronously by the remote Brain Daemon.*

## Technical Context
The agent successfully executed an offloaded task.
"""
        with open(engram_path, 'w') as ef:
            cf = ef.write(engram_content)
            
        print(f"  -> Successfully forged engram: {engram_path}")
        
        # Move the raw session file out of the inbox to prevent re-processing
        dest_file = os.path.join(PROCESSED_DIR, os.path.basename(session_file))
        shutil.move(session_file, dest_file)
        print(f"  -> Pipeline complete. Session archived to {PROCESSED_DIR}")
        
    except Exception as e:
        print(f"  [ERROR] Pipeline failed on {session_file}: {e}")

def start_daemon():
    setup_directories()
    
    try:
        while True:
            # Poll the inbox for new session payload files
            if os.path.exists(INBOX_DIR):
                files = [os.path.join(INBOX_DIR, f) for f in os.listdir(INBOX_DIR) if f.endswith('.json')]
                for f in files:
                    run_memory_pipeline(f)
            
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] A.I.M. Brain Daemon Shutting Down. Goodbye.")

if __name__ == "__main__":
    start_daemon()
