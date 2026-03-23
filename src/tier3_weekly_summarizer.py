#!/usr/bin/env python3
import os
import json
import glob
import sys
from datetime import datetime, timedelta
from reasoning_utils import generate_reasoning, AIM_ROOT

# --- CONFIGURATION ---
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

MEMORY_DIR = CONFIG['paths'].get('memory_dir')
DAILY_DIR = os.path.join(MEMORY_DIR, "daily")
WEEKLY_DIR = os.path.join(MEMORY_DIR, "weekly")
CORE_MEMORY_PATH = os.path.join(AIM_ROOT, "core/MEMORY.md")

def weekly_summarize():
    """Tier 3: Consolidates Daily Distillations into a Weekly Arc and performs Delta Pruning."""
    today = datetime.now()
    week_str = today.strftime('%Y-W%W')
    print(f"--- A.I.M. TIER 3: WEEKLY DISTILLATION ({week_str}) ---")
    
    # 1. Gather Daily Reports from the last 7 days
    reports = []
    file_paths = []
    for i in range(7):
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        path = os.path.join(DAILY_DIR, f"{date_str}.md")
        if os.path.exists(path):
            file_paths.append(path)
            with open(path, 'r') as f:
                reports.append(f"--- DAILY LOG: {date_str} ---\n{f.read()}\n")

    if not reports:
        print("  [SKIP] No daily reports found for this week.")
        return

    print(f"  -> Synthesizing {len(reports)} daily distillations...")
    
    # 2. Read Core Memory for Delta Pruning
    core_memory = ""
    if os.path.exists(CORE_MEMORY_PATH):
        with open(CORE_MEMORY_PATH, 'r') as f:
            core_memory = f.read()

    # 3. Scholastic Reasoning (Tier 3)
    prompt = f"""
You are the A.I.M. Tier 3 Weekly Summarizer. Your goal is to synthesize a week of daily logs into a 'Weekly Strategic Arc'.
Crucially, you must perform Delta Pruning: Compare the week's trajectory against the Core Memory to identify what is stale and what is new.

MANDATE:
1. FOCUS: Identify major architectural shifts, completed milestones, and systemic technical debt.
2. SQUASH: Collapse daily back-and-forth into cohesive weekly outcomes. Ignore temporary bugs that were fixed days later.
3. PRUNE: Identify facts in the Core Memory that are now entirely obsolete based on this week's pivot.

CURRENT CORE MEMORY:
{core_memory}

WEEKLY DATA:
{"".join(reports)}

Output format:
## Weekly Distillation: {week_str}
### 🏆 Major Milestones
(Surgical bullets)

### 🏗️ Architectural Evolution
(Systemic shifts or new patterns)

### 🧹 Delta Pruning Proposal
- **Stale (Remove):** (Obsolete goals or defunct architectural decisions)
- **New (Add):** (Core truths established this week that must be permanently remembered)
"""

    system_instr = "You are a high-level technical summarizer. Consolidate daily history into a strategic weekly arc."

    try:
        report = generate_reasoning(prompt, system_instruction=system_instr, brain_type="fellow")
        
        os.makedirs(WEEKLY_DIR, exist_ok=True)
        report_path = os.path.join(WEEKLY_DIR, f"{week_str}.md")
        with open(report_path, 'w') as f:
            f.write(report)
            
        # Phase 28: Rolling Proposal System
        # Extract the Delta Pruning section and save it as a formal proposal
        proposal_dir = os.path.join(AIM_ROOT, "memory/proposals")
        os.makedirs(proposal_dir, exist_ok=True)
        prop_path = os.path.join(proposal_dir, f"PROPOSAL_{week_str}_T3.md")
        
        if "### 🧹 Delta Pruning Proposal" in report:
            delta = report.split("### 🧹 Delta Pruning Proposal")[1].strip()
            with open(prop_path, 'w') as f:
                f.write(f"### 3. MEMORY DELTA\n\n{delta}")
        else:
            with open(prop_path, 'w') as f:
                f.write(f"### 3. MEMORY DELTA\n\n{report}")
            
        print(f"  [SUCCESS] Weekly Proposal generated: {os.path.basename(prop_path)}")
        
        # 4. AUTOMATIC GARBAGE COLLECTION
        print("  [GC] Cleaning up 7-day cycle...")
        for p in file_paths:
            try:
                os.remove(p)
            except Exception as move_e:
                print(f"  [WARNING] Could not delete daily log {p}: {move_e}")
                
        print("  [SUCCESS] Daily logs purged.")
        
    except Exception as e:
        print(f"  [ERROR] Tier 3 reasoning failed: {e}")

if __name__ == "__main__":
    weekly_summarize()
