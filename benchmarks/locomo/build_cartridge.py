#!/usr/bin/env python3
"""
A.I.M. DataJack Cartridge Builder for LoCoMo (Long-term Conversational Memory)
Downloads the Aman279/Locomo dataset from Hugging Face, generates markdown flight recorders,
and embeds them into a persistent ForensicDB.
"""

import json
import time
from pathlib import Path
import sys
import re
from datasets import load_dataset

# Add A.I.M. root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "aim_core"))

from aim_core.plugins.datajack.forensic_utils import ForensicDB, chunk_text, get_embedding

DATA_DIR = Path(__file__).parent / "data"
MD_DIR = DATA_DIR / "flight_recorders"

def main():
    print("🚀 Starting A.I.M. DataJack Cartridge Builder for LoCoMo dataset")

    MD_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading dataset 'Aman279/Locomo' from Hugging Face...")
    ds = load_dataset('Aman279/Locomo')
    
    train_ds = ds['train']
    print(f"Loaded {len(train_ds)} dialogues. Generating Markdown Flight Recorders...")

    # Generate MD files
    for row in train_ds:
        dialogue_id = str(row['dialogue_id'])
        turns_data = json.loads(row['turns'])
        speakers = turns_data.get('speaker_role', [])
        utterances = turns_data.get('utterance', [])
        
        md_content = f"# LoCoMo Dialogue {dialogue_id}\n\n"
        for i, (speaker, utterance) in enumerate(zip(speakers, utterances)):
            match = re.search(r'\b(?:19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}\b|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(?:19|20)\d{2}\b', utterance, re.IGNORECASE)
            if match:
                current_date = f'[{match.group(0)}]'
            else:
                current_date = locals().get('current_date', '[Date Unknown]')
            md_content += f'{current_date} **{speaker}**: {utterance}\n\n'
        
        md_file = MD_DIR / f"{dialogue_id}.md"
        md_file.write_text(md_content, encoding="utf-8")

    print(f"Generated {len(train_ds)} Markdown files in {MD_DIR}.")

    # Persistent DB
    db_path = DATA_DIR / "locomo.db"
    db = ForensicDB(custom_path=str(db_path))

    # Step 1: Get all files
    all_files = list(MD_DIR.glob("*.md"))
    total_sessions = len(all_files)

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