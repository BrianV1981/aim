# A.I.M. Brain Map (Cognitive Architecture)

This document maps the complete anatomical structure of the A.I.M. "Brain." Unlike the `SCRIPT_MAP.md` which catalogs user-facing CLI commands, this map details the background systems, automated hooks, data pipelines, and storage mediums that give the agent memory, continuity, and technical constraints.

---

## 1. The Continuity Layer (Working Memory)
This subsystem handles immediate context preservation. It guarantees that an agent spawned in a new terminal session instantly knows exactly what the previous agent was doing.

*   **`src/handoff_pulse_generator.py`**: The pulse engine. When a session ends (or `aim handoff` is run), it reads the chat history and distills the immediate state into `continuity/CURRENT_PULSE.md`.
*   **`hooks/context_injector.py`**: The awakening protocol. Fired on `SessionStart`. It forcefully injects `CURRENT_PULSE.md` and pending memory proposals into the AI's system prompt before it can speak.
*   **`hooks/failsafe_context_snapshot.py`**: The safety net. Fired after every tool call. It dumps the raw JSON array of the current conversation to `continuity/private/FALLBACK_TAIL.json` so context isn't lost if the terminal crashes mid-session.

## 2. The Engram DB (Subconscious Knowledge / RAG)
This is the vast, searchable archive of foundational rules, syntax guides, and specific technical documentation. It prevents hallucination by enforcing an empirical "Search First" mandate.

*   **The Database (`archive/engram.db`)**: A local SQLite database utilizing the `sqlite-vec` extension for semantic vector embeddings and FTS5 for exact keyword matching.
*   **`src/forensic_utils.py`**: Defines the `ForensicDB` schema and manages the raw database connection and table creation.
*   **`src/indexer.py`**: The ingestion engine. It traverses `synapse/` (expert docs) and `docs/` (foundation docs), chunks the markdown, generates local vector embeddings (via Nomic/Ollama by default), and inserts them into the database.
*   **`src/retriever.py`**: The query engine. Powering `aim search`, it executes Hybrid Search (combining Vector similarity with BM25 keyword matching) to extract relevant fragments for the agent.

## 3. The Sync & Portability Layer (The GitOps Bridge)
Because SQLite binaries (`engram.db`) cannot be cleanly tracked in Git without massive bloat and merge conflicts, this layer translates the brain into a Git-friendly format.

*   **`src/sovereign_sync.py`**: The translator. During `aim push`, it exports every row in `engram.db` to flat, diffable `.jsonl` files in `archive/sync/`.
*   **`src/back-populator.py`**: The reconstructor. During `aim update`, it reads the pulled `.jsonl` files and completely rebuilds the local `engram.db` to match the remote repository state.
*   **`scripts/aim_bake.py` / `aim_exchange.py`**: The cartridge foundry. Allows packaging specific folders into portable `.engram` files that can be injected into different A.I.M. instances to instantly transfer learned capabilities.

## 4. The Executive Guardrails (Anti-Drift Shield)
These background hooks act as the "superego," silently watching the AI's actions to ensure it doesn't violate core directives or get lost in infinite loops.

*   **`hooks/cognitive_mantra.py`**: The attention-reset mechanism. It counts background tool calls. At 25 calls, it injects a silent "Subconscious Whisper" reminder of the rules. At 50 calls, it forces the AI to halt and output a `<MANTRA>` block reciting its core mandates to wash away "Lost in the Middle" context degradation.
*   **`hooks/safety_sentinel.py`**: Intercepts `run_shell_command` requests to verify safety before execution.
*   **`hooks/secret_shield.py`**: Intercepts file writes to prevent the AI from accidentally committing API keys or credentials.
*   **`hooks/workspace_guardrail.py`**: Prevents the AI from straying outside the designated `BASE_DIR`.

## 5. The Memory Refinement Pipeline (Long-Term Memory)
This subsystem is responsible for extracting durable facts from chaotic chat logs and merging them into the permanent `core/MEMORY.md` file using a high-frequency Delta Ledger model.

*   **`hooks/session_summarizer.py` (Tier 1 - Session Summarizer)**: Fired on `SessionEnd`. It converts raw chat logs into technical narratives in `memory/hourly/`.
*   **`src/memory_proposer.py` (Tier 2 - Memory Proposer)**: Triggered via `aim memory`. It reads recent summaries and proposes structured **Delta Ledger** updates.
*   **`src/daily_refiner.py` (Tier 3 - Daily Refiner)**: Triggered via `aim memory`. Consolidates and deduplicates hourly proposals into a unified daily state.
*   **`src/weekly_consolidator.py` (Tier 4 - Weekly Consolidator)**: Triggered via `aim memory`. Distills the past 7 daily states into high-level project milestones and architectural shifts.
*   **`src/monthly_archivist.py` (Tier 5 - Monthly Archivist)**: Triggered via `aim memory`. Compresses long-term stable architecture into dense axioms and archives stale context.
*   **`scripts/aim_cli.py` (The Merge Tool)**: The `cmd_commit` function parses the `### 3. MEMORY DELTA` block and safely applies it.

---