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
    
    # Ask the user for the Gameplan
    print("\n[!] CONTEXT FADE DETECTED: We are initiating Reincarnation.")
    print("What is the Gameplan for the next agent? Give it explicit, rigid directives.")
    gameplan_input = input("Gameplan: ")
    
    gameplan_path = os.path.join(AIM_ROOT, "continuity", "REINCARNATION_GAMEPLAN.md")
    os.makedirs(os.path.dirname(gameplan_path), exist_ok=True)
    with open(gameplan_path, "w", encoding="utf-8") as f:
        f.write("# REINCARNATION GAMEPLAN\n\n")
        f.write("## ⚠️ URGENT DIRECTIVE FOR THE INCOMING AGENT\n")
        f.write("You are reading this because the previous agent suffered from 'System Prompt Fade'. ")
        f.write("Your primary directive upon waking up is to execute the following:\n\n")
        f.write(f"{gameplan_input}\n")
    print("      [Success] Gameplan written to continuity/REINCARNATION_GAMEPLAN.md\n")
    
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
    
    wake_up_prompt = "Wake up. MANDATE: 1. Read GEMINI.md and acknowledge your core constraints. 2. Read handoff.md. 3. You must read continuity/LAST_SESSION_CLEAN.md, continuity/CURRENT_PULSE.md, and ISSUE_TRACKER.md before taking any action or responding."
    try:
        subprocess.run(
            ["tmux", "send-keys", "-t", session_name, wake_up_prompt, "C-m"],
            check=True
        )
        print(f"      [Success] New agent is awake in tmux session: {session_name}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to inject prompt: {e}")
        # We don't exit here, because tmux is running, maybe they can manually do it.
        
    # 4. The Teleport (Self-Termination)
    print("[4/4] Executing Teleport Sequence...")
    
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
