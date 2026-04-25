#!/usr/bin/env python3
import os
import json
from extract_signal import skeleton_to_markdown
import sys
import glob
from datetime import datetime
from reasoning_utils import generate_reasoning, AIM_ROOT
try:
    from extract_signal import extract_signal, skeleton_to_markdown
except ImportError:
    sys.path.append(os.path.join(AIM_ROOT, "aim_core"))
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
    native_cli_dir = os.path.expanduser(f"~/.gemini/tmp/{project_name}/chats/*.jsonl")
    raw_files = glob.glob(native_cli_dir)
    
    if not raw_files:
        raw_files = glob.glob(os.path.join(ARCHIVE_RAW_DIR, "*.jsonl"))
        
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
        # Verify valid JSONL
        with open(latest_transcript, 'r') as f:
            for line in f:
                if line.strip(): json.loads(line)
            
        skeleton = extract_signal(latest_transcript)
        
        # Write clean session artifact (Rolling Delta or Full History)
        os.makedirs(CONTINUITY_DIR, exist_ok=True)
        clean_path = os.path.join(CONTINUITY_DIR, "LAST_SESSION_FLIGHT_RECORDER.md")
        
        # Convert JSON skeleton into pure Markdown dialogue
        session_id = os.path.basename(latest_transcript).replace('.jsonl', '')
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
                # Use Popen instead of run so the background compiler does not block the reincarnation handoff
                log_path = os.path.join(AIM_ROOT, "memory-wiki", "daemon.log")
                daemon_log = open(log_path, "a")
                subprocess.Popen([sys.executable, os.path.join(AIM_ROOT, "hooks", "session_summarizer.py"), archive_path], 
                               stdout=daemon_log, stderr=daemon_log, start_new_session=True)
                print(f"      [Monolithic] Triggered Subconscious Wiki Daemon & Vector Ingestion (Logging to memory-wiki/daemon.log).")
            except Exception as e:
                print(f"      [Monolithic] Subconscious daemon error: {e}")
        
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
        pulse_path = os.path.join(CONTINUITY_DIR, "CURRENT_PULSE.md")
        with open(pulse_path, "w") as f:
            f.write(pulse_content)
            
        flight_path = os.path.join(CONTINUITY_DIR, "LAST_SESSION_FLIGHT_RECORDER.md")
        with open(flight_path, "w") as f:
            f.write(f"## showing the entire session\n\n" + skeleton_to_markdown(skeleton, os.path.basename(latest_transcript)))

        print("\n\033[92m--- A.I.M. HANDOFF READY ---\033[0m")


    except Exception as e:
        print(f"      Handoff Generator Error: {e}")

if __name__ == "__main__":
    generate_handoff_pulse()
