#!/usr/bin/env python3
import sys, json
from retriever import perform_forensic_search

try:
    args_json = sys.argv[1] if len(sys.argv) > 1 else "{}"
    args = json.loads(args_json)
    query = args.get("query", "latest changes")
    results = perform_forensic_search(query, top_k=10)
    print(json.dumps({"results": results}, indent=2))
except Exception as e:
    print(json.dumps({"error": str(e)}))