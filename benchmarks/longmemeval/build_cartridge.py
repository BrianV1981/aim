#!/usr/bin/env python3
"""
A.I.M. LongMemEval Cartridge Builder (Resumable)
Embeds all unique sessions into a single, persistent ForensicDB.
If killed, simply run it again to resume exactly where it left off.
"""

import json
import time
from pathlib import Path
import sys

# Add A.I.M. root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "aim_core"))

from aim_core.plugins.datajack.forensic_utils import ForensicDB, chunk_text, get_embedding

DATA_DIR = Path(__file__).parent / "data"
MD_DIR = DATA_DIR / "flight_recorders"

def main():
    print("🚀 Starting A.I.M. DataJack Cartridge Builder for LongMemEval (S dataset)")

    if not MD_DIR.exists():
        print(f"Error: {MD_DIR} not found.")
        sys.exit(1)

    # We want a persistent DB that we can package as a cartridge
    db_path = DATA_DIR / "longmemeval_s.db"
    
    # If the DB already exists, we resume. If not, it creates a new one.
    db = ForensicDB(custom_path=str(db_path))

    # Step 1: Get all files
    all_files = list(MD_DIR.glob("*.md"))
    total_sessions = len(all_files)
    print(f"Found {total_sessions} unique Markdown Flight Recorders to embed.")

    # Step 2: Check what's already in the DB (for resuming)
    db.cursor.execute("SELECT id FROM sessions")
    existing_sessions = {row[0] for row in db.cursor.fetchall()}
    print(f"Found {len(existing_sessions)} sessions already embedded in {db_path.name}.")

    files_to_process = []
    for f in all_files:
        sid = f.stem
        if sid not in existing_sessions:
            files_to_process.append((sid, f))

    if not files_to_process:
        print("✅ All sessions are already embedded. Rebuilding FTS index just in case...")
        db.rebuild_fts()
        print("Done. Ready to package cartridge.")
        return

    print(f"Embedding {len(files_to_process)} remaining sessions...")
    
    start_time = time.perf_counter()
    processed_count = 0

    try:
        for sid, md_file in files_to_process:
            db.add_session(sid, md_file.name, time.time())
            content = md_file.read_text(encoding="utf-8").strip()
            
            all_fragments = []
            if content:
                for chunk in chunk_text(content):
                    try:
                        vec = get_embedding(chunk, task_type='RETRIEVAL_DOCUMENT')
                    except Exception as e:
                        print(f"\nEmbedding Error on {sid}: {e}")
                        vec = None
                        
                    all_fragments.append({
                        'type': 'session_history',
                        'content': chunk,
                        'embedding': vec
                    })
            
            if all_fragments:
                db.add_fragments(sid, all_fragments)
                
            processed_count += 1
            elapsed = time.perf_counter() - start_time
            avg_time = elapsed / processed_count
            remaining = (len(files_to_process) - processed_count) * avg_time
            
            print(f"Progress: {processed_count}/{len(files_to_process)} | "
                  f"Avg: {avg_time:.1f}s | "
                  f"ETA: {remaining/60:.1f}m", end="\r")

            # Commit periodically to ensure we don't lose progress if killed
            if processed_count % 50 == 0:
                db.conn.commit()

    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted. Progress saved. Run script again to resume.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n\n⚠️ Unexpected crash: {e}. Progress saved. Run script again to resume.")
    finally:
        print("\nRebuilding FTS5 Lexical Index...")
        db.rebuild_fts()
        db.conn.commit()
        db.close()
        print(f"✅ Finished embedding. Database saved to: {db_path}")

if __name__ == "__main__":
    main()