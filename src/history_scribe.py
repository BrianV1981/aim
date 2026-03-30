#!/usr/bin/env python3
import sys
import json
import os
import glob
import sqlite3
from datetime import datetime

# --- DYNAMIC ROOT DISCOVERY ---
def find_aim_root():
    """Dynamically discovers the A.I.M. root directory."""
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core", "CONFIG.json")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
sys.path.append(os.path.join(AIM_ROOT, "src"))
sys.path.append(os.path.join(AIM_ROOT, "scripts"))

try:
    from extract_signal import extract_signal, skeleton_to_markdown
except ImportError:
    # Fallback if not in path
    extract_signal = None
    skeleton_to_markdown = None

HISTORY_DB = os.path.join(AIM_ROOT, "archive/history.db")
HISTORY_DIR = os.path.join(AIM_ROOT, "archive/history")
RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")

class HistoryDB:
    def __init__(self):
        os.makedirs(os.path.dirname(HISTORY_DB), exist_ok=True)
        self.conn = sqlite3.connect(HISTORY_DB)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                session_id TEXT PRIMARY KEY,
                timestamp TEXT,
                content TEXT
            )
        """)
        # FTS5 for session search
        self.cursor.execute("DROP TABLE IF EXISTS history_fts")
        self.cursor.execute("CREATE VIRTUAL TABLE history_fts USING fts5(session_id UNINDEXED, timestamp UNINDEXED, content)")
        self.conn.commit()

    def add_session(self, session_id, timestamp, content):
        self.cursor.execute("INSERT OR REPLACE INTO history (session_id, timestamp, content) VALUES (?, ?, ?)", 
                           (session_id, timestamp, content))
        self.cursor.execute("INSERT OR REPLACE INTO history_fts (session_id, timestamp, content) VALUES (?, ?, ?)",
                           (session_id, timestamp, content))
        self.conn.commit()

def scribe_all_sessions():
    if not extract_signal:
        print("[ERROR] extract_signal.py not found. Cannot scribe history.")
        return

    db = HistoryDB()
    os.makedirs(HISTORY_DIR, exist_ok=True)
    
    # Target both current tmp chats and archive/raw
    project_name = os.path.basename(AIM_ROOT)
    native_cli_dir = os.path.expanduser(f"~/.gemini/tmp/{project_name}/chats/*.json")
    
    transcripts = glob.glob(native_cli_dir) + glob.glob(os.path.join(RAW_DIR, "*.json"))
    
    print(f"--- History Scribe: Processing {len(transcripts)} sessions ---")
    
    processed_count = 0
    for t_path in transcripts:
        try:
            with open(t_path, 'r') as f:
                data = json.load(f)
            
            session_id = data.get('sessionId') or data.get('session_id')
            if not session_id: continue
            
            md_path = os.path.join(HISTORY_DIR, f"{session_id}.md")
            
            # Skip if already exists and not the very latest file
            if os.path.exists(md_path):
                continue
            
            skeleton = extract_signal(t_path)
            if not skeleton: continue
            
            md_content = skeleton_to_markdown(skeleton, session_id)
            
            # Save Clean MD for Obsidian Mirroring
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            # Index in Dedicated History DB
            ts = data.get('startTime') or datetime.now().isoformat()
            db.add_session(session_id, ts, md_content)
            processed_count += 1
            
        except Exception as e:
            # Skip errors silently for individual files
            pass
            
    print(f"[SUCCESS] Scribed {processed_count} new historical sessions into archive/history/")

if __name__ == "__main__":
    scribe_all_sessions()
