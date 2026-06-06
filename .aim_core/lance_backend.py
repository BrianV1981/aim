import os
import sqlite3
import struct
import lancedb
import pyarrow as pa
import pandas as pd
from lancedb.rerankers import Reranker
import re

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANCE_DB_PATH = os.path.join(AIM_ROOT, "memory/lance")

def blob_to_vec(blob):
    if not blob: return None
    n = len(blob) // 4
    return list(struct.unpack(f'{n}f', blob))

def generate_tantivy_query(query):
    stopwords = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", "should", "so", "some", "such", "t", "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "would", "you", "your", "yours", "yourself", "yourselves"}
    
    tokens = re.findall(r"\b[A-Za-z]+\b|\(|\)", query)
    processed = []
    proper_nouns = []
    
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
            proper_nouns.append(t)
            processed.append("+" + t.lower() + "*") # STRICT INCLUSION
        else:
            processed.append(t.lower() + "*")
        
    fts_query = " ".join(processed)
    
    # Cleanup dangling operators
    fts_query = re.sub(r'\(\s*(AND|OR)\b', '(', fts_query)
    fts_query = re.sub(r'\b(AND|OR)\s*\)', ')', fts_query)
    fts_query = re.sub(r'\b(AND|OR)\s+(AND|OR)\b', r'\1', fts_query)
    fts_query = re.sub(r'^\s*(AND|OR)\b', '', fts_query)
    fts_query = re.sub(r'\b(AND|OR)\s*$', '', fts_query)
    
    return fts_query.strip(), proper_nouns


class EntityIntersectionReranker(Reranker):
    def __init__(self, proper_nouns=None):
        super().__init__()
        self.proper_nouns = proper_nouns or []

    def rerank_hybrid(self, query: str, vector_results: pa.Table, fts_results: pa.Table) -> pa.Table:
        vec_df = vector_results.to_pandas() if vector_results.num_rows > 0 else pd.DataFrame()
        fts_df = fts_results.to_pandas() if fts_results.num_rows > 0 else pd.DataFrame()
        
        scores = {}
        fts_ids = set()
        k = 60
        
        if not fts_df.empty:
            for rank, row in fts_df.iterrows():
                idx = f"{row['fragment_id']}_{row['session_id']}"
                fts_ids.add(idx)
                scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)
                
        if not vec_df.empty:
            for rank, row in vec_df.iterrows():
                idx = f"{row['fragment_id']}_{row['session_id']}"
                scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)
                
        if vec_df.empty and fts_df.empty:
            return vector_results
            
        combined_df = pd.concat([vec_df, fts_df]).drop_duplicates(subset=['fragment_id', 'session_id'])
        combined_df['_uid'] = combined_df['fragment_id'].astype(str) + "_" + combined_df['session_id'].astype(str)
        
        combined_df = combined_df[combined_df['_uid'].isin(scores.keys())].copy()
        
        combined_df['_relevance_score'] = combined_df['_uid'].map(scores)

        if self.proper_nouns:
            def _boost(row):
                content = str(row.get('content', '')).lower()
                if any(pn.lower() in content for pn in self.proper_nouns):
                    return row['_relevance_score'] * 1.5
                return row['_relevance_score']
            combined_df['_relevance_score'] = combined_df.apply(_boost, axis=1)

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
        if self.table_name not in self.db.table_names():
            schema = pa.schema([
                pa.field("fragment_id", pa.int64()),
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
        
    def add_fragments(self, fragments):
        table = self.get_table()
        current_id = table.count_rows() + 1
        
        from datetime import datetime
        records = []
        for frag in fragments:
            if 'vector' not in frag or not frag['vector'] or len(frag['vector']) != 768:
                continue
                
            records.append({
                "fragment_id": frag.get("fragment_id", current_id),
                "session_id": frag.get("session_id", ""),
                "type": frag.get("type", "session_history"),
                "content": frag.get("content", ""),
                "timestamp": frag.get("timestamp", datetime.utcnow().isoformat() + "Z"),
                "metadata": frag.get("metadata", "{}"),
                "parent_id": frag.get("parent_id", None),
                "source_db": frag.get("source_db", "live_session"),
                "vector": frag['vector']
            })
            current_id += 1
            
        if records:
            table.add(records)
            table.create_fts_index("content", replace=True)
            print(f"[SUCCESS] Added {len(records)} fragments to LanceDB RAM and rebuilt FTS index.")

    def search(self, query_vec, original_query, top_k=10, session_filter=None):
        table = self.get_table()
        
        fts_query, proper_nouns = generate_tantivy_query(original_query)
        reranker = EntityIntersectionReranker(proper_nouns=proper_nouns)
        
        def execute_query(t):
            if query_vec is not None:
                q = t.search(query_type="hybrid").rerank(reranker)
                q = q.vector(query_vec)
                if fts_query:
                    q = q.text(fts_query)
            else:
                if not fts_query:
                    return []
                q = t.search(fts_query, query_type="fts")
            if session_filter:
                q = q.where(f"session_id = '{session_filter}'")
            return q.limit(max(100, top_k * 2)).to_list()
            
        results = execute_query(table)
        
        # Federated Querying against Parquet ROMs
        cartridges_dir = os.path.join(AIM_ROOT, ".archive", "cartridges")
        if os.path.exists(cartridges_dir):
            import pyarrow.dataset as ds
            import glob
            mem_db = lancedb.connect("memory://")
            for parquet_file in glob.glob(os.path.join(cartridges_dir, "*.parquet")):
                try:
                    table_name = os.path.basename(parquet_file)
                    if table_name not in mem_db.table_names():
                        dataset = ds.dataset(parquet_file)
                        t = mem_db.create_table(table_name, data=dataset)
                        try:
                            t.create_fts_index("content", replace=True)
                        except:
                            pass # If FTS index creation fails on dataset, skip
                    else:
                        t = mem_db.open_table(table_name)
                    
                    rom_results = execute_query(t)
                    results.extend(rom_results)
                except Exception as e:
                    print(f"[WARNING] Failed to search ROM {parquet_file}: {e}")
                    
        # Sort combined results by score
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        results = results[:max(100, top_k * 2)]
        
        # Format results to match what retriever expects
        formatted_results = []
        for r in results:
            formatted_results.append({
                "id": r["fragment_id"],
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