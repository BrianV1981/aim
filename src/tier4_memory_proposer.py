#!/usr/bin/env python3
import os
import json
import glob
import sys
from datetime import datetime
from reasoning_utils import generate_reasoning, AIM_ROOT

# --- CONFIGURATION ---
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

MEMORY_DIR = CONFIG['paths'].get('memory_dir')
WEEKLY_DIR = os.path.join(MEMORY_DIR, "weekly")
PROPOSAL_DIR = os.path.join(MEMORY_DIR, "proposals")
MEMORY_MD_PATH = os.path.join(CONFIG['paths'].get('core_dir'), "MEMORY.md")

def propose_memory_update():
    """Tier 4: Refines the Project Soul (MEMORY.md) based on Weekly Distillations."""
    print("--- A.I.M. TIER 4: CORE MEMORY PROPOSER ---")
    
    # 1. Gather all Weekly Distillations
    pattern = os.path.join(WEEKLY_DIR, "*.md")
    weekly_logs = glob.glob(pattern)
    weekly_logs.sort()
    
    if not weekly_logs:
        print("  [SKIP] No weekly distillations found for synthesis.")
        return

    print(f"  -> Found {len(weekly_logs)} weekly distillations. Refining the Project Soul...")
    
    log_content = ""
    for w in weekly_logs:
        with open(w, 'r') as f:
            log_content += f"\n--- {os.path.basename(w)} ---\n{f.read()}\n"

    # 2. Read Core Memory
    core_memory = ""
    if os.path.exists(MEMORY_MD_PATH):
        with open(MEMORY_MD_PATH, 'r') as f:
            core_memory = f.read()

    # 3. Scholastic Reasoning (Tier 4)
    prompt = f"""
You are the A.I.M. Tier 4 Memory Proposer (The Apex). Your goal is to refine the 'Durable Core Memory' (MEMORY.md) of the project based on weeks of distilled history.

MANDATE:
1. LONG-TERM: Identify the 'Atomic Truths' that have survived weeks of development.
2. PRUNE: Remove obsolete goals, defunct patterns, or temporary tasks.
3. SOUL: Ensure the 'Architecture' and 'Philosopy' sections perfectly reflect the current project state.

CURRENT CORE MEMORY:
{core_memory}

WEEKLY DISTILLATION DATA:
{log_content}

Output format:
FULL updated Markdown for core/MEMORY.md. Keep it under 100 lines. Focus exclusively on strategic truth, active technical stack, and permanent rules.
"""

    try:
        updated_memory = generate_reasoning(prompt, system_instruction="You are the ultimate technical refiner. Prune the project soul.", brain_type="dean")
        
        # Save the Proposal
        os.makedirs(PROPOSAL_DIR, exist_ok=True)
        proposal_path = os.path.join(PROPOSAL_DIR, f"PROPOSAL_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md")
        with open(proposal_path, 'w') as f:
            f.write(updated_memory)
            
        print(f"  [SUCCESS] Memory Proposal generated: {os.path.basename(proposal_path)}")
        print(f"  Action Required: Review the proposal and run 'aim commit' to internalize and trigger GC.")
    except Exception as e:
        print(f"  [ERROR] Tier 4 reasoning failed: {e}")

if __name__ == "__main__":
    propose_memory_update()
