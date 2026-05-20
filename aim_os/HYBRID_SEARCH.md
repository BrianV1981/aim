# Hybrid Retrieval & Post-Retrieval Context Expansion

This document details the mechanics of the RAG 5.21 retrieval engine (`aim search`), outlining how A.I.M. processes natural language queries to retrieve highly accurate context from the LanceDB memory pool.

## 1. Query Engineering (Tantivy Engine)
Before a query ever hits the database, the `generate_tantivy_query()` function mathematically optimizes the natural language:
*   **Stopword Incineration:** Common English words are stripped to prevent FTS (Full-Text Search) pollution.
*   **Proper Noun Strict Inclusion:** Capitalized words (e.g., "Django") are translated into strict inclusion tags (`+Django*`), ensuring the lexical engine strictly prioritizes documents containing those exact entities.
*   **Fuzzy Wildcard Stemming:** Words receive an asterisk to natively match variations without needing complex semantic math.

## 2. Hybrid Search & Reciprocal Rank Fusion (RRF)
A.I.M. executes a true Hybrid Search via LanceDB, firing both a semantic vector query (using embedded tensors) and a lexical FTS query (Tantivy) simultaneously.
*   **The Reranker:** To merge these disparate scoring scales, the `EntityIntersectionReranker` calculates a unified score using the Reciprocal Rank Fusion formula (`1.0 / (k + rank)`).
*   **The Multiplier:** Fragments that appear high on *both* lists, and specifically contain the exact Proper Nouns requested, receive a massive 1.5x score multiplier. This cures vector "Entity Blindness."

## 3. "Sandwich" Context Expansion (N-1 / N+1)
A.I.M. chunks data precisely by speaker boundaries (500-1500 chars). A retrieved fragment only contains the dialogue for that specific moment. If an event spans multiple turns, the LLM needs more context.
*   **Sequential ID Tracking:** When LanceDB returns a highly ranked fragment (e.g., `fragment_id = 42`), the `retriever.py` script intercepts the payload.
*   **Native PyArrow Filtering:** It automatically executes a secondary query using `pyarrow.dataset` to fetch `fragment_id = 41` (the previous chunk) and `fragment_id = 43` (the next chunk).
*   **The Sandwich:** It stitches them together into a seamless conversational "sandwich." This guarantees the agent sees the historical setup, the actual event, and the future reaction, resolving "lost in the middle" hallucinations.

## 4. Graceful Lexical Degradation
If the local embedding server (e.g., Ollama) fails, rate-limits, or crashes with an OOM error during retrieval, the system does not crash.
*   The `get_embedding()` function catches the exception and passes `query_vec = None` to the backend.
*   LanceDB dynamically detects the missing vector, aborts the cosine-similarity calculations, and completely falls back to a pure Tantivy FTS keyword search, ensuring the system remains indestructible under heavy load.