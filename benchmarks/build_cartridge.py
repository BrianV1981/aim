#!/usr/bin/env python3
"""
A.I.M. LongMemEval Cartridge Builder
Embeds all unique sessions into a single, persistent ForensicDB
"""

import json
import time
from pathlib import Path
import sys

# Add A.I.M. root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "aim_core"))

from aim_core.plugins.datajack.forensic_utils import ForensicDB, chunk_text, get_embedding

DATA_DIR = Path(__file__).parent / "data"
TEST_FILE  = DATA_DIR / "longmemeval_s_cleaned.json"

def main():
    print("🚀 Starting A.I.M. DataJack Cartridge Builder for LongMemEval (S dataset)")

    if not TEST_FILE.exists():
        print(f"Error: {TEST_FILE} not found.")
        sys.exit(1)

    questions = json.loads(TEST_FILE.read_text())
    
    # We want a persistent DB that we can package as a cartridge
    db_path = DATA_DIR / "longmemeval_s.db"
    
    # If the DB already exists, we resume. If not, it creates a new one.
    db = ForensicDB(custom_path=str(db_path))

    # Step 1: Deduplicate all sessions across all questions
    print("Parsing unique sessions...")
    unique_sessions = {}
    for item in questions:
        for sid, msgs in zip(item["haystack_session_ids"], item["haystack_sessions"]):
            if sid not in unique_sessions:
                unique_sessions[sid] = msgs

    total_sessions = len(unique_sessions)
    print(f"Found {total_sessions} unique sessions to embed.")

    # Step 2: Check what's already in the DB (for resuming)
    db.cursor.execute("SELECT id FROM sessions")
    existing_sessions = {row[0] for row in db.cursor.fetchall()}
    print(f"Found {len(existing_sessions)} sessions already embedded in {db_path.name}.")

    sessions_to_process = []
    for sid, msgs in unique_sessions.items():
        if sid not in existing_sessions:
            sessions_to_process.append((sid, msgs))

    if not sessions_to_process:
        print("✅ All sessions are already embedded. Rebuilding FTS index just in case...")
        db.rebuild_fts()
        print("Done. Ready to package cartridge.")
        return

    print(f"Embedding {len(sessions_to_process)} remaining sessions...")
    
    start_time = time.perf_counter()
    processed_count = 0

    try:
        for sid, msgs in sessions_to_process:
            db.add_session(sid, f"{sid}.json", time.time())
            all_fragments = []
            
            for msg in msgs:
                content = msg.get("content", "").strip()
                if content:
                    for chunk in chunk_text(content):
                        try:
                            vec = get_embedding(chunk, task_type='RETRIEVAL_DOCUMENT')
                        except Exception as e:
                            print(f"\nEmbedding Error: {e}")
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
            remaining = (len(sessions_to_process) - processed_count) * avg_time
            
            print(f"Progress: {processed_count}/{len(sessions_to_process)} | "
                  f"Avg: {avg_time:.1f}s | "
                  f"ETA: {remaining/60:.1f}m", end="\r")

            # Commit periodically to ensure we don't lose progress if killed
            if processed_count % 50 == 0:
                db.conn.commit()

    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted. Progress saved. Run script again to resume.")
    finally:
        print("\nRebuilding FTS5 Lexical Index...")
        db.rebuild_fts()
        db.conn.commit()
        db.close()
        print(f"✅ Finished embedding. Database saved to: {db_path}")

if __name__ == "__main__":
    main()