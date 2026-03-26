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
        
        # Phase 33: The Cognitive Mantra Protocol
        if tool_count > 0:
            if tool_count % mantra_interval == 0:
                mantra = f"\n\n[A.I.M. MANTRA PROTOCOL]: You have executed {mantra_interval} autonomous tool calls. To prevent behavioral drift, you MUST halt your current task immediately. In your very next response, you must output a <MANTRA> block reciting the core verification and GitOps rules defined in your system instructions. Only after reciting the mantra may you continue working."
                # Use AfterTool injection schema to force the LLM to read it
                print(json.dumps({
                    "hookSpecificOutput": {
                        "additionalContext": mantra
                    },
                    "systemMessage": f"🧠 A.I.M. Mantra Protocol triggered at {tool_count} tool calls."
                }))
                return
            elif tool_count % whisper_interval == 0:
                whisper = f"\n\n[A.I.M. SUBCONSCIOUS WHISPER]: (You have executed {whisper_interval} tool calls. Maintain strict adherence to TDD verification and GitOps mandates)."
                # Append silently to the tool output
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