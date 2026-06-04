#!/usr/bin/env python3
import os
import json
import glob
import sys
import time
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
if current_dir not in sys.path: sys.path.append(current_dir)
if aim_root not in sys.path: sys.path.append(aim_root)

from config_utils import CONFIG, AIM_ROOT
from .aim_core.plugins.datajack.forensic_utils import get_embedding, chunk_text
from .aim_core.lance_backend import VectorBackend

def verify_embedding_engine():
    test_text = "Establishing foundation knowledge."
    try:
        vec = get_embedding(test_text)
        if vec: return True
    except Exception as e:
        import sys; print(f"\n[DEBUG] Embedding test failed: {e}", file=sys.stderr)
    print("\n[NOTICE] Semantic Engine Offline (Ollama/Nomic not found).")
    return False

def bootstrap_foundation():
    embeddings_active = verify_embedding_engine()
    print("\n--- A.I.M. BRAIN BOOTSTRAP ---")
    
    foundation_targets = [
        os.path.join(AIM_ROOT, "AGENTS.md"),
        os.path.join(AIM_ROOT, "aim.wiki/*.md"),
        os.path.join(AIM_ROOT, "core/*.md"),
        os.path.join(AIM_ROOT, "memory/*.md")
    ]
    
    foundry_dir = os.path.join(AIM_ROOT, "foundry")
    backend = VectorBackend()
    
    new_fragments = 0
    
    print("[1/2] Syncing Foundation Knowledge...")
    for pattern in foundation_targets:
        for file_path in glob.glob(pattern):
            if "memory/archive" in file_path: continue
            new_fragments += index_file(backend, file_path, "foundation_knowledge", ingest_only=False, use_embeddings=embeddings_active)

    print("[2/2] Melting down Foundry materials into Engrams...")
    if os.path.exists(foundry_dir):
        for root, _, files in os.walk(foundry_dir):
            for file in files:
                if file.endswith((".md", ".markdown", ".txt", ".py", ".rs", ".js", ".ts", ".rst")):
                    file_path = os.path.join(root, file)
                    new_fragments += index_file(backend, file_path, "expert_knowledge", ingest_only=True, use_embeddings=embeddings_active)

    try:
        table = backend.get_table()
        total_in_db = table.count_rows()
    except Exception:
        total_in_db = 0
        
    print(f"\n[SUCCESS] Bootstrap complete.")
    print(f"      -> New Fragments:   {new_fragments}")
    print(f"      -> Total Brain Size: {total_in_db} fragments")

def index_file(backend, file_path, frag_type, ingest_only=False, use_embeddings=True):
    filename = os.path.basename(file_path)
    try:
        mtime = os.path.getmtime(file_path)
        fsize = os.path.getsize(file_path)
    except: return 0

    if fsize == 0:
        if not ingest_only:
            print(f"  [SKIP] {filename} (Empty file)")
        return 0

    session_id = f"foundation-{filename}" if frag_type == "foundation_knowledge" else f"expert-{filename}"
    
    print(f"  -> {filename} ({fsize/1024:.1f} KB)")
    try:
        with open(file_path, "r", errors="ignore", encoding="utf-8") as f:
            content = f.read()
        
        chunks = chunk_text(content)
        fragments = []
        for i, chunk in enumerate(chunks):
            vec = get_embedding(chunk) if use_embeddings else None
            fragments.append({
                "session_id": session_id,
                "type": frag_type,
                "content": chunk,
                "timestamp": datetime.now().isoformat() + "Z",
                "metadata": json.dumps({"source": filename, "chunk": i, "total": len(chunks)}),
                "source_db": "live_session",
                "vector": vec if vec and len(vec) == 768 else ([0.0]*768)
            })
            
        if fragments:
            backend.add_fragments(fragments)
        return len(fragments)
    except Exception as e:
        print(f"    [SKIP] {filename}: {e}")
        return 0

if __name__ == "__main__":
    bootstrap_foundation()
