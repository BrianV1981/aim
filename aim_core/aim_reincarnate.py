#!/usr/bin/env python3
import os
import sys
import subprocess
import time

def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh")): return current
        if os.path.exists(os.path.join(current, "setup.sh")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()

def main():
    print("--- A.I.M. REINCARNATION PROTOCOL ---")
    print("\n[!] CONTEXT FADE DETECTED: We are initiating Reincarnation.")

    print("Assuming the live agent has already written REINCARNATION_GAMEPLAN.md...")
    
    gameplan_path = os.path.join(AIM_ROOT, "continuity", "REINCARNATION_GAMEPLAN.md")
    if not os.path.exists(gameplan_path):
        print(f"\n[FATAL] Missing {gameplan_path}!")
        print("You MUST write a Reincarnation Gameplan before triggering a handoff.")
        sys.exit(1)
        
    mtime = os.path.getmtime(gameplan_path)
    if time.time() - mtime > 300: # 5 minutes
        print(f"\n[FATAL] The REINCARNATION_GAMEPLAN.md is stale (last updated over 5 minutes ago)!")
        print("You MUST update the Gameplan to reflect the current state before triggering a handoff.")
        sys.exit(1)

    print("Verified live agent has recently updated REINCARNATION_GAMEPLAN.md...")

    
    # Give the CLI time to sync the final agent turn
    print("[0/4] Giving the CLI filesystem time to sync the final agent turn...")
    time.sleep(3)
    
    venv_python = os.path.join(AIM_ROOT, "venv", "bin", "python3")
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    # 1. Trigger Pulse & Sync Issues
    print("[1/4] Mechanically extracting session signal & routing to pipelines...")
    try:
        subprocess.run(
            [venv_python, os.path.join(AIM_ROOT, "aim_core", "handoff_pulse_generator.py")],
            cwd=AIM_ROOT, check=True, timeout=120
        )
        
        print("      Syncing remote issues and harvesting closed bugs...")
        subprocess.run(
            [venv_python, os.path.join(AIM_ROOT, "aim_core", "sync_issue_tracker.py")],
            cwd=AIM_ROOT, check=True, timeout=30
        )
        
        # Harvest recently completed bugs into foundry/scraped_docs
        subprocess.run(
            [venv_python, os.path.join(AIM_ROOT, "aim_core", "aim_scraper.py"), "github", "closed", "--limit", "5"],
            cwd=AIM_ROOT, check=False, timeout=30
        )
        
    except subprocess.TimeoutExpired as e:
        print(f"\n[WARNING] A reincarnation subprocess timed out: {e}\nContinuing reincarnation protocol anyway to preserve context...")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to generate handoff: {e}")
        sys.exit(1)
        
    # Pre-capture current session before we spawn a new one, avoiding the tmux default to newest session
    current_session = None
    if os.environ.get("TMUX"):
        try:
            result = subprocess.run(["tmux", "display-message", "-p", "#S"], capture_output=True, text=True)
            current_session = result.stdout.strip()
        except Exception:
            pass

    # 2. Spawn Detached Tmux Session
    print("[2/4] Spawning new host vessel (tmux session)...")
    session_name = f"aim_reincarnation_{int(time.time())}"
    wake_up_prompt = "Wake up. MANDATE: 1. Read AGENTS.md and acknowledge your core constraints. 2. Read continuity/REINCARNATION_GAMEPLAN.md, continuity/ISSUE_TRACKER.md, and continuity/REINCARNATION_CONNECT.md before taking any action or responding. (NOTE: Use run_shell_command with 'cat' to read the continuity files, as they are gitignored and your read_file tool will fail)."
    
    try:
        # Interactive TUI mode — wake-up prompt injected via paste-buffer in [3/4]
        subprocess.run(
            ["tmux", "new-session", "-d", "-s", session_name, "-c", AIM_ROOT, "opencode"],
            check=True
        )
        print(f"      [Success] New agent is awake in tmux session: {session_name}")
    except FileNotFoundError:
        print("[ERROR] 'tmux' is not installed. The Reincarnation Protocol requires tmux.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to spawn tmux session: {e}")
        sys.exit(1)
        
    # 3. Inject Wake-Up Prompt via Buffer System
    print("[3/4] Waiting for TUI to render, then injecting wake-up prompt...")
    time.sleep(3)
    
    tmp_file = "/tmp/reincarnation_prompt.txt"
    with open(tmp_file, "w") as f:
        f.write(wake_up_prompt)
        
    try:
        subprocess.run(["tmux", "load-buffer", tmp_file], check=True)
        subprocess.run(["tmux", "paste-buffer", "-t", session_name], check=True)
        time.sleep(0.5)
        subprocess.run(["tmux", "send-keys", "-t", session_name, "Enter"], check=True)
    except Exception as e:
        print(f"[WARNING] Failed to inject prompt via buffer: {e}")
        
    # 4. The Teleport (Self-Termination)
    print("[4/4] Executing Teleport Sequence...")
    
    time.sleep(2)
    
    teleport_succeeded = False
    
    if os.environ.get("TMUX") and current_session:
        print(f"      [Teleport] TMUX detected. Switching clients from {current_session} to {session_name}...")
        try:
            clients_result = subprocess.run(
                ["tmux", "list-clients", "-t", current_session, "-F", "#{client_name}"],
                capture_output=True, text=True
            )
            clients = clients_result.stdout.strip().split("\n")
            
            for client in clients:
                client = client.strip()
                if client:
                    subprocess.run(
                        ["tmux", "switch-client", "-c", client, "-t", session_name],
                        check=True
                    )
            
            time.sleep(1)
            # Verify: old session should have zero clients after switch
            remaining = subprocess.run(
                ["tmux", "list-clients", "-t", current_session],
                capture_output=True, text=True
            )
            if not remaining.stdout.strip():
                print(f"      [Teleport] All clients switched. Killing old session {current_session}...")
                subprocess.run(["tmux", "kill-session", "-t", current_session])
                teleport_succeeded = True
            else:
                print(f"      [Teleport] {len(remaining.stdout.strip().split(chr(10)))} clients still on {current_session}. Falling through to manual guidance.")
        except Exception as e:
            print(f"      [Teleport] Switch error: {e}. Falling through to manual guidance.")
    
    if not teleport_succeeded:
        connect_dir = os.path.join(AIM_ROOT, "continuity")
        os.makedirs(connect_dir, exist_ok=True)
        connect_path = os.path.join(connect_dir, "REINCARNATION_CONNECT.md")
        instructions = f"""# Reincarnation Connect Instructions

The new agent has been spawned in tmux session: **{session_name}**

## To connect:

**Option A — Attach directly via tmux:**
```
tmux attach-session -t {session_name}
```

**Option B — If opencode needs session selection:**
After attaching via tmux, if opencode shows multiple sessions, use:
```
/session
```
to select the current reincarnation session.

## Session Details
- Session name: `{session_name}`
- Working directory: `{AIM_ROOT}`
- Agent type: opencode (interactive TUI)
"""
        with open(connect_path, "w") as f:
            f.write(instructions)

        print(f"""
[!] Reincarnation complete. The new agent is alive in tmux session: {session_name}

To connect, choose one of the following:

  Option A (direct attach):
    tmux attach-session -t {session_name}

  Option B (if opencode needs session selection):
    tmux attach-session -t {session_name}
    /session

Full instructions saved to: {connect_path}
""")

if __name__ == "__main__":
    main()
