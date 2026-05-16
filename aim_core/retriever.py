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
    if not timestamp_str:
        return score
    try:
        ts_clean = timestamp_str.replace('Z', '+00:00')
        frag_time = datetime.fromisoformat(ts_clean)
        if frag_time.tzinfo is None:
            frag_time = frag_time.replace(tzinfo=timezone.utc)
            
        now = datetime.now(timezone.utc)
        age_days = (now - frag_time).days
        if age_days < 0: age_days = 0
        
        decay_factor = math.exp(-decay_rate * age_days)
        return score * decay_factor
    except Exception:
        return score

def find_aim_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
if AIM_ROOT not in sys.path: sys.path.append(AIM_ROOT)
src_dir = os.path.join(AIM_ROOT, "aim_core")
if src_dir not in sys.path: sys.path.append(src_dir)

from config_utils import CONFIG
from aim_core.plugins.datajack.forensic_utils import get_embedding

def get_fragment_hash(res):
    content = res.get('content', '')
    f_type = res.get('type', '')
    session = res.get('session_id') or res.get('sessionId') or 'Global'
    return hashlib.md5(f"{f_type}:{session}:{content[:500]}".encode()).hexdigest()

def get_aggregated_knowledge_map():
    k_map = {
        "foundation_knowledge": [],
        "expert_knowledge": [],
        "session_history": []
    }
    
    from aim_core.lance_backend import VectorBackend
    import pandas as pd
    
    # 1. Query RAM (memory_lance)
    try:
        table = VectorBackend().get_table()
        df = table.search().limit(1000000).to_pandas()
        for t in ["foundation_knowledge", "expert_knowledge", "session_history"]:
            sub_df = df[df['type'] == t]
            for sess_id, group in sub_df.groupby('session_id'):
                k_map[t].append({
                    "id": sess_id,
                    "filename": group.iloc[0].get('source_db', 'live_session'),
                    "fragments": len(group)
                })
    except Exception:
        pass
        
    # 2. Query ROM (Parquet Cartridges)
    cartridges_dir = os.path.join(AIM_ROOT, "archive", "cartridges")
    if os.path.exists(cartridges_dir):
        import glob
        import pyarrow.dataset as ds
        for parquet_file in glob.glob(os.path.join(cartridges_dir, "*.parquet")):
            try:
                dataset = ds.dataset(parquet_file)
                df = dataset.to_table().to_pandas()
                for t in ["foundation_knowledge", "expert_knowledge", "session_history"]:
                    if t not in df['type'].values: continue
                    sub_df = df[df['type'] == t]
                    for sess_id, group in sub_df.groupby('session_id'):
                        k_map[t].append({
                            "id": sess_id,
                            "filename": os.path.basename(parquet_file),
                            "fragments": len(group)
                        })
            except Exception:
                pass
                
    return k_map

def print_knowledge_map():
    k_map = get_aggregated_knowledge_map()
    
    print("\n--- A.I.M. KNOWLEDGE MAP (Index of Keys) ---")
    
    def print_category(title, items):
        if not items: return
        print(f"\n## {title}")
        for item in items:
            print(f"  - {item['filename']} [{item['fragments']} fragments] (ID: {item['id']})")
            
    print_category("FOUNDATION KNOWLEDGE (Mandates)", k_map["foundation_knowledge"])
    print_category("EXPERT KNOWLEDGE (Synapse)", k_map["expert_knowledge"])
    
    if k_map["session_history"]:
        print(f"\n## SESSION HISTORY")
        print(f"  - {len(k_map['session_history'])} historical sessions indexed.")
        print(f"    (Use '{os.path.basename(AIM_ROOT)} search' with --session to narrow down specific events)")

    print(f"\nUse '{os.path.basename(AIM_ROOT)} search \"<filename>\" --full' to surgically recall specific keys.")

def expand_sandwich_context(results):
    expanded_results = []
    seen_ids = set()
    
    from aim_core.lance_backend import VectorBackend
    backend = VectorBackend()
    try:
        table = backend.get_table()
    except Exception:
        table = None
        
    import pyarrow.dataset as ds
    import lancedb

    mem_db = lancedb.connect("memory://")

    def query_fragments(source_db, cond_str):
        if source_db and source_db.endswith(".parquet"):
            parquet_path = os.path.join(AIM_ROOT, "archive", "cartridges", source_db)
            if not os.path.exists(parquet_path):
                return []
            try:
                table_name = os.path.basename(parquet_path)
                if table_name not in mem_db.table_names():
                    dataset = ds.dataset(parquet_path)
                    t = mem_db.create_table(table_name, data=dataset)
                else:
                    t = mem_db.open_table(table_name)
                return t.search().where(cond_str).to_list()
            except Exception:
                return []
        else:
            if table is None: return []
            try:
                return table.search().where(cond_str).to_list()
            except Exception:
                return []

    for res in results:
        frag_id = res['id']
        session_id = res['session_id']
        parent_id = res['parent_id']
        source_db = res.get('filename') or res.get('source', '')
        
        uid = f"{session_id}_{frag_id}"
        if uid in seen_ids:
            continue
            
        if res['type'] not in ('session_history', 'expert_knowledge', 'foundation_knowledge'):
            expanded_results.append(res)
            seen_ids.add(uid)
            continue
            
        if parent_id is not None:
            try:
                cond_parent = f"session_id = '{session_id}' AND fragment_id = {parent_id}"
                parent_rows = query_fragments(source_db, cond_parent)
            except:
                cond_parent = f"session_id = '{session_id}' AND sqlite_id = {parent_id}"
                parent_rows = query_fragments(source_db, cond_parent)
            
            parent_content = parent_rows[0]['content'] if parent_rows else ""
            
            try:
                cond_adj = f"session_id = '{session_id}' AND parent_id = {parent_id} AND fragment_id >= {frag_id - 1} AND fragment_id <= {frag_id + 1}"
                adjacent = query_fragments(source_db, cond_adj)
            except:
                cond_adj = f"session_id = '{session_id}' AND parent_id = {parent_id} AND sqlite_id >= {frag_id - 1} AND sqlite_id <= {frag_id + 1}"
                adjacent = query_fragments(source_db, cond_adj)
            
            try:
                adjacent.sort(key=lambda x: x['fragment_id'])
            except KeyError:
                adjacent.sort(key=lambda x: x['sqlite_id'])
            
            combined = []
            if parent_content: combined.append(f"[OVERARCHING PARENT SUMMARY]\\n{parent_content}")
            for r in adjacent:
                combined.append(r['content'])
                try:
                    seen_ids.add(f"{session_id}_{r['fragment_id']}")
                except KeyError:
                    seen_ids.add(f"{session_id}_{r['sqlite_id']}")
                
            res['content'] = "\\n\\n---\\n\\n".join(combined)
            expanded_results.append(res)
        else:
            try:
                cond_adj = f"session_id = '{session_id}' AND fragment_id >= {frag_id - 1} AND fragment_id <= {frag_id + 1}"
                adjacent = query_fragments(source_db, cond_adj)
            except:
                cond_adj = f"session_id = '{session_id}' AND sqlite_id >= {frag_id - 1} AND sqlite_id <= {frag_id + 1}"
                adjacent = query_fragments(source_db, cond_adj)
                
            adjacent = [r for r in adjacent if r.get('parent_id') is None]
            
            try:
                adjacent.sort(key=lambda x: x['fragment_id'])
            except KeyError:
                adjacent.sort(key=lambda x: x['sqlite_id'])
            
            combined = []
            for r in adjacent:
                combined.append(r['content'])
                try:
                    seen_ids.add(f"{session_id}_{r['fragment_id']}")
                except KeyError:
                    seen_ids.add(f"{session_id}_{r['sqlite_id']}")
                
            res['content'] = "\\n\\n---\\n\\n".join(combined)
            expanded_results.append(res)
            
    return expanded_results

def perform_search_internal(query, top_k=10, session_filter=None):
    from aim_core.lance_backend import VectorBackend
    mandate_keywords = ["POLICY", "MANDATE", "SOUL", "TDD", "SENTINEL", "GUARDRAIL", "HANDBOOK"]
    
    try:
        query_vec = get_embedding(query, task_type='RETRIEVAL_QUERY')
    except:
        query_vec = None

    if not query_vec:
        print("\\n[NOTICE] Semantic Engine Offline: Falling back to exact-keyword (Lexical) search.")
        print(f"         Run '{os.path.basename(AIM_ROOT)} tui' to configure local embeddings for deep semantic recall.\\n")

    try:
        backend = VectorBackend()
        results = backend.search(query_vec, query, top_k=top_k, session_filter=session_filter)
    except Exception as e:
        print(f"\\n[!] LanceDB Search Error: {e}")
        results = []

    results = expand_sandwich_context(results)

    try:
        from flashrank import Ranker, RerankRequest
        cache_dir = os.path.join(AIM_ROOT, "archive", "flashrank_cache")
        os.makedirs(cache_dir, exist_ok=True)
        ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir=cache_dir)
        
        passages = []
        for r in results:
            passages.append({
                "id": str(r.get("id")),
                "text": r.get("content", ""),
                "meta": r
            })
            
        if passages:
            rerankreq = RerankRequest(query=query, passages=passages)
            reranked = ranker.rerank(rerankreq)
            
            final_results = []
            for r in reranked:
                meta = r['meta']
                meta['score'] = float(calculate_temporal_decay(float(r['score']), meta.get('timestamp')))
                final_results.append(meta)
                
            results = final_results
    except ImportError:
        pass

    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    return results[:top_k]

def perform_search(query, top_k=10, show_context=False):
    return perform_search_internal(query, top_k)

def main():
    parser = argparse.ArgumentParser(description="A.I.M. Autonomous Knowledge Retriever (Native LanceDB/Parquet)")
    parser.add_argument("query", nargs="*", help="The search query")
    parser.add_argument("--full", action="store_true", help="Retrieve full fragments")
    parser.add_argument("--session", help="Filter by specific session ID")
    parser.add_argument("--map", action="store_true", help="Print the knowledge map")
    
    args = parser.parse_args()
    
    if args.map:
        print_knowledge_map()
        sys.exit(0)
        
    query = " ".join(args.query)
    if not query:
        print("[ERROR] No query provided.")
        sys.exit(1)
        
    results = perform_search_internal(query, session_filter=args.session)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
