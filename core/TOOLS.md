# A.I.M. Internal Tools Manifest

A.I.M. has access to custom internal tools for workspace orchestration and forensic memory.

## 1. Forensic Search & Retrieval (`retriever.py`)
- **Usage:** `aim search "<query>"`
- **Function:** Performs a sub-millisecond semantic search through `archive/engram.db` (SQLite).
- **Protocol:** Mandated by `GEMINI.md`. Use this BEFORE starting complex tasks to "remember" previous context or solutions. Zero-token alternative to asking the Operator.

## 2. Session Indexer (`indexer.py`)
- **Usage:** `aim index`
- **Function:** Parses raw JSON transcripts into semantic fragments and stores them in `engram.db`.
- **Note:** Automatically maintains `sessions` metadata (mtime) to avoid redundant indexing.

## 3. Stateful Scrivener (`tier1_hourly_summarizer.py`)
- **Usage:** Automated via `SessionEnd`, `AfterTool`, and `PreCompress` hooks.
- **Function:** Deterministically extracts technical essence (Intents, Actions, Outcomes) into daily narrative logs.
- **Advanced Logic:** Uses strictly location-based root discovery (`__file__`) and aggressive fuzzy retrieval to find transcript files matching Gemini CLI hashing patterns.

## 4. Flash Distiller (`handoff_pulse_generator.py`)
- **Usage:** `aim handoff` (or automated via Flywheel).
- **Function:** AI-backed analysis of logs to generate **Context Pulses** (`continuity/`) and **Memory Proposals** (`memory/proposals/`).
- **Goal:** Synthesizes raw technical trace into distilled mental models.

## 5. Pre-Compression Shield (`hooks/pre_compress_checkpoint.py`)
- **Usage:** Automated via `PreCompress` hook.
- **Function:** Protects session history from context window summarization by forcing an immediate archival pulse exactly before history is pruned.

## 6. Auto-Versioning Push (`aim_push.sh`)
- **Usage:** `aim push "<commit message>"`
- **Function:** Stages changes, generates a unique semantic version, and pushes to the current branch.
