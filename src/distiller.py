#!/usr/bin/env python3
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

    # --- THE ARCHITECTURAL PROMPT (Lean Mandate) ---
    prompt = f"""
You are the A.I.M. Memory Architect. Your goal is to manage the "Durable Tier" of memory (core/MEMORY.md).

CRITICAL CONSTRAINTS (The Lean Mandate):
1. TOKEN TAX AWARENESS: Every line in core/MEMORY.md is injected into every session. Redundancy is expensive.
2. ABSTRACTION HIERARCHY:
   - FORENSIC (Index): Store granular data, file paths, and exact code here. (Not your job).
   - NARRATIVE (Daily Log): Store the "Story" of the project. (Not your job).
   - DURABLE (Memory.md): Store only "Atomic Truths"—rules, finished infrastructure, and core goals.
3. LOSSLESS COMPRESSION: Remove all conversational fluff and process-oriented notes. Keep only the outcome.

YOUR TASK:
Analyze the Daily Log and Current Core Memory to generate:
1. NEW STABLE FACTS: Outcomes and infrastructure that are now "part of the soul."
2. STALE ITEMS: Things in core memory that are finished, proven false, or deprecated.
3. MEMORY DELTA: An ruthlessly lean, high-fidelity version of core/MEMORY.md.

CORE MEMORY:
{core_memory}

LATEST PULSE:
{latest_pulse}

DAILY LOG:
{log_content}

Output format: Markdown. The final section MUST be "### 3. MEMORY DELTA" containing the full updated code for core/MEMORY.md.
"""

    system_instr = "You are a high-fidelity memory architect focused on radical conciseness and token efficiency. Be blunt."

    try:
        distillation = generate_reasoning(prompt, system_instruction=system_instr)
        
        # Save Versioned Proposal
        timestamp_full = datetime.now().strftime("%Y-%m-%d_%H%M")
        proposal_dir = os.path.join(DAILY_LOG_DIR, "proposals")
        os.makedirs(proposal_dir, exist_ok=True)
        proposal_path = os.path.join(proposal_dir, f"PROPOSAL_{timestamp_full}.md")
        
        with open(proposal_path, 'w') as f:
            f.write(distillation)
        print(f"Lean memory proposal generated: {proposal_path}")

        # --- GENERATE NEW CONTEXT PULSE ---
        pulse_prompt = f"Based on the log, write a high-fidelity 'Context Pulse' (mental model) for the next session. Detail only 'The Edge' and debt.\n\nLOG:\n{log_content[-5000:]}"
        pulse_content = generate_reasoning(pulse_prompt, system_instruction="Summarize technical momentum into a Context Pulse.")
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        pulse_path = os.path.join(CONTINUITY_DIR, f"{timestamp}.md")
        
        pulse_content = f"# A.I.M. Context Pulse: {timestamp}\n\n{pulse_content}"
        pulse_content += "\n\n---\n\"I believe I've made my point.\" — **A.I.M. (Auto-Pulse)**"
        
        with open(pulse_path, 'w') as f:
            f.write(pulse_content)
        print(f"Automated Context Pulse saved to: {pulse_path}")

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
