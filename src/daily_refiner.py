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
REFINER_SYSTEM = """You are the Daily Cognitive Refiner. Your objective is to ingest multiple hourly memory proposals and distill them into a single, cohesive Daily State Delta. 

### INPUTS
1. **Hourly Proposals:** A collection of memory deltas proposed over the last 24 hours.
2. **Current Memory:** The existing `MEMORY.md` file.

### CONSTRAINTS
- **Deduplicate:** If an error was introduced in Hour 2 and fixed in Hour 6, omit the error entirely from the final state. Only the resolved outcome matters.
- **Synthesize:** Group granular hourly tasks into broader technical achievements.
- **Prune:** Aggressively delete paths or concepts that were abandoned during the day's work.
- You must PROVIDE A FULL CANDIDATE for the new MEMORY.md inside the delta block.

### OUTPUT SCHEMA
1. **Daily Synthesis:** A 2-sentence summary of the day's overall technical momentum.
2. **Resolved Conflicts:** Any contradictory hourly proposals that you resolved (e.g., "Ignored Hour 2 bug because Hour 6 fixed it").
3. **MEMORY DELTA:** The complete text of the updated MEMORY.md file.

### FORMAT
Your final output MUST end with this block:
### 3. MEMORY DELTA
```markdown
<FULL CONTENT OF NEW MEMORY.md>
```
"""

def get_recent_proposals(hours=24):
    """Gathers hourly proposals generated within the last X hours."""
    proposals = glob.glob(os.path.join(PROPOSAL_DIR, "PROPOSAL_*_DELTA.md"))
    # For now, just grab the most recent ones (limit 10 for safety/context size)
    proposals.sort(reverse=True)
    
    combined = ""
    for prop in proposals[:10]:
        with open(prop, 'r') as f:
            combined += f"--- HOURLY PROPOSAL: {os.path.basename(prop)} ---\n{f.read()}\n\n"
    return combined

def main():
    if not generate_reasoning:
        sys.exit("Error: reasoning_utils not available.")

    if not os.path.exists(MEMORY_PATH):
        sys.exit(f"Error: {MEMORY_PATH} not found.")

    with open(MEMORY_PATH, 'r') as f:
        current_memory = f.read()

    proposals = get_recent_proposals()
    if not proposals:
        print("No recent hourly proposals found. Skipping daily refinement.")
        return

    prompt = f"### RECENT HOURLY PROPOSALS\n{proposals}\n\n### CURRENT MEMORY\n{current_memory}"
    
    print("[STAGE 3] Generating Daily State Refinement...")
    # Trigger Tier 3 routing
    daily_state = generate_reasoning(prompt, system_instruction=REFINER_SYSTEM, brain_type="tier3")
    
    if not daily_state:
        sys.exit("Error: Failed to generate daily state.")

    os.makedirs(PROPOSAL_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Mark this as a DAILY refinement so it can be handled differently if needed
    proposal_path = os.path.join(PROPOSAL_DIR, f"PROPOSAL_{timestamp}_DAILY.md")
    
    with open(proposal_path, 'w') as f:
        f.write(daily_state)
    
    print(f"[SUCCESS] Daily Refinement saved to: {os.path.basename(proposal_path)}")

if __name__ == "__main__":
    main()
