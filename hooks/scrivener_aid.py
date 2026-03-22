#!/usr/bin/env python3
import os
import time
import json
import sys
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
    from config_utils import CONFIG, AIM_ROOT
except ImportError:
    print(json.dumps({}))
    sys.exit(0)

def main():
    try:
        if not input_data:
            print(json.dumps({}))
            return
        
        # 1. PILLAR B: ROLLING INTERIM BACKUP & FALLBACK TAIL
        backup_path = os.path.join(AIM_ROOT, "continuity/INTERIM_BACKUP.json")
        tail_path = os.path.join(AIM_ROOT, "continuity/FALLBACK_TAIL.md")
        try:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            with open(backup_path, 'w') as bf:
                bf.write(input_data)
                
            # Phase 20: The Failsafe Context Tail
            data = json.loads(input_data)
            history = data.get('messages', []) or data.get('session_history', [])
            if history:
                tail_content = "# A.I.M. FALLBACK CONTEXT TAIL\n\n*Note: This is an automatic, zero-token snapshot of the last few turns.* \n\n"
                # Get last 10 turns
                recent_turns = history[-10:]
                for msg in recent_turns:
                    role = msg.get('type', 'unknown').upper()
                    tail_content += f"### {role}\n"
                    
                    if role == 'USER':
                        content_list = msg.get('content', [])
                        text = " ".join([c.get('text', '') for c in content_list if 'text' in c])
                        tail_content += f"{text[:500]}...\n\n" if len(text) > 500 else f"{text}\n\n"
                    elif role == 'GEMINI':
                        content = msg.get('content', '')
                        if content:
                            tail_content += f"{content[:500]}...\n\n" if len(content) > 500 else f"{content}\n\n"
                        tool_calls = msg.get('toolCalls', [])
                        for call in tool_calls:
                            tool_name = call.get('name', 'tool')
                            args = json.dumps(call.get('args', {}))
                            tail_content += f"**Tool Call:** `{tool_name}`\n```json\n{args[:200]}\n```\n\n"
                            
                with open(tail_path, 'w') as tf:
                    tf.write(tail_content)
            
            # PHASE 17: Mirror global transcripts to local archive
            porter_path = os.path.join(AIM_ROOT, "scripts/session_porter.py")
            if os.path.exists(porter_path):
                subprocess.run([venv_python, porter_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass

        print(json.dumps({}))

    except Exception: 
        print(json.dumps({}))

if __name__ == "__main__":
    main()
