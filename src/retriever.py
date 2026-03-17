#!/usr/bin/env python3
import json
import os
import glob
import math
import requests
import sys

# --- CONFIGURATION ---
ARCHIVE_INDEX_DIR = "/home/kingb/aim/archive/index"
OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"

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

    def get_query_embedding(self, text):
        """Calls Ollama to get the embedding for the search query."""
        try:
            response = requests.post(OLLAMA_URL, json={
                "model": MODEL,
                "prompt": text
            })
            return response.json().get('embedding')
        except Exception as e:
            print(f"Error calling Ollama: {e}", file=sys.stderr)
            return None

    def search(self, query_text, top_k=5):
        """Searches through indexed fragments for the most relevant matches."""
        query_vector = self.get_query_embedding(query_text)
        if not query_vector:
            return []

        results = []
        fragment_files = glob.glob(os.path.join(self.index_dir, "*.fragments.json"))
        
        for file_path in fragment_files:
            with open(file_path, 'r') as f:
                fragments = json.load(f)
                
            for frag in fragments:
                embedding = frag.get('embedding')
                if not embedding:
                    continue
                
                score = cosine_similarity(query_vector, embedding)
                
                # We store a reference to the fragment and its score
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
    if len(sys.argv) < 2:
        print("Usage: ./retriever.py <query_text>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    retriever = AIMRetriever()
    matches = retriever.search(query)

    print(f"\n--- A.I.M. Forensic Search Results for: '{query}' ---")
    for i, match in enumerate(matches):
        print(f"\n[{i+1}] Score: {match['score']:.4f} | Type: {match['type']}")
        print(f"Session: {match['session_file']}")
        print(f"Content: {match['content'][:300]}...")
    print("\n---------------------------------------------------")

if __name__ == "__main__":
    main()
