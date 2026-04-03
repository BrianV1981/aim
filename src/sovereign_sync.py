import os
import json
import sqlite3
import glob

def export_to_jsonl(db, sync_dir):
    """
    Exports all sessions and fragments from the Engram DB into JSONL files.
    Creates one .jsonl file per session_id to minimize git merge conflicts.
    """
    os.makedirs(sync_dir, exist_ok=True)
    
    # Get all sessions
    db.cursor.execute("SELECT id, filename, mtime FROM sessions")
    sessions = db.cursor.fetchall()
    
    exported_count = 0
    for session in sessions:
        session_id, filename, mtime = session
        
        # Get fragments for this session
        db.cursor.execute("SELECT type, content, timestamp, embedding, metadata FROM fragments WHERE session_id = ?", (session_id,))
        fragments = db.cursor.fetchall()
        
        jsonl_path = os.path.join(sync_dir, f"{session_id}.jsonl")
        
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            # First line is the session metadata
            session_meta = {
                "_record_type": "session",
                "session_id": session_id,
                "filename": filename,
                "mtime": mtime
            }
            f.write(json.dumps(session_meta) + "\n")
            
            # Subsequent lines are fragments
            for frag in fragments:
                frag_type, content, timestamp, embedding_blob, metadata_str = frag
                embedding = db._blob_to_vec(embedding_blob) if embedding_blob else None
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                frag_data = {
                    "_record_type": "fragment",
                    "type": frag_type,
                    "content": content,
                    "timestamp": timestamp,
                    "embedding": embedding,
                    "metadata": metadata
                }
                f.write(json.dumps(frag_data) + "\n")
                
        exported_count += 1
        
    return exported_count

def import_from_jsonl(db, sync_dir):
    """
    Imports JSONL files back into the Engram DB.
    Only imports if the JSONL file represents a newer or missing session.
    """
    if not os.path.exists(sync_dir):
        return 0
        
    imported_count = 0
    jsonl_files = glob.glob(os.path.join(sync_dir, "*.jsonl"))
    
    for jpath in jsonl_files:
        with open(jpath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines: continue
        
        try:
            session_meta = json.loads(lines[0])
            if session_meta.get("_record_type") != "session":
                continue
                
            session_id = session_meta["session_id"]
            filename = session_meta["filename"]
            mtime = session_meta["mtime"]
            
            # Compare mtime with existing DB
            db_mtime = db.get_session_mtime(session_id)
            if db_mtime >= mtime:
                continue # DB is already up-to-date
                
            # It's newer or missing, let's parse fragments
            fragments = []
            for line in lines[1:]:
                frag_data = json.loads(line)
                if frag_data.get("_record_type") == "fragment":
                    fragments.append({
                        "type": frag_data["type"],
                        "content": frag_data["content"],
                        "timestamp": frag_data["timestamp"],
                        "embedding": frag_data["embedding"],
                        "metadata": frag_data["metadata"]
                    })
            
            db.add_session(session_id, filename, mtime)
            db.add_fragments(session_id, fragments)
            imported_count += 1
            
        except Exception as e:
            print(f"Error importing {jpath}: {e}")
            
    return imported_count

if __name__ == "__main__":
    import sys
    try:
        from plugins.datajack.forensic_utils import ForensicDB
        import config_utils
        db = ForensicDB()
        sync_dir = os.path.join(config_utils.AIM_ROOT, "archive", "sync")
        if len(sys.argv) > 1 and sys.argv[1] == "export":
            export_to_jsonl(db, sync_dir)
        elif len(sys.argv) > 1 and sys.argv[1] == "import":
            import_from_jsonl(db, sync_dir)
        db.close()
    except Exception as e:
        sys.stderr.write(f"Sovereign Sync Daemon Error: {e}\n")
