#!/home/kingb/aim/venv/bin/python3
import json
import os
import glob
import math
import sys
import argparse
from forensic_utils import get_embedding

ARCHIVE_INDEX_DIR = "/home/kingb/aim/archive/index"

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

    def search(self, query_text, top_k=5):
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
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--full", action="store_true", help="Show full content instead of snippet")
    
    # If called via aim_cli, the args might be different, but let's support direct use
    args = parser.parse_args()
    query = " ".join(args.query)
    
    retriever = AIMRetriever()
    matches = retriever.search(query, top_k=args.top_k)

    print(f"\n--- A.I.M. Forensic Search Results for: '{query}' ---")
    for i, match in enumerate(matches):
        print(f"\n[{i+1}] Score: {match['score']:.4f} | Type: {match['type']}")
        print(f"Session: {match['session_file']}")
        
        content = match['content']
        if not args.full and len(content) > 300:
            content = content[:300] + "..."
            
        print(f"Content: {content}")
    print("\n---------------------------------------------------")

if __name__ == "__main__":
    main()
