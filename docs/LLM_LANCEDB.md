**LanceDB Integration Proposal for A.I.M.**  
**Status:** Active Epic
**Date:** May 2, 2026

### 1. Executive Summary: The Death of the Python Intersection Loop
Currently, A.I.M. utilizes a federated SQLite + manual vector BLOBs + FTS5 setup. To eradicate "Global RAG Pollution" during the LoCoMo benchmark, we successfully built the **RAG 4.2 Entity-Enforced Intersection** architecture in `aim_core/retriever.py`. 

This architecture generates a semantic query and a strict Boolean query, pulls both lists, and uses a manual Python Reciprocal Rank Fusion (RRF) loop to brutally delete semantic hits that don't appear in the FTS5 hit-list. 

While this mathematically achieved 100% pollution elimination and an 81.4% True Correct score on Qwen3.5:4b, it is the **manual/legacy** way of doing vector search. As long-term agent memory scales to hundreds of thousands of engrams, doing intersection math in a Python loop will throttle the system.

**LanceDB** is the ultimate upgrade to replace the Python loop. It is a fully embedded database built on the ultra-efficient Lance columnar format (zero-copy reads). Crucially, **LanceDB natively supports Hybrid Search at the hardware (Rust/C++) level**.

### 2. How LanceDB Solves the RAG 4.2 Bottleneck
Instead of running two distinct queries and fusing them in Python:
```python
# The Old Python Way (RAG 4.2)
db_results = db.search_fragments(query_vec)
lexical_results = db.search_lexical(boolean_query)
# ... 30 lines of Python dictionary intersection math ...
```

We simply pass the Vector and the keyword filters in a single LanceDB API call:
```python
# The New LanceDB Way
result = table.search(query_vector).where(f"text LIKE '%{proper_noun}%'").limit(25).to_pandas()
```
LanceDB handles the Entity-Enforced Intersection natively, making the retrieval engine exponentially faster and eliminating the strict syntax failure traps of SQLite FTS5 (like parenthesis destruction and wildcard stem matching).

### 3. Proposed Architecture (The Adapter Pattern)
LanceDB will **not** replace SQLite entirely. 
- **SQLite:** Remains the source of truth for relational/project data (`project_core.db`, session logging, hierarchies).
- **LanceDB:** Becomes the dedicated high-performance **vector memory store** (`memory_lance/`).

**The Implementation:**
Create `core/memory/vector_backend.py` with an abstract interface that both SQLite and LanceDB implement:
- `add_engram(text, metadata)`
- `search(query, limit, filters)`
- `hybrid_search(...)`

The rest of A.I.M. (daemon, MCP tools, DataJacks) calls the abstract backend — zero changes elsewhere. A new `CONFIG.json` flag will dictate which backend is used:
```json
"memory": {
    "backend": "lancedb",
    "lancedb_uri": "./archive/memory_lance"
}
```

### 4. Migration Path (One-Time Script)
We will ship an `aim migrate-to-lancedb` command that:
1. Reads existing engrams from SQLite `datajack_library.db` and `project_core.db`.
2. Grabs the pre-computed `nomic` BLOBs (avoiding API re-embedding overhead).
3. Inserts them into LanceDB.
4. Keeps the old SQLite tables for fallback backward compatibility.

### 5. Next Steps for the Assigned Agent
1. Branch out and add `lancedb` to `requirements.txt`.
2. Create the abstract `VectorBackend` interface.
3. Migrate `retriever.py` to route vector math to the new backend, keeping the RAG 4.2 Dual-Query generation intact but leveraging LanceDB's native `.where()` clause for the intersection.
4. Run the LoCoMo benchmark on Track A to prove the LanceDB hybrid search retrieves the identical `conv-26.md` fragments at a fraction of the latency.