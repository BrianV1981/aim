#!/usr/bin/env python3
import sys
import json
import os
import glob
from datetime import datetime

# --- DYNAMIC ROOT DISCOVERY ---
def find_aim_root():
    """Dynamically discovers the A.I.M. root directory."""
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core", "CONFIG.json")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
sys.path.append(os.path.join(AIM_ROOT, "src"))

try:
    from reasoning_utils import generate_reasoning
except ImportError:
    generate_reasoning = None

try:
    from memory_utils import should_run_tier, mark_tier_run, cleanup_consumed_files
except ImportError:
    should_run_tier = lambda x, y: True
    mark_tier_run = lambda x: None
    cleanup_consumed_files = lambda x, y: None

CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
MEMORY_PATH = os.path.join(AIM_ROOT, "core/MEMORY.md")
PROPOSAL_DIR = os.path.join(AIM_ROOT, "memory/proposals")

if not os.path.exists(CONFIG_PATH):
    sys.exit("Error: CONFIG.json not found.")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

# --- PROMPT ---
CONSOLIDATOR_SYSTEM = """You are the Strategic Consolidator (Tier 4). Distill the past week of Daily States into high-level project milestones. Focus on permanent architectural changes and core dependencies.

### INPUTS
1. **Daily States:** A collection of Tier 3 daily memory refinements from the past week.
2. **Current Memory:** The existing `MEMORY.md` file.

### CONSTRAINTS
- **ARC ONLY:** Do not output the entire MEMORY.md file.
- **Elevate:** Move from 'micro' technical details to 'macro' project arcs.
"""

def get_recent_daily_states():
    """Gathers Tier 3 proposals."""
    proposals = glob.glob(os.path.join(PROPOSAL_DIR, "PROPOSAL_*_DAILY.md"))
    proposals.sort()
    
    combined = ""
    for prop in proposals:
        with open(prop, 'r') as f:
            combined += f"--- DAILY STATE: {os.path.basename(prop)} ---\n{f.read()}\n\n"
    return proposals, combined

def main():
    # WATERFALL CHECK
    interval = CONFIG.get('memory_pipeline', {}).get('intervals', {}).get('tier4', 72)
    if not should_run_tier("tier4", interval):
        return

    if not generate_reasoning:
        sys.exit("Error: reasoning_utils not available.")

    if not os.path.exists(MEMORY_PATH):
        sys.exit(f"Error: {MEMORY_PATH} not found.")

    with open(MEMORY_PATH, 'r') as f:
        current_memory = f.read()

    proposal_files, combined_daily = get_recent_daily_states()
    if not combined_daily:
        return

    prompt = f"### RECENT DAILY STATES\n{combined_daily}\n\n### CURRENT MEMORY\n{current_memory}"
    
    print("[TIER 4] Generating Weekly ARC Consolidation...")
    weekly_state = generate_reasoning(prompt, system_instruction=CONSOLIDATOR_SYSTEM, brain_type="tier4")
    
    if not weekly_state or "[ERROR: CAPACITY_LOCKOUT]" in weekly_state:
        return

    os.makedirs(PROPOSAL_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    proposal_path = os.path.join(PROPOSAL_DIR, f"PROPOSAL_{timestamp}_WEEKLY.md")
    
    with open(proposal_path, 'w') as f:
        f.write(weekly_state)
    
    print(f"[SUCCESS] Tier 4 Weekly State saved: {os.path.basename(proposal_path)}")

    # CONSUME & CLEAN
    mode = CONFIG.get('memory_pipeline', {}).get('cleanup_mode', 'archive')
    cleanup_consumed_files(proposal_files, mode)
    mark_tier_run("tier4")

if __name__ == "__main__":
    main()
