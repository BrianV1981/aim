# Key Feature: Hybrid RAG (Semantic + Lexical)

**The Problem:** Pure Semantic Vector Search (Cosine Similarity) is brilliant at finding "vibes" and abstract concepts. However, it is notoriously terrible at finding exact variable names, specific error codes, or unique hex strings. If your AI agent needs to find the exact file where `init_workspace_guardrail` is defined, a pure vector search might fail to retrieve it.

**The Solution:** The A.I.M. Engram DB implements a true **Hybrid RAG** engine, fusing deep semantic understanding with instant, exact-match keyword indexing directly at the SQLite level.

---

## 1. The Semantic Layer (Vector Embeddings)
*   **The Engine:** Nomic Embed Text (`nomic-embed-text` via Ollama).
*   **The Mechanism:** Every document or JSON transcript ingested into the database is mapped as a 768-dimensional float array (`BLOB`). 
*   **The Use Case:** Abstract queries. If the agent searches for *"How do we isolate subagents?"*, the vector math correctly identifies the "Contractor Protocol" and "The Bouncer," even though the word "subagent" might not appear in the target text.

## 2. The Lexical Layer (FTS5 BM25)
*   **The Engine:** SQLite FTS5 (Full-Text Search).
*   **The Mechanism:** A.I.M. generates a virtual `fragments_fts` table that acts as a shadow copy of the main database. Using advanced SQLite Triggers (`AFTER INSERT`, `AFTER UPDATE`), every word ingested is instantly tokenized into a high-speed keyword index.
*   **The Use Case:** Needle-in-a-haystack queries. If the agent searches for the exact string `TypeError: 'NoneType'`, the BM25 algorithm instantly retrieves the exact log where that error occurred.

## 3. The "Photograph" Effect (Hybrid Fusion)
Human memory works via hybrid retrieval. If someone asks, *"Do you remember that time?"* (Semantic), you might draw a blank. But if they show you a specific photograph (Lexical), the entire context of the memory floods back.

When A.I.M. executes `aim search "query"`:
1.  It runs the query through the Nomic embedding model to find the closest semantic vectors.
2.  It runs the exact same query through the SQLite FTS5 index to find exact string matches using the BM25 algorithm.
3.  It merges both lists, deduplicates the fragments, and hands the AI an absolute, mathematically perfect subset of context.

## The Result
A.I.M. never suffers from "Lost in the Middle" syndrome. Whether the agent remembers the philosophical concept or the exact line of code, the database will return the correct file in sub-millisecond response times.

---

## 4. Modularity and The Re-Vectorization Constraint
The A.I.M. architecture is designed to be highly modular. By default, it uses `nomic-embed-text` (a 768-dimension local model) because it is free, fast, and private. 

However, you can technically swap the embedding provider in the configuration to use a completely different model (e.g., OpenAI's `text-embedding-3-small` or Voyage AI). 

### The Mathematical Reality of Provider Swapping
If you change your semantic embedding model, **you must re-vectorize the entire `engram.db`**. 
Vector embeddings from different models exist in fundamentally different mathematical universes. A 768-dimension vector from Nomic is mathematically incompatible with a 1536-dimension vector from OpenAI. If you swap providers without re-embedding, all semantic searches will instantly fail or return complete garbage.

### Lossless Cartridges (You do not need the original files)
The brilliant structural design of the `.engram` cartridge (and the `archive/engram.db`) is that it is **Lossless**.

When you run `aim bake` or `aim jack-in`, the SQLite database stores the pre-calculated Nomic math (`embedding`), but it *also* stores the raw plaintext (`content`) directly side-by-side in the same row.

**To answer the critical question:** No, you do NOT need the original `.md` or `.txt` files to re-vectorize an engram. 
If you decide to switch your entire ecosystem from Nomic to OpenAI tomorrow, you simply run a Python script that iterates over every row in your `engram.db`. The script reads the raw `content` column, asks OpenAI to generate a new vector, and overwrites the `embedding` column. Because the exact raw text is perfectly preserved inside the database, your knowledge base can seamlessly migrate between different AI models over the decades without ever losing the original data.