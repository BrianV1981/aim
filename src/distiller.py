#!/usr/bin/env python3
import os
import json
import sys
import glob
import subprocess
from datetime import datetime
from reasoning_utils import generate_reasoning, AIM_ROOT

# --- CONFIGURATION (Load from core/CONFIG.json) ---
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

DAILY_LOG_DIR = CONFIG['paths']['memory_dir']
CONTINUITY_DIR = CONFIG['paths']['continuity_dir']
MEMORY_MD_PATH = os.path.join(CONFIG['paths']['core_dir'], "MEMORY.md")

def distill(target_date=None):
    """
    Distills session logs into memory proposals and context pulses.
    target_date: YYYY-MM-DD string. If None, uses today.
    """
    date_to_process = target_date or datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(DAILY_LOG_DIR, f"{date_to_process}.md")
    
    if not os.path.exists(log_path):
        # sys.stderr.write(f"Distiller: Log not found for {date_to_process}\n")
        return

    # 1. Read Daily Log
    with open(log_path, 'r') as f:
        log_content = f.read()

    # 2. Skip Reading Core Memory (Per Objective 2 Mandate)
    # We no longer summarize the durable tier here to avoid token bloat.

    # 3. Read Latest Pulse (if exists)
    pulse_pattern = os.path.join(CONTINUITY_DIR, "202[0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9][0-9][0-9].md")
    pulses = glob.glob(pulse_pattern)
    latest_pulse = ""
    if pulses:
        pulses.sort(reverse=True)
        with open(pulses[0], 'r') as f:
            latest_pulse = f.read()

    # --- THE CONTINUITY PROMPT (Objective 2) ---
    prompt = f"""
You are the A.I.M. Continuity Engine. Your goal is to synthesize the "Project Edge"—the absolute current frontier of development.

CRITICAL CONSTRAINTS (The Lean Mandate):
1. NO CORE MEMORY: Do not summarize stable facts. Focus ONLY on the immediate technical delta, the "Edge," and the "Intent."
2. PROJECT EDGE: Identify what was just finished, what is currently broken or blocked, and what the very next step is.
3. HANDOFF ALIGNMENT: Prioritize the user's latest /handoff intent or closing instructions.
4. LOSSLESS COMPRESSION: Remove all conversational fluff. Keep only technical outcomes.

SCRIVENER NOTES & DAILY LOGS:
{log_content[-10000:]}

Output format:
### 1. Project Edge
(Lean bullets on the current technical frontier, including specific file paths and symbols)

### 2. Handoff Intent
(Synthesis of the next objective and the user's explicit /handoff goal)

### 3. Technical Debt & Blocks
(Immediate items to fix or known unknowns)
"""

    system_instr = "You are a high-fidelity continuity engine focused on technical momentum. Be surgical."

    try:
        distillation = generate_reasoning(prompt, system_instruction=system_instr)
        
        # Save Versioned Continuity Report
        timestamp_full = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        os.makedirs(CONTINUITY_DIR, exist_ok=True)
        report_path = os.path.join(CONTINUITY_DIR, f"REPORT_{timestamp_full}.md")
        
        with open(report_path, 'w') as f:
            f.write(distillation)
        print(f"      Continuity Report generated: {os.path.basename(report_path)}")

        # --- GENERATE NEW CONTEXT PULSE ---
        pulse_prompt = f"Based on the Continuity Report, write a 1-paragraph 'Context Pulse' for immediate injection into the next session start. Focus ONLY on momentum.\n\nREPORT:\n{distillation}"
        pulse_content = generate_reasoning(pulse_prompt, system_instruction="Summarize technical momentum into a Context Pulse.")
        
        # Use the date from the LOG for the Pulse filename if provided, else current time
        pulse_ts = f"{date_to_process}_{datetime.now().strftime('%H%M')}"
        pulse_path = os.path.join(CONTINUITY_DIR, f"{pulse_ts}.md")
        
        pulse_output = f"# A.I.M. Context Pulse: {pulse_ts}\n\n{pulse_content}"
        pulse_output += "\n\n---\n\"I believe I've made my point.\" — **A.I.M. (Auto-Pulse)**"
        
        with open(pulse_path, 'w') as f:
            f.write(pulse_output)
        print(f"      Pulse saved: {os.path.basename(pulse_path)}")

    except Exception as e:
        print(f"      Distiller Error: {e}")

if __name__ == "__main__":
    # If a date is provided as sys.argv[1], use it.
    target = sys.argv[1] if len(sys.argv) > 1 else None
    distill(target)
