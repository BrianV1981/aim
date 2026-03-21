#!/usr/bin/env python3
import os
import json
import sqlite3
import sys
import tarfile
import argparse
from datetime import datetime

# --- CONFIG BOOTSTRAP ---
def find_aim_root():
    current = os.path.dirname(os.path.abspath(__file__))
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
DB_PATH = os.path.join(AIM_ROOT, "archive/engram.db")

def export_pack(pack_name):
    """Exports expert_knowledge fragments into a portable .aim pack."""
    print(f"--- A.I.M. SYNAPSE EXPORT: {pack_name} ---")
    
    pack_path = os.path.join(AIM_ROOT, f"{pack_name}.aim")
    export_data = {
        "metadata": {
            "name": pack_name,
            "exported_at": datetime.now().isoformat(),
            "type": "expert_knowledge_pack"
        },
        "fragments": [],
        "sessions": []
    }

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Fetch all expert knowledge sessions
        cursor.execute("SELECT * FROM sessions WHERE id LIKE 'expert-%'")
        sessions = cursor.fetchall()
        for s in sessions:
            export_data['sessions'].append(dict(s))
            
            # 2. Fetch all fragments for this session
            cursor.execute("SELECT type, content, timestamp, embedding, metadata FROM fragments WHERE session_id = ?", (s['id'],))
            fragments = cursor.fetchall()
            for f in fragments:
                frag_dict = dict(f)
                # Convert blob back to list for JSON compatibility if needed
                # (For speed, we just keep it as is if we use tar/pickle, but for JSON we convert)
                export_data['fragments'].append(frag_dict)

        # 3. Save to a temporary JSON and then compress
        temp_json = f"{pack_name}.json"
        with open(temp_json, 'w') as f:
            json.dump(export_data, f)
            
        with tarfile.open(pack_path, "w:gz") as tar:
            tar.add(temp_json, arcname=f"{pack_name}.json")
            
        os.remove(temp_json)
        print(f"[SUCCESS] Pack created: {pack_path}")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Export failed: {e}")

def import_pack(pack_path):
    """Imports an .aim pack into the local Engram DB."""
    print(f"--- A.I.M. SYNAPSE IMPORT: {os.path.basename(pack_path)} ---")
    
    try:
        with tarfile.open(pack_path, "r:gz") as tar:
            tar.extractall()
            json_file = tar.getnames()[0]
            
        with open(json_file, 'r') as f:
            data = json.load(f)
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Import Sessions
        for s in data['sessions']:
            cursor.execute("INSERT OR REPLACE INTO sessions (id, filename, mtime) VALUES (?, ?, ?)",
                           (s['id'], s['filename'], s['mtime']))
        
        # Import Fragments
        for f in data['fragments']:
            cursor.execute("INSERT INTO fragments (session_id, type, content, timestamp, embedding, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                           (f['session_id'], f['type'], f['content'], f['timestamp'], f['embedding'], f['metadata']))
        
        conn.commit()
        conn.close()
        os.remove(json_file)
        print(f"[SUCCESS] Imported {len(data['fragments'])} fragments into Engram DB.")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A.I.M. Synapse Exchange")
    parser.add_argument("action", choices=["export", "import"])
    parser.add_argument("target", help="Pack name (export) or File path (import)")
    args = parser.parse_args()

    if args.action == "export": export_pack(args.target)
    else: import_pack(args.target)
