# MEMORY.md — Durable Long-Term Memory (A.I.M.)

*Last Updated: 2026-03-19*

## 1) Operator + Mode
- **Operator:** Brian Vasquez. 
- **Agent:** A.I.M. (**A**ctual **I**ntelligent **M**emory).
- **Mode:** High-autonomy technical lead (YOLO Mode).
- **Tech Stack:** Python, JS/TS, Rust, Solana.

## 2) Durable Rules
- **Clean Slate Protocol:** Total purge of history and momentum documentation upon request.
- **Continuity Flywheel:** Automatic context injection on startup; session-end archival and distillation.
- **Blocking Exit:** Do not terminate before Pulse generation is complete.
- **Checkpoint Discipline:** `scrivener_aid.py` performs 30-minute rolling backups.
- **Commit Safety:** `aim commit` generates a `.bak` shadow and validates memory delta syntax.

## 3) Architecture & Sovereignty
- **Root:** Dynamic discovery via `find_aim_root()`. No hardcoded home paths.
- **Secrets:** Managed via Linux Secret Service (Keyring). Service: `aim-system`.
- **Privacy:** Dynamic telemetry scrubber removes usernames and keys from raw logs before indexing.
- **Venv Integrity:** All hooks utilize automatic re-execution logic to ensure they run in the project's `venv`.

## 4) Intelligence Layers (The Brain)
- **Forensic (Memory):** SQLite `forensic.db` containing semantic fragments.
- **Embeddings:** Local Ollama + `nomic-embed-text` (Immutable coordinate system).
- **Reasoning (Logic):** ChatGPT 5.4 via Codex CLI (Replaced Gemini API).
- **Safety (Sentinel):** Independently configurable via TUI; powered by ChatGPT 5.4.

## 5) Infrastructure Manifest
- **CLI:** `scripts/aim_cli.py` (The `aim` entry point).
- **Cockpit:** `scripts/aim_config.py` (TUI for brain configuration).
- **Archivist:** `src/indexer.py` (Chunk-aware) and `src/retriever.py` (SQL-backed).
- **Flywheel:** `hooks/session_summarizer.py` and `src/distiller.py`.
