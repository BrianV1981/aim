# A.I.M. Protocol: LanceDB Ingestion & Embedding (RAG 5.2)

## Overview
This protocol defines the standard architecture and workflow for processing, chunking, and embedding conversational datasets into the LanceDB vector store, enabling high-performance RAG and FTS.

## The 5-Stage Pipeline

1.  **Multimodal Flattening (Data Layer):**
    Pre-process raw conversational datasets to inject OCR text/captions directly into dialogue transcripts as clean text. This removes `img_url` keys and bloat, reducing token usage during retrieval.

2.  **Format Shifting (Decontamination):**
    The ingestion script parses dialogue transcripts and dynamically applies typographical format shifting (changing bracket styles, timestamp formatting) to shatter LLM memorization n-grams and minimize pre-training data leakage.

3.  **Speaker-Boundary Session Chunking:**
    Instead of arbitrary token slicing, chunks are created at strict speaker/session boundaries.
    *   **Logic:** Fragments are merged into contiguous dialogue flows.
    *   **Size Constraints:** 500 to 1,500 characters per chunk.
    *   **Formatting:** Double line breaks (`\n\n`) are injected for whitespace decontamination and improved retrieval readability.

4.  **Embedding & Native Ingestion (RAG 5.2):**
    RAG 5.2 replaces the legacy SQLite bottleneck.
    *   **Embeddings:** Raw text chunks are passed to `nomic-embed-text` (Ollama/local) to generate semantic vectors.
    *   **Ingestion:** Vectors are written directly into LanceDB using PyArrow, creating a highly optimized, searchable vector index in `aim-locomo/memory_lance`.

5.  **Full-Text Search (FTS) Indexing:**
    A LanceDB Full-Text Search (Tantivy) index is constructed on the `content` column. This enables **Hybrid Search** (Semantic + Keyword) for robust retrieval across diverse conversational contexts.
