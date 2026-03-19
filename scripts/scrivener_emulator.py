#!/usr/bin/env python3
import os
import json
import sys
import glob
from datetime import datetime

# --- CONFIG ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return "/home/kingb/aim"

AIM_ROOT = find_aim_root(os.getcwd())
CHATS_DIR = "/home/kingb/.gemini/tmp/aim/chats"
MEMORY_DIR = os.path.join(AIM_ROOT, "memory")

def get_scrivener_notes(history):
    """NON-AI: Determinstically extracts the technical essence from messages."""
    if not history: return "No activity recorded."
    
    notes = []
    for msg in history:
        m_type = msg.get('type')
        ts = msg.get('timestamp', 'Unknown Time')
        content = msg.get('content', '')
        
        # Handle content as either string or list of parts
        text_content = ""
        if isinstance(content, str):
            text_content = content
        elif isinstance(content, list):
            text_content = " ".join([c.get('text', '') for c in content if isinstance(c, dict) and 'text' in c])
        
        if m_type == 'user':
            notes.append(f"[{ts}] [USER] {text_content[:500]}...")
        elif m_type == 'gemini':
            if text_content:
                notes.append(f"[{ts}] [A.I.M.] {text_content[:500]}...")
            
            # Extract tool calls
            for call in msg.get('toolCalls', []):
                notes.append(f"[{ts}] [ACTION] {call.get('name')} -> {json.dumps(call.get('args'))[:300]}...")
    
    return "\n".join(notes)

def emulate_scrivener():
    print("--- A.I.M. SCRIVENER EMULATOR (NON-AI) ---")
    
    # 1. Identify today's transcripts
    # Use today's date from system if needed, but here we use the specific 3/19 pattern
    pattern = os.path.join(CHATS_DIR, "session-2026-03-19*.json")
    transcripts = glob.glob(pattern)
    transcripts.sort()
    
    if not transcripts:
        print("No transcripts found for today.")
        return

    print(f"Archiving {len(transcripts)} transcripts for 3/19...")
    
    full_log_content = ""
    
    for t_path in transcripts:
        print(f"Processing: {os.path.basename(t_path)}")
        try:
            with open(t_path, 'r') as f:
                data = json.load(f)
            
            history = data.get('messages', [])
            session_id = data.get('sessionId')
            
            # Combine into a final forensic block
            final_block = f"\n## Session Log: 3/19\nSession ID: `{session_id}`\n\n### Scrivener Notes (Deterministic Trace):\n"
            final_block += get_scrivener_notes(history)
            final_block += "\n---\n"
            
            full_log_content += final_block
            
        except Exception as e:
            print(f"Error processing {t_path}: {e}")

    # 2. Write the log
    log_path = os.path.join(MEMORY_DIR, "2026-03-19.md")
    with open(log_path, 'w') as f:
        f.write(full_log_content)
    
    print(f"\n[SUCCESS] High-fidelity deterministic log created: {log_path}")

if __name__ == "__main__":
    emulate_scrivener()
