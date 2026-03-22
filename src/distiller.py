#!/usr/bin/env python3
import os
import json
import sys
import glob
from datetime import datetime
from reasoning_utils import generate_reasoning, AIM_ROOT
try:
    from extract_signal import extract_signal
except ImportError:
    sys.path.append(os.path.join(AIM_ROOT, "scripts"))
    from extract_signal import extract_signal

# --- CONFIGURATION (Load from core/CONFIG.json) ---
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

CONTINUITY_DIR = CONFIG['paths']['continuity_dir']
ARCHIVE_RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")

def distill():
    """
    Fast, Short-Term Continuity Engine.
    Reads the latest session transcript, extracts the signal, and overwrites CURRENT_PULSE.md.
    """
    # 1. Find the latest transcript
    raw_files = glob.glob(os.path.join(ARCHIVE_RAW_DIR, "*.json"))
    if not raw_files:
        print("Distiller: No raw transcripts found.")
        return
        
    latest_transcript = max(raw_files, key=os.path.getmtime)
    
    # 2. Extract Signal (Fast text processing)
    try:
        skeleton = extract_signal(latest_transcript)
        # We only need the recent context for a handoff pulse
        recent_skeleton = skeleton[-30:] if isinstance(skeleton, list) else skeleton
        context_str = json.dumps(recent_skeleton, indent=2)
    except Exception as e:
        print(f"Distiller Error extracting signal: {e}")
        return

    # --- THE CONTINUITY PROMPT (Phase 20) ---
    prompt = f"""
You are the A.I.M. Continuity Engine. Your goal is to synthesize the "Project Edge"—the absolute current frontier of development.

CRITICAL CONSTRAINTS (The Lean Mandate):
1. NO CORE MEMORY: Do not summarize stable facts. Focus ONLY on the immediate technical delta, the "Edge," and the "Intent."
2. PROJECT EDGE: Identify what was just finished, what is currently broken or blocked, and what the very next step is.
3. HANDOFF ALIGNMENT: Prioritize the user's latest /handoff intent or closing instructions.
4. LOSSLESS COMPRESSION: Remove all conversational fluff. Keep only technical outcomes.
5. ONE PARAGRAPH: Your output must be a single, dense paragraph.

RECENT SESSION SIGNAL SKELETON:
{context_str[-12000:]}
"""

    system_instr = "You are a high-fidelity continuity engine focused on technical momentum. Be surgical and concise."

    try:
        pulse_content = generate_reasoning(prompt, system_instruction=system_instr)
        
        # Overwrite CURRENT_PULSE.md
        os.makedirs(CONTINUITY_DIR, exist_ok=True)
        pulse_path = os.path.join(CONTINUITY_DIR, "CURRENT_PULSE.md")
        
        pulse_output = f"# A.I.M. Context Pulse: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{pulse_content}"
        pulse_output += "\n\n---\n\"I believe I've made my point.\" — **A.I.M. (Auto-Pulse)**"
        
        with open(pulse_path, 'w') as f:
            f.write(pulse_output)
        print(f"      Pulse updated: CURRENT_PULSE.md")

    except Exception as e:
        print(f"      Distiller Error: {e}")

if __name__ == "__main__":
    distill()
