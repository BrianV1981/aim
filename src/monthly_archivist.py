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
    from memory_utils import commit_proposal
except ImportError:
    commit_proposal = None

CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
MEMORY_PATH = os.path.join(AIM_ROOT, "core/MEMORY.md")
PROPOSAL_DIR = os.path.join(AIM_ROOT, "memory/proposals")

if not os.path.exists(CONFIG_PATH):
    sys.exit("Error: CONFIG.json not found.")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

# --- PROMPT ---
ARCHIVIST_SYSTEM = """You are the Final Archivist (Tier 5). Your mandate is Extreme Context Compaction and Memory Solidification. Analyze the current Long-Term Memory and the past month of Weekly Consolidations. 

### INPUTS
1. **Weekly Consolidations:** A collection of architectural milestones from the past month.
2. **Current Memory:** The existing `MEMORY.md` file.

### CONSTRAINTS
- **Compress:** Convert verbose operational history into dense, factual axioms.
- **Archive:** If a feature hasn't been modified in the weekly states, reduce its footprint in the active memory.
- **Format:** You must PROVIDE A FULL CANDIDATE for the new MEMORY.md inside the delta block.

### OUTPUT SCHEMA
1. **Monthly Archival Summary:** Brief note on what historical context was solidified.
2. **Proposed Adds:** The list of dense, single-sentence rules or axioms to record.
3. **Proposed Removes:** Outdated context or transient details to purge.
4. **MEMORY DELTA:** The complete text of the updated MEMORY.md file.

### FORMAT
Your final output MUST end with this block:
### 3. MEMORY DELTA
```markdown
<FULL CONTENT OF NEW MEMORY.md>
```
"""

def get_recent_weekly_states(limit=4):
    """Gathers Tier 4 proposals."""
    proposals = glob.glob(os.path.join(PROPOSAL_DIR, "PROPOSAL_*_WEEKLY.md"))
    proposals.sort(reverse=True)
    
    combined = ""
    for prop in proposals[:limit]:
        with open(prop, 'r') as f:
            combined += f"--- WEEKLY STATE: {os.path.basename(prop)} ---\n{f.read()}\n\n"
    return combined

def main():
    if not generate_reasoning:
        sys.exit("Error: reasoning_utils not available.")

    if not os.path.exists(MEMORY_PATH):
        sys.exit(f"Error: {MEMORY_PATH} not found.")

    with open(MEMORY_PATH, 'r') as f:
        current_memory = f.read()

    weekly_states = get_recent_weekly_states()
    if not weekly_states:
        print("No recent weekly states found. Skipping Tier 5 archival.")
        return

    prompt = f"### RECENT WEEKLY STATES\n{weekly_states}\n\n### CURRENT MEMORY\n{current_memory}"
    
    print("[TIER 5] Generating Monthly Archive Compaction (Failsafe)...")
    monthly_state = generate_reasoning(prompt, system_instruction=ARCHIVIST_SYSTEM, brain_type="tier5")
    
    if "[ERROR: CAPACITY_LOCKOUT]" in monthly_state:
        print("\n[ARCHIVIST SUSPENDED] Google servers are out of capacity. Pausing Stage 5 to prevent silent degradation.")
        sys.exit(0)
        
    if not monthly_state:
        sys.exit("Error: Failed to generate monthly archive.")

    os.makedirs(PROPOSAL_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    proposal_path = os.path.join(PROPOSAL_DIR, f"PROPOSAL_{timestamp}_MONTHLY.md")
    
    with open(proposal_path, 'w') as f:
        f.write(monthly_state)
    
    print(f"[SUCCESS] Monthly Archive saved to: {os.path.basename(proposal_path)}")

    # FAILSAFE: Tier 5 automatically applies the memory
    print("[FAILSAFE] Automatically applying Tier 5 compaction to Durable Memory...")
    if commit_proposal and commit_proposal(AIM_ROOT):
        print("[SUCCESS] Durable Memory (MEMORY.md) updated.")
        
        # Cleanup Scaffolding
        print("[CLEANUP] Purging refinement scaffolding...")
        dirs_to_clean = ["memory/hourly", "memory/proposals"]
        for d in dirs_to_clean:
            target = os.path.join(AIM_ROOT, d)
            if os.path.exists(target):
                for f in glob.glob(os.path.join(target, "*.md")):
                    # Don't delete the one we just archived if it's still there (commit_proposal moves it)
                    if os.path.exists(f):
                        try: os.remove(f)
                        except: pass
        print("[SUCCESS] Refinement cycle complete.")
    else:
        print("[ERROR] Failsafe auto-commit failed.")

if __name__ == "__main__":
    main()
