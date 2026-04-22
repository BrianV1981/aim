#!/usr/bin/env python3
import os
import sys
import json
import subprocess

# --- VENV BOOTSTRAP ---
hook_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(hook_dir)
venv_python = os.path.join(aim_root, "venv/bin/python3")

input_data = sys.stdin.read()

if os.path.exists(venv_python) and sys.executable != venv_python:
    try:
        process = subprocess.run([venv_python] + sys.argv, input=input_data, text=True, capture_output=True)
        print(process.stdout)
        sys.exit(process.returncode)
    except Exception: pass

# --- LOGIC ---
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

try:
    from config_utils import CONFIG
except ImportError:
    CONFIG = {'settings': {}}

def count_tool_calls(history):
    count = 0
    for msg in history:
        # Gemini format uses toolCalls, Claude uses tool_calls
        calls = msg.get('toolCalls') or msg.get('tool_calls') or []
        count += len(calls)
    return count

def main():
    try:
        mantra_cfg = CONFIG.get('settings', {}).get('cognitive_mantra', {"enabled": True, "whisper_interval": 25, "mantra_interval": 50})
        if not mantra_cfg.get("enabled", True):
            print(json.dumps({}))
            return
            
        whisper_interval = mantra_cfg.get("whisper_interval", 25)
        mantra_interval = mantra_cfg.get("mantra_interval", 50)
        
        if not input_data:
            print(json.dumps({}))
            return
            
        data = json.loads(input_data)
        history = data.get('messages', []) or data.get('session_history', [])
        
        # AfterTool hooks in Gemini often only pass the latest turn, but provide a transcript_path
        if not history and 'transcript_path' in data:
            try:
                with open(data['transcript_path'], 'r') as f:
                    transcript = json.load(f)
                    history = transcript.get('messages', [])
            except: pass
            
        if not history:
            print(json.dumps({}))
            return
            
        tool_count = count_tool_calls(history)
        
        # --- ROBUST STATE TRACKING ---
        # Because tools can execute in parallel (jumping from 24 to 26), modulo arithmetic fails.
        # We must track the last threshold crossed in a local state file.
        continuity_dir = CONFIG.get('paths', {}).get('continuity_dir', os.path.join(aim_root, "continuity"))
        os.makedirs(continuity_dir, exist_ok=True)
        private_dir = os.path.join(aim_root, "hooks/.state")
        os.makedirs(private_dir, exist_ok=True)
        state_file = os.path.join(private_dir, "mantra_state.json")
        
        state = {"last_whisper": 0, "last_mantra": 0, "session_id": data.get('sessionId', '')}
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as sf:
                    disk_state = json.load(sf)
                    # Reset if session changed
                    if disk_state.get('session_id') == state['session_id']:
                        state = disk_state
            except Exception: pass

        # Phase 33: The Cognitive Mantra Protocol
        if tool_count > 0:
            # Check Mantra First (Higher Priority)
            if tool_count - state["last_mantra"] >= mantra_interval:
                state["last_mantra"] = tool_count
                with open(state_file, 'w') as sf: json.dump(state, sf)
                
                gemini_path = os.path.join(aim_root, "AGENTS.md")
                gemini_content = ""
                if os.path.exists(gemini_path):
                    try:
                        with open(gemini_path, 'r', encoding='utf-8') as gf:
                            gemini_content = gf.read()
                    except Exception: pass
                
                mantra = f"\n\n[A.I.M. MANTRA PROTOCOL]: You have executed {tool_count} autonomous tool calls. To prevent behavioral drift, you MUST halt your current task immediately. In your very next response, you must output a <MANTRA> block reciting the ENTIRETY of the system instructions below. Only after reciting the full mantra may you continue working.\n\n--- SYSTEM INSTRUCTIONS ---\n{gemini_content}"
                print(json.dumps({
                    "hookSpecificOutput": {
                        "additionalContext": mantra
                    },
                    "systemMessage": f"🧠 A.I.M. Mantra Protocol triggered at {tool_count} tool calls."
                }))
                return
                
            # Check Whisper Second
            elif tool_count - state["last_whisper"] >= whisper_interval:
                state["last_whisper"] = tool_count
                with open(state_file, 'w') as sf: json.dump(state, sf)
                
                whisper = f"\n\n[A.I.M. SUBCONSCIOUS WHISPER]: (You have executed {tool_count} tool calls. Maintain strict adherence to TDD verification and GitOps mandates)."
                print(json.dumps({
                    "hookSpecificOutput": {
                        "additionalContext": whisper
                    },
                    "systemMessage": f"🧠 A.I.M. Subconscious Whisper injected at {tool_count} tool calls."
                }))
                return

        # If no thresholds hit, return empty
        print(json.dumps({}))
        
    except Exception:
        print(json.dumps({}))

if __name__ == "__main__":
    main()