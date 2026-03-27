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
    Reads the latest session transcript directly from the native CLI temporary folder
    (to bypass context compression logic), extracts the signal, and overwrites CURRENT_PULSE.md.
    """
    project_name = os.path.basename(AIM_ROOT)
    native_cli_dir = os.path.expanduser(f"~/.gemini/tmp/{project_name}/chats/*.json")
    raw_files = glob.glob(native_cli_dir)
    
    if not raw_files:
        raw_files = glob.glob(os.path.join(ARCHIVE_RAW_DIR, "*.json"))
        
    if not raw_files:
        print("Handoff Generator: No raw transcripts found.")
        return
        
    latest_transcript = max(raw_files, key=os.path.getmtime)
    
    # 2. Extract Signal
    try:
        # Verify valid JSON
        with open(latest_transcript, 'r') as f:
            json.load(f)
            
        skeleton = extract_signal(latest_transcript)
        
        # Write clean session artifact
        os.makedirs(CONTINUITY_DIR, exist_ok=True)
        clean_path = os.path.join(CONTINUITY_DIR, "LAST_SESSION_CLEAN.md")
        with open(clean_path, "w", encoding="utf-8") as cf:
            cf.write("# A.I.M. Clean Session Transcript\n")
            cf.write("*This is a noise-reduced flight recorder. NOT injected into LLM context.*\n\n")
            if isinstance(skeleton, list):
                for i, turn in enumerate(skeleton):
                    cf.write(f"### Turn {i+1}\n```json\n{json.dumps(turn, indent=2)}\n```\n\n")
            else:
                cf.write(f"```json\n{json.dumps(skeleton, indent=2)}\n```\n")
                
        recent_skeleton = skeleton[-40:] if isinstance(skeleton, list) else skeleton
        context_str = json.dumps(recent_skeleton, indent=2)

    except Exception as e:
        print(f"Handoff Generator: Signal extraction failure on {latest_transcript}: {e}")
        return

    # --- THE CONTINUITY PROMPT ---
    prompt = f"""
You are the A.I.M. Continuity Engine. Your goal is to synthesize the "Project Edge."

CRITICAL CONSTRAINTS:
1. NO CORE MEMORY: Do not summarize stable facts. Focus ONLY on the immediate technical delta.
2. PROJECT EDGE: Identify what was just finished, what is currently broken or blocked, and what the very next step is.
3. OBSIDIAN FORMATTING: Use wikilinks `[[file_path]]`.

RECENT SESSION SIGNAL SKELETON:
{context_str[-12000:]}
"""

    system_instr = "You are a high-fidelity continuity engine. Be surgical, concise, and use Obsidian wikilinks."

    try:
        pulse_content = generate_reasoning(prompt, system_instruction=system_instr)
        
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        timestamp_str = now.strftime('%H:%M:%S')
        file_ts = now.strftime('%Y-%m-%d_%H%M')
        
        pulse_output = f"---\ndate: {date_str}\ntime: \"{timestamp_str}\"\ntype: handoff\n---\n\n"
        pulse_output += f"# A.I.M. Context Pulse: {date_str} {timestamp_str}\n\n{pulse_content}"
        pulse_output += "\n\n---\n\"I believe I've made my point.\" — **A.I.M. (Auto-Pulse)**"
        
        pulse_path = os.path.join(CONTINUITY_DIR, "CURRENT_PULSE.md")
        with open(pulse_path, 'w') as f:
            f.write(pulse_output)
            
        os.makedirs(PULSES_DIR, exist_ok=True)
        with open(os.path.join(PULSES_DIR, f"{file_ts}.md"), 'w') as f:
            f.write(pulse_output)
            
        print(f"      Pulse updated: CURRENT_PULSE.md and {file_ts}.md")

    except Exception as e:
        print(f"      Handoff Generator Error: {e}")

if __name__ == "__main__":
    generate_handoff_pulse()
