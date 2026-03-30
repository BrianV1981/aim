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

CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
MEMORY_PATH = os.path.join(AIM_ROOT, "core/MEMORY.md")
PROPOSAL_DIR = os.path.join(AIM_ROOT, "memory/proposals")

if not os.path.exists(CONFIG_PATH):
    sys.exit("Error: CONFIG.json not found.")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

# --- PROMPT ---
CONSOLIDATOR_SYSTEM = """You are the Strategic Consolidator (Tier 4). Distill the past 7 Daily States into high-level project milestones. Strip away transient debugging steps. Focus only on permanent architectural changes and core dependencies.

### INPUTS
1. **Daily States:** A collection of Tier 3 daily memory refinements from the past week.
2. **Current Memory:** The existing `MEMORY.md` file.

### CONSTRAINTS
- **ARC ONLY:** Do not output the entire MEMORY.md file.
- **Elevate:** Move from 'micro' technical details to 'macro' project arcs.
- **Deduplicate:** Merge related daily updates into single cohesive feature blocks.

### OUTPUT SCHEMA
1. **Weekly Arc Synthesis:** A high-level summary of the week's primary achievements.
2. **Proposed Adds:** Consolidated architectural milestones or rules.
3. **Proposed Removes:** Outdated facts or redundant operational details.
4. **Architectural Shifts:** Major structural changes or new dependencies introduced.
"""

def get_recent_daily_states(limit=10):
    """Gathers Tier 3 proposals."""
    proposals = glob.glob(os.path.join(PROPOSAL_DIR, "PROPOSAL_*_DAILY.md"))
    proposals.sort(reverse=True)
    
    combined = ""
    for prop in proposals[:limit]:
        with open(prop, 'r') as f:
            combined += f"--- DAILY STATE: {os.path.basename(prop)} ---\n{f.read()}\n\n"
    return combined

def main():
    if not generate_reasoning:
        sys.exit("Error: reasoning_utils not available.")

    if not os.path.exists(MEMORY_PATH):
        sys.exit(f"Error: {MEMORY_PATH} not found.")

    with open(MEMORY_PATH, 'r') as f:
        current_memory = f.read()

    daily_states = get_recent_daily_states()
    if not daily_states:
        print("No recent daily states found. Skipping Tier 4 consolidation.")
        return

    prompt = f"### RECENT DAILY STATES\n{daily_states}\n\n### CURRENT MEMORY\n{current_memory}"
    
    print("[TIER 4] Generating Weekly ARC Consolidation...")
    weekly_state = generate_reasoning(prompt, system_instruction=CONSOLIDATOR_SYSTEM, brain_type="tier4")
    
    if "[ERROR: CAPACITY_LOCKOUT]" in weekly_state:
        print("\n[CONSOLIDATOR SUSPENDED] Google servers are out of capacity. Pausing Tier 4.")
        sys.exit(0)
        
    if not weekly_state:
        sys.exit("Error: Failed to generate weekly consolidation.")

    os.makedirs(PROPOSAL_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    proposal_path = os.path.join(PROPOSAL_DIR, f"PROPOSAL_{timestamp}_WEEKLY.md")
    
    with open(proposal_path, 'w') as f:
        f.write(weekly_state)
    
    print(f"[SUCCESS] Tier 4 Weekly State saved to: {os.path.basename(proposal_path)}")

if __name__ == "__main__":
    main()
