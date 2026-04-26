#!/usr/bin/env python3
"""
A.I.M. LongMemEval Benchmark - Cartridge Edition
Uses the pre-embedded longmemeval_s.db cartridge.
"""

import json
import time
from pathlib import Path
import sys
from typing import List, Dict

# Add A.I.M. root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "aim_core"))

from aim_core.plugins.datajack.forensic_utils import ForensicDB, get_embedding

DATA_DIR = Path(__file__).parent / "data"
ORACLE_FILE = DATA_DIR / "longmemeval_oracle.json"
TEST_FILE  = DATA_DIR / "longmemeval_s_cleaned.json"

def load_data():
    oracle = json.loads(ORACLE_FILE.read_text())
    test_data = json.loads(TEST_FILE.read_text())
    return test_data, oracle

def main():
    print("🚀 Starting A.I.M. LongMemEval benchmark (Cartridge Edition)")

    db_path = DATA_DIR / "longmemeval_s.db"
    if not db_path.exists():
        print(f"Error: Cartridge database {db_path.name} not found.")
        print("Please wait for build_cartridge.py to finish embedding.")
        sys.exit(1)

    questions, oracle = load_data()
    db = ForensicDB(custom_path=str(db_path))

    total = len(questions)
    recall5 = 0
    recall10 = 0
    latencies: List[float] = []

    print(f"Evaluating all {total} questions against the pre-embedded cartridge...")
    
    for i, item in enumerate(questions):
        haystack = set(item["haystack_session_ids"])
        
        query = item["question"]
        start = time.perf_counter()

        try:
            query_vec = get_embedding(query, task_type='RETRIEVAL_QUERY')
        except Exception as e:
            print(f"DEBUG QUERY EXCEPTION: {e}")
            query_vec = None
            
        # We query for top 500 to ensure we have enough results to filter down to the specific haystack
        semantic_results = db.search_fragments(query_vec, top_k=500) if query_vec else []
        lexical_results = db.search_lexical(query, top_k=500)
        
        merged = {}
        for r in semantic_results + lexical_results:
            sid_match = r.get('session_id') or r.get('session_file', '').replace('.json', '')
            
            # CRITICAL: Only consider results that are actually in this question's haystack
            if sid_match not in haystack:
                continue
                
            score = r['score']
            if sid_match not in merged or score > merged[sid_match]['score']:
                merged[sid_match] = r
                
        results = sorted(merged.values(), key=lambda x: x['score'], reverse=True)

        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)

        correct_ids = item.get("answer_session_ids", [])
        if not correct_ids and "ground_truth_session_id" in item:
            correct_ids = [item["ground_truth_session_id"]]
            
        top5_ids = [r.get("session_id") or r.get('session_file', '').replace('.json', '') for r in results[:5]]
        top10_ids = [r.get("session_id") or r.get('session_file', '').replace('.json', '') for r in results[:10]]

        if any(cid in top5_ids for cid in correct_ids):
            recall5 += 1
        if any(cid in top10_ids for cid in correct_ids):
            recall10 += 1

        print(f"Progress: {i+1}/{total} | Latency: {latency:.1f}ms", end="\r")

    r5 = (recall5 / total) * 100 if total > 0 else 0
    r10 = (recall10 / total) * 100 if total > 0 else 0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    print("\n" + "="*70)
    print("A.I.M. LONGMEMEVAL RESULTS (cleaned S dataset)")
    print("="*70)
    print(f"Recall @5     : {r5:.2f}%")
    print(f"Recall @10    : {r10:.2f}%")
    print(f"Avg Latency   : {avg_latency:.1f} ms")
    print(f"Total sessions: {total}")
    print("="*70)

if __name__ == "__main__":
    main()