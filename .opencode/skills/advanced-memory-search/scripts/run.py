#!/usr/bin/env python3
import sys, json, os
from pathlib import Path

aim_root = Path(__file__).parent.parent
sys.path.append(str(aim_root / "src"))

from plugins.datajack.forensic_utils import ForensicDB, get_embedding

try:
    args_json = sys.argv[1] if len(sys.argv) > 1 else "{}"
    args = json.loads(args_json)
    query = args.get("query", "latest changes")
    top_k = int(args.get("top_k", 10))
    
    db = ForensicDB()
    
    query_vec = get_embedding(query, task_type='RETRIEVAL_QUERY')
    semantic_results = []
    if query_vec:
        semantic_results = db.search_fragments(query_vec, top_k=top_k)
    lexical_results = db.search_lexical(query, top_k=top_k)
    db.close()
    
    # Simple merge
    all_results = semantic_results + lexical_results
    
    print(json.dumps({"results": all_results}, indent=2))
except Exception as e:
    print(json.dumps({"error": str(e)}))
