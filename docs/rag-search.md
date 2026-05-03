# RAG & Search

The A.I.M. retrieval pipeline, fully migrated to LanceDB with native hybrid search.

## Architecture

```
User Query
    │
    ▼
generate_tantivy_query()     ← Stopword removal, fuzzy stemming, parenthesis preservation
    │
    ▼
LanceDB Hybrid Search        ← Vector (nomic-embed-text) + FTS (Tantivy) in one query
    │
    ▼
EntityIntersectionReranker   ← Deletes semantic hits missing mandatory Proper Nouns
    │
    ▼
FlashRank Cross-Encoder      ← Local re-ranker (ms-marco-MiniLM-L-6-v2)
    │
    ▼
Knowledge Priority Weighting ← Boosts foundation + expert knowledge
    │
    ▼
Temporal Decay               ← Zep-inspired exponential decay on older fragments
    │
    ▼
Top-K Results
```

## Components

### LanceDB VectorBackend (`lance_backend.py`)

Replaces the old SQLite + manual BLOB vector approach. Key features:

- **Native hybrid search**: Vector + FTS in a single LanceDB query
- **Zero-copy columnar format**: Million-row scale without Python loops
- **Tantivy FTS index**: Full-text search without SQLite FTS5 syntax traps
- **Single-table omniscience**: Federated Archipelago merged into one LanceDB table with `source_db` metadata

### Tantivy Query Generator

`generate_tantivy_query(user_query)` converts natural language into optimized LanceDB FTS:

1. Removes 100+ stopwords (a, the, what, did, how, etc.)
2. Appends `*` to word roots (fuzzy wildcard stemming)
3. Preserves parentheses and boolean operators (`AND`, `OR`)
4. Detects Proper Nouns (capitalized words) for Entity Intersection
5. Cleans dangling operators after stopword removal

### EntityIntersectionReranker

Custom LanceDB reranker that prevents "RAG pollution":

- When Proper Nouns are detected, deletes ANY semantic hit that lacks those nouns in the FTS hit-list
- Implements Reciprocal Rank Fusion (RRF) for combining vector + FTS scores
- Ruthlessly enforces the Entity-Enforced Intersection mandate from RAG 4.2

### FlashRank Cross-Encoder

Local, offline re-ranker that re-scores LanceDB's top results using deep semantic comparison:

- Model: `ms-marco-MiniLM-L-6-v2`
- Cache: `archive/flashrank_cache/`
- Reranks top 50 results, pushing the true target into the top 5

### Coreference Rewriter (`hooks/coreference_rewriter.py`)

Intercepts conversational follow-ups and resolves pronouns:

- Detects: "it", "this", "that", "they", "he", "she"
- Uses `qwen3.5:4b` locally to rewrite into standalone queries
- Prevents "How do I fix it?" from searching literally

## Federated Archipelago

All databases are searched simultaneously:

| Database | Purpose |
|---|---|
| `archive/project_core.db` | Project-specific knowledge |
| `archive/global_skills.db` | Cross-project skills and mandates |
| `archive/datajack_library.db` | Imported .engram DataJack cartridges |
| `archive/subagent_ephemeral.db` | Session-specific subagent memory |

After LanceDB migration, all four are merged into a single `memory_lance/` table with `source_db` metadata for traceability.

## Migration

```bash
# Migrate existing SQLite vectors to LanceDB (zero re-embedding)
python -c "from aim_core.lance_backend import VectorBackend; VectorBackend().migrate_from_sqlite()"

# The table is created at memory_lance/fragments.lance
# Tantivy FTS index is built automatically
# Existing SQLite databases are preserved for backward compatibility
```

## Query Example

```python
from aim_core.retriever import perform_search

# Semantic + FTS hybrid search with FlashRank reranking
perform_search("What did Melanie paint?", top_k=10, show_context=True)

# Internal pipeline:
# 1. Tantivy: "melanie* paint*" (stopwords removed, wildcards added)
# 2. LanceDB: vector search + FTS with EntityIntersection (Melanie is Proper Noun)
# 3. FlashRank: rerank top 50
# 4. Temporal decay: penalize old results
# 5. Knowledge priority: boost foundation mandates
```

## Performance

| Metric | SQLite (old) | LanceDB (new) |
|---|---|---|
| Vector search | Python loop over BLOBs | Native zero-copy columnar |
| FTS | SQLite FTS5 (regex traps) | Tantivy (robust, fast) |
| Hybrid | Separate queries + manual fusion | Single hybrid query |
| Scale | Slows at 10k+ rows | Scales to millions |
| Reranking | None | FlashRank + EntityIntersection |
