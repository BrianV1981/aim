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

## 4. Active Checkpointing vs. SessionEnd (2026-03-17)
- **Status:** **Accepted**
- **Context:** Empirical testing proved that Gemini CLI's `SessionEnd` hook is unreliable in TUI mode and does not consistently fire on exit.
- **Decision:** Shift the primary context archival and distillation responsibility to the `AfterTool` hook (`scrivener_aid.py`).
- **Consequence:** The system now performs "Rolling Saves" every 30 minutes. The `/handoff` command is still recommended for manual high-fidelity closure.

## 5. Warmup Guardrail Protocol (2026-03-18)
- **Status:** **Accepted**
- **Context:** High-autonomy (YOLO) mode occasionally leads to "aggressive execution" immediately following session initialization, bypassing the operator's opportunity to set or shift priorities.
- **Decision:** Establish a mandatory "Warmup Guardrail" where A.I.M. must synthesize "The Edge" and wait for an explicit Directive before initiating autonomous sprints.
- **Consequence:** Initial "Hello" turns are restricted to inquiry and context synthesis.

## 6. Decommissioning Real-Time Heartbeat (2026-03-18)
- **Status:** **Accepted**
- **Context:** Implementing a high-frequency (10-min) background distillation loop (`src/heartbeat.py`) creates a high token-burn risk with diminishing returns on architectural clarity.
- **Decision:** Deactivate and decommission the automated `heartbeat.py` trigger. Rely on the existing 30-minute reactive `scrivener_aid.py` for periodic distillation.
- **Consequence:** `src/heartbeat.py` remains in the codebase as a prototype but is disconnected from all automated hooks.

## 7. Stateful Summarization / Quadratic Bloat Patch (2026-03-18)
- **Status:** **Accepted**
- **Context:** `session_summarizer.py` was appending the *entire* session history to the daily log on every checkpoint, leading to quadratic growth (e.g., a single session log exceeding 9,000 lines).
- **Decision:** Implement a stateful "Last Index" tracker. The summarizer now reads the last recorded message count for a session and only appends the *delta* (new messages) since the last checkpoint.
- **Consequence:** Dramatically reduced disk usage, cleaner daily logs, and lower token burn for future project distillation.

## 8. Foundational Embedding Provider: Local (Ollama/Nomic) (2026-03-18)
- **Status:** **Final / Immutable**
- **Context:** The Google Embedding API has strict daily quotas (1,000/day) that are insufficient for high-volume forensic indexing. Switching between providers causes "Semantic Incoherence" where old data cannot be searched by new models due to coordinate and dimensionality mismatches.
- **Decision:** Establish **Ollama (nomic-embed-text)** as the permanent, foundational embedding provider for A.I.M.'s forensic memory. 
- **Consequence:** 
    - Unlimited indexing volume with zero token cost.
    - **MANDATE:** Do not change the `embedding_provider` in `CONFIG.json` for the lifespan of this agent. A provider switch is a destructive operation requiring a total archive wipe and re-index.
    - All future forensic tools must maintain compatibility with the 768-dimension Nomic coordinate system.
