#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import signal

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
        
    # 2. Spawn Detached Tmux Session
    print("[2/4] Spawning new host vessel (tmux session)...")
    session_name = f"aim_reincarnation_{int(time.time())}"
    wake_up_prompt = "Wake up. MANDATE: 1. Read AGENTS.md and acknowledge your core constraints. 2. Read continuity/REINCARNATION_GAMEPLAN.md and continuity/ISSUE_TRACKER.md before taking any action or responding. (NOTE: Use run_shell_command with 'cat' to read the continuity files, as they are gitignored and your read_file tool will fail)."
    
    try:
        subprocess.run(
            ["tmux", "new-session", "-d", "-s", session_name, "-c", AIM_ROOT, "gemini", "--yolo", "--prompt-interactive", wake_up_prompt],
            check=True
        )
        print(f"      [Success] New agent is awake in tmux session: {session_name}")
    except FileNotFoundError:
        print("[ERROR] 'tmux' is not installed. The Reincarnation Protocol requires tmux.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to spawn tmux session: {e}")
        sys.exit(1)
        
    # 3. Inject Wake-Up Prompt
    print("[3/4] Context prompt injected during vessel creation.")
        
    # 4. The Teleport (Self-Termination)
    print("[4/4] Executing Teleport Sequence...")
    
    time.sleep(2)
    
    if os.environ.get("TMUX"):
        print("      [Teleport] TMUX detected. Switching clients...")
        try:
            result = subprocess.run(["tmux", "display-message", "-p", "#S"], capture_output=True, text=True)
            current_session = result.stdout.strip()
            
            clients_result = subprocess.run(["tmux", "list-clients", "-t", current_session, "-F", "#{client_name}"], capture_output=True, text=True)
            clients = clients_result.stdout.strip().split("\n")
            
            for client in clients:
                client = client.strip()
                if client:
                    subprocess.run(["tmux", "switch-client", "-c", client, "-t", session_name], check=True)
            
            if current_session:
                subprocess.run(["tmux", "kill-session", "-t", current_session])
        except Exception as e:
            print(f"[ERROR] Teleport failed: {e}")
            sys.exit(1)
    else:
        print(f"\n[!] You are not in tmux. To view the new agent, run:\n    tmux attach-session -t {session_name}")
        try:
            input("\nPress Enter to safely exit this session and kill the current agent...")
        except (EOFError, KeyboardInterrupt):
            pass
        parent_pid = os.getppid()
        try:
            os.kill(parent_pid, signal.SIGTERM)
        except Exception as e:
            print(f"[ERROR] Could not self-terminate: {e}")

if __name__ == "__main__":
    main()
