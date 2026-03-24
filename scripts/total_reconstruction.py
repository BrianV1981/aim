#!/usr/bin/env python3
import os
import json
import glob
import sys
import re
from datetime import datetime

# --- DYNAMIC ROOT DISCOVERY ---
def find_aim_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
src_dir = os.path.join(AIM_ROOT, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

ARCHIVE_RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")
DAILY_LOG_DIR = os.path.join(AIM_ROOT, "memory")

def get_scrivener_notes(history, target_date):
    """Only pulls notes from messages matching the target date."""
    if not history: return ""
    notes = []
    
    # We look for '2026-03-20' in the timestamp
    for msg in history:
        ts = msg.get('timestamp', '')
        if target_date not in ts: continue
        
        m_type = msg.get('role') or msg.get('type')
        if m_type == 'user':
            content = msg.get('content', [])
            text = ""
            if isinstance(content, list):
                text = " ".join([c.get('text', '') for c in content if 'text' in c])
            else: text = content
            if text: notes.append(f"- [USER] {str(text)[:400]}...")
        elif m_type in ['gemini', 'model']:
            body = msg.get('content', '')
            if body and len(str(body)) < 1000:
                notes.append(f"- [A.I.M.] {str(body).strip()}")
            
            tool_calls = msg.get('toolCalls') or msg.get('tool_calls') or []
            for call in tool_calls:
                name = call.get('name') or call.get('function', {}).get('name')
                args = call.get('args') or call.get('function', {}).get('arguments')
                notes.append(f"- [ACTION] {name} -> {json.dumps(args)[:300]}...")
                
    return "\n".join(notes) if notes else ""

def reconstruct_day(target_date):
    print(f"--- A.I.M. DEEP TEMPORAL RECONSTRUCTION: {target_date} ---")
    log_path = os.path.join(DAILY_LOG_DIR, f"{target_date}.md")
    
    # 1. Scrape EVERY JSON in the archive (because big sessions span days)
    transcripts = glob.glob(os.path.join(ARCHIVE_RAW_DIR, "*.json"))
    transcripts.sort()
    
    # 2. Reset the log file
    with open(log_path, 'w') as f:
        f.write(f"# A.I.M. Technical Narrative: {target_date} (DEEP RESTORE)\n")
        f.write(f"> Reconstructed on {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

    # 3. Process each session, filtering for INTERNAL timestamps
    total_entries = 0
    for t_path in transcripts:
        try:
            with open(t_path, 'r') as f:
                data = json.load(f)
            
            session_id = data.get('sessionId') or data.get('session_id')
            history = data.get('messages', [])
            if not history: continue
            
            notes = get_scrivener_notes(history, target_date)
            if notes:
                print(f"  -> Found relevant history in: {os.path.basename(t_path)}")
                with open(log_path, "a") as f:
                    f.write(f"\n## Session Record: {os.path.basename(t_path)}\n")
                    f.write(f"Session ID: `{session_id}`\n")
                    f.write("\n### Scrivener Notes:\n")
                    f.write(notes)
                    f.write("\n---\n")
                total_entries += 1
        except Exception as e:
            print(f"    [ERROR] Failed: {os.path.basename(t_path)} -> {e}")

    print(f"\n[SUCCESS] Reconstructed narrative from {total_entries} files.")
    print(f"Check memory/{target_date}.md for the full technical arc.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    reconstruct_day(target)
