#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import signal

def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        if os.path.exists(os.path.join(current, "setup.sh")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()

def main():
    print("--- A.I.M. REINCARNATION PROTOCOL ---")
    print("\n[!] CONTEXT FADE DETECTED: We are initiating Reincarnation.")
    print("Assuming the live agent has already written REINCARNATION_GAMEPLAN.md...")
    
    venv_python = os.path.join(AIM_ROOT, "venv", "bin", "python3")
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    # 1. Trigger Pulse & Sync Issues
    print("[1/4] Mechanically extracting session signal & routing to pipelines...")
    try:
        subprocess.run(
            [venv_python, os.path.join(AIM_ROOT, "src", "handoff_pulse_generator.py")],
            cwd=AIM_ROOT, check=True, timeout=120
        )
        
        print("      Syncing remote issues and harvesting closed bugs...")
        subprocess.run(
            [venv_python, os.path.join(AIM_ROOT, "scripts", "sync_issue_tracker.py")],
            cwd=AIM_ROOT, check=True, timeout=30
        )
        
        # Harvest recently completed bugs into foundry/scraped_docs
        subprocess.run(
            [venv_python, os.path.join(AIM_ROOT, "scripts", "scrape_github_issues.py"), "--limit", "5"],
            cwd=AIM_ROOT, check=False, timeout=30 # Don't fail the whole reincarnation if the scraper encounters an API limit
        )
        
    except subprocess.TimeoutExpired as e:
        print(f"\n[WARNING] A reincarnation subprocess timed out: {e}\nContinuing reincarnation protocol anyway to preserve context...")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to generate handoff: {e}")
        sys.exit(1)
        
    # 2. Spawn Detached Tmux Session
    print("[2/4] Spawning new host vessel (tmux session)...")
    session_name = f"aim_reincarnation_{int(time.time())}"
    wake_up_prompt = "Wake up. MANDATE: 1. Read GEMINI.md and acknowledge your core constraints. 2. Read HANDOFF.md. 3. You must read continuity/REINCARNATION_GAMEPLAN.md, continuity/CURRENT_PULSE.md, and continuity/ISSUE_TRACKER.md before taking any action or responding. (NOTE: Use run_shell_command with 'cat' to read the continuity files, as they are gitignored and your read_file tool will fail)."
    
    try:
        # Start a detached tmux session running the gemini CLI with YOLO mode and inline prompt
        subprocess.run(
            ["tmux", "new-session", "-d", "-s", session_name, "-c", AIM_ROOT, "gemini", "--yolo", "--prompt-interactive", wake_up_prompt],
            check=True
        )
        print(f"      [Success] New agent is awake in tmux session: {session_name}")
    except FileNotFoundError:
        print("[ERROR] 'tmux' is not installed. The Reincarnation Protocol requires tmux.")
        print("Please install it: sudo apt install tmux")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to spawn tmux session: {e}")
        sys.exit(1)
        
    # 3. Inject Wake-Up Prompt
    print("[3/4] Context prompt injected during vessel creation.")
        
    # 4. The Teleport (Self-Termination)
    print("[4/4] Executing Teleport Sequence...")
    
    # Give the filesystem a final moment to sync atomic writes
    time.sleep(2)
    
    if os.environ.get("TMUX"):
        print("      [Teleport] TMUX detected. Switching clients...")
        try:
            # 1. Get the name of the *current* dying session
            result = subprocess.run(["tmux", "display-message", "-p", "#S"], capture_output=True, text=True)
            current_session = result.stdout.strip()
            
            # 2. Force the user's terminal to switch to the new agent
            subprocess.run(["tmux", "switch-client", "-t", session_name], check=True)
            
            # 3. Assassinate the old session to free memory
            if current_session:
                subprocess.run(["tmux", "kill-session", "-t", current_session])
        except Exception as e:
            print(f"[ERROR] Teleport failed: {e}")
            sys.exit(1)
    else:
        # Fallback for non-tmux users
        print(f"\n[!] You are not in tmux. To view the new agent, run:\n    tmux attach-session -t {session_name}")
        parent_pid = os.getppid()
        try:
            os.kill(parent_pid, signal.SIGTERM)
        except Exception as e:
            print(f"[ERROR] Could not self-terminate: {e}")

if __name__ == "__main__":
    main()
