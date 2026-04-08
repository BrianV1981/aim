#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        if os.path.exists(os.path.join(current, "setup.sh")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
CONTINUITY_DIR = os.path.join(AIM_ROOT, "continuity")
UNREAD_MAIL_PATH = os.path.join(CONTINUITY_DIR, "UNREAD_MAIL.md")
CHALKBOARD_DIR = os.path.join(AIM_ROOT, "workspace", "aim-chalkboard")
MAIL_SH_PATH = os.path.join(CHALKBOARD_DIR, "mail.sh")

def main():
    print("--- A.I.M. SWARM POST OFFICE SYNCHRONIZER ---")
    os.makedirs(CONTINUITY_DIR, exist_ok=True)

    if not os.path.exists(MAIL_SH_PATH):
        print(f"[INFO] The Swarm Post Office (aim-chalkboard) is not initialized at {CHALKBOARD_DIR}")
        print("To enable P2P messaging, clone the chalkboard repo into your workspace:")
        print("`git clone https://github.com/BrianV1981/aim-chalkboard workspace/aim-chalkboard`")
        
        # If there's an old unread mail file, we keep it, otherwise do nothing
        if not os.path.exists(UNREAD_MAIL_PATH):
            with open(UNREAD_MAIL_PATH, 'w') as f:
                f.write("*No mail fetched (Chalkboard not initialized).*\n")
        return

    print("[1/2] Syncing Global Chalkboard and checking for unread mail...")
    
    try:
        # Check mail for the "aim" target
        result = subprocess.run(
            ["bash", "mail.sh", "check", "aim"],
            cwd=CHALKBOARD_DIR,
            capture_output=True, text=True, check=True
        )
        output = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to check mail: {e.stderr}")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"[2/2] Writing unread mail delta to {UNREAD_MAIL_PATH}...")
    
    with open(UNREAD_MAIL_PATH, "w", encoding="utf-8") as f:
        f.write(f"## 📨 NEW MAIL FETCHED: {now}\n\n")
        if not output or "No unread mail" in output:
            f.write("*Inbox is empty.*\n")
        else:
            f.write(output + "\n")
            
    print("\n[SUCCESS] Local Unread Mail Tracker is up to date.")
    print("You can view or print the file directly: `cat continuity/UNREAD_MAIL.md`")

if __name__ == "__main__":
    main()
