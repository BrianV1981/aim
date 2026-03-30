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

def generate_reincarnation_gameplan(user_directive=""):
    """
    Analyzes the full session essence and generates a rigid REINCARNATION_GAMEPLAN.md.
    Uses the user's input as the 'Commander's Intent'.
    """
    print("      Analyzing session heartbeat for Gameplan...")
    clean_path = os.path.join(CONTINUITY_DIR, "LAST_SESSION_CLEAN.md")
    
    session_essence = ""
    if os.path.exists(clean_path):
        with open(clean_path, "r", encoding="utf-8") as f:
            # Read up to 50k characters of the history to capture the arc without blowing context
            session_essence = f.read()[-50000:]
            
    gameplan_prompt = f"""
You are the A.I.M. Reincarnation Strategist. An agent is about to die and pass the baton to a fresh vessel.
Your goal is to capture the "Essence" and "Heartbeat" of this session and distill it into a rigid, 3-step Executive Directive.

COMMANDER'S INTENT (User Injection):
"{user_directive}"

SESSION HISTORY ESSENCE (Tail):
{session_essence}

STRICT CONSTRAINTS:
1. DO NOT just summarize. Write a battle plan.
2. Identify exactly what was thrashed upon and what the final "Eureka" direction was.
3. Provide 3-5 rigid, numbered steps for the next agent to follow immediately upon waking.
4. Bypassing noise: Ignore direction changes that were closed or abandoned. Focus only on the active technical momentum.
"""

    system_instr = "You are a high-level technical strategist. Be rigid, prescriptive, and focus on the project's heartbeat."

    try:
        gameplan_content = generate_reasoning(gameplan_prompt, system_instruction=system_instr)
        
        output_path = os.path.join(CONTINUITY_DIR, "REINCARNATION_GAMEPLAN.md")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        full_gameplan = f"# REINCARNATION GAMEPLAN\n\n"
        full_gameplan += "## ⚠️ URGENT DIRECTIVE FOR THE INCOMING AGENT\n"
        full_gameplan += "You are waking up in the middle of a high-momentum development cycle. "
        full_gameplan += "The previous agent has distilled the session heartbeat into these rigid directives:\n\n"
        full_gameplan += gameplan_content
        full_gameplan += f"\n\n---\n**Commander's Intent:** {user_directive}\n"
        full_gameplan += f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        atomic_write(output_path, full_gameplan)
            
        print(f"      [Success] Gameplan written to: {os.path.basename(output_path)}")
        return True
    except Exception as e:
        print(f"      Gameplan Generation Error: {e}")
        return False

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
        clean_path = os.path.join(CONTINUITY_DIR, "LAST_SESSION_CLEAN.md")
        
        # Convert JSON skeleton into pure Markdown dialogue
        session_id = os.path.basename(latest_transcript).replace('.json', '')
        md_content = skeleton_to_markdown(skeleton, session_id)
        
        # Load configurable line limit, default to 0 (Full History)
        tail_lines = CONFIG.get('settings', {}).get('handoff_context_lines', 0)
        
        if tail_lines > 0:
            md_lines = md_content.splitlines()
            if len(md_lines) > tail_lines:
                truncated_lines = md_lines[-tail_lines:]
            else:
                truncated_lines = md_lines
                
            clean_content = "# A.I.M. Clean Session Transcript (Rolling Delta)\n"
            clean_content += f"*This is a noise-reduced flight recorder showing only the last {tail_lines} lines. NOT automatically injected into LLM context.*\n\n"
            clean_content += '\n'.join(truncated_lines) + '\n'
            atomic_write(clean_path, clean_content)
        else:
            clean_content = "# A.I.M. Clean Session Transcript (Full History)\n"
            clean_content += f"*This is a noise-reduced flight recorder showing the entire session. NOT automatically injected into LLM context.*\n\n"
            clean_content += md_content + '\n'
            atomic_write(clean_path, clean_content)
                
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
        atomic_write(pulse_path, pulse_output)
            
        # Phase 39: Context Preemption Fix (The Double-Bind Handoff)
        handoff_path = os.path.join(AIM_ROOT, "HANDOFF.md")
        handoff_content = f"""# A.I.M. Continuity Handoff

## ⚠️ CRITICAL INSTRUCTION FOR INCOMING AGENT ⚠️
You are waking up in the middle of a continuous operational loop.
To prevent hallucination, you must establish **Epistemic Certainty** regarding the previous agent's actions before you write any code.

### The Continuity Protocol (The Reincarnation Gameplan)
1. Read `continuity/REINCARNATION_GAMEPLAN.md` (The rigid executive directive passed by the previous agent).
2. Read `continuity/CURRENT_PULSE.md` (The explicit handoff state and project edge).
3. Read `ISSUE_TRACKER.md` (The local ledger of all open and closed tickets).
4. (Optional) Read `continuity/LAST_SESSION_CLEAN.md` ONLY IF the Gameplan explicitly requires historical context extraction.
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
    # If called with an argument, generate the gameplan too
    if len(sys.argv) > 1:
        generate_reincarnation_gameplan(sys.argv[1])
