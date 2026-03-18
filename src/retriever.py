#!/home/kingb/aim/venv/bin/python3
import json
import os
import glob
import math
import sys
import argparse
from forensic_utils import get_embedding

ARCHIVE_INDEX_DIR = "/home/kingb/aim/archive/index"
ARCHIVE_RAW_DIR = "/home/kingb/aim/archive/raw"

def cosine_similarity(v1, v2):
    """Calculates cosine similarity between two vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)

class AIMRetriever:
    def __init__(self):
        self.index_dir = ARCHIVE_INDEX_DIR
        self.raw_dir = ARCHIVE_RAW_DIR

    def get_full_context(self, session_filename, content_fragment, window=2000):
        """
        Attempts to find the fragment in the raw session file and return surrounding context.
        """
        raw_file = os.path.join(self.raw_dir, session_filename.replace(".fragments.json", ".json"))
        if not os.path.exists(raw_file):
            return None
        
        try:
            with open(raw_file, 'r') as f:
                # We read as plain text to find the fragment location easily
                full_text = f.read()
            
            # Find the fragment in the raw JSON text
            # (Note: fragments are slightly processed, so we look for a unique substring)
            search_str = content_fragment[:100] # Use first 100 chars
            idx = full_text.find(search_str)
            
            if idx == -1:
                return "Context not found in raw file (fragment might be processed)."
            
            start = max(0, idx - window)
            end = min(len(full_text), idx + len(content_fragment) + window)
            
            return full_text[start:end]
        except Exception as e:
            return f"Error retrieving context: {e}"

    def search(self, query_text, top_k=10):
        """Searches through indexed fragments for the most relevant matches."""
        query_vector = get_embedding(query_text, task_type='RETRIEVAL_QUERY')
        if not query_vector:
            return []

        results = []
        fragment_files = glob.glob(os.path.join(self.index_dir, "*.fragments.json"))
        
        for file_path in fragment_files:
            try:
                with open(file_path, 'r') as f:
                    fragments = json.load(f)
            except:
                continue
                
            for frag in fragments:
                embedding = frag.get('embedding')
                if not embedding:
                    continue
                
                score = cosine_similarity(query_vector, embedding)
                
                results.append({
                    "score": score,
                    "type": frag.get('type'),
                    "content": frag.get('content'),
                    "timestamp": frag.get('timestamp'),
                    "session_file": os.path.basename(file_path)
                })

        # Sort by score descending and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

def main():
    parser = argparse.ArgumentParser(description="A.I.M. Forensic Retriever")
    parser.add_argument("query", nargs="+", help="The search query")
    parser.add_argument("--top-k", type=int, default=10, help="Number of results to return (default: 10)")
    parser.add_argument("--full", action="store_true", help="Show full content of the match")
    parser.add_argument("--context", type=int, nargs='?', const=2000, help="Show surrounding context (default: 2000 chars)")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    retriever = AIMRetriever()
    matches = retriever.search(query, top_k=args.top_k)

    print(f"\n--- A.I.M. Forensic Search Results for: '{query}' ---")
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
            
    print("\n---------------------------------------------------")

if __name__ == "__main__":
    main()
