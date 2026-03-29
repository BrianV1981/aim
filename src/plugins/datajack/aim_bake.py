#!/usr/bin/env python3
import os
import sys
import tempfile
import argparse
import json
import zipfile
from pathlib import Path

# Fix python path for local imports
# aim_bake.py is in src/plugins/datajack
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

if aim_root not in sys.path:
    sys.path.append(aim_root)
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from forensic_utils import ForensicDB
from bootstrap_brain import index_file

def bake_cartridge(target_dir, output_file):
    print(f"\n--- A.I.M. DATAJACK FOUNDRY (Atomic Baking) ---")
    if not os.path.isdir(target_dir):
        print(f"[ERROR] Target directory not found: {target_dir}")
        sys.exit(1)

    if not output_file.endswith(".engram"):
        output_file += ".engram"

    output_path = os.path.abspath(output_file)

    # 1. Namespace Isolation (Temporary DB & Sync Folder)
    with tempfile.TemporaryDirectory(prefix="aim_foundry_") as tmpdir:
        tmp_db_path = os.path.join(tmpdir, "factory.db")
        tmp_sync_dir = os.path.join(tmpdir, "sync")
        os.makedirs(tmp_sync_dir, exist_ok=True)
        
        print(f"[*] Spun up isolated factory namespace at {tmpdir}")
        db = ForensicDB(custom_path=tmp_db_path)
        
        # 2. Targeted Ingestion
        print(f"[*] Ingesting raw materials from: {target_dir}")
        fragments_added = 0
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith(('.md', '.markdown', '.txt', '.py', '.rs', '.js', '.ts', '.rst')):
                    file_path = os.path.join(root, file)
                    # Use a clean keyword to guarantee we export exactly what we ingested
                    fragments_added += index_file(db, file_path, "factory_export", ingest_only=True)
                    
        if fragments_added == 0:
            print("[ERROR] No valid documentation files found in target directory.")
            sys.exit(1)
            
        print(f"[*] Calculated embeddings for {fragments_added} semantic chunks.")
        
        # 3. Dump isolated DB to temporary JSONL sync files
        db.cursor.execute("SELECT id, filename, mtime FROM sessions")
        sessions = db.cursor.fetchall()
        
        import hashlib
        hasher = hashlib.sha256()
        
        # Sort by ID so hashing order matches import alphabetical order
        sessions.sort(key=lambda x: x[0])
        
        for sess_id, filename, mtime in sessions:
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
                    rec = {"_record_type": "fragment", "id": frag_id, "text": content, "embedding": db._blob_to_vec(emb), "metadata": meta_dict}
                    rec_str = json.dumps(rec) + "\n"
                    f.write(rec_str)
                    hasher.update(rec_str.encode('utf-8'))
                    
        db.close()
        
        # Write metadata.json with the payload hash
        metadata = {
            "type": "baked_cartridge",
            "payload_hash": hasher.hexdigest(),
            "fragments": fragments_added
        }
        with open(os.path.join(tmp_sync_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # 4. Compile into final .engram
        print(f"[*] Compiling Atomic Cartridge...")
        try:
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for jsonl_file in os.listdir(tmp_sync_dir):
                    zf.write(os.path.join(tmp_sync_dir, jsonl_file), arcname=jsonl_file)
            print(f"[SUCCESS] Atomic Cartridge forged successfully: {output_path}")
        except Exception as e:
            print(f"[ERROR] Failed to compile cartridge: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Bake an isolated atomic .engram cartridge without touching active memory.")
    parser.add_argument("directory", help="The raw documentation directory to vectorize")
    parser.add_argument("output", help="The name of the resulting .engram file (e.g. pytest.engram)")
    args = parser.parse_args()
    bake_cartridge(args.directory, args.output)

if __name__ == "__main__":
    main()