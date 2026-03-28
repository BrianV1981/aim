#!/usr/bin/env python3
import os
import json
import sys
import glob
from datetime import datetime
from reasoning_utils import generate_reasoning, AIM_ROOT
try:
    from extract_signal import extract_signal, skeleton_to_markdown
except ImportError:
    sys.path.append(os.path.join(AIM_ROOT, "scripts"))
    from extract_signal import extract_signal, skeleton_to_markdown

# --- CONFIGURATION (Load from core/CONFIG.json) ---
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

CONTINUITY_DIR = CONFIG['paths']['continuity_dir']
ARCHIVE_RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")

def generate_handoff_pulse():
    """
    Fast, Short-Term Continuity Engine.
    Reads the latest significant session transcript directly from the native CLI temporary folder
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
        
    raw_files.sort(key=os.path.getmtime, reverse=True)
    latest_transcript = raw_files[0]
    
    # Anti-Cannibalization Check: If the newest file is tiny (e.g. a brand new session that just woke up to run this), 
    # skip it and grab the previous one so we don't overwrite a massive history with a 3-turn wake-up log.
    if len(raw_files) > 1:
        try:
            with open(latest_transcript, 'r') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) < 15:
                    print(f"Handoff Generator: {os.path.basename(latest_transcript)} has < 15 turns. Skipping to previous session to prevent context cannibalization.")
                    latest_transcript = raw_files[1]
        except Exception:
            pass
    
    # 2. Extract Signal
    try:
        # Verify valid JSON
        with open(latest_transcript, 'r') as f:
            json.load(f)
            
        skeleton = extract_signal(latest_transcript)
        
        # Write clean session artifact (Rolling Delta to prevent 2000-line truncation bugs)
        os.makedirs(CONTINUITY_DIR, exist_ok=True)
        clean_path = os.path.join(CONTINUITY_DIR, "LAST_SESSION_CLEAN.md")
        
        # Load configurable tail limit, default to 30
        tail_limit = CONFIG.get('settings', {}).get('handoff_context_tail', 30)
        
        # Convert JSON skeleton into pure Markdown dialogue
        session_id = os.path.basename(latest_transcript).replace('.json', '')
        md_content = skeleton_to_markdown(skeleton, session_id)
        md_lines = md_content.splitlines()
        
        # Find all turn headers (using actual markdown outputs)
        turn_indices = [i for i, line in enumerate(md_lines) if line.startswith("## 👤 USER") or line.startswith("## 🤖 A.I.M.")]
        
        # Apply turn-based truncation
        if tail_limit > 0 and len(turn_indices) > tail_limit:
            cutoff_index = turn_indices[-tail_limit]
            truncated_lines = md_lines[cutoff_index:]
        else:
            truncated_lines = md_lines
            
        # Hard limit: ensure we never exceed 1990 lines to prevent context overflow (leaving a small buffer)
        if len(truncated_lines) > 1990:
            truncated_lines = truncated_lines[-1990:]
        
        with open(clean_path, "w", encoding="utf-8") as cf:
            cf.write("# A.I.M. Clean Session Transcript (Rolling Delta)\n")
            cf.write(f"*This is a noise-reduced flight recorder showing only the last {tail_limit} turns (max 1990 lines). NOT injected into LLM context.*\n\n")
            cf.write('\n'.join(truncated_lines) + '\n')
                
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
            
        # Phase 39: Context Preemption Fix (The Double-Bind Handoff)
        handoff_path = os.path.join(AIM_ROOT, "handoff.md")
        handoff_content = f"""# A.I.M. Continuity Handoff

## ⚠️ CRITICAL INSTRUCTION FOR INCOMING AGENT ⚠️
You are waking up in the middle of a continuous operational loop.
To prevent hallucination, you must establish **Epistemic Certainty** regarding the previous agent's actions before you write any code.

### The Continuity Protocol
1. Read `continuity/LAST_SESSION_CLEAN.md` (The bottom 2000 lines of exactly what just happened).
2. Read `continuity/CURRENT_PULSE.md` (The explicit handoff state).
3. Read `ISSUE_TRACKER.md` (The local ledger of all open and closed tickets).
4. Do not blindly assume success. Verify the state via file reads or tests.

---
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        with open(handoff_path, "w", encoding="utf-8") as f:
            f.write(handoff_content)
            
        print("      Pulse updated: CURRENT_PULSE.md")
        print("\n\033[92m--- A.I.M. HANDOFF READY ---\033[0m")
        print("To prevent 'Context Preemption' on the next boot, copy and paste this exact prompt:")
        print("\033[93mWake up. 1. Read GEMINI.md and acknowledge your core constraints. 2. Read handoff.md to receive your immediate context and directives.\033[0m\n")

    except Exception as e:
        print(f"      Handoff Generator Error: {e}")

if __name__ == "__main__":
    generate_handoff_pulse()
