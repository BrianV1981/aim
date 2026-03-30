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
HOURLY_LOG_DIR = os.path.join(AIM_ROOT, "memory/hourly")

if not os.path.exists(CONFIG_PATH):
    sys.exit("Error: CONFIG.json not found.")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

# --- PROMPT ---
PROPOSER_SYSTEM = """You are a Memory Architect (Tier 2). Your goal is to ingest recent activity reports and propose specific, reasoning-backed updates for the Durable Memory (MEMORY.md).

### INPUTS
1. **Hourly Reports:** Structured technical narratives of recent session deltas.
2. **Current Memory:** The existing state of durable memory.

### CONSTRAINTS
- **ARC SCHEMA:** You must identify exactly what to ADD, REMOVE, or what CONTRADICTS existing knowledge.
- **REASONING ONLY:** Do not output the entire MEMORY.md file. Only output the specific changes needed.

### OUTPUT SCHEMA
1. **Rationale:** Brief summary of why these changes are necessary.
2. **Proposed Adds:** New facts or milestones to record.
3. **Proposed Removes:** Outdated or redundant facts to purge.
4. **Contradictions:** Existing rules in MEMORY.md that are superseded by this delta.
"""

def get_recent_summaries():
    """Gathers all new hourly reports."""
    logs = glob.glob(os.path.join(HOURLY_LOG_DIR, "*.md"))
    logs.sort()
    
    combined = ""
    for log in logs:
        with open(log, 'r') as f:
            combined += f"--- HOURLY REPORT: {os.path.basename(log)} ---\n{f.read()}\n\n"
    return logs, combined

def main():
    # WATERFALL CHECK
    interval = CONFIG.get('memory_pipeline', {}).get('intervals', {}).get('tier2', 12)
    if not should_run_tier("tier2", interval):
        return

    if not generate_reasoning:
        sys.exit("Error: reasoning_utils not available.")

    if not os.path.exists(MEMORY_PATH):
        sys.exit(f"Error: {MEMORY_PATH} not found.")

    with open(MEMORY_PATH, 'r') as f:
        current_memory = f.read()

    log_files, summaries = get_recent_summaries()
    if not summaries:
        return

    prompt = f"### ACTIVITY REPORTS\n{summaries}\n\n### CURRENT MEMORY\n{current_memory}"
    
    print("[TIER 2] Generating ARC Proposal from Hourly Reports...")
    proposal = generate_reasoning(prompt, system_instruction=PROPOSER_SYSTEM, brain_type="tier2")
    
    if not proposal or "[ERROR: CAPACITY_LOCKOUT]" in proposal:
        return

    os.makedirs(PROPOSAL_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    proposal_path = os.path.join(PROPOSAL_DIR, f"PROPOSAL_{timestamp}_DELTA.md")
    
    with open(proposal_path, 'w') as f:
        f.write(proposal)
    
    print(f"[SUCCESS] Tier 2 ARC Proposal saved: {os.path.basename(proposal_path)}")

    # CONSUME & CLEAN
    mode = CONFIG.get('memory_pipeline', {}).get('cleanup_mode', 'archive')
    cleanup_consumed_files(log_files, mode)
    mark_tier_run("tier2")

if __name__ == "__main__":
    main()
