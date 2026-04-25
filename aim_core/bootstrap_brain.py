#!/usr/bin/env python3
import os
import json
import glob
import sys
import time
import sqlite3
from datetime import datetime

# --- CONFIG BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
if current_dir not in sys.path: sys.path.append(current_dir)

from config_utils import CONFIG, AIM_ROOT
from aim_core.plugins.datajack.forensic_utils import get_embedding, ForensicDB, chunk_text

def verify_embedding_engine():
    """Checks for Semantic Engine, but allows Graceful Lexical Fallback if missing."""
    test_text = "Establishing foundation knowledge."
    try:
        vec = get_embedding(test_text)
        if vec: return True
    except Exception as e:
        import sys; print(f"\n[DEBUG] Embedding test failed: {e}", file=sys.stderr)
    print("\n[NOTICE] Semantic Engine Offline (Ollama/Nomic not found).")
    print("         A.I.M. will gracefully degrade to pure FTS5 Lexical Search.")
    print(f"         (Run '{os.path.basename(AIM_ROOT)} tui' later to configure embeddings for deep semantic recall).")
    return False

def bootstrap_foundation():
    """Indexes core project docs and external synapse knowledge."""
    embeddings_active = verify_embedding_engine()

    print("\n--- A.I.M. BRAIN BOOTSTRAP ---")
    
    # 1. Base Project Soul (Synchronized)
    foundation_targets = [
        os.path.join(AIM_ROOT, "AGENTS.md"),
        os.path.join(AIM_ROOT, "aim.wiki/*.md"),
        os.path.join(AIM_ROOT, "core/*.md"),
        os.path.join(AIM_ROOT, "memory/*.md"),
        os.path.join(AIM_ROOT, "docs/*.md"),
        os.path.join(AIM_ROOT, "continuity/*.md")
    ]
    
    # 2. Foundry Raw Materials (Ingest-Only)
    foundry_dir = os.path.join(AIM_ROOT, "foundry")
    
    db = ForensicDB()
    
    new_fragments = 0
    
    # --- PROCESS FOUNDATION (Sync Mode) ---
    print("[1/2] Syncing Foundation Knowledge...")
    for pattern in foundation_targets:
        for file_path in glob.glob(pattern):
            # We skip memory archive files to avoid bloating foundation
            if "memory/archive" in file_path: continue
            new_fragments += index_file(db, file_path, "foundation_knowledge", ingest_only=False, use_embeddings=embeddings_active)

    # --- PROCESS FOUNDRY (Ingest Mode) ---
    print("[2/2] Melting down Foundry materials into Engrams...")
    if os.path.exists(foundry_dir):
        for root, _, files in os.walk(foundry_dir):
            for file in files:
                if file.endswith(('.md', '.markdown', '.txt', '.py', '.rs', '.js', '.ts', '.rst')):
                    file_path = os.path.join(root, file)
                    new_fragments += index_file(db, file_path, "expert_knowledge", ingest_only=True, use_embeddings=embeddings_active)

        # --- PROCESS PRE-COMPILED CARTRIDGES (Engrams) ---
    print("[3/3] Ingesting Default OS Cartridges...")
    engrams_dir = os.path.join(AIM_ROOT, "engrams")
    if os.path.exists(engrams_dir):
        from aim_core.plugins.datajack.aim_exchange import import_cartridge
        for root, _, files in os.walk(engrams_dir):
            for file in files:
                if file.endswith('.engram'):
                    print(f"  -> Ingesting {file} into DataJack Library...")
                    import_cartridge(os.path.join(root, file), auto_confirm=True)

    # --- GET TOTAL STATS ---
    db.cursor.execute("SELECT count(*) FROM fragments")
    total_in_db = db.cursor.fetchone()[0]
    db.close()
    
    print(f"\n[SUCCESS] Bootstrap complete.")
    print(f"      -> New Fragments:   {new_fragments}")
    print(f"      -> Total Brain Size: {total_in_db} fragments")

def index_file(db, file_path, frag_type, ingest_only=False, use_embeddings=True):
    filename = os.path.basename(file_path)
    try:
        mtime = os.path.getmtime(file_path)
        fsize = os.path.getsize(file_path)
    except: return 0

    # SAFETY: Skip 0-byte files to prevent hollowing out engrams
    if fsize == 0:
        if not ingest_only: # Only warning for foundation files
            print(f"  [SKIP] {filename} (Empty file)")
        return 0

    session_id = f"foundation-{filename}" if frag_type == "foundation_knowledge" else f"expert-{filename}"
    
    # INCREMENTAL CHECK: Only index if file is newer than DB state
    if db.get_session_mtime(session_id) >= mtime:
        return 0 

    print(f"  -> {filename} ({fsize/1024:.1f} KB)")
    try:
        with open(file_path, 'r', errors='ignore', encoding='utf-8') as f:
            content = f.read()
        
        chunks = chunk_text(content)
        fragments = []
        for i, chunk in enumerate(chunks):
            vec = get_embedding(chunk) if use_embeddings else None
            # Allow indexing even if vec is None (for FTS5 lexical fallback)
            fragments.append({
                "type": frag_type,
                "content": chunk,
                "timestamp": datetime.now().isoformat(),
                "embedding": vec,
                "metadata": {"source": filename, "chunk": i, "total": len(chunks)}
            })
        
        db.add_session(session_id, filename, mtime)
        db.add_fragments(session_id, fragments)
        return len(fragments)
    except Exception as e:
        print(f"    [SKIP] {filename}: {e}")
        return 0

if __name__ == "__main__":
    bootstrap_foundation()
