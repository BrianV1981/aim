import os
import json
import sqlite3
import struct
import math

from config_utils import AIM_ROOT
try:
    from aim_core.plugins.datajack.forensic_utils import get_embedding, chunk_text, summarize_massive_turn, cosine_similarity
except ModuleNotFoundError:
    from plugins.datajack.forensic_utils import get_embedding, chunk_text, summarize_massive_turn, cosine_similarity

class ForensicDB:
    def __init__(self, custom_path=None):
        self.db_path = custom_path if custom_path else os.path.join(AIM_ROOT, "archive/project_core.db")
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
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
                parent_id INTEGER,
                FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                FOREIGN KEY(parent_id) REFERENCES fragments(id) ON DELETE CASCADE
            )
        """)
        
        # Ensure parent_id exists for older databases
        try:
            self.cursor.execute("ALTER TABLE fragments ADD COLUMN parent_id INTEGER REFERENCES fragments(id) ON DELETE CASCADE")
        except sqlite3.OperationalError:
            pass # Column already exists
        
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
        
        id_map = {}
        
        # Pass 1: Parents (parent_id is null)
        for frag in fragments:
            if frag.get('parent_id') is not None:
                continue
            embedding_blob = self._vec_to_blob(frag.get('embedding'))
            metadata = json.dumps(frag.get('metadata', {}))
            self.cursor.execute(
                "INSERT INTO fragments (session_id, type, content, timestamp, embedding, metadata, parent_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (session_id, frag['type'], frag['content'], frag.get('timestamp'), embedding_blob, metadata, None)
            )
            if frag.get('original_id') is not None:
                id_map[frag['original_id']] = self.cursor.lastrowid
                
        # Pass 2: Children
        for frag in fragments:
            if frag.get('parent_id') is None:
                continue
            embedding_blob = self._vec_to_blob(frag.get('embedding'))
            metadata = json.dumps(frag.get('metadata', {}))
            new_parent_id = id_map.get(frag.get('parent_id'))
            
            self.cursor.execute(
                "INSERT INTO fragments (session_id, type, content, timestamp, embedding, metadata, parent_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (session_id, frag['type'], frag['content'], frag.get('timestamp'), embedding_blob, metadata, new_parent_id)
            )
        
        self.conn.commit()

    
    def ingest_document(self, session_id, text, record_type='session_history', filename=None, mtime=None, context_header=None):
        import time
        import re
        if filename and mtime is not None:
            self.add_session(session_id, filename, mtime)
            
        # RAG 4.0 Pre-Ingestion Cleaning: Strip Internal Monologues
        text = re.sub(r'> \*\*Internal Monologue:\*\*\n(?:> \* .*\n)*', '', text)
            
        # Regex to split by the start of a turn or session header
        raw_chunks = re.split(r'\n(?=\[.*?\] \*\*.*?\*\*|\[.*?\] \*\[Visual Description|\#\# Session|\# |\#\# 👤|\#\# 🤖)', '\n' + text)
        final_turns = [t.strip() for t in raw_chunks if t.strip()]
        
        all_fragments = []
        for i, turn_text in enumerate(final_turns):
            if len(turn_text) > 2000:
                parent_id_str = f"parent_{session_id}_{i}"
                
                # Parent: Raw Text (no embedding)
                all_fragments.append({
                    'original_id': parent_id_str,
                    'type': record_type,
                    'content': turn_text,
                    'embedding': None
                })
                
                # Child 1: Semantic Anchor (Summary)
                summary_anchor = summarize_massive_turn(turn_text)
                summary_embed_text = f"{context_header}\n{summary_anchor}" if context_header else summary_anchor
                try:
                    vec = get_embedding(summary_embed_text, task_type='RETRIEVAL_DOCUMENT')
                except Exception:
                    vec = None
                    
                all_fragments.append({
                    'parent_id': parent_id_str,
                    'type': record_type,
                    'content': f"[OVERARCHING SUMMARY] {summary_anchor}",
                    'embedding': vec
                })
                
                # Child 2+: Overlapping chunks
                start = 0
                max_chars = 500
                overlap = 50
                while start < len(turn_text):
                    end = start + max_chars
                    chunk_text = turn_text[start:end]
                    start += (max_chars - overlap)
                    embed_text = f"{context_header}\n{chunk_text}" if context_header else chunk_text
                    try:
                        vec = get_embedding(embed_text, task_type='RETRIEVAL_DOCUMENT')
                    except Exception:
                        vec = None
                    all_fragments.append({
                        'parent_id': parent_id_str,
                        'type': record_type,
                        'content': chunk_text,
                        'embedding': vec
                    })
            else:
                embed_text = f"{context_header}\n{turn_text}" if context_header else turn_text
                try:
                    vec = get_embedding(embed_text, task_type='RETRIEVAL_DOCUMENT')
                except Exception:
                    vec = None
                    
                all_fragments.append({
                    'type': record_type,
                    'content': turn_text,
                    'embedding': vec
                })
                
        if all_fragments:
            self.add_fragments(session_id, all_fragments)
            self.conn.commit()
        return len(all_fragments)

    def _expand_and_deduplicate(self, top_hits, is_lexical=False):
        final_results = []
        seen_ids = set()
        for hit in top_hits:
            score = hit[0]
            row = hit[1]
            frag_id, sess_id, frag_type, content, timestamp, emb_blob, filename, parent_id = row
            if frag_id in seen_ids:
                continue
            if parent_id is not None:
                seen_ids.add(frag_id)
                final_results.append({"score": score, "type": frag_type, "content": content, "timestamp": timestamp, "session_file": filename, "is_lexical": is_lexical})
            else:
                self.cursor.execute("""
                    SELECT id, content, parent_id 
                    FROM fragments 
                    WHERE session_id = ? AND id BETWEEN ? AND ? 
                    ORDER BY id ASC
                """, (sess_id, frag_id - 2, frag_id + 2))
                context_rows = self.cursor.fetchall()
                block_content = []
                for cr in context_rows:
                    c_id, c_content, c_parent_id = cr
                    seen_ids.add(c_id)
                    if c_parent_id is not None:
                        continue
                    if len(c_content) > 2000 and c_id != frag_id:
                        block_content.append(c_content[:300] + "\n... [MASSIVE TEXT BLOCK OMITTED TO PRESERVE CONTEXT LIMIT] ...\n" + c_content[-300:])
                    else:
                        block_content.append(c_content)
                merged_content = "\n\n---\n\n".join(block_content)
                final_results.append({"score": score, "type": frag_type, "content": merged_content, "timestamp": timestamp, "session_file": filename, "is_lexical": is_lexical})
        return final_results

    def get_session_mtime(self, session_id):
        self.cursor.execute("SELECT mtime FROM sessions WHERE id = ?", (session_id,))
        res = self.cursor.fetchone()
        return float(res[0]) if res else 0.0

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
        
        hit_scores = []
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
        sql = """
            SELECT f.id, f.session_id, f.type, f.content, f.timestamp, f.embedding, s.filename, f.parent_id 
            FROM fragments f 
            JOIN sessions s ON f.session_id = s.id
        """
        params = []
        if session_filter:
            sql += " WHERE f.session_id = ?"
            params.append(session_filter)
        
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        
        hit_scores = []
        for row in rows:
            frag_id, sess_id, frag_type, content, timestamp, emb_blob, filename, parent_id = row
            embedding = self._blob_to_vec(emb_blob)
            score = cosine_similarity(query_vector, embedding)
            hit_scores.append((score, row))
        
        hit_scores.sort(key=lambda x: x[0], reverse=True)
        return self._expand_and_deduplicate(hit_scores[:top_k], is_lexical=False)

    def search_lexical(self, query_text, top_k=10):
        """Phase 25: Fast exact-match keyword search using FTS5."""
        import re
        # Sanitize query for FTS (remove punctuation that breaks FTS5)
        safe_query = re.sub(r'[^\w\s\(\)]', ' ', query_text) # Preserve parentheses for FTS5 boolean logic

        # Implement FTS5 Fuzzy Matcher (Append * to alphabetic words, ignoring operators and stopwords)
        stopwords = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "which's", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"}
        
        tokens = safe_query.split()
        fuzzy_tokens = []
        for t in tokens:
            if t.upper() in ["AND", "OR", "NOT"]:
                fuzzy_tokens.append(t)
            elif t.lower() in stopwords:
                continue
            else:
                prefix = ""
                suffix = ""
                core = t
                while core.startswith("("):
                    prefix += "("
                    core = core[1:]
                while core.endswith(")"):
                    suffix += ")"
                    core = core[:-1]
                
                if re.match(r'^[A-Za-z0-9_]+$', core):
                    fuzzy_tokens.append(f"{prefix}{core}*{suffix}")
                else:
                    fuzzy_tokens.append(t)

        fuzzy_query = " ".join(fuzzy_tokens)
        if not fuzzy_query.strip():
            return [] # If query was only stopwords

        sql = """
            SELECT f.id, f.type, f.content, p.content, f.timestamp, s.filename, bm25(fragments_fts) as score
            FROM fragments_fts fts
            JOIN fragments f ON fts.rowid = f.id
            JOIN sessions s ON f.session_id = s.id
            LEFT JOIN fragments p ON f.parent_id = p.id
            WHERE fragments_fts MATCH ?
            ORDER BY score
            LIMIT ?
        """

        # We negate the bm25 score because smaller is better in SQLite bm25,
        # but we map it to a 0.0 - 1.0 positive scale for hybrid matching.
        # Actually, standard FTS5 BM25 returns a negative value, more negative = better match.
        try:
            self.cursor.execute(sql, (fuzzy_query, top_k))
            rows = self.cursor.fetchall()            
            results = []
            for row in rows:
                frag_id, frag_type, child_content, parent_content, timestamp, filename, bm25_score = row
                
                if parent_content and child_content in parent_content:
                    idx = parent_content.find(child_content)
                    start = max(0, idx - 2000)
                    end = min(len(parent_content), idx + len(child_content) + 2000)
                    final_content = parent_content[start:end]
                    if start > 0: final_content = "..." + final_content
                    if end < len(parent_content): final_content = final_content + "..."
                else:
                    final_content = parent_content if parent_content else child_content
                
                # Normalize BM25 to a rough 0-1 score to blend with semantic search
                # Extremely rough normalization: -10 is amazing, 0 is bad.
                normalized_score = max(0.0, min(1.0, abs(bm25_score) / 10.0))
                
                results.append({
                    "score": normalized_score,
                    "type": frag_type,
                    "content": final_content,
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

