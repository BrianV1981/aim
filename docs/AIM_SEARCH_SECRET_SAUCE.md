# A.I.M. Search: The "Secret Sauce"

The A.I.M. (Actual Intelligent Memory) hybrid search architecture outperforms standard vector databases because it relies on a highly structured, intercept-and-refine pipeline spanning both the ingestion and retrieval phases. 

While typical RAG systems blindly embed raw text and execute basic cosine-similarity queries, A.I.M. treats memory mathematically and semantically.

## Part 1: The Ingestion Pipeline (Context Preservation)

"Garbage in, garbage out." A.I.M. structures memory before the database ever sees it.

1. **Parent-Child Categorization:** 
   Standard RAG systems chop documents into arbitrary 500-word chunks, destroying pronoun references (e.g., chunk 2 has "He", but chunk 1 has "John"). A.I.M. embeds highly granular "child" fragments for surgical mathematical matching, but rigidly links them to their "parent" macro-context. When a child hits, the agent retrieves the entire conversational block, curing LLM amnesia.
2. **Sovereign, High-Context Embeddings:** 
   Instead of using ChromaDB's default `all-MiniLM-L6-v2` (256-token limit), A.I.M. utilizes `nomic-embed-text` locally. This provides a massive 8,192-token context window for rich, high-dimensional semantic vectors with zero API cost and absolute data privacy.
3. **LLaVA Visual Flattening (Multimodal RAG):** 
   Standard databases cannot search images natively. A.I.M. utilizes LLaVA to "visually flatten" images into rich, highly descriptive text before embedding. This translates pixels into semantics, allowing the agent to query visual memories using standard text logic.

## Part 2: The Retrieval Pipeline (Query Engineering)

When an agent requests a memory, the query is aggressively optimized before and after hitting the LanceDB engine.

1. **Conversational Boolean Rewriting:** 
   Natural language queries (e.g., "When did Caroline go to the support group?") are intercepted by `generate_tantivy_query`.
   * **Stopword Incineration:** Removes 100+ common English words, boiling the query down to core entities.
   * **Fuzzy Wildcard Stemming:** Appends `*` to roots (e.g., `camp` becomes `camp*` to hit `camping` and `camper`).
   * **Parenthesis Preservation:** Retains logical groupings (`AND`, `OR`, `()`) formulated by the LLM, enabling complex conditional searches standard LanceDB FTS cannot execute.
2. **Single-Table Omniscience:** 
   Rather than siloing memory into separate databases, A.I.M. merges the Federated Archipelago (`project_core`, `global_skills`, `datajack_library`) into a single LanceDB table with a `source_db` metadata column. This forces Reciprocal Rank Fusion (RRF) to calculate token frequencies against the *entire* digital brain simultaneously, vastly improving score accuracy.
3. **Entity-Enforced Intersection (The Antidote to RAG Pollution):** 
   Standard hybrid search normalizes and adds Vector and FTS scores, allowing strong semantic matches to override missing exact keywords (causing hallucinations). A.I.M.'s custom `EntityIntersectionReranker` detects Proper Nouns (e.g., "Caroline"). If a fragment scores high semantically but lacks the mandatory Proper Noun in the FTS hit-list, the reranker ruthlessly deletes it.

## Conclusion
A.I.M. does not just pass queries to a database. It cleans, parses, bolsters, and enforces logic on the query *before* it searches, and then ruthlessly prunes the results based on Proper Noun intersection *after* it searches. This multi-layered architecture guarantees near-perfect retrieval accuracy against adversarial data.