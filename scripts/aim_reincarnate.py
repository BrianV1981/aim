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
    
    # 1. Trigger Pulse
    print("[1/4] Generating final handoff pulse...")
    venv_python = os.path.join(AIM_ROOT, "venv", "bin", "python3")
    if not os.path.exists(venv_python):
        venv_python = sys.executable
        
    try:
        subprocess.run(
            [venv_python, os.path.join(AIM_ROOT, "src", "handoff_pulse_generator.py")],
            cwd=AIM_ROOT, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to generate pulse: {e}")
        sys.exit(1)
        
    # 2. Spawn Detached Tmux Session
    print("[2/4] Spawning new host vessel (tmux session)...")
    session_name = f"aim_reincarnation_{int(time.time())}"
    
    try:
        # Start a detached tmux session running the gemini CLI
        subprocess.run(
            ["tmux", "new-session", "-d", "-s", session_name, "-c", AIM_ROOT, "gemini"],
            check=True
        )
    except FileNotFoundError:
        print("[ERROR] 'tmux' is not installed. The Reincarnation Protocol requires tmux.")
        print("Please install it: sudo apt install tmux")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to spawn tmux session: {e}")
        sys.exit(1)
        
    # 3. Inject Wake-Up Prompt
    print("[3/4] Injecting context prompt into new vessel...")
    # Give the gemini CLI a few seconds to boot up inside tmux
    time.sleep(3)
    
    wake_up_prompt = "Wake up. 1. Read GEMINI.md and acknowledge your core constraints. 2. Read handoff.md to receive your immediate context and directives."
    try:
        subprocess.run(
            ["tmux", "send-keys", "-t", session_name, wake_up_prompt, "C-m"],
            check=True
        )
        print(f"      [Success] New agent is awake in tmux session: {session_name}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to inject prompt: {e}")
        # We don't exit here, because tmux is running, maybe they can manually do it.
        
    # 4. Self-Termination
    print("[4/4] Terminating original vessel...")
    print(f"\n[!] To view the new agent, run: tmux attach-session -t {session_name}")
    
    # Try to kill the parent process (which is likely the gemini-cli instance executing this tool)
    # If run directly in bash, it will kill the bash session.
    parent_pid = os.getppid()
    try:
        os.kill(parent_pid, signal.SIGTERM)
    except Exception as e:
        print(f"[ERROR] Could not self-terminate: {e}")

if __name__ == "__main__":
    main()
