# A.I.M. Architectural Decisions (ADR)

This document records the major architectural decisions that have shaped the A.I.M. platform.

## 1. High-Autonomy (YOLO) Operational Mode (2026-03-17)
- **Status:** **Accepted**
- **Decision:** A.I.M. is empowered to execute end-to-end tasks autonomously within a defined roadmap.

## 2. Sovereign Keyring Migration (2026-03-17)
- **Status:** **Accepted**
- **Decision:** Migrate all secrets to a local keyring managed via the `keyring` Python package.

## 3. Google GenAI SDK for Reasoning (2026-03-17)
- **Status:** **Accepted**
- **Decision:** Use `gemini-flash` for distillation and high-order reasoning while keeping embeddings local.

## 4. Active Checkpointing vs. SessionEnd (2026-03-17)
- **Status:** **Accepted**
- **Decision:** Shift primary context archival responsibility to the `AfterTool` hook (`scrivener_aid.py`) to bypass unreliable `SessionEnd` events.

## 5. Foundational Embedding Provider: Local (Ollama/Nomic) (2026-03-18)
- **Status:** **Final / Immutable**
- **Decision:** Establish **Ollama (nomic-embed-text)** as the permanent embedding provider for forensic memory to ensure zero cost and unlimited scaling.

## 6. Unified Forensic Database (SQLite) (2026-03-19)
- **Status:** **Accepted**
- **Context:** O(N) file-scanning for thousands of `.fragments.json` files was becoming a performance bottleneck.
- **Decision:** Consolidate all session fragments into a single `forensic.db` SQLite database.
- **Consequence:** Search is now sub-millisecond; indexing is more reliable.

## 7. Dynamic Privacy Hardening (2026-03-19)
- **Status:** **Accepted**
- **Decision:** Telemetry scrubbing must be dynamic, pulling the current `USER` and `keyring` secrets at runtime rather than relying on hardcoded patterns.

## 8. Path Normalization (2026-03-19)
- **Status:** **Accepted**
- **Decision:** Eliminate all hardcoded paths (e.g., `/home/kingb/aim`) in favor of dynamic root discovery via `find_aim_root()`.
- **Consequence:** The platform is now fully portable across different systems and usernames.

## 9. Commit Safety Shadowing (2026-03-19)
- **Status:** **Accepted**
- **Decision:** Every `aim commit` must generate a `MEMORY.md.bak` shadow and perform regex validation on the proposal syntax.
