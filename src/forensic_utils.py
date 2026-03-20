import os
import json
import keyring
import requests
import sys
import sqlite3
import struct
import math
from google import genai

# --- CONFIGURATION (Dynamic Load) ---
from config_utils import CONFIG, AIM_ROOT
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

# --- PROVIDER LOGIC ---
PROVIDER_TYPE = CONFIG['models'].get('embedding_provider', 'local') # google, local (ollama), openai-compat
PROVIDER_MODEL = CONFIG['models'].get('embedding', 'nomic-embed-text')
PROVIDER_ENDPOINT = CONFIG['models'].get('embedding_endpoint', 'http://localhost:11434/api/embeddings')

def get_embedding(text, task_type='RETRIEVAL_DOCUMENT'):
    """
    Unified entry point for embeddings. Supports:
    - google: Gemini API
    - local: Ollama Native API
    - openai-compat: Standard OpenAI Embedding API (LocalAI, vLLM, OpenAI)
    """
    if not text: return None
    
    # 1. GOOGLE PROVIDER
    if PROVIDER_TYPE == 'google':
        api_key = keyring.get_password("aim-system", "google-api-key")
        if not api_key:
            sys.stderr.write("Error: Google API Key not found in keyring.\n")
            return None
        try:
            client = genai.Client(api_key=api_key)
            result = client.models.embed_content(
                model=PROVIDER_MODEL,
                contents=text,
                config={'task_type': task_type}
            )
            return result.embeddings[0].values
        except Exception as e:
            sys.stderr.write(f"Google Embedding Error: {e}\n")
            return None

    # 2. OLLAMA PROVIDER (Native)
    elif PROVIDER_TYPE == 'local':
        try:
            payload = { "model": PROVIDER_MODEL, "prompt": text }
            response = requests.post(PROVIDER_ENDPOINT, json=payload, timeout=15)
            response.raise_for_status()
            return response.json().get('embedding')
        except Exception as e:
            sys.stderr.write(f"Ollama Embedding Error: {e}\n")
            return None

    # 3. OPENAI-COMPATIBLE PROVIDER
    elif PROVIDER_TYPE == 'openai-compat':
        api_key = keyring.get_password("aim-system", "embedding-api-key") or ""
        try:
            # Note: Standard OpenAI format is /v1/embeddings
            url = PROVIDER_ENDPOINT if "/embeddings" in PROVIDER_ENDPOINT else f"{PROVIDER_ENDPOINT.rstrip('/')}/v1/embeddings"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = { "model": PROVIDER_MODEL, "input": text }
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            # OpenAI format: data[0].embedding
            return response.json()['data'][0]['embedding']
        except Exception as e:
            sys.stderr.write(f"OpenAI-Compat Embedding Error: {e}\n")
            return None
    
    return None

def cosine_similarity(v1, v2):
    if not v1 or not v2 or len(v1) != len(v2): return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    if magnitude1 == 0 or magnitude2 == 0: return 0.0
    return dot_product / (magnitude1 * magnitude2)

def chunk_text(text, max_chars=2000, overlap=200):
    """
    Splits long text into overlapping chunks to stay within embedding model limits.
    """
    if not text or len(text) <= max_chars:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start += (max_chars - overlap)
    return chunks

class ForensicDB:
    def __init__(self):
        self.db_path = os.path.join(AIM_ROOT, "archive/engram.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._initialize_schema()

    def _initialize_schema(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                mtime REAL NOT NULL,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS fragments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT,
                embedding BLOB,
                metadata TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def _vec_to_blob(self, vec):
        if not vec: return None
        return struct.pack(f'{len(vec)}f', *vec)

    def _blob_to_vec(self, blob):
        if not blob: return None
        n = len(blob) // 4
        return list(struct.unpack(f'{n}f', blob))

    def add_session(self, session_id, filename, mtime):
        self.cursor.execute(
            "INSERT OR REPLACE INTO sessions (id, filename, mtime) VALUES (?, ?, ?)",
            (session_id, filename, mtime)
        )
        self.conn.commit()

    def add_fragments(self, session_id, fragments):
        # Clear existing fragments for this session if re-indexing
        self.cursor.execute("DELETE FROM fragments WHERE session_id = ?", (session_id,))
        
        for frag in fragments:
            embedding_blob = self._vec_to_blob(frag.get('embedding'))
            metadata = json.dumps(frag.get('metadata', {}))
            self.cursor.execute(
                "INSERT INTO fragments (session_id, type, content, timestamp, embedding, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, frag['type'], frag['content'], frag.get('timestamp'), embedding_blob, metadata)
            )
        self.conn.commit()

    def get_session_mtime(self, session_id):
        self.cursor.execute("SELECT mtime FROM sessions WHERE id = ?", (session_id,))
        res = self.cursor.fetchone()
        return res[0] if res else 0

    def search_fragments(self, query_vector, top_k=10, session_filter=None):
        sql = "SELECT f.type, f.content, f.timestamp, f.embedding, s.filename FROM fragments f JOIN sessions s ON f.session_id = s.id"
        params = []
        if session_filter:
            sql += " WHERE f.session_id = ?"
            params.append(session_filter)
        
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        
        results = []
        for row in rows:
            frag_type, content, timestamp, embedding_blob, filename = row
            embedding = self._blob_to_vec(embedding_blob)
            score = cosine_similarity(query_vector, embedding)
            results.append({
                "score": score,
                "type": frag_type,
                "content": content,
                "timestamp": timestamp,
                "session_file": filename
            })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def close(self):
        self.conn.close()
