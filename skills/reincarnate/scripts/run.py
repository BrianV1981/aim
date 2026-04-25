#!/usr/bin/env python3
import sys, json, subprocess, os
from pathlib import Path

def find_aim_root():
    current = Path.cwd()
    while current != current.parent:
        if (current / "setup.sh").exists() or (current / "core" / "CONFIG.json").exists():
            return current
        current = current.parent
    return Path.cwd()

aim_root = find_aim_root()

def main():
    try:
        print(json.dumps({"status": "Triggering Reincarnation Pipeline. Disconnecting..."}))
        subprocess.Popen(
            [sys.executable, str(aim_root / "aim_core" / "aim_reincarnate.py")],
            start_new_session=True
        )
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
