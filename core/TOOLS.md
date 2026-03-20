# A.I.M. Internal Tools Manifest

A.I.M. has access to custom internal tools for workspace orchestration and forensic memory.

## 1. Forensic Search & Retrieval (`retriever.py`)
- **Usage:** `aim search "<query>"`
- **Function:** Performs a sub-millisecond semantic search through `archive/forensic.db` (SQLite).
- **Supports:** `--context`, `--full`, and `--session` filters.
- **Protocol:** Mandated by `GEMINI.md`. Use this BEFORE starting complex tasks to "remember" previous context or solutions. Zero-token alternative to asking the Operator.

## 2. Session Indexer (`indexer.py`)
- **Usage:** `aim index`
- **Function:** Parses raw JSON transcripts into semantic fragments and stores them in `forensic.db`.
- **Note:** Automatically maintains `sessions` metadata (mtime) to avoid redundant indexing.

## 3. Stateful Scrivener (`session_summarizer.py`)
- **Usage:** Automated via `SessionEnd` and `AfterTool` hooks.
- **Function:** Deterministically extracts technical essence (Intents, Actions, Outcomes) into daily narrative logs.
- **Advanced Logic:** Uses aggressive disk-peeking to reconstruct history from partial hook payloads and maintains a "Last Index" state to ensure delta-only, zero-redundancy logging.
- **Locking:** Uses `.aim.lock` to prevent concurrency race conditions.

## 4. Flash Distiller (`distiller.py`)
- **Usage:** `aim handoff` (or automated via Flywheel).
- **Function:** Analyzes logs to generate **Context Pulses** (`continuity/`) and **Memory Proposals** (`memory/proposals/`).
- **Goal:** Maintains the "Edge" of technical momentum.

## 5. Auto-Versioning Push (`aim_push.sh`)
- **Usage:** `aim push "<commit message>"`
- **Function:** Stages all changes, generates a unique semantic version (e.g., `v1.20260319.1200`), and pushes to GitHub.
