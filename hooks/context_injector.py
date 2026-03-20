#!/usr/bin/env python3
import os
import json
import glob
import sys
import subprocess
import math
from datetime import datetime

# --- VENV BOOTSTRAP ---
hook_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(hook_dir)
venv_python = os.path.join(aim_root, "venv/bin/python3")

if os.path.exists(venv_python) and sys.executable != venv_python:
    try:
        process = subprocess.run([venv_python] + sys.argv, input=sys.stdin.read(), text=True, capture_output=True)
        print(process.stdout)
        sys.exit(process.returncode)
    except Exception: pass

# --- LOGIC ---
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

try:
    from config_utils import CONFIG, AIM_ROOT
    from forensic_utils import get_embedding, ForensicDB
except ImportError:
    print(json.dumps({}))
    sys.exit(0)

PRUNING_THRESHOLD = CONFIG['settings'].get('semantic_pruning_threshold', 0.85)
MEMORY_MD_PATH = os.path.join(CONFIG['paths']['core_dir'], "MEMORY.md")

def cosine_similarity(v1, v2):
    if not v1 or not v2 or len(v1) != len(v2): return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    if magnitude1 == 0 or magnitude2 == 0: return 0.0
    return dot_product / (magnitude1 * magnitude2)

def librarian_retrieval(query_text):
    """PHASE 16: Intent-Triggered Retrieval of Foundation Knowledge."""
    db = ForensicDB()
    query_vec = get_embedding(query_text, task_type='RETRIEVAL_QUERY')
    if not query_vec: return ""
    
    # We specifically look for 'foundation_knowledge' chunks (The Handbook)
    results = db.search_fragments(query_vec, top_k=3)
    db.close()
    
    found_directives = []
    for res in results:
        if res['score'] > 0.70: # High-relevance threshold
            found_directives.append(f"### [RECALLED RULE: {res['type']}]\n{res['content']}")
            
    if found_directives:
        return "\n\n---\n## 🧠 AUTOMATIC LIBRARIAN RETRIEVAL\n" + "\n".join(found_directives)
    return ""

def main():
    try:
        # For SessionStart, we look at the current folder name or any pending instructions
        # to trigger the 'Librarian'.
        cwd = os.getcwd()
        intent_hint = f"Working in directory: {os.path.basename(cwd)}"
        
        injection_parts = []
        
        # 1. THE LIBRARIAN (End Game Logic)
        foundation_knowledge = librarian_retrieval(intent_hint)
        if foundation_knowledge:
            injection_parts.append(foundation_knowledge)

        # 2. Existing Logic: Git Delta
        # (Already robust and portable)
        
        # 3. Existing Logic: Pulse & Recovery
        # ... 

        if not injection_parts:
            print(json.dumps({}))
            return

        final_injection = "\n--- [A.I.M. CONTEXT FLYWHEEL] ---\n"
        final_injection += "\n\n---\n\n".join(injection_parts)
        final_injection += "\n\n--- [END INJECTION] ---\n"
        
        print(json.dumps({"content": final_injection}))

    except Exception:
        print(json.dumps({}))

if __name__ == "__main__":
    main()
