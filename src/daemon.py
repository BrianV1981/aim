#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import json
from datetime import datetime

# --- CONFIG BOOTSTRAP ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root(os.getcwd())
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
DAEMON_LOG = os.path.join(AIM_ROOT, "archive/daemon.log")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(DAEMON_LOG, "a") as f:
        f.write(line + "\n")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

# --- ENVIRONMENTAL SENSES (THE STATE MACHINE) ---

def check_combat_loop():
    """State 1: Are tests failing?"""
    if not os.path.exists(os.path.join(AIM_ROOT, "pytest.ini")) and not os.path.exists(os.path.join(AIM_ROOT, "tests")):
        return False, ""
    try:
        res = subprocess.run(["pytest"], cwd=AIM_ROOT, capture_output=True, text=True)
        if res.returncode != 0:
            return True, "The Combat Loop (Tests Failing)"
    except Exception:
        pass
    return False, ""

def check_nav_loop():
    """State 2: Are there uncommitted changes?"""
    try:
        res = subprocess.run(["git", "status", "--porcelain"], cwd=AIM_ROOT, capture_output=True, text=True)
        if res.stdout.strip():
            return True, "The Nav Loop (Uncommitted Changes)"
    except Exception:
        pass
    return False, ""

def check_looting_loop():
    """State 3: Are there open GitHub issues?"""
    try:
        res = subprocess.run(["gh", "issue", "list", "--state", "open", "--json", "number"], cwd=AIM_ROOT, capture_output=True, text=True)
        if res.returncode == 0:
            issues = json.loads(res.stdout)
            if len(issues) > 0:
                return True, f"The Looting Loop ({len(issues)} Open Issues)"
    except Exception:
        pass
    return False, ""

def get_environmental_state():
    """Evaluates the state machine hierarchy (Combat > Nav > Looting > Buff)."""
    is_combat, c_msg = check_combat_loop()
    if is_combat:
        return c_msg, "[URGENT] Pytest is failing. You must immediately isolate the failing test, read the stack trace, and apply a fix to the codebase."
    
    cli_name = os.path.basename(AIM_ROOT)
    is_nav, n_msg = check_nav_loop()
    if is_nav:
        return n_msg, f"There are uncommitted changes in the workspace. You must finish your current thought, verify the code works, and run `{cli_name} push` to complete the GitOps deployment."

    is_looting, l_msg = check_looting_loop()
    if is_looting:
        return l_msg, f"There are open bugs in the issue tracker. Run `{cli_name} bug` or use the GitHub CLI to read the top issue, checkout a fix branch (`{cli_name} fix <id>`), and patch the bug."
    return "The Buff Loop (Green Status)", "The repository is stable. No failing tests, no open bugs, and no pending commits. Read `docs/ROADMAP.md` and autonomously begin implementing the next unchecked phase."

from plugins.datajack.quarantine_daemon import process_quarantine

# --- THE PULSE INJECTOR ---

def inject_pulse(prompt):
    """Fires the autonomic prompt into the AI."""
    log(f"Injecting Pulse: {prompt}")
    
    # We write the Daemon directive to a specific file so the AI has context
    pulse_file = os.path.join(AIM_ROOT, "core/DAEMON_PULSE.md")
    with open(pulse_file, "w") as f:
        f.write(f"# AUTONOMIC HEARTBEAT\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n**DIRECTIVE:**\n{prompt}\n")

    # In a headless environment, we pipe the prompt directly into the Gemini CLI.
    # We append the 'y' flag mentally, or let it rely on the operator's YOLO setting.
    injection_command = f'echo "SYSTEM OVERRIDE: {prompt} Read core/DAEMON_PULSE.md for details." | gemini chat'
    
    try:
        subprocess.Popen(injection_command, shell=True, cwd=AIM_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        log(f"Failed to inject pulse: {e}")

# --- DAEMON MAIN LOOP ---

def run_subconscious_daemon(vault_path):
    import shutil
    inbox_dir = os.path.join(vault_path, "AIM_Inbox")
    engrams_dir = os.path.join(vault_path, ".engrams")
    processed_dir = os.path.join(vault_path, "AIM_Processed")
    
    os.makedirs(inbox_dir, exist_ok=True)
    os.makedirs(engrams_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    log(f"A.I.M. Subconscious Watchdog started.")
    log(f"Monitoring: {inbox_dir}")
    log(f"Outputting to: {engrams_dir}")
    
    # Event-Driven Polling Loop (Platform Agnostic)
    while True:
        try:
            if os.path.exists(inbox_dir):
                files = [f for f in os.listdir(inbox_dir) if f.endswith('.md')]
                for file_name in files:
                    file_path = os.path.join(inbox_dir, file_name)
                    log(f"🧠 SIGNAL DETECTED in Inbox: {file_name}")
                    
                    # We copy it to the local archive/history directory
                    history_dir = os.path.join(AIM_ROOT, "archive/history")
                    os.makedirs(history_dir, exist_ok=True)
                    local_path = os.path.join(history_dir, file_name)
                    shutil.copy2(file_path, local_path)
                    
                    # Trigger the Single-Shot Compiler
                    log(f"Triggering Single-Shot Compiler on {file_name}...")
                    subprocess.run([sys.executable, os.path.join(AIM_ROOT, "hooks/session_summarizer.py"), local_path], cwd=AIM_ROOT)
                    
                    # Move the processed file out of the inbox
                    shutil.move(file_path, os.path.join(processed_dir, file_name))
                    log(f"Compilation complete. Session {file_name} archived.")
                    
            time.sleep(5) # Watchdog interval
        except KeyboardInterrupt:
            log("Watchdog terminated by user.")
            break
        except Exception as e:
            log(f"Watchdog error: {e}")
            time.sleep(10)

def run_daemon():
    config = load_config()
    mode = config.get('settings', {}).get('cognitive_mode', 'monolithic')
    vault_path = config.get('settings', {}).get('obsidian_vault_path', '')
    
    if mode == "subconscious":
        if not vault_path:
            log("[ERROR] Subconscious mode requires an Obsidian Vault Path to be configured.")
            return
        run_subconscious_daemon(vault_path)
        return
        
    # Default Monolithic Pulse Daemon
    interval = config.get("settings", {}).get("daemon_interval_seconds", 14400)
    
    log(f"A.I.M. Autonomous Daemon started. Polling interval: {interval} seconds.")
    
    while True:
        try:
            process_quarantine()
            state_name, prompt = get_environmental_state()
            log(f"Environment Assessed -> {state_name}")
            inject_pulse(prompt)
            
            # Sleep until the next heartbeat
            time.sleep(interval)
        except KeyboardInterrupt:
            log("Daemon terminated by user.")
            break
        except Exception as e:
            log(f"Daemon encountered a fatal error: {e}")
            time.sleep(60) # Backoff on error

if __name__ == "__main__":
    run_daemon()
