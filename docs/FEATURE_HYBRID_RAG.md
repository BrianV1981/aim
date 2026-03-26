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