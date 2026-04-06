#!/usr/bin/env python3
import sys
import os
import json
import argparse
import re
import hashlib
import math
from datetime import datetime, timezone

def calculate_temporal_decay(score, timestamp_str, decay_rate=0.01):
    """
    Applies Zep-inspired temporal decay to older memory fragments.
    decay_rate of 0.01 = approx 50% score reduction after 70 days.
    """
    if not timestamp_str:
        return score
    try:
        # Handle format: '2026-03-26T06:54:43.176Z' or '2026-03-26 12:00:00'
        ts_clean = timestamp_str.replace('Z', '+00:00')
        frag_time = datetime.fromisoformat(ts_clean)
        # Ensure frag_time is timezone aware for comparison
        if frag_time.tzinfo is None:
            frag_time = frag_time.replace(tzinfo=timezone.utc)
            
        now = datetime.now(timezone.utc)
        age_days = (now - frag_time).days
        if age_days < 0: age_days = 0
        
        # Exponential decay multiplier
        decay_factor = math.exp(-decay_rate * age_days)
        return score * decay_factor
    except Exception:
        return score

# --- CONFIG BOOTSTRAP ---
def find_aim_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
src_dir = os.path.join(AIM_ROOT, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

from config_utils import CONFIG
from plugins.datajack.forensic_utils import get_embedding, ForensicDB

def get_fragment_hash(res):
    """Creates a unique fingerprint for a fragment to prevent de-duplication crashes."""
    content = res.get('content', '')
    f_type = res.get('type', '')
    session = res.get('session_id') or res.get('sessionId') or 'Global'
    # Simple hash of content + metadata
    return hashlib.md5(f"{f_type}:{session}:{content[:500]}".encode()).hexdigest()

def print_knowledge_map():
    db = ForensicDB()
    k_map = db.get_knowledge_map()
    db.close()
    
    print("\n--- A.I.M. KNOWLEDGE MAP (Index of Keys) ---")
    
    def print_category(title, items):
        if not items: return
        print(f"\n## {title}")
        # Group by first letter or just list if small
        for item in items:
            print(f"  - {item['filename']} [{item['fragments']} fragments] (ID: {item['id']})")
            
    print_category("FOUNDATION KNOWLEDGE (Mandates)", k_map["foundation_knowledge"])
    print_category("EXPERT KNOWLEDGE (Synapse)", k_map["expert_knowledge"])
    
    if k_map["session_history"]:
        print(f"\n## SESSION HISTORY")
        print(f"  - {len(k_map['session_history'])} historical sessions indexed.")
        print(f"    (Use '{os.path.basename(AIM_ROOT)} search' with --session to narrow down specific events)")

    print(f"\nUse '{os.path.basename(AIM_ROOT)} search \"<filename>\" --full' to surgically recall specific keys.")
def perform_search(query, top_k=10, show_context=False):
    db = ForensicDB()
    
    # 1. MANDATE OVERRIDE (Keyword-First)
    mandate_keywords = ["POLICY", "MANDATE", "SOUL", "TDD", "SENTINEL", "GUARDRAIL", "HANDBOOK"]
    found_mandates = []
    if any(k in query.upper() for k in mandate_keywords):
        for kw in mandate_keywords:
            if kw in query.upper():
                found_mandates.extend(db.search_by_source_keyword(kw))

    # 2. SEMANTIC SEARCH (Vector-Second)
    query_vec = get_embedding(query, task_type='RETRIEVAL_QUERY')
    if not query_vec:
        print("Error: Failed to vectorize query.")
        return

    results = db.search_fragments(query_vec, top_k=top_k * 2)
    
    # Phase 25: Hybrid Search (Lexical)
    lexical_results = db.search_lexical(query, top_k=top_k * 2)
    results.extend(lexical_results)
    
    db.close()

    # 3. KNOWLEDGE PRIORITY WEIGHTING
    processed_hashes = set()
    final_results = []

    # Inject Mandates First
    for m in found_mandates:
        m['priority'] = True
        m['score'] = 1.0 
        f_hash = get_fragment_hash(m)
        if f_hash not in processed_hashes:
            final_results.append(m)
            processed_hashes.add(f_hash)

    # Process Semantic Results with Boosting
    for res in results:
        f_hash = get_fragment_hash(res)
        if f_hash in processed_hashes: continue
        
        # Boost foundation knowledge (Soul/Handbook)
        if res.get('type') == 'foundation_knowledge':
            res['score'] = min(1.0, res['score'] * 1.35)
            res['priority'] = True
        
        # Boost expert mandates
        elif res.get('type') == 'expert_knowledge':
            source = str(res.get('source', '') or res.get('filename', '')).upper()
            if any(k in source for k in mandate_keywords):
                res['score'] = min(1.0, res['score'] * 1.50)
                res['priority'] = True
            else:
                res['priority'] = False
        else:
            res['priority'] = False
            
        # Apply Temporal Decay to all results (Penalizes older session knowledge)
        # Mandates implicitly bypass this because their priority boost overcomes the decay, 
        # but we apply it universally for a clean Zep curve.
        res['score'] = calculate_temporal_decay(res['score'], res.get('timestamp'))
        
        final_results.append(res)
        processed_hashes.add(f_hash)

    # Re-sort based on boosted scores
    final_results.sort(key=lambda x: x['score'], reverse=True)
    final_results = final_results[:top_k]

    if not final_results:
        print(f"No forensic record matches found for: '{query}'")
        return

    print(f"\n--- A.I.M. Forensic Search Results for: '{query}' ---")
    for i, res in enumerate(final_results, 1):
        priority_tag = " [MANDATE]" if res.get('priority') else ""
        score_display = f"{res['score']:.4f}"
        session_id = res.get('session_id') or res.get('sessionId') or "Global"
        
        print(f"\n[{i}] Score: {score_display} | Type: {res['type']}{priority_tag}")
        print(f"Source: {res.get('source', res.get('filename', 'Unknown'))} ({session_id})")
        
        content = res['content']
        if not show_context:
            content = (content[:300] + '...') if len(content) > 300 else content
        
        print(f"Content: {content}")
        print("-" * 45)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A.I.M. Forensic Memory Search")
    parser.add_argument("query", nargs="*", help="Semantic search query")
    parser.add_argument("--full", action="store_true", help="Show full content")
    parser.add_argument("--context", action="store_true", help="Alias for --full")
    parser.add_argument("--k", type=int, default=10, help="Number of results")
    parser.add_argument("--map", action="store_true", help="Print the Index of Keys (Knowledge Map)")
    args = parser.parse_args()

    if args.map:
        print_knowledge_map()
    else:
        query_str = " ".join(args.query)
        if not query_str:
            parser.print_help()
            sys.exit(1)
        perform_search(query_str, top_k=args.k, show_context=(args.full or args.context))
