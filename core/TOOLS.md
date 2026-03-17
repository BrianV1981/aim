# A.I.M. Internal Tools Manifest

A.I.M. has access to custom internal tools for workspace orchestration and forensic memory.

## 1. Forensic Search (`retriever.py`)
- **Usage:** `./aim/src/retriever.py "<query>"`
- **Function:** Performs a semantic search across past A.I.M. sessions.
- **When to use:** Use this BEFORE starting complex tasks to "remember" how we solved similar problems or what the previous context was.

## 2. Session Indexer (`indexer.py`)
- **Usage:** `./aim/src/indexer.py`
- **Function:** Parses raw JSON transcripts into semantic fragments and generates embeddings using Ollama (nomic-embed-text).
- **When to use:** Runs automatically via chron or manual batch trigger at the start of a session.

## 3. Session Summarizer (`session_summarizer.py`)
- **Usage:** Triggered by `SessionEnd` hook.
- **Function:** Forensic-grade archival of raw JSON session data and creation of daily MD logs.
- **Target:** `/home/kingb/aim/archive/raw/` and `/home/kingb/memory/`.
