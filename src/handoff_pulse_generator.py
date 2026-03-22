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
PULSES_DIR = os.path.join(CONFIG['paths'].get('memory_dir'), "pulses")

def generate_handoff_pulse():
    """
    Fast, Short-Term Continuity Engine (Dual-Target).
    Reads the latest session transcript, extracts the signal, and overwrites CURRENT_PULSE.md.
    Also creates a permanent, Obsidian-friendly copy in memory/pulses/.
    """
    # 1. Find the latest transcript
    raw_files = glob.glob(os.path.join(ARCHIVE_RAW_DIR, "*.json"))
    if not raw_files:
        print("Handoff Generator: No raw transcripts found.")
        return
        
    latest_transcript = max(raw_files, key=os.path.getmtime)
    
    # 2. Extract Signal (Fast text processing)
    try:
        skeleton = extract_signal(latest_transcript)
        # We only need the recent context for a handoff pulse
        recent_skeleton = skeleton[-30:] if isinstance(skeleton, list) else skeleton
        context_str = json.dumps(recent_skeleton, indent=2)
    except Exception as e:
        print(f"Handoff Generator Error extracting signal: {e}")
        return

    # --- THE CONTINUITY PROMPT (Phase 21 - Obsidian Native) ---
    prompt = f"""
You are the A.I.M. Continuity Engine. Your goal is to synthesize the "Project Edge"—the absolute current frontier of development.

CRITICAL CONSTRAINTS:
1. NO CORE MEMORY: Do not summarize stable facts. Focus ONLY on the immediate technical delta, the "Edge," and the "Intent."
2. PROJECT EDGE: Identify what was just finished, what is currently broken or blocked, and what the very next step is.
3. HANDOFF ALIGNMENT: Prioritize the user's latest /handoff intent or closing instructions.
4. OBSIDIAN FORMATTING: You MUST format the output using Obsidian-native markdown:
    - Use explicit wikilinks for files (e.g., `[[src/main.py]]`).
    - Include 2-3 relevant tags at the bottom (e.g., `#handoff`, `#bugfix`, `#phase21`).

RECENT SESSION SIGNAL SKELETON:
{context_str[-12000:]}
"""

    system_instr = "You are a high-fidelity continuity engine. Be surgical, concise, and use Obsidian wikilinks for all file paths."

    try:
        pulse_content = generate_reasoning(prompt, system_instruction=system_instr)
        
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        timestamp_str = now.strftime('%H:%M:%S')
        file_ts = now.strftime('%Y-%m-%d_%H%M')
        
        # Construct the Dual-Target Markdown with YAML Frontmatter
        pulse_output = f"---\ndate: {date_str}\ntime: \"{timestamp_str}\"\ntype: handoff\n---\n\n"
        pulse_output += f"# A.I.M. Context Pulse: {date_str} {timestamp_str}\n\n{pulse_content}"
        pulse_output += "\n\n---\n\"I believe I've made my point.\" — **A.I.M. (Auto-Pulse)**"
        
        # Target A: The Active AI Context
        os.makedirs(CONTINUITY_DIR, exist_ok=True)
        pulse_path = os.path.join(CONTINUITY_DIR, "CURRENT_PULSE.md")
        with open(pulse_path, 'w') as f:
            f.write(pulse_output)
            
        # Target B: The Obsidian Vault
        os.makedirs(PULSES_DIR, exist_ok=True)
        obsidian_path = os.path.join(PULSES_DIR, f"{file_ts}.md")
        with open(obsidian_path, 'w') as f:
            f.write(pulse_output)
            
        print(f"      Pulse updated: CURRENT_PULSE.md and {os.path.basename(obsidian_path)}")

    except Exception as e:
        print(f"      Handoff Generator Error: {e}")

if __name__ == "__main__":
    generate_handoff_pulse()
