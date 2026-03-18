#!/home/kingb/aim/venv/bin/python3
import json
import os
import glob
import math
import sys
import keyring
from google import genai

# --- CONFIGURATION ---
# Retrieve API key from local keyring
API_KEY = keyring.get_password("aim-system", "google-api-key")
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    print("ERROR: GOOGLE_API_KEY not found in keyring. Run scripts/set_key.py first.", file=sys.stderr)
    sys.exit(1)

ARCHIVE_INDEX_DIR = "/home/kingb/aim/archive/index"
MODEL = "models/gemini-embedding-2-preview"

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
    def __init__(self, client):
        self.client = client
        self.index_dir = ARCHIVE_INDEX_DIR

    def get_query_embedding(self, text):
        """Calls Google GenAI SDK for the search query embedding."""
        try:
            result = self.client.models.embed_content(
                model=MODEL,
                contents=text,
                config={
                    'task_type': 'RETRIEVAL_QUERY'
                }
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"Error calling Google Embedding API: {e}", file=sys.stderr)
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
    if not client:
        print("ERROR: GOOGLE_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: ./retriever.py <query_text>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    retriever = AIMRetriever(client)
    matches = retriever.search(query)

    print(f"\n--- A.I.M. Forensic Search Results (Sovereign SDK) for: '{query}' ---")
    for i, match in enumerate(matches):
        print(f"\n[{i+1}] Score: {match['score']:.4f} | Type: {match['type']}")
        print(f"Session: {match['session_file']}")
        print(f"Content: {match['content'][:300]}...")
    print("\n---------------------------------------------------")

if __name__ == "__main__":
    main()
