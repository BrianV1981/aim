# A.I.M. Technical Specification

This document provides the literal, metaphor-free engineering specifications for the A.I.M. exoskeleton.

## 1. Database Schema (`engram.db`)
The core memory layer is a local SQLite database utilizing parameterized queries to prevent SQL injection. It implements Hybrid Retrieval (Semantic Cosine Similarity + FTS5 BM25).

### `sessions` Table
Tracks ingestion sources and provides chronological metadata.
*   `id` (TEXT PRIMARY KEY)
*   `filename` (TEXT NOT NULL)
*   `mtime` (REAL NOT NULL)
*   `indexed_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

### `fragments` Table
Stores the actual semantic chunks.
*   `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
*   `session_id` (TEXT NOT NULL) - Foreign Key to `sessions(id)` ON DELETE CASCADE
*   `type` (TEXT NOT NULL) - e.g., 'foundation_knowledge', 'expert_knowledge', 'user_prompt', 'model_response'
*   `content` (TEXT NOT NULL)
*   `timestamp` (TEXT)
*   `embedding` (BLOB) - 768-dimensional float array packed via `struct` (Nomic standard).
*   `metadata` (TEXT) - JSON string containing tool call arguments or routing data.

### `fragments_fts` (Virtual Table)
An FTS5 virtual table synchronized via 3 SQLite triggers (`AFTER INSERT`, `AFTER DELETE`, `AFTER UPDATE`) on the `fragments` table to provide zero-latency exact-match keyword search (BM25 algorithm).

## 2. Token Economics & Benchmarks
The distillation pipeline operates to drastically reduce token payload before semantic embedding. 
Empirical benchmarks run on actual usage:

*   **Raw Session Payload (e.g., 50 Turns):** ~8.76 MB (Includes sprawling `stdout` from terminal tools).
*   **Signal Skeleton (`extract_signal.py`):** ~1.39 MB (Strips ANSI codes, raw outputs, isolates intents and outcomes).
*   **Compression Ratio:** ~6.4x to 8.5x reduction.
*   **Result:** Offloading the raw skeleton to a secondary distillation model (e.g., Gemini Flash) costs fractions of a cent while preserving exact API parameter integrity.

## 3. The DataJack Protocol (.engram files)
An `.engram` file is a standard ZIP archive containing:
1.  `metadata.json`
2.  `chunks/*.jsonl`

**Security:** The `aim jack-in` command does **not** execute raw SQL scripts. It safely parses the JSONL dictionaries and uses parameterized SQLite execution (`INSERT INTO fragments (session_id, type, content, timestamp, embedding) VALUES (?, ?, ?, ?, ?)`) to prevent supply-chain SQL injection attacks. An explicit operator confirmation is required before execution.

## 4. Source Control & Branching
A.I.M. uses Timestamped Archive Branching (`archive-<branch>-<datetime>`) instead of Git Tags during the Phase Protocol. This is a deliberate, non-standard design choice. AI CLI agents struggle to navigate detached HEAD states and `git reflog` recovery. Explicit archival branches provide safe, verifiable "Save States" that an AI can easily list, checkout, and restore from without breaking the local git tree.