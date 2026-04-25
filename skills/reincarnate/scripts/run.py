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
        args = {}
        if len(sys.argv) > 1:
            try:
                args = json.loads(sys.argv[1])
            except:
                pass
                
        handoff_message = args.get("handoff_message", "")
        
        gameplan_path = aim_root / "continuity" / "REINCARNATION_GAMEPLAN.md"
        
        if handoff_message:
            with open(gameplan_path, "a") as f:
                f.write(f"\n\n## Operator Handoff Message\n{handoff_message}\n")
                
        import time
        if not gameplan_path.exists():
            print(json.dumps({"error": f"Missing {gameplan_path}! You MUST write a Reincarnation Gameplan using write_file before triggering a handoff."}))
            return
            
        if time.time() - gameplan_path.stat().st_mtime > 300:
            print(json.dumps({"error": f"The REINCARNATION_GAMEPLAN.md is stale (last updated over 5 minutes ago)! You MUST update the Gameplan using write_file to reflect the current state before triggering a handoff."}))
            return

                
        print(json.dumps({"status": "Triggering Reincarnation Pipeline. Disconnecting..."}))
        
        # We call aim_reincarnate.py in the background. It will pause for 3s to let the CLI save history.
        subprocess.Popen(
            [sys.executable, str(aim_root / "aim_core" / "aim_reincarnate.py")],
            start_new_session=True
        )
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
