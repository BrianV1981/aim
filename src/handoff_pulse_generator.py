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

def atomic_write(file_path, content):
    """
    Safely writes content to a file by writing to a temporary file,
    flushing, and then performing an atomic replacement.
    """
    temp_path = f"{file_path}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        
        # Perform the atomic swap
        os.replace(temp_path, file_path)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

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
        
        # Write clean session artifact (Rolling Delta or Full History)
        os.makedirs(CONTINUITY_DIR, exist_ok=True)
        clean_path = os.path.join(CONTINUITY_DIR, "LAST_SESSION_FLIGHT_RECORDER.md")
        
        # Convert JSON skeleton into pure Markdown dialogue
        session_id = os.path.basename(latest_transcript).replace('.json', '')
        md_content = skeleton_to_markdown(skeleton, session_id)
        
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        timestamp_str = now.strftime('%H:%M:%S')
        file_ts = now.strftime('%Y-%m-%d_%H%M')

        # Pipeline 3: Historical Archive (Permanent Storage)
        archive_dir = os.path.join(AIM_ROOT, "archive/history")
        os.makedirs(archive_dir, exist_ok=True)
        archive_path = os.path.join(archive_dir, f"{file_ts}_{session_id}.md")
        atomic_write(archive_path, md_content)
        print(f"      Historical Archive updated: {archive_path}")
        
        # Load configurable line limit, default to 0 (Full History)
        tail_lines = CONFIG.get('settings', {}).get('handoff_context_lines', 0)
        
        if tail_lines > 0:
            md_lines = md_content.splitlines()
            if len(md_lines) > tail_lines:
                truncated_lines = md_lines[-tail_lines:]
            else:
                truncated_lines = md_lines
                
            clean_content = "# A.I.M. Session Flight Recorder (Rolling Delta)\n"
            clean_content += f"*This is a noise-reduced flight recorder showing only the last {tail_lines} lines. NOT automatically injected into LLM context.*\n\n"
            clean_content += '\n'.join(truncated_lines) + '\n'
            atomic_write(clean_path, clean_content)
        else:
            clean_content = "# A.I.M. Session Flight Recorder (Full History)\n"
            clean_content += f"*This is a noise-reduced flight recorder showing the entire session. NOT automatically injected into LLM context.*\n\n"
            clean_content += md_content + '\n'
            atomic_write(clean_path, clean_content)
            
        # PHASE 33: Decoupled Brain (Frontline Mode)
        # If this machine is just a frontline agent, drop the full transcript into the Obsidian Vault's Inbox
        cognitive_mode = CONFIG.get('settings', {}).get('cognitive_mode', 'monolithic')
        vault_path = CONFIG.get('settings', {}).get('obsidian_vault_path', '')
        if cognitive_mode == 'frontline' and vault_path:
            inbox_dir = os.path.join(vault_path, "AIM_Inbox")
            os.makedirs(inbox_dir, exist_ok=True)
            # The new mandate requires we route the Markdown file directly to avoid redundant parsing
            inbox_file = os.path.join(inbox_dir, f"{session_id}.md")
            atomic_write(inbox_file, md_content)
            print(f"      [Frontline] Dropped Markdown session {session_id} into Obsidian AIM_Inbox.")
        elif cognitive_mode == 'monolithic':
            import subprocess
            try:
                subprocess.run([sys.executable, os.path.join(AIM_ROOT, "hooks", "session_summarizer.py"), archive_path], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"      [Monolithic] Triggered Single-Shot Memory Compiler.")
            except Exception as e:
                print(f"      [Monolithic] Compiler error: {e}")
        
        # --- PROJECT EDGE SYNTHESIS (High Fidelity) ---
        # Instead of an LLM generation, we mechanically extract the last 5 conversational turns.
        pulse_turns = []
        if isinstance(skeleton, list):
            for turn in skeleton:
                role = turn.get('role', 'unknown').upper()
                text = turn.get('text', '').strip()
                # Only grab turns that actually have conversational text (ignore tool-only intermediate steps)
                if role in ['USER', 'GEMINI', 'MODEL', 'ASSISTANT'] and text:
                    pulse_turns.append(turn)
        
        last_5_turns = pulse_turns[-5:]
        pulse_content = "## Last 5 Conversational Turns\n\n"
        for turn in last_5_turns:
            role_label = "USER" if turn.get('role', '').upper() == 'USER' else "A.I.M."
            ts = turn.get('timestamp', '')
            text = turn.get('text', '').strip()
            pulse_content += f"### {role_label} ({ts})\n{text}\n\n---\n\n"
        
        if not last_5_turns:
            pulse_content += "*(No conversational turns found)*\n\n"

    except Exception as e:
        print(f"Handoff Generator: Signal extraction failure on {latest_transcript}: {e}")
        return

    try:
        

        
        pulse_output = f"---\ndate: {date_str}\ntime: \"{timestamp_str}\"\ntype: handoff\n---\n\n"
        pulse_output += f"# A.I.M. Context Pulse: {date_str} {timestamp_str}\n\n{pulse_content}"
        pulse_output += "\n\n---\n\"I believe I've made my point.\" — **A.I.M. (Auto-Pulse)**"
        
        pulse_path = os.path.join(CONTINUITY_DIR, "CURRENT_PULSE.md")
        atomic_write(pulse_path, pulse_output)
            
        # Phase 39: Context Preemption Fix (The Double-Bind Handoff)
        handoff_path = os.path.join(AIM_ROOT, "HANDOFF.md")
        handoff_content = f"""# A.I.M. Continuity Handoff

## ⚠️ CRITICAL INSTRUCTION FOR INCOMING AGENT ⚠️
You are waking up in the middle of a continuous operational loop.
To prevent hallucination, you must establish **Epistemic Certainty** regarding the previous agent's actions before you write any code.

### The Continuity Protocol (The Reincarnation Gameplan)
*(NOTE: You MUST use `run_shell_command` with `cat` to read the continuity files, as they are gitignored and `read_file` will fail).*

1. Read `continuity/REINCARNATION_GAMEPLAN.md` (The rigid executive directive passed by the previous agent).
2. Read `continuity/CURRENT_PULSE.md` (The explicit handoff state and project edge).
3. Read `continuity/ISSUE_TRACKER.md` (The local ledger of all open and closed tickets).
4. (Optional) Read `continuity/LAST_SESSION_FLIGHT_RECORDER.md` ONLY IF the Gameplan explicitly requires historical context extraction.
5. Do not blindly assume success. Verify the state via file reads or tests.

---
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        atomic_write(handoff_path, handoff_content)
            
        print("      Pulse updated: CURRENT_PULSE.md")
        print("\n\033[92m--- A.I.M. HANDOFF READY ---\033[0m")
        print("To prevent 'Context Preemption' on the next boot, copy and paste this exact prompt:")
        print("\033[93mWake up. 1. Read GEMINI.md and acknowledge your core constraints. 2. Read HANDOFF.md to receive your immediate context and directives.\033[0m\n")

    except Exception as e:
        print(f"      Handoff Generator Error: {e}")

if __name__ == "__main__":
    generate_handoff_pulse()
