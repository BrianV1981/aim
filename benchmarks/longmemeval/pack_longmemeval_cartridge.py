#!/usr/bin/env python3
"""
A.I.M. LongMemEval Cartridge Packager
Converts the finished longmemeval_s.db into a portable .engram cartridge.
"""

import os
import sys
import json
import zipfile
import hashlib
import tempfile
from pathlib import Path

# Add A.I.M. root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "aim_core"))

from aim_core.plugins.datajack.forensic_utils import ForensicDB
from aim_core.config_utils import CONFIG

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "longmemeval_s.db"
OUTPUT_FILE = DATA_DIR / "longmemeval_s_cleaned.engram"

def main():
    print("--- A.I.M. DATAJACK FOUNDRY ---")
    
    if not DB_PATH.exists():
        print(f"[ERROR] Database {DB_PATH} not found.")
        print("Please wait for build_cartridge.py to finish before packaging.")
        sys.exit(1)

    print(f"[*] Reading completed embeddings from {DB_PATH.name}...")
    db = ForensicDB(custom_path=str(DB_PATH))
    
    # Check if it's finished
    db.cursor.execute("SELECT count(*) FROM sessions")
    session_count = db.cursor.fetchone()[0]
    
    if session_count < 19000:
        print(f"[WARNING] Database only has {session_count} sessions.")
        print("The background builder (build_cartridge.py) is likely still running.")
        confirm = input("Are you sure you want to package an incomplete cartridge? [y/N]: ")
        if confirm.lower() != 'y':
            sys.exit(0)

    # 1. Namespace Isolation (Temporary Sync Folder)
    with tempfile.TemporaryDirectory(prefix="aim_foundry_") as tmpdir:
        tmp_sync_dir = os.path.join(tmpdir, "sync")
        os.makedirs(tmp_sync_dir, exist_ok=True)
        
        hasher = hashlib.sha256()
        
        # 3. Sovereign Sync Conversion
        print("[*] Translating SQLite vectors to JSONL chunks for portability...")
        db.cursor.execute("SELECT id, filename, mtime FROM sessions")
        sessions = db.cursor.fetchall()
        
        fragments_added = 0
        for i, (sess_id, filename, mtime) in enumerate(sessions):
            db.cursor.execute("SELECT id, content, embedding, metadata FROM fragments WHERE session_id = ?", (sess_id,))
            fragments = db.cursor.fetchall()
            
            jsonl_path = os.path.join(tmp_sync_dir, f"{sess_id}.jsonl")
            with open(jsonl_path, 'w') as f:
                header = {"_record_type": "session", "session_id": sess_id, "filename": filename, "mtime": mtime}
                header_str = json.dumps(header) + "\n"
                f.write(header_str)
                hasher.update(header_str.encode('utf-8'))
                
                for frag_id, content, emb, meta in fragments:
                    try:
                        meta_dict = json.loads(meta) if meta else {}
                    except:
                        meta_dict = {}
                    
                    # Convert binary blob back to float list for JSON
                    vec = db._blob_to_vec(emb) if emb else None
                    rec = {"_record_type": "fragment", "id": frag_id, "text": content, "embedding": vec, "metadata": meta_dict}
                    rec_str = json.dumps(rec) + "\n"
                    f.write(rec_str)
                    hasher.update(rec_str.encode('utf-8'))
                    fragments_added += 1
            
            if (i+1) % 1000 == 0:
                print(f"  -> Translated {i+1}/{len(sessions)} sessions...")
                
        db.close()
        
        # Write metadata.json
        embedding_model = CONFIG.get('models', {}).get('embedding', 'nomic-embed-text')
        metadata = {
            "type": "baked_cartridge",
            "manifest": {
                "author": "A.I.M. Autonomous Benchmark Pipeline",
                "version": "1.0.0",
                "description": "LongMemEval (S Cleaned Dataset) Pre-Embedded Haystack",
                "embedding_model": embedding_model
            },
            "payload_hash": hasher.hexdigest(),
            "fragments": fragments_added
        }
        with open(os.path.join(tmp_sync_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # 4. Compile into final .engram
        print(f"[*] Compiling Atomic Cartridge...")
        try:
            with zipfile.ZipFile(OUTPUT_FILE, "w", zipfile.ZIP_DEFLATED) as zf:
                for jsonl_file in os.listdir(tmp_sync_dir):
                    zf.write(os.path.join(tmp_sync_dir, jsonl_file), arcname=jsonl_file)
            print(f"[SUCCESS] Atomic Cartridge forged successfully: {OUTPUT_FILE}")
            print(f"          Size: {OUTPUT_FILE.stat().st_size / (1024*1024):.2f} MB")
            print("You can now seed this cartridge via `aim export` or share it manually.")
        except Exception as e:
            print(f"[ERROR] Failed to compile cartridge: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()