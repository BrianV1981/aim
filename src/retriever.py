#!/usr/bin/env python3
import json
import os
import glob
import math
import sys
import argparse
from forensic_utils import get_embedding, ForensicDB, AIM_ROOT

ARCHIVE_INDEX_DIR = os.path.join(AIM_ROOT, "archive/index")
ARCHIVE_RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")

class AIMRetriever:
    def __init__(self):
        self.index_dir = ARCHIVE_INDEX_DIR
        self.raw_dir = ARCHIVE_RAW_DIR
        self.db = ForensicDB()

    def get_full_context(self, session_filename, content_fragment, window=2000):
        """
        Attempts to find the fragment in the raw session file and return surrounding context.
        """
        raw_file = os.path.join(self.raw_dir, session_filename)
        if not os.path.exists(raw_file):
            return None
        
        try:
            with open(raw_file, 'r') as f:
                full_text = f.read()
            
            search_str = content_fragment[:100] # Use first 100 chars
            idx = full_text.find(search_str)
            
            if idx == -1:
                return "Context not found in raw file (fragment might be processed)."
            
            start = max(0, idx - window)
            end = min(len(full_text), idx + len(content_fragment) + window)
            
            return full_text[start:end]
        except Exception as e:
            return f"Error retrieving context: {e}"

    def search(self, query_text, top_k=10, session_filter=None):
        """Searches through indexed fragments for the most relevant matches using SQLite."""
        query_vector = get_embedding(query_text, task_type='RETRIEVAL_QUERY')
        if not query_vector:
            return []

        return self.db.search_fragments(query_vector, top_k=top_k, session_filter=session_filter)

def main():
    parser = argparse.ArgumentParser(description="A.I.M. Forensic Retriever")
    parser.add_argument("query", nargs="+", help="The search query")
    parser.add_argument("--top-k", type=int, default=10, help="Number of results to return (default: 10)")
    parser.add_argument("--full", action="store_true", help="Show full content of the match")
    parser.add_argument("--context", type=int, nargs='?', const=2000, help="Show surrounding context (default: 2000 chars)")
    parser.add_argument("--session", type=str, help="Filter results to a specific Session ID")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    retriever = AIMRetriever()
    matches = retriever.search(query, top_k=args.top_k, session_filter=args.session)

    print(f"\n--- A.I.M. Forensic Search Results for: '{query}' ---")
    if args.session:
        print(f"Filter: Session ID '{args.session}'")

    for i, match in enumerate(matches):
        print(f"\n[{i+1}] Score: {match['score']:.4f} | Type: {match['type']}")
        print(f"Session: {match['session_file']}")
        
        if args.context:
            print(f"--- Context (Window: {args.context}) ---")
            context = retriever.get_full_context(match['session_file'], match['content'], window=args.context)
            print(context if context else "Raw file not found.")
            print("---------------------------------------")
        else:
            content = match['content']
            if not args.full and len(content) > 300:
                content = content[:300] + "..."
            print(f"Content: {content}")
            
    if not matches:
        print("No matches found.")
    print("\n---------------------------------------------------")
    
    retriever.db.close()

if __name__ == "__main__":
    main()
