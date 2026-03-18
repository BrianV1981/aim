# A.I.M. Internal Tools Manifest

A.I.M. has access to custom internal tools for workspace orchestration and forensic memory.

## 1. Forensic Search (`retriever.py`)
- **Usage:** `python3 src/retriever.py "<query>"`
- **Function:** Performs a semantic search across past A.I.M. sessions.
- **When to use:** Use this BEFORE starting complex tasks to "remember" how we solved similar problems or what the previous context was.

## 2. Session Indexer (`indexer.py`)
- **Usage:** `python3 src/indexer.py`
- **Function:** Parses raw JSON transcripts into semantic fragments and generates embeddings using Google GenAI SDK (`gemini-embedding-2-preview`).
- **When to use:** Runs automatically via `SessionEnd` hook to index new session data, but can be manually triggered if needed.

## 3. Session Summarizer (`session_summarizer.py`)
- **Usage:** Triggered by `SessionEnd` hook and `AfterTool` active checkpointing.
- **Function:** Forensic-grade archival of raw JSON session data, creation of daily MD logs, and triggering of the Flash Distiller.
- **Target:** `archive/raw/` and `memory/`.

## 4. Auto-Versioning Push (`aim_push.sh`)
- **Usage:** `./scripts/aim_push.sh "<commit message>"`
- **Function:** Automatically stages changes, generates a unique semantic version timestamp (e.g., `v1.20260318.0156`), commits, and pushes to GitHub.
- **When to use:** Use this for ALL pushes to the remote repository to ensure exact state traceability.
