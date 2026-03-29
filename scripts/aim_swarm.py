#!/usr/bin/env python3
"""
A.I.M. Swarm Orchestrator
Provides the frictionless `aim swarm up` and `aim swarm down` commands.
"""

import sys
import os
import subprocess
import time

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNAPSE_DIR = os.path.expanduser("~/Synapse")

def cmd_down():
    """Kills all Swarm nodes, bridges, and the Synapse server."""
    print("--- ASSASSINATING SWARM ---")
    
    # 1. Kill the Synapse UI and Server
    stop_script = os.path.join(SYNAPSE_DIR, "scripts/dev-stack-stop.sh")
    if os.path.exists(stop_script):
        subprocess.run(["bash", stop_script, "claw95"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(["tmux", "kill-session", "-t", "claw95"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    # 2. Kill the A.I.M. Agent Nodes
    subprocess.run(["tmux", "kill-session", "-t", "backend_node"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["tmux", "kill-session", "-t", "frontend_node"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 3. Purge the Python Bridges
    subprocess.run(["pkill", "-f", "claw_bridge.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("[SUCCESS] All nodes offline. Swarm is dead.")

def cmd_up():
    """Boots the entire Swarm architecture and attaches the user."""
    print("--- BOOTING SOVEREIGN SWARM ---")
    
    if not os.path.exists(SYNAPSE_DIR):
        print(f"[ERROR] Synapse directory not found at {SYNAPSE_DIR}.")
        sys.exit(1)

    # 1. Ensure a clean slate
    cmd_down()
    print("")
    
    # 2. Spawn the A.I.M. Agents
    print("[*] Spawning Agent: Backend (Headless Tmux)")
    backend_cmd = 'cd ~/aim_benchmarks/swarm_backend && source venv/bin/activate && gemini'
    subprocess.run(["tmux", "new-session", "-d", "-s", "backend_node", f"bash -c '{backend_cmd}'"], check=True)
    
    print("[*] Spawning Agent: Frontend (Headless Tmux)")
    frontend_cmd = 'cd ~/aim_benchmarks/swarm_frontend && source venv/bin/activate && gemini'
    subprocess.run(["tmux", "new-session", "-d", "-s", "frontend_node", f"bash -c '{frontend_cmd}'"], check=True)
    
    # 3. Boot the Synapse Server silently in the background
    print("[*] Starting Synapse WebSocket Server...")
    # dev-stack.sh creates the UI, so we just run it. It will attach automatically at the end.
    
    # 4. Plug in the Bridges
    print("[*] Jacking agents into the WebSocket room via Bridge...")
    python_bin = os.path.join(AIM_ROOT, "venv/bin/python3")
    bridge_script = os.path.join(AIM_ROOT, "scripts/claw_bridge.py")
    
    # Fire and forget
    subprocess.Popen([python_bin, bridge_script, "--name", "Backend", "--tmux", "backend_node"], 
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.Popen([python_bin, bridge_script, "--name", "Frontend", "--tmux", "frontend_node"], 
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                     
    time.sleep(1.5) # Give the bridges a second to bind
    
    print("[SUCCESS] Swarm is online. Dropping you into the Cortex...")
    time.sleep(1)
    
    # 5. Launch the UI (This hijacks the terminal)
    dev_stack = os.path.join(SYNAPSE_DIR, "scripts/dev-stack.sh")
    os.system(f"cd {SYNAPSE_DIR} && {dev_stack}")

def cmd_status():
    print("--- SWARM STATUS ---")
    os.system("tmux ls")

def main():
    if len(sys.argv) < 2:
        print("Usage: aim swarm [up|down|status]")
        sys.exit(1)
        
    action = sys.argv[1].lower()
    if action == "up":
        cmd_up()
    elif action == "down":
        cmd_down()
    elif action == "status":
        cmd_status()
    else:
        print(f"Unknown action: {action}")

if __name__ == "__main__":
    main()
