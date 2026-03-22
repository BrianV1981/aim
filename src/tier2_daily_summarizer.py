#!/usr/bin/env python3
import os
import json
import glob
import sys
from datetime import datetime
from reasoning_utils import generate_reasoning, AIM_ROOT

# --- CONFIGURATION ---
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

MEMORY_DIR = CONFIG['paths'].get('memory_dir')
HOURLY_DIR = os.path.join(MEMORY_DIR, "hourly")
DAILY_DIR = os.path.join(MEMORY_DIR, "daily")
CORE_MEMORY_PATH = os.path.join(AIM_ROOT, "core/MEMORY.md")

def daily_summarize(target_date=None):
    """
    Tier 2: Consolidates Hourly Logs into a Daily Distillation and performs Delta Pruning.
    """
    date_str = target_date or datetime.now().strftime("%Y-%m-%d")
    print(f"--- A.I.M. TIER 2: DAILY DISTILLATION ({date_str}) ---")
    
    # 1. Gather all Hourly Logs for the target day
    pattern = os.path.join(HOURLY_DIR, f"{date_str}_*.md")
    hourly_logs = glob.glob(pattern)
    hourly_logs.sort()
    
    if not hourly_logs:
        print(f"  [SKIP] No hourly logs found for {date_str}.")
        return

    print(f"  -> Found {len(hourly_logs)} hourly logs. Synthesizing...")
    
    log_content = ""
    for p in hourly_logs:
        with open(p, 'r') as f:
            log_content += f"\n--- {os.path.basename(p)} ---\n{f.read()}\n"

    # 2. Read Core Memory for Delta Pruning
    core_memory = ""
    if os.path.exists(CORE_MEMORY_PATH):
        with open(CORE_MEMORY_PATH, 'r') as f:
            core_memory = f.read()

    # 3. Scholastic Reasoning (Tier 2 / Chancellor)
    prompt = f"""
You are the A.I.M. Tier 2 Daily Summarizer. Your goal is to synthesize the granular hourly logs into a single 'Daily Distillation'.
Crucially, you must perform Delta Pruning: Compare the day's work against the Core Memory to identify what is stale and what is new.

MANDATE:
1. FOCUS: Capture logic shifts, finished features, and major technical hurdles.
2. SQUASH: Collapse tasks that were started in the morning and finished in the afternoon into single outcomes.
3. PRUNE: Identify facts in the Core Memory that are now obsolete based on today's work.

CURRENT CORE MEMORY:
{core_memory}

HOURLY LOGS FOR {date_str}:
{log_content}

Output format:
## Daily Distillation: {date_str}
### 🚀 Key Technical Achievements
(Surgical bullets)

### 🏗️ Architectural Shifts
(Changes to logic or structure)

### 🧹 Delta Pruning Proposal
- **Stale (Remove):** (Facts from core memory that are now obsolete)
- **New (Add):** (Facts from today that should be permanently remembered)
"""

    system_instr = "You are a high-level technical summarizer. Consolidate granular hourly history and propose delta memory pruning."

    try:
        # Route to Chancellor tier reasoning
        report = generate_reasoning(prompt, system_instruction=system_instr, brain_type="chancellor")
        
        # Save the Daily Report
        os.makedirs(DAILY_DIR, exist_ok=True)
        report_path = os.path.join(DAILY_DIR, f"{date_str}.md")
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"  [SUCCESS] Daily Distillation generated: {os.path.basename(report_path)}")
        
        # 4. AUTOMATIC GARBAGE COLLECTION
        # Delete the hourly logs now that they are safely rolled up
        print("  [GC] Cleaning up 24-hour cycle...")
        for p in hourly_logs:
            try:
                os.remove(p)
            except Exception as move_e:
                print(f"  [WARNING] Could not delete hourly log {p}: {move_e}")
                
        print("  [SUCCESS] Hourly logs purged.")
            
    except Exception as e:
        print(f"  [ERROR] Tier 2 reasoning failed: {e}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    daily_summarize(target)
