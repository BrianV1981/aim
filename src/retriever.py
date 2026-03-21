#!/usr/bin/env python3
import sys
import os
import json
import argparse

# --- CONFIG BOOTSTRAP ---
def find_aim_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
src_dir = os.path.join(AIM_ROOT, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

from config_utils import CONFIG
from forensic_utils import get_embedding, ForensicDB

def perform_search(query, top_k=10, show_context=False):
    db = ForensicDB()
    
    # Generate embedding for the query
    query_vec = get_embedding(query, task_type='RETRIEVAL_QUERY')
    if not query_vec:
        print("Error: Failed to vectorize query.")
        return

    # Initial SQL search
    results = db.search_fragments(query_vec, top_k=top_k * 2)
    db.close()

    # --- PHASE 17: KNOWLEDGE PRIORITY WEIGHTING ---
    for res in results:
        if res.get('type') == 'foundation_knowledge':
            res['score'] = min(1.0, res['score'] * 1.35) # 35% Boost for Handbook/Soul
            res['priority'] = True
        else:
            res['priority'] = False

    # Re-sort based on boosted scores
    results.sort(key=lambda x: x['score'], reverse=True)
    final_results = results[:top_k]

    if not final_results:
        print(f"No forensic record matches found for: '{query}'")
        return

    print(f"\n--- A.I.M. Forensic Search Results for: '{query}' ---")
    for i, res in enumerate(final_results, 1):
        priority_tag = " [MANDATE]" if res.get('priority') else ""
        score_display = f"{res['score']:.4f}"
        
        # Schema-Agnostic Session ID retrieval
        session_id = res.get('session_id') or res.get('sessionId') or "Global"
        
        print(f"\n[{i}] Score: {score_display} | Type: {res['type']}{priority_tag}")
        print(f"Source: {session_id}")
        
        content = res['content']
        if not show_context:
            content = (content[:300] + '...') if len(content) > 300 else content
        
        print(f"Content: {content}")
        print("-" * 45)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A.I.M. Forensic Memory Search")
    parser.add_argument("query", help="Semantic search query")
    parser.add_argument("--full", action="store_true", help="Show full content")
    parser.add_argument("--context", action="store_true", help="Alias for --full")
    parser.add_argument("--k", type=int, default=10, help="Number of results")
    args = parser.parse_args()

    perform_search(args.query, top_k=args.k, show_context=(args.full or args.context))
