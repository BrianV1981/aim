#!/home/kingb/aim/venv/bin/python3
import os
import json
import sys
import glob
import subprocess
from datetime import datetime
from reasoning_utils import generate_reasoning, AIM_ROOT

# --- CONFIGURATION (Load from core/CONFIG.json) ---
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

DAILY_LOG_DIR = CONFIG['paths']['memory_dir']
CONTINUITY_DIR = CONFIG['paths']['continuity_dir']
MEMORY_MD_PATH = os.path.join(CONFIG['paths']['core_dir'], "MEMORY.md")

def distill():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(DAILY_LOG_DIR, f"{today}.md")
    
    if not os.path.exists(log_path):
        return

    # 1. Read Daily Log
    with open(log_path, 'r') as f:
        log_content = f.read()

    # 2. Read Core Memory
    core_memory = ""
    if os.path.exists(MEMORY_MD_PATH):
        with open(MEMORY_MD_PATH, 'r') as f:
            core_memory = f.read()

    # 3. Read Latest Pulse (if exists)
    pulse_pattern = os.path.join(CONTINUITY_DIR, "202[0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9][0-9][0-9].md")
    pulses = glob.glob(pulse_pattern)
    latest_pulse = ""
    if pulses:
        pulses.sort(reverse=True)
        with open(pulses[0], 'r') as f:
            latest_pulse = f.read()

    # --- THE ARCHITECTURAL PROMPT ---
    prompt = f"""
You are the A.I.M. Distiller. Your job is to analyze the daily log and current core memory to generate:
1. NEW STABLE FACTS (Techniques, decisions, tools built).
2. STALE ITEMS (Things in core memory that are finished or deprecated).
3. A MEMORY DELTA (A concise, updated version of core/MEMORY.md).

CORE MEMORY:
{core_memory}

LATEST PULSE:
{latest_pulse}

DAILY LOG:
{log_content}

Output the response in Markdown format. The final section MUST be titled "### 3. MEMORY DELTA" and contain the full updated content for core/MEMORY.md.
"""

    system_instr = "You are a high-fidelity memory architect. Be blunt, direct, and technically precise."

    try:
        # Call Unified Reasoning Utility
        distillation = generate_reasoning(prompt, system_instruction=system_instr)
        
        # Save Proposal
        proposal_path = os.path.join(DAILY_LOG_DIR, "DISTILLATION_PROPOSAL.md")
        with open(proposal_path, 'w') as f:
            f.write(distillation)
        print(f"Memory distillation proposal generated: {proposal_path}")

        # --- GENERATE NEW CONTEXT PULSE ---
        # A simpler, transient version for immediate continuity
        pulse_prompt = f"Based on the daily log below, write a high-fidelity 'Context Pulse' (mental model) for the next session. Detail only 'The Edge' (what we are doing right now) and technical debt. Be concise.\n\nLOG:\n{log_content[-5000:]}"
        
        pulse_content = generate_reasoning(pulse_prompt, system_instruction="Summarize the current technical momentum into a Context Pulse.")
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        pulse_path = os.path.join(CONTINUITY_DIR, f"{timestamp}.md")
        
        # Add a clear separator
        pulse_content = f"# A.I.M. Context Pulse: {timestamp}\n\n{pulse_content}"
        pulse_content += "\n\n---\n\"I believe I've made my point.\" — **A.I.M. (Auto-Pulse)**"
        
        with open(pulse_path, 'w') as f:
            f.write(pulse_content)
        print(f"Automated Context Pulse saved to: {pulse_path}")

        # --- OBSIDIAN SYNC (Zero-Burn Integration) ---
        sync_script = os.path.join(AIM_ROOT, "scripts/obsidian_sync.py")
        if os.path.exists(sync_script):
            try:
                subprocess.run([sys.executable, sync_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("Vault sync completed.")
            except: pass
        
    except Exception as e:
        print(f"Failed to generate automated pulse: {e}")

if __name__ == "__main__":
    distill()
