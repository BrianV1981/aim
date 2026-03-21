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

DAILY_LOG_DIR = CONFIG['paths'].get('memory_dir')

def fellow_review():
    """Tier 3: Consolidates Daily Reports into Weekly Strategic Arcs."""
    print("--- A.I.M. FELLOW WEEKLY REVIEW ---")
    
    # 1. Gather Daily Reports from the last 7 days
    today = datetime.now()
    reports = []
    for i in range(7):
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        path = os.path.join(DAILY_LOG_DIR, f"DAILY_REPORT_{date_str}.md")
        if os.path.exists(path):
            with open(path, 'r') as f:
                reports.append(f"--- REPORT {date_str} ---\n{f.read()}\n")

    if not reports:
        print("  [SKIP] No daily reports found for this week.")
        return

    print(f"  -> Synthesizing {len(reports)} daily reports...")
    
    # 2. Scholastic Reasoning (Fellow Tier)
    prompt = f"""
You are the A.I.M. Fellow (Tier 3 Specialist). Your goal is to synthesize a week of engineering into a 'Weekly Strategic Arc'.

MANDATE:
1. FOCUS: Identify major architectural shifts, roadmap progress, and technical debt accumulated.
2. VERIFY: Query the Engram DB for any claims that seem inconsistent.
3. STRATEGY: Suggest the primary technical focus for the upcoming week.

WEEKLY DATA:
{"".join(reports)}

Output format:
## Weekly Strategic Arc: {today.strftime('%Y-W%W')}
### 🏆 Major Milestones
### 🏗️ Architectural Evolution
### 📍 The Next Frontier (Upcoming Week)
"""

    try:
        report = generate_reasoning(prompt, system_instruction="You are a high-level technical fellow.", brain_type="fellow")
        report_path = os.path.join(DAILY_LOG_DIR, f"WEEKLY_ARC_{today.strftime('%Y_%W')}.md")
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"  [SUCCESS] Weekly Arc generated: {os.path.basename(report_path)}")
    except Exception as e:
        print(f"  [ERROR] Fellow reasoning failed: {e}")

if __name__ == "__main__":
    fellow_review()
