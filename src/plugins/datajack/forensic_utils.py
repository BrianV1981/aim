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
    def __init__(self, custom_path=None):
        self.db_path = custom_path if custom_path else os.path.join(AIM_ROOT, "archive/engram.db")
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
        
        # Phase 25: Lexical Search (FTS5)
        self.cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS fragments_fts USING fts5(
                content,
                content='fragments',
                content_rowid='id'
            )
        """)
        self.cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS fragments_ai AFTER INSERT ON fragments BEGIN
                INSERT INTO fragments_fts(rowid, content) VALUES (new.id, new.content);
            END;
        """)
        self.cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS fragments_ad AFTER DELETE ON fragments BEGIN
                INSERT INTO fragments_fts(fragments_fts, rowid, content) VALUES('delete', old.id, old.content);
            END;
        """)
        self.cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS fragments_au AFTER UPDATE ON fragments BEGIN
                INSERT INTO fragments_fts(fragments_fts, rowid, content) VALUES('delete', old.id, old.content);
                INSERT INTO fragments_fts(rowid, content) VALUES (new.id, new.content);
            END;
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

    def get_knowledge_map(self):
        """Phase 19: Returns a surgical Index of Keys (documents and session types) available in the DB."""
        # Get count of fragments per session/filename
        query = """
            SELECT s.id, s.filename, COUNT(f.id) as frag_count, MAX(f.type) as primary_type
            FROM sessions s
            JOIN fragments f ON s.id = f.session_id
            GROUP BY s.id, s.filename
            ORDER BY primary_type ASC, s.filename ASC
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        
        knowledge_map = {
            "foundation_knowledge": [],
            "expert_knowledge": [],
            "session_history": []
        }
        
        for row in rows:
            s_id, filename, count, p_type = row
            entry = {"id": s_id, "filename": filename, "fragments": count}
            
            if "foundation" in p_type or s_id.startswith("foundation-"):
                knowledge_map["foundation_knowledge"].append(entry)
            elif "expert" in p_type or s_id.startswith("expert-"):
                knowledge_map["expert_knowledge"].append(entry)
            else:
                knowledge_map["session_history"].append(entry)
                
        return knowledge_map

    def search_by_source_keyword(self, keyword):
        """Phase 17: Fast keyword search across fragment sources (Mandates)."""
        query = """
            SELECT f.id, f.session_id, f.type, f.content, f.timestamp
            FROM fragments f
            JOIN sessions s ON f.session_id = s.id
            WHERE s.filename LIKE ?
        """
        self.cursor.execute(query, (f"%{keyword}%",))
        rows = self.cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "session_id": row[1],
                "type": row[2],
                "content": row[3],
                "timestamp": row[4]
            })
        return results

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

    def search_lexical(self, query_text, top_k=10):
        """Phase 25: Fast exact-match keyword search using FTS5."""
        # Sanitize query for FTS (remove quotes, etc.)
        safe_query = query_text.replace('"', '""')
        
        sql = """
            SELECT f.id, f.type, f.content, f.timestamp, s.filename, bm25(fragments_fts) as score
            FROM fragments_fts fts
            JOIN fragments f ON fts.rowid = f.id
            JOIN sessions s ON f.session_id = s.id
            WHERE fragments_fts MATCH ?
            ORDER BY score
            LIMIT ?
        """
        
        # We negate the bm25 score because smaller is better in SQLite bm25,
        # but we map it to a 0.0 - 1.0 positive scale for hybrid matching.
        # Actually, standard FTS5 BM25 returns a negative value, more negative = better match.
        try:
            self.cursor.execute(sql, (safe_query, top_k))
            rows = self.cursor.fetchall()
            
            results = []
            for row in rows:
                frag_id, frag_type, content, timestamp, filename, bm25_score = row
                
                # Normalize BM25 to a rough 0-1 score to blend with semantic search
                # Extremely rough normalization: -10 is amazing, 0 is bad.
                normalized_score = max(0.0, min(1.0, abs(bm25_score) / 10.0))
                
                results.append({
                    "score": normalized_score,
                    "type": frag_type,
                    "content": content,
                    "timestamp": timestamp,
                    "session_file": filename,
                    "is_lexical": True
                })
            return results
        except sqlite3.OperationalError:
            # FTS might fail on weird characters
            return []

    def rebuild_fts(self):
        """Backfills the FTS virtual table with existing fragments."""
        self.cursor.execute("INSERT INTO fragments_fts(fragments_fts) VALUES('rebuild')")
        self.conn.commit()

    def close(self):
        self.conn.close()

