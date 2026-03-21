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

DAILY_LOG_DIR = CONFIG['paths'].get('memory_dir')
MEMORY_MD_PATH = os.path.join(CONFIG['paths'].get('core_dir'), "MEMORY.md")

def dean_synthesis():
    """Tier 4: Refines the Project Soul (MEMORY.md) based on Monthly Arcs."""
    print("--- A.I.M. DEAN MONTHLY SYNTHESIS ---")
    
    # 1. Gather all Weekly Arcs for the current year
    pattern = os.path.join(DAILY_LOG_DIR, "WEEKLY_ARC_*.md")
    arcs = glob.glob(pattern)
    arcs.sort()
    
    if not arcs:
        print("  [SKIP] No weekly arcs found for synthesis.")
        return

    print(f"  -> Found {len(arcs)} weekly arcs. Refining the Project Soul...")
    
    arc_content = ""
    for a in arcs:
        with open(a, 'r') as f:
            arc_content += f"\n--- WEEKLY ARC ---\n{f.read()}\n"

    # 2. Scholastic Reasoning (Dean Tier)
    prompt = f"""
You are the A.I.M. Dean (Tier 4 Specialist). Your goal is to refine the 'Durable Core Memory' (MEMORY.md) of the project.

MANDATE:
1. LONG-TERM: Identify the 'Atomic Truths' that have survived weeks of development.
2. PRUNE: Remove obsolete goals or temporary tasks.
3. SOUL: Ensure the 'Architecture' and 'Philosopy' sections reflect the current project state.

CURRENT CORE MEMORY:
{open(MEMORY_MD_PATH).read() if os.path.exists(MEMORY_MD_PATH) else "Empty."}

MONTHLY MOMENTUM DATA:
{arc_content}

Output format:
FULL updated Markdown for core/MEMORY.md. Keep it under 50 lines. Focus on strategic truth.
"""

    try:
        updated_memory = generate_reasoning(prompt, system_instruction="You are the ultimate technical dean. Refine the project soul.", brain_type="dean")
        
        # Save the Proposal (Dean doesn't auto-commit, he proposes)
        proposal_path = os.path.join(DAILY_LOG_DIR, f"proposals/DEAN_SOUL_PROPOSAL_{datetime.now().strftime('%Y%m%d')}.md")
        os.makedirs(os.path.dirname(proposal_path), exist_ok=True)
        with open(proposal_path, 'w') as f:
            f.write(updated_memory)
            
        print(f"  [SUCCESS] Dean Soul Proposal generated: {os.path.basename(proposal_path)}")
        print(f"  Action Required: Review and run 'aim commit' to internalize.")
    except Exception as e:
        print(f"  [ERROR] Dean reasoning failed: {e}")

if __name__ == "__main__":
    dean_synthesis()
