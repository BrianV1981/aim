#!/usr/bin/env python3
import os
import json
import glob
import sys
import time

# --- CONFIG BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
if current_dir not in sys.path: sys.path.append(current_dir)

from datetime import datetime
from config_utils import CONFIG, AIM_ROOT
from forensic_utils import get_embedding, ForensicDB, chunk_text

def verify_embedding_engine():
    """CRITICAL: Enforces the Mandatory Embedding rule."""
    print("[1/3] Verifying Embedding Engine (Mandatory)...")
    test_text = "Establishing foundation knowledge."
    try:
        # Attempt a test embedding
        vec = get_embedding(test_text)
        if vec:
            print("[OK] Embedding engine is ONLINE.")
            return True
    except Exception as e:
        print(f"[ERROR] Embedding Engine is OFFLINE: {e}")
    
    print("\n[FATAL] A.I.M. requires a functional embedding provider to initialize its brain.")
    print("Action Required: Ensure Ollama is running and 'nomic-embed-text' is pulled.")
    print("Command: ollama run nomic-embed-text")
    return False

def bootstrap_foundation():
    """Indexes core project docs into the forensic DB."""
    if not verify_embedding_engine():
        sys.exit(1)

    print("[2/3] Scanning project documentation for 'Base Truths'...")
    
    # We index GEMINI.md and everything in docs/
    targets = [
        os.path.join(AIM_ROOT, "clean-install-docs/*.md"),
        os.path.join(AIM_ROOT, "GEMINI.md"),
        os.path.join(AIM_ROOT, "docs/*.md"),
        os.path.join(AIM_ROOT, "core/*.md")
    ]
    
    db = ForensicDB()
    total_fragments = 0
    
    for pattern in targets:
        for file_path in glob.glob(pattern):
            filename = os.path.basename(file_path)
            print(f"  -> Indexing: {filename}")
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Split into semantic chunks
                chunks = chunk_text(content)
                fragments = []
                
                for i, chunk in enumerate(chunks):
                    vec = get_embedding(chunk)
                    if vec:
                        fragments.append({
                            "type": "foundation_knowledge",
                            "content": chunk,
                            "timestamp": datetime.now().isoformat(),
                            "embedding": vec,
                            "metadata": {
                                "source": filename,
                                "chunk": i,
                                "total_chunks": len(chunks),
                                "tier": "Level 0: Foundation"
                            }
                        })
                
                # Use a pseudo-session ID for foundation knowledge
                db.add_session(f"foundation-{filename}", filename, os.path.getmtime(file_path))
                db.add_fragments(f"foundation-{filename}", fragments)
                total_fragments += len(fragments)
                
            except Exception as e:
                print(f"  [SKIP] Failed to index {filename}: {e}")

    db.close()
    print(f"[3/3] Foundation complete. {total_fragments} fragments indexed.")
    print("\n[SUCCESS] A.I.M. now possesses innate technical knowledge of itself.")

if __name__ == "__main__":
    from datetime import datetime
    bootstrap_foundation()
