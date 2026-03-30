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
HOURLY_LOG_DIR = os.path.join(AIM_ROOT, "memory/hourly")

if not os.path.exists(CONFIG_PATH):
    sys.exit("Error: CONFIG.json not found.")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

# --- PROMPT ---
PROPOSER_SYSTEM = """You are a Memory Architect (Tier 2). Your goal is to ingest recent 30-minute activity reports and propose updates for the Durable Memory (MEMORY.md).

### INPUTS
1. **Hourly Reports:** Structured reports from Tier 1 identifying Adds, Removes, and Contradictions.
2. **Current Memory:** The existing state of durable memory.

### CONSTRAINTS
- You must output a consolidated structured report.
- Prioritize DELETION of stale facts over simple concatenation.
- Identify contradictory instructions or logic shifts across multiple reports.
- PROVIDE A FULL CANDIDATE for the new MEMORY.md inside the delta block.

### OUTPUT SCHEMA
1. **Rationale:** Brief summary of the consolidated activity.
2. **Proposed Adds:** New facts, milestones, or rules to record.
3. **Proposed Removes:** Outdated or redundant facts to purge.
4. **Contradictions:** Any existing rules in MEMORY.md that were violated or superseded.
5. **MEMORY DELTA:** The complete text of the updated MEMORY.md file.

### FORMAT
Your final output MUST end with this block:
### 3. MEMORY DELTA
```markdown
<FULL CONTENT OF NEW MEMORY.md>
```
"""

def get_recent_summaries(limit=10):
    """Gathers the latest hourly summaries."""
    logs = glob.glob(os.path.join(HOURLY_LOG_DIR, "*.md"))
    logs.sort(reverse=True)
    
    combined = ""
    for log in logs[:limit]:
        with open(log, 'r') as f:
            combined += f"--- HOURLY REPORT: {os.path.basename(log)} ---\n{f.read()}\n\n"
    return combined

def main():
    if not generate_reasoning:
        sys.exit("Error: reasoning_utils not available.")

    if not os.path.exists(MEMORY_PATH):
        sys.exit(f"Error: {MEMORY_PATH} not found.")

    with open(MEMORY_PATH, 'r') as f:
        current_memory = f.read()

    summaries = get_recent_summaries()
    if not summaries:
        print("No recent hourly reports found. Skipping tier 2 proposal.")
        return

    prompt = f"### HOURLY REPORTS\n{summaries}\n\n### CURRENT MEMORY\n{current_memory}"
    
    print("[TIER 2] Consolidating Hourly Reports into Delta Proposal...")
    proposal = generate_reasoning(prompt, system_instruction=PROPOSER_SYSTEM, brain_type="tier2")
    
    if "[ERROR: CAPACITY_LOCKOUT]" in proposal:
        print("\n[PROPOSER SUSPENDED] Google servers are out of capacity. Pausing Tier 2 to prevent silent degradation.")
        sys.exit(0)
        
    if not proposal:
        sys.exit("Error: Failed to generate proposal.")

    os.makedirs(PROPOSAL_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    proposal_path = os.path.join(PROPOSAL_DIR, f"PROPOSAL_{timestamp}_DELTA.md")
    
    with open(proposal_path, 'w') as f:
        f.write(proposal)
    
    print(f"[SUCCESS] Tier 2 Proposal saved to: {os.path.basename(proposal_path)}")

if __name__ == "__main__":
    main()
