#!/usr/bin/env python3
import sys
import json
import os
import glob
from datetime import datetime

# --- DYNAMIC ROOT DISCOVERY ---
def find_aim_root():
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
ARCHIVIST_SYSTEM = """You are the Final Archivist. Your mandate is Extreme Context Compaction. Analyze the current Long-Term Memory and the past month of Weekly Consolidations. Identify systems, features, or logic that have been stable for over a month and compress them into single-sentence axioms. If a feature is 'done', it no longer needs granular operational details in the active brain.

### INPUTS
1. **Weekly Consolidations:** A collection of weekly architectural milestones from the past month.
2. **Current Memory:** The existing `MEMORY.md` file.

### CONSTRAINTS
- **Compress:** Convert verbose operational history into dense, factual axioms.
- **Archive:** If a feature hasn't been actively modified in the weekly states, reduce its footprint in the active memory.
- **Format:** You must PROVIDE A FULL CANDIDATE for the new MEMORY.md inside the delta block.

### OUTPUT SCHEMA
1. **Monthly Archival Summary:** A brief note on what historical context was successfully compressed into cold storage.
2. **Core Axioms:** The list of dense, single-sentence rules that define the currently stable architecture.
3. **MEMORY DELTA:** The complete text of the updated MEMORY.md file.

### FORMAT
Your final output MUST end with this block:
### 3. MEMORY DELTA
```markdown
<FULL CONTENT OF NEW MEMORY.md>
```
"""

def get_recent_weekly_states(weeks=4):
    """Gathers weekly state files generated within the last X weeks."""
    proposals = glob.glob(os.path.join(PROPOSAL_DIR, "PROPOSAL_*_WEEKLY.md"))
    # For safety/context, limit to the recent month's worth (roughly 4 files)
    proposals.sort(reverse=True)
    
    combined = ""
    for prop in proposals[:weeks]:
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
        print("No recent weekly states found. Skipping monthly archival.")
        return

    prompt = f"### RECENT WEEKLY STATES\n{weekly_states}\n\n### CURRENT MEMORY\n{current_memory}"
    
    print("[STAGE 5] Generating Monthly Archive Compaction...")
    # Trigger Tier 5 routing
    monthly_state = generate_reasoning(prompt, system_instruction=ARCHIVIST_SYSTEM, brain_type="tier5")
    
    if "[ERROR: CAPACITY_LOCKOUT]" in monthly_state:
        print("\n[ARCHIVIST SUSPENDED] Google servers are out of capacity. Pausing Stage 5 to prevent silent degradation.")
        sys.exit(0)
        
    if not monthly_state:
        sys.exit("Error: Failed to generate monthly archive.")

    os.makedirs(PROPOSAL_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Mark this as a MONTHLY consolidation (the final tier)
    proposal_path = os.path.join(PROPOSAL_DIR, f"PROPOSAL_{timestamp}_MONTHLY.md")
    
    with open(proposal_path, 'w') as f:
        f.write(monthly_state)
    
    print(f"[SUCCESS] Monthly Archive saved to: {os.path.basename(proposal_path)}")

if __name__ == "__main__":
    main()
