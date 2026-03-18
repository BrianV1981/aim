# A.I.M. Architectural Decisions (ADR)

This document records the major architectural decisions that have shaped the A.I.M. platform.

## 1. High-Autonomy (YOLO) Operational Mode (2026-03-17)
- **Status:** **Accepted**
- **Context:** The previous "per-step confirmation" model was inefficient for roadmap-level execution.
- **Decision:** A.I.M. is empowered to execute end-to-end tasks autonomously within a defined roadmap.
- **Consequence:** Requires a "Never Overconfident" mandate. Destructive or multi-file changes MUST perform a pre-flight backup.

## 2. Sovereign Keyring Migration (2026-03-17)
- **Status:** **Accepted**
- **Context:** Storing API keys in `.bashrc` or environment variables is a security risk.
- **Decision:** Migrate all secrets (e.g., `GOOGLE_API_KEY`) to a local keyring managed via the `keyring` Python package.
- **Consequence:** Hardcoded exports in `~/.bashrc` are deprecated and should be removed.

## 3. Google GenAI SDK for Forensic Engine (2026-03-17)
- **Status:** **Accepted**
- **Context:** Moving away from local Ollama/Nomic embeddings to leverage Google's managed intelligence for higher precision and context windows.
- **Decision:** Use `text-embedding-004` and `gemini-2.0-flash` for indexing and distillation.
- **Consequence:** Requires transition of `src/indexer.py` and `src/distiller.py`.
