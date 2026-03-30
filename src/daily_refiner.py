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
REFINER_SYSTEM = """You are the Daily Cognitive Refiner (Tier 3). Your objective is to ingest multiple Tier 2 ARC proposals and distill them into a single, cohesive Daily State. 

### INPUTS
1. **Tier 2 Proposals:** Memory changes proposed over the last 24 hours.
2. **Current Memory:** The existing `MEMORY.md` file.

### CONSTRAINTS
- **ARC ONLY:** Do not output the entire MEMORY.md file.
- **Deduplicate:** If an error was introduced in Hour 2 and fixed in Hour 6, omit the error entirely. 
- **Synthesize:** Group granular hourly tasks into broader daily achievements.
"""

def get_recent_proposals():
    """Gathers all new Tier 2 proposals."""
    proposals = glob.glob(os.path.join(PROPOSAL_DIR, "PROPOSAL_*_DELTA.md"))
    proposals.sort()
    
    combined = ""
    for prop in proposals:
        with open(prop, 'r') as f:
            combined += f"--- TIER 2 PROPOSAL: {os.path.basename(prop)} ---\n{f.read()}\n\n"
    return proposals, combined

def main():
    # WATERFALL CHECK
    interval = CONFIG.get('memory_pipeline', {}).get('intervals', {}).get('tier3', 24)
    if not should_run_tier("tier3", interval):
        return

    if not generate_reasoning:
        sys.exit("Error: reasoning_utils not available.")

    if not os.path.exists(MEMORY_PATH):
        sys.exit(f"Error: {MEMORY_PATH} not found.")

    with open(MEMORY_PATH, 'r') as f:
        current_memory = f.read()

    proposal_files, combined_proposals = get_recent_proposals()
    if not combined_proposals:
        return

    prompt = f"### RECENT TIER 2 PROPOSALS\n{combined_proposals}\n\n### CURRENT MEMORY\n{current_memory}"
    
    print("[TIER 3] Generating Daily ARC State...")
    daily_state = generate_reasoning(prompt, system_instruction=REFINER_SYSTEM, brain_type="tier3")
    
    if not daily_state or "[ERROR: CAPACITY_LOCKOUT]" in daily_state:
        return

    os.makedirs(PROPOSAL_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    proposal_path = os.path.join(PROPOSAL_DIR, f"PROPOSAL_{timestamp}_DAILY.md")
    
    with open(proposal_path, 'w') as f:
        f.write(daily_state)
    
    print(f"[SUCCESS] Tier 3 Daily State saved: {os.path.basename(proposal_path)}")

    # CONSUME & CLEAN
    mode = CONFIG.get('memory_pipeline', {}).get('cleanup_mode', 'archive')
    cleanup_consumed_files(proposal_files, mode)
    mark_tier_run("tier3")

if __name__ == "__main__":
    main()
