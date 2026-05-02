import os
import sqlite3
import struct
import lancedb
import pyarrow as pa
import pandas as pd
from lancedb.rerankers import Reranker
import re

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANCE_DB_PATH = os.path.join(AIM_ROOT, "memory_lance")

def blob_to_vec(blob):
    if not blob: return None
    n = len(blob) // 4
    return list(struct.unpack(f'{n}f', blob))

def generate_tantivy_query(query):
    stopwords = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", "should", "so", "some", "such", "t", "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "would", "you", "your", "yours", "yourself", "yourselves"}
    
    tokens = re.findall(r"\b[A-Za-z]+\b|\(|\)", query)
    processed = []
    has_proper_noun = False
    
    for t in tokens:
        if t in ("(", ")"):
            processed.append(t)
            continue
        if t.upper() in ("AND", "OR"):
            processed.append(t.upper())
            continue
        if t.lower() in stopwords or len(t) <= 1:
            continue
            
        if t[0].isupper():
            has_proper_noun = True
            
        processed.append(t.lower() + "*")
        
    fts_query = " ".join(processed)
    
    # Cleanup dangling operators
    fts_query = re.sub(r'\(\s*(AND|OR)\b', '(', fts_query)
    fts_query = re.sub(r'\b(AND|OR)\s*\)', ')', fts_query)
    fts_query = re.sub(r'\b(AND|OR)\s+(AND|OR)\b', r'\1', fts_query)
    fts_query = re.sub(r'^\s*(AND|OR)\b', '', fts_query)
    fts_query = re.sub(r'\b(AND|OR)\s*$', '', fts_query)
    
    return fts_query.strip(), has_proper_noun


class EntityIntersectionReranker(Reranker):
    def __init__(self, enforce_intersection=False):
        super().__init__()
        self.enforce_intersection = enforce_intersection

    def rerank_hybrid(self, query: str, vector_results: pa.Table, fts_results: pa.Table) -> pa.Table:
        vec_df = vector_results.to_pandas() if vector_results.num_rows > 0 else pd.DataFrame()
        fts_df = fts_results.to_pandas() if fts_results.num_rows > 0 else pd.DataFrame()
        
        scores = {}
        fts_ids = set()
        k = 60
        
        if not fts_df.empty:
            for rank, row in fts_df.iterrows():
                idx = f"{row['sqlite_id']}_{row['session_id']}"
                fts_ids.add(idx)
                scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)
                
        if not vec_df.empty:
            for rank, row in vec_df.iterrows():
                idx = f"{row['sqlite_id']}_{row['session_id']}"
                if self.enforce_intersection and idx not in fts_ids:
                    continue # Ruthless deletion
                scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)
                
        if vec_df.empty and fts_df.empty:
            return vector_results
            
        combined_df = pd.concat([vec_df, fts_df]).drop_duplicates(subset=['sqlite_id', 'session_id'])
        combined_df['_uid'] = combined_df['sqlite_id'].astype(str) + "_" + combined_df['session_id'].astype(str)
        
        combined_df = combined_df[combined_df['_uid'].isin(scores.keys())].copy()
        combined_df['_relevance_score'] = combined_df['_uid'].map(scores)
        combined_df.sort_values('_relevance_score', ascending=False, inplace=True)
        
        combined_df['score'] = combined_df['_relevance_score']
        
        if combined_df.empty:
            return pa.Table.from_pandas(combined_df)
            
        return pa.Table.from_pandas(combined_df)


class VectorBackend:
    def __init__(self, path=LANCE_DB_PATH):
        self.path = path
        self.db = lancedb.connect(self.path)
        self.table_name = "fragments"
        
    def ensure_table(self):
        if self.table_name not in self.db.list_tables():
            schema = pa.schema([
                pa.field("sqlite_id", pa.int64()),
                pa.field("session_id", pa.string()),
                pa.field("type", pa.string()),
                pa.field("content", pa.string()),
                pa.field("timestamp", pa.string()),
                pa.field("metadata", pa.string()),
                pa.field("parent_id", pa.int64()),
                pa.field("source_db", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), 768))
            ])
            self.db.create_table(self.table_name, schema=schema)
            
    def get_table(self):
        self.ensure_table()
        return self.db.open_table(self.table_name)
        
    def migrate_from_sqlite(self):
        print(f"[*] Migrating SQLite databases to LanceDB ({self.path})...")
        from aim_core.retriever import get_federated_dbs
        from aim_core.plugins.datajack.forensic_utils import ForensicDB
        
        table = self.get_table()
        
        if table.count_rows() > 0:
            print("[*] LanceDB table already populated. Skipping migration.")
            return

        records = []
        for db_path in get_federated_dbs():
            if not os.path.exists(db_path): continue
            try:
                db = ForensicDB(db_path)
                db.cursor.execute("SELECT id, session_id, type, content, timestamp, embedding, metadata, parent_id FROM fragments")
                rows = db.cursor.fetchall()
                for row in rows:
                    vec = blob_to_vec(row[5])
                    if vec is None or len(vec) != 768:
                        continue 
                    
                    records.append({
                        "sqlite_id": row[0] or 0,
                        "session_id": row[1] or "",
                        "type": row[2] or "",
                        "content": row[3] or "",
                        "timestamp": row[4] or "",
                        "metadata": row[6] or "",
                        "parent_id": row[7] or 0,
                        "source_db": os.path.basename(db_path),
                        "vector": vec
                    })
                db.close()
            except Exception as e:
                print(f"[!] Error migrating {db_path}: {e}")
            
        if records:
            table.add(records)
            table.create_fts_index("content", replace=True)
            print(f"[SUCCESS] Migrated {len(records)} fragments to LanceDB and built Tantivy FTS index.")
        else:
            print("[*] No fragments with valid vectors found for migration.")

    def search(self, query_vec, original_query, top_k=10, session_filter=None):
        table = self.get_table()
        
        fts_query, has_proper_noun = generate_tantivy_query(original_query)
        reranker = EntityIntersectionReranker(enforce_intersection=has_proper_noun)
        
        q = table.search(query_type="hybrid").rerank(reranker)
        if query_vec is not None:
            q = q.vector(query_vec)
        if fts_query:
            q = q.text(fts_query)
        if session_filter:
            q = q.where(f"session_id = '{session_filter}'")
            
        results = q.limit(max(100, top_k * 2)).to_list()
        
        # Format results to match what retriever expects
        formatted_results = []
        for r in results:
            formatted_results.append({
                "id": r["sqlite_id"],
                "session_id": r["session_id"],
                "type": r["type"],
                "content": r["content"],
                "timestamp": r["timestamp"],
                "metadata": r["metadata"],
                "parent_id": r["parent_id"],
                "score": r.get("score", 0),
                "filename": r.get("source_db", "")
            })
        return formatted_results
