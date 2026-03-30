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
ARCHIVIST_SYSTEM = """You are the Final Archivist (Tier 5). Your mandate is Extreme Context Compaction and Memory Solidification. Analyze the past month of Weekly ARC reports. 

### INPUTS
1. **Weekly ARC Reports:** A collection of architectural milestones from the past month.
2. **Current Memory:** The existing `MEMORY.md` file.

### CONSTRAINTS
- **Solidify:** Identify stable architecture and convert it into dense, factual axioms.
- **ARC OUTPUT:** Output a final monthly ARC report identifying exactly what to ADD, REMOVE, or CONTRADICT in the permanent record.
"""

# The Merger Prompt (Used by Tier 5 and aim commit)
MERGE_SYSTEM = """You are the Memory Merger. Your goal is to apply an ARC (Add/Remove/Contradict) report to the Durable Memory (MEMORY.md).

### INPUTS
1. **ARC Report:** The reasoning-backed proposed changes.
2. **Current Memory:** The existing state of durable memory.

### CONSTRAINTS
- **REWRITE:** You must output the ENTIRE updated MEMORY.md file.
- **EXECUTE:** Surgically apply the Adds, Removes, and Contradictions.
- **ZERO LOSS:** Do not lose the Operator's identity or core directives.

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

    # 1. Generate Final ARC Report
    print("[TIER 5] Generating Monthly ARC Compaction...")
    final_arc = generate_reasoning(f"### WEEKLY REPORTS\n{weekly_states}\n\n### CURRENT MEMORY\n{current_memory}", 
                                  system_instruction=ARCHIVIST_SYSTEM, brain_type="tier5")
    
    if not final_arc:
        sys.exit("Error: Failed to generate monthly ARC.")

    # 2. Trigger the Merger to produce the Full Candidate
    print("[TIER 5] Triggering Master Merger to produce new MEMORY.md...")
    full_candidate = generate_reasoning(f"### ARC REPORT\n{final_arc}\n\n### CURRENT MEMORY\n{current_memory}", 
                                       system_instruction=MERGE_SYSTEM, brain_type="tier5")

    if not full_candidate:
        sys.exit("Error: Failed to generate full memory candidate.")

    os.makedirs(PROPOSAL_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    proposal_path = os.path.join(PROPOSAL_DIR, f"PROPOSAL_{timestamp}_MONTHLY.md")
    
    with open(proposal_path, 'w') as f:
        f.write(full_candidate)
    
    print(f"[SUCCESS] Monthly Archive (Full Candidate) saved to: {os.path.basename(proposal_path)}")

    # 3. FAILSAFE: Auto-Apply
    print("[FAILSAFE] Automatically applying Tier 5 to Durable Memory...")
    # Import locally to avoid circular dependencies
    try:
        from memory_utils import commit_proposal
        if commit_proposal(AIM_ROOT):
            print("[SUCCESS] Durable Memory updated.")
            # Full Cleanup
            dirs_to_clean = ["memory/hourly", "memory/proposals"]
            for d in dirs_to_clean:
                target = os.path.join(AIM_ROOT, d)
                if os.path.exists(target):
                    for f in glob.glob(os.path.join(target, "*.md")):
                        try: os.remove(f)
                        except: pass
            print("[SUCCESS] Refinement cycle complete.")
    except Exception as e:
        print(f"[ERROR] Auto-commit failed: {e}")

if __name__ == "__main__":
    main()
