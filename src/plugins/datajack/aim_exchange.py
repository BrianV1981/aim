#!/usr/bin/env python3
import sys
import os
import zipfile
import json
import hashlib
import glob

def _find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, 'core/CONFIG.json')): return current
        if os.path.exists(os.path.join(current, 'setup.sh')): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

AIM_ROOT_TMP = _find_aim_root()
if AIM_ROOT_TMP not in sys.path:
    sys.path.append(AIM_ROOT_TMP)
src_dir = os.path.join(AIM_ROOT_TMP, 'src')
if src_dir not in sys.path:
    sys.path.append(src_dir)

from plugins.datajack.forensic_utils import ForensicDB

def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        if os.path.exists(os.path.join(current, "setup.sh")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

AIM_ROOT = find_aim_root()

def import_cartridge(cartridge_path):
    print(f"--- A.I.M. DATAJACK: IMPORT ---")
    print(f"[INFO] Analyzing Engram Cartridge: {os.path.basename(cartridge_path)}")
    
    if not os.path.exists(cartridge_path):
        print(f"[ERROR] Cartridge not found: {cartridge_path}")
        return

    import_dir = os.path.join(AIM_ROOT, "archive", "tmp_engram_import")
    os.makedirs(import_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(cartridge_path, 'r') as zf:
            zf.extractall(import_dir)

        metadata_path = os.path.join(import_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            print("[ERROR] Invalid Cartridge: Missing metadata.json")
            return

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        manifest = metadata.get("manifest", {})
        if manifest:
            print("\n--- CARTRIDGE MANIFEST ---")
            print(f"Author:      {manifest.get('author', 'Unknown')}")
            print(f"Version:     {manifest.get('version', '1.0.0')}")
            print(f"Description: {manifest.get('description', 'No description provided.')}")
            print("--------------------------\n")

        expected_hash = metadata.get("payload_hash")
        if not expected_hash:
            print("[ERROR] Invalid Cartridge: Missing payload_hash in metadata")
            return

        print("[INFO] Verifying Payload Integrity (SHA-256)...")
        hasher = hashlib.sha256()

        # Hash all jsonl files in deterministic order to verify payload
        chunk_files = sorted(glob.glob(os.path.join(import_dir, "*.jsonl")))
        for chunk_file in chunk_files:
            with open(chunk_file, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)

        actual_hash = hasher.hexdigest()

        if actual_hash != expected_hash:
            print(f"[ERROR] Integrity Check Failed!")
            print(f"  Expected: {expected_hash}")
            print(f"  Actual:   {actual_hash}")
            print("[ERROR] Cartridge is corrupt or tampered with. Aborting import.")
            return

        print(f"[SUCCESS] Integrity Verified: {actual_hash[:16]}...")

        # Perform Import
        print("[INFO] Injecting memories into local ForensicDB...")
        db_path = os.path.join(AIM_ROOT, "archive", "datajack_library.db")
        db = ForensicDB(db_path)

        current_session = "Global"
        for chunk_file in chunk_files:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    data = json.loads(line)
                    
                    if data.get("_record_type") == "session":
                        current_session = data.get("session_id", "Global")
                        db.add_session(current_session, data.get("mtime", 0), data.get("filename", ""))
                        
                    elif data.get("_record_type") == "fragment":
                        frag = {
                            "type": "expert_knowledge",
                            "content": data.get("text", ""),
                            "embedding": data.get("embedding", []),
                            "metadata": data.get("metadata", {}),
                            "timestamp": None
                        }
                        db.add_fragments(current_session, [frag])

        db.rebuild_fts()
        print("[SUCCESS] Engram successfully assimilated into the Swarm.")

    except zipfile.BadZipFile:
        print("[ERROR] Invalid zip archive.")
        return
    finally:
        import shutil
        if os.path.exists(import_dir):
            shutil.rmtree(import_dir)

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "import":
        print("Usage: aim_exchange.py import <file.engram>")
        sys.exit(1)
    import_cartridge(sys.argv[2])
