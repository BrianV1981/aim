#!/usr/bin/env python3
import sys
import os
import json
import argparse
import re
import hashlib
import math
import sqlite3
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
if AIM_ROOT not in sys.path: sys.path.append(AIM_ROOT)
src_dir = os.path.join(AIM_ROOT, "aim_core")
if src_dir not in sys.path: sys.path.append(src_dir)

from config_utils import CONFIG
from aim_core.plugins.datajack.forensic_utils import get_embedding, ForensicDB

def get_fragment_hash(res):
    """Creates a unique fingerprint for a fragment to prevent de-duplication crashes."""
    content = res.get('content', '')
    f_type = res.get('type', '')
    session = res.get('session_id') or res.get('sessionId') or 'Global'
    # Simple hash of content + metadata
    return hashlib.md5(f"{f_type}:{session}:{content[:500]}".encode()).hexdigest()

def get_federated_dbs():
    """Returns a list of all databases in the Federated Archipelago Model."""
    return [
        os.path.join(AIM_ROOT, "archive/project_core.db"),
        os.path.join(AIM_ROOT, "archive/global_skills.db"),
        os.path.join(AIM_ROOT, "archive/datajack_library.db"),
        os.path.join(AIM_ROOT, "archive/subagent_ephemeral.db")
    ]

def get_aggregated_knowledge_map():
    k_map = {
        "foundation_knowledge": [],
        "expert_knowledge": [],
        "session_history": []
    }
    for db_path in get_federated_dbs():
        if not os.path.exists(db_path):
            continue
        try:
            db = ForensicDB(db_path)
            sub_map = db.get_knowledge_map()
            k_map["foundation_knowledge"].extend(sub_map.get("foundation_knowledge", []))
            k_map["expert_knowledge"].extend(sub_map.get("expert_knowledge", []))
            k_map["session_history"].extend(sub_map.get("session_history", []))
            db.close()
        except sqlite3.OperationalError:
            pass # DB might be uninitialized
    return k_map

def print_knowledge_map():
    k_map = get_aggregated_knowledge_map()
    
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

def generate_boolean_query(query):
    """Deterministically generates an FTS5 boolean query using a Smart Python Lexical filter."""
    import re
    stopwords = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", "should", "so", "some", "such", "t", "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "would", "you", "your", "yours", "yourself", "yourselves"}
    
    raw_tokens = re.findall(r"\b[A-Za-z]+\b", query)
    proper_nouns = []
    regular_words = []
    
    for t in raw_tokens:
        if t.lower() in stopwords or len(t) <= 1:
            continue
        # Treat words starting with capital letters (after the first word if it was a stopword) as proper nouns
        if t[0].isupper():
            proper_nouns.append(t.lower())
        else:
            regular_words.append(t.lower())
            
    if not proper_nouns and not regular_words:
        return query
        
    fts_query = ""
    if proper_nouns:
        fts_query += " AND ".join(proper_nouns)
    if regular_words:
        if proper_nouns:
            fts_query += " AND "
        fts_query += "(" + " OR ".join(regular_words) + ")"
        
    return fts_query

def perform_search_internal(query, top_k=10, session_filter=None):
    mandate_keywords = ["POLICY", "MANDATE", "SOUL", "TDD", "SENTINEL", "GUARDRAIL", "HANDBOOK"]
    found_mandates = []
    
    all_semantic = []
    all_lexical = []
    
    # 1. SEMANTIC SEARCH (Vector)
    try:
        query_vec = get_embedding(query, task_type='RETRIEVAL_QUERY')
    except:
        query_vec = None

    if not query_vec:
        print("\n[NOTICE] Semantic Engine Offline: Falling back to exact-keyword (Lexical) search.")
        print(f"         Run '{os.path.basename(AIM_ROOT)} tui' to configure local embeddings for deep semantic recall.\\n")

    for db_path in get_federated_dbs():
        if not os.path.exists(db_path):
            continue
        try:
            db = ForensicDB(db_path)
            
            # Keyword mandates
            if any(k in query.upper() for k in mandate_keywords):
                for kw in mandate_keywords:
                    if kw in query.upper():
                        found_mandates.extend(db.search_by_source_keyword(kw))

            

            boolean_query = generate_boolean_query(query)
            db_results = db.search_fragments(query_vec, top_k=max(100, top_k * 2), session_filter=session_filter) if query_vec else []
            lexical_results = db.search_lexical(boolean_query, top_k=max(100, top_k * 2))
            
            all_semantic.extend(db_results)
            all_lexical.extend(lexical_results)
            
            db.close()
        except sqlite3.OperationalError:
            pass # DB might be uninitialized

    # 2. RECIPROCAL RANK FUSION (RRF) & ENTITY-ENFORCED INTERSECTION
    all_semantic.sort(key=lambda x: x.get('score', 0), reverse=True)
    all_lexical.sort(key=lambda x: x.get('score', float('inf'))) # Lexical SQLite BM25 is negative, lower is better

    rrf_scores = {}
    fragment_data = {}
    k_rrf = 60
    
    # RAG 4.2: If the boolean query contains an AND (meaning we found a proper noun),
    # we enforce INTERSECTION: any semantic hit MUST exist in the lexical hits to survive.
    enforce_intersection = " AND " in boolean_query

    lexical_hashes = {get_fragment_hash(res) for res in all_lexical}

    for rank, res in enumerate(all_semantic, 1):
        f_hash = get_fragment_hash(res)
        if enforce_intersection and f_hash not in lexical_hashes:
            continue # RUTHLESSLY DELETE semantic pollution that lacks the proper noun
        rrf_scores[f_hash] = rrf_scores.get(f_hash, 0) + (1.0 / (k_rrf + rank))
        fragment_data[f_hash] = res

    for rank, res in enumerate(all_lexical, 1):
        f_hash = get_fragment_hash(res)
        rrf_scores[f_hash] = rrf_scores.get(f_hash, 0) + (1.0 / (k_rrf + rank))
        fragment_data[f_hash] = res
        
    # Rebuild results with RRF scores
    results = []
    for f_hash, score in rrf_scores.items():
        res = fragment_data[f_hash]
        res['score'] = score
        results.append(res)

    results.sort(key=lambda x: x['score'], reverse=True)
    results = results[:max(100, top_k * 2)]

    # 3. LOCAL CROSS-ENCODER RERANKING
    try:
        from flashrank import Ranker, RerankRequest
        cache_dir = os.path.join(AIM_ROOT, "archive", "flashrank_cache")
        os.makedirs(cache_dir, exist_ok=True)
        ranker = Ranker(model_name="ms-marco-MiniLM-L-6-v2", cache_dir=cache_dir)
        
        passages = [{"id": get_fragment_hash(r), "text": r['content'], "meta": r} for r in results]
        rerankrequest = RerankRequest(query=query, passages=passages)
        rerank_results = ranker.rerank(rerankrequest)
        
        reranked_final = []
        for r in rerank_results:
            orig = r['meta']
            orig['score'] = r['score']
            reranked_final.append(orig)
        results = reranked_final
    except Exception as e:
        pass

    # 4. KNOWLEDGE PRIORITY WEIGHTING
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

    # Process RRF Results with Boosting
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
        res['score'] = calculate_temporal_decay(res['score'], res.get('timestamp'))
        
        final_results.append(res)
        processed_hashes.add(f_hash)

    # Re-sort based on boosted RRF scores
    final_results.sort(key=lambda x: x['score'], reverse=True)
    return final_results[:top_k]

def perform_search(query, top_k=10, show_context=False):
    final_results = perform_search_internal(query, top_k)

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
