# Architecture Decision Record: Two-Stage Filter & Rank

**Date:** May 2026
**Status:** Accepted
**Context:** A.I.M. OS Information Retrieval

## Problem
During the LoCoMo V2 benchmark, the agent retrieved documents for Question 24 regarding "Melanie's books" using a highly generic query (`Melanie read book reading author`). LanceDB's Tantivy FTS engine evaluated space-separated words as an `OR` query. This caused the engine to return highly-ranked documents containing the word "book" (from other characters like Tim and John), completely burying the specific visual metadata document containing Melanie's book ("Nothing is Impossible").

Initial attempts to fix this involved a "ruthless" Pandas string-matching hack inside the `EntityIntersectionReranker` to manually delete rows missing the proper noun. However, this bypassed the database entirely, wasting compute and risking false positives.

## Decision
We are adopting a true **Two-Stage Filter & Rank** architecture:

### Stage 1: Deterministic Database Filtering (Tantivy Strict Inclusion)
Instead of relying on Python to filter results after the fact, we intercept the query formulation in `generate_tantivy_query`. If a word is identified as a proper noun (e.g., `Melanie`), we prepend the Tantivy `+` operator (e.g., `+melanie*`).
This forces the Rust-based database engine to natively reject any document that does not contain the target entity, guaranteeing a 100% pure candidate pool (e.g., 100 documents that *all* contain "Melanie").

### Stage 2: Semantic Sorting (FlashRank Cross-Encoder)
With a guaranteed clean candidate pool from Stage 1, the retrieval pipeline leverages the local `ms-marco-MiniLM-L-6-v2` FlashRank cross-encoder to semantically sort the 100 documents. The cross-encoder evaluates the contextual meaning of the prompt against the text, seamlessly pushing the most relevant facts to the Top-10.

## Consequences
- **Positive:** Zero false positives for proper noun retrieval. Complete elimination of cross-contamination between speakers in large conversational datasets. Maximum utilization of the LanceDB engine's native performance.
- **Negative:** Requires accurate capitalization in the agent's search query to trigger the `+` operator. If the agent searches for `melanie` (lowercase), it will fall back to an `OR` query.