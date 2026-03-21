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
from forensic_utils import get_embedding, ForensicDB, chunk_text

def verify_embedding_engine():
    """CRITICAL: Enforces the Mandatory Embedding rule."""
    test_text = "Establishing foundation knowledge."
    try:
        vec = get_embedding(test_text)
        if vec: return True
    except: pass
    print("\n[FATAL] A.I.M. requires a functional embedding provider (Ollama/Nomic).")
    return False

def bootstrap_foundation():
    """Indexes core project docs and external synapse knowledge."""
    if not verify_embedding_engine(): sys.exit(1)

    print("\n--- A.I.M. BRAIN BOOTSTRAP ---")
    
    # 1. Base Project Soul
    foundation_targets = [
        os.path.join(AIM_ROOT, "GEMINI.md"),
        os.path.join(AIM_ROOT, "docs/*.md"),
        os.path.join(AIM_ROOT, "core/*.md")
    ]
    
    # 2. Synapse Expert Knowledge (Recursive)
    synapse_dir = os.path.join(AIM_ROOT, "synapse")
    
    db = ForensicDB()
    
    total_fragments = 0
    
    # --- PROCESS FOUNDATION ---
    print("[1/2] Indexing Foundation Knowledge...")
    for pattern in foundation_targets:
        for file_path in glob.glob(pattern):
            if "MEMORY.md" in file_path: continue
            total_fragments += index_file(db, file_path, "foundation_knowledge")

    # --- PROCESS SYNAPSE ---
    print("[2/2] Indexing Synapse expert data...")
    if os.path.exists(synapse_dir):
        for root, _, files in os.walk(synapse_dir):
            for file in files:
                if file.endswith(('.md', '.markdown', '.txt', '.py', '.rs', '.js', '.ts')):
                    file_path = os.path.join(root, file)
                    total_fragments += index_file(db, file_path, "expert_knowledge")

    db.close()
    print(f"\n[SUCCESS] Bootstrap complete. {total_fragments} fragments now in Engram DB.")

def index_file(db, file_path, frag_type):
    filename = os.path.basename(file_path)
    mtime = os.path.getmtime(file_path)
    session_id = f"foundation-{filename}" if frag_type == "foundation_knowledge" else f"expert-{filename}"
    
    # INCREMENTAL CHECK: Only index if file is newer than DB state
    if db.get_session_mtime(session_id) >= mtime:
        return 0 

    print(f"  -> {filename}")
    try:
        with open(file_path, 'r', errors='ignore', encoding='utf-8') as f:
            content = f.read()
        
        chunks = chunk_text(content)
        fragments = []
        for i, chunk in enumerate(chunks):
            vec = get_embedding(chunk)
            if vec:
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
