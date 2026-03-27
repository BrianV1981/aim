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
HOURLY_LOG_DIR = os.path.join(AIM_ROOT, "memory/hourly")

if not os.path.exists(CONFIG_PATH):
    sys.exit("Error: CONFIG.json not found.")

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

# --- PROMPT ---
PROPOSER_SYSTEM = """You are a Memory Architect. Your goal is to propose a Delta Ledger for updating A.I.M.'s Durable Long-Term Memory (MEMORY.md).

### INPUTS
1. **Recent Summaries:** Tight narrative summaries of recent session activity.
2. **Current Memory:** The existing state of durable memory.

### CONSTRAINTS
- You must output a STRICT SCHEMA.
- You must prioritize DELETION of stale facts over concatenation.
- You must preserve the Operator's identity and core directives.
- You must PROVIDE A FULL CANDIDATE for the new MEMORY.md inside the delta block.

### OUTPUT SCHEMA
1. **Rationale:** Why are these changes being proposed?
2. **Proposed Adds:** New facts or milestones to be recorded.
3. **Proposed Removes:** Outdated or redundant facts to be purged.
4. **Proposed Modifications:** Existing facts that need surgical updates.
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
            combined += f"--- LOG: {os.path.basename(log)} ---\n{f.read()}\n\n"
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
        print("No recent summaries found. Skipping delta proposal.")
        return

    prompt = f"### RECENT SUMMARIES\n{summaries}\n\n### CURRENT MEMORY\n{current_memory}"
    
    print("[STAGE 2] Generating Memory Delta Proposal...")
    proposal = generate_reasoning(prompt, system_instruction=PROPOSER_SYSTEM, brain_type="tier2")
    
    if "[ERROR: CAPACITY_LOCKOUT]" in proposal:
        print("\n[PROPOSER SUSPENDED] Google servers are out of capacity. Pausing Stage 2 to prevent silent degradation.")
        sys.exit(0)
        
    if not proposal:
        sys.exit("Error: Failed to generate proposal.")

    os.makedirs(PROPOSAL_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    proposal_path = os.path.join(PROPOSAL_DIR, f"PROPOSAL_{timestamp}_DELTA.md")
    
    with open(proposal_path, 'w') as f:
        f.write(proposal)
    
    print(f"[SUCCESS] Proposal saved to: {os.path.basename(proposal_path)}")

if __name__ == "__main__":
    main()
