#!/usr/bin/env python3
import os
import sys
import json
import zipfile
import shutil
from datetime import datetime

# --- PATH BOOTSTRAP ---
def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
SRC_DIR = os.path.join(AIM_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from forensic_utils import ForensicDB
import sovereign_sync

def export_cartridge(keyword, out_file):
    """Exports fragments matching a keyword in the source filename to an .engram cartridge."""
    print(f"--- A.I.M. DATAJACK: EXTRACTING '{keyword}' ---")
    
    if not out_file.endswith(".engram"):
        out_file += ".engram"
        
    db = ForensicDB()
    # Find matching sessions
    db.cursor.execute("SELECT id, filename, mtime FROM sessions WHERE id LIKE ? OR filename LIKE ?", (f"%{keyword}%", f"%{keyword}%"))
    sessions = db.cursor.fetchall()
    
    if not sessions:
        print(f"[ERROR] No knowledge found matching keyword: {keyword}")
        db.close()
        return

    # Create temporary build dir
    tmp_dir = os.path.join(AIM_ROOT, "archive", "tmp_engram_build")
    os.makedirs(tmp_dir, exist_ok=True)
    
    metadata = {
        "keyword": keyword,
        "exported_at": datetime.now().isoformat(),
        "sessions_count": len(sessions)
    }
    
    with open(os.path.join(tmp_dir, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)

    chunks_dir = os.path.join(tmp_dir, "chunks")
    os.makedirs(chunks_dir, exist_ok=True)
    
    exported_count = 0
    for sid, filename, mtime in sessions:
        db.cursor.execute("SELECT type, content, timestamp, embedding, metadata FROM fragments WHERE session_id = ?", (sid,))
        fragments = []
        for row in db.cursor.fetchall():
            fragments.append({
                "type": row[0],
                "content": row[1],
                "timestamp": row[2],
                "embedding": db._blob_to_vec(row[3]),
                "metadata": json.loads(row[4]) if row[4] else {}
            })
        
        if fragments:
            jsonl_path = os.path.join(chunks_dir, f"{sid}.jsonl")
            with open(jsonl_path, 'w') as f:
                header = {"session_id": sid, "filename": filename, "mtime": mtime}
                f.write(json.dumps(header) + "\n")
                for frag in fragments:
                    f.write(json.dumps(frag) + "\n")
            exported_count += 1
            
    db.close()
    
    print(f"[1/2] Extracted {exported_count} session chunks.")
    print(f"[2/2] Compiling {out_file}...")
    
    with zipfile.ZipFile(out_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(tmp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, tmp_dir)
                zf.write(file_path, arcname)
                
    shutil.rmtree(tmp_dir)
    print(f"[SUCCESS] Cartridge compiled: {out_file}")


def import_cartridge(engram_file):
    """Imports an .engram cartridge directly into the SQLite DB."""
    print(f"--- A.I.M. DATAJACK: JACKING IN '{engram_file}' ---")
    if not os.path.exists(engram_file):
        print(f"[ERROR] Cartridge not found: {engram_file}")
        return
        
    tmp_dir = os.path.join(AIM_ROOT, "archive", "tmp_engram_import")
    os.makedirs(tmp_dir, exist_ok=True)
    
    print("[1/4] Unpacking cartridge...")
    try:
        with zipfile.ZipFile(engram_file, 'r') as zf:
            zf.extractall(tmp_dir)
    except Exception as e:
        print(f"[ERROR] Failed to unpack cartridge: {e}")
        shutil.rmtree(tmp_dir)
        return
        
    metadata_path = os.path.join(tmp_dir, "metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            meta = json.load(f)
            print(f"[2/4] Cartridge Identity: {meta.get('keyword', 'Unknown')}")
    else:
        print("[2/4] Legacy or unknown cartridge format.")

    chunks_dir = os.path.join(tmp_dir, "chunks")
    if not os.path.exists(chunks_dir):
        print("[ERROR] No chunks directory found in cartridge.")
        shutil.rmtree(tmp_dir)
        return

    # Phase 26: DataJack Security Audit
    print("\n[!!!] SECURITY WARNING [!!!]")
    print("You are about to execute parameterized data ingestion from an untrusted external cartridge.")
    print("This will directly modify your local Engram DB.")
    confirm = input("Do you wish to proceed? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("\n[ABORTED] Import cancelled by operator.")
        shutil.rmtree(tmp_dir)
        return

    print("\n[3/4] Downloading Math (Nomic Embeddings) into Subconscious...")
    db = ForensicDB()
    imported_count = 0
    for filename in os.listdir(chunks_dir):
        if not filename.endswith(".jsonl"): continue
        file_path = os.path.join(chunks_dir, filename)
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
            if not lines: continue
            
            header = json.loads(lines[0])
            session_id = header.get("session_id")
            s_filename = header.get("filename", session_id)
            mtime = header.get("mtime", time.time())
            
            fragments = []
            for line in lines[1:]:
                fragments.append(json.loads(line))
                
            db.add_session(session_id, s_filename, mtime)
            db.add_fragments(session_id, fragments)
            imported_count += 1
            
    print("[4/4] Synchronizing FTS5 Lexical Index...")
    db.rebuild_fts()
    db.close()
    
    shutil.rmtree(tmp_dir)
    print(f"\n[SUCCESS] I know Kung Fu. ({imported_count} knowledge sessions injected)")

def unplug_cartridge(keyword):
    """Deletes all fragments and sessions matching a keyword in the source filename."""
    print(f"--- A.I.M. DATAJACK: UNPLUGGING '{keyword}' ---")
    
    db = ForensicDB()
    # Find matching sessions
    db.cursor.execute("SELECT id FROM sessions WHERE filename LIKE ?", (f"%{keyword}%",))
    sessions = [row[0] for row in db.cursor.fetchall()]
    
    if not sessions:
        print(f"[ERROR] No knowledge found matching keyword: {keyword}")
        db.close()
        return

    print(f"[1/3] Identifying {len(sessions)} neural connections...")
    
    deleted_count = 0
    for sid in sessions:
        # Fragments cascade delete because of the FOREIGN KEY ON DELETE CASCADE constraint
        db.cursor.execute("DELETE FROM sessions WHERE id = ?", (sid,))
        deleted_count += 1
        
    db.conn.commit()
    print(f"[2/3] Deleted {deleted_count} root sessions. Fragments cascaded.")
    
    print("[3/3] Synchronizing FTS5 Lexical Index...")
    # Delete from FTS table to clear orphaned keywords (we just rebuild it completely for safety)
    db.cursor.execute("DELETE FROM fragments_fts")
    db.conn.commit()
    db.rebuild_fts()
    db.close()
    
    print(f"\n[SUCCESS] Cartridge unplugged. The knowledge has been purged.")

def main():
    if len(sys.argv) < 3:
        print("Usage: aim exchange export <keyword> --out <file.engram>")
        print("       aim exchange import <file.engram>")
        print("       aim exchange unplug <keyword>")
        sys.exit(1)
        
    command = sys.argv[1]
    target = sys.argv[2]
    
    if command == "export":
        out_file = "export.engram"
        if "--out" in sys.argv:
            idx = sys.argv.index("--out")
            if idx + 1 < len(sys.argv):
                out_file = sys.argv[idx + 1]
        export_cartridge(target, out_file)
    elif command == "import":
        import_cartridge(target)
    elif command == "unplug":
        unplug_cartridge(target)
    else:
        print("Unknown command. Use export, import, or unplug.")

if __name__ == "__main__":
    main()
