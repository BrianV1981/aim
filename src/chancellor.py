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

DAILY_LOG_DIR = CONFIG['paths'].get('memory_dir')
CONTINUITY_DIR = CONFIG['paths'].get('continuity_dir')

def chancellor_audit(target_date=None):
    """
    Tier 2: Consolidates Session Pulses into Daily Milestone Reports.
    """
    date_str = target_date or datetime.now().strftime("%Y-%m-%d")
    print(f"--- A.I.M. CHANCELLOR AUDIT: {date_str} ---")
    
    # 1. Gather all Session Pulses for the target day
    pattern = os.path.join(CONTINUITY_DIR, f"{date_str}_*.md")
    pulses = glob.glob(pattern)
    pulses.sort()
    
    if not pulses:
        print(f"  [SKIP] No Librarian pulses found for {date_str}.")
        return

    print(f"  -> Found {len(pulses)} session pulses. Synthesizing...")
    
    pulse_content = ""
    for p in pulses:
        with open(p, 'r') as f:
            pulse_content += f"\n--- SESSION PULSE ---\n{f.read()}\n"

    # 2. Scholastic Reasoning (Chancellor Tier)
    prompt = f"""
You are the A.I.M. Chancellor (Tier 2 Specialist). Your goal is to synthesize multiple session pulses into a single, surgical 'Daily Milestone Report'.

MANDATE:
1. FOCUS: Only capture logic shifts, finished features, and major technical hurdles.
2. DISCARD: Remove granular task-level chatter. 
3. VERIFIABLE: Ensure all file paths and symbols are preserved.
4. TONE: Dry, technical, and high-fidelity.

SESSION PULSES FOR {date_str}:
{pulse_content}

Output format:
## Daily Milestone Report: {date_str}
### 🚀 Key Technical Achievements
(Surgical bullets)

### 🏗️ Architectural Shifts
(Changes to logic or structure)

### 📍 Project Edge
(Exactly where the project stands at the end of the day)
"""

    system_instr = "You are a high-level technical chancellor. Consolidate granular history into strategic milestones."

    try:
        # Route to Chancellor tier reasoning
        report = generate_reasoning(prompt, system_instruction=system_instr, brain_type="chancellor")
        
        # Save the Daily Report
        report_path = os.path.join(DAILY_LOG_DIR, f"DAILY_REPORT_{date_str}.md")
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"  [SUCCESS] Daily Report generated: {os.path.basename(report_path)}")
        
        # 3. ARCHIVE THE USED PULSES
        # (We move them to memory/archive to keep the continuity folder clean)
        archive_dir = os.path.join(DAILY_LOG_DIR, "archive/pulses")
        os.makedirs(archive_dir, exist_ok=True)
        for p in pulses:
            shutil_move = shutil_move_logic(p, os.path.join(archive_dir, os.path.basename(p)))
            
    except Exception as e:
        print(f"  [ERROR] Chancellor reasoning failed: {e}")

def shutil_move_logic(src, dest):
    import shutil
    try:
        shutil.move(src, dest)
        return True
    except: return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    chancellor_audit(target)
