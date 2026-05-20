# A.I.M. Cognitive Architecture (The Brain Map)

This document defines the complete anatomical structure of the A.I.M. "Brain" and how data flows through the system. Future agents must reference this map to understand where state lives and how memory is retrieved.

## 1. The Failsafe Snapshot Layer
*   **Trigger:** Executed silently in the background on every turn by `hooks/failsafe_context_snapshot.py`.
*   **Storage:** `continuity/INTERIM_BACKUP.json` and `continuity/FALLBACK_TAIL.md`.
*   **Purpose:** Ephemeral session rescue. If the agent crashes (e.g., V8 OOM), `aim crash` uses these files to reconstruct the active state without data loss.

## 2. The Continuity Pulse (The Handoff)
*   **Trigger:** Executed mechanically during `/reincarnate` by `aim_core/handoff_pulse_generator.py`.
*   **Storage:** `continuity/REINCARNATION_GAMEPLAN.md` (The "Will") and `continuity/CURRENT_PULSE.md` (The "State").
*   **Purpose:** To teleport context to a fresh agent before "System Prompt Fade" occurs. The incoming agent reads these files to gain instant epistemic certainty.

## 3. The Persistent LLM Wiki (Synthesized Lore)
*   **Trigger:** The `aim_core/aim_reincarnate.py` script spawns `session_summarizer.py` as a detached daemon.
*   **Storage:** `wiki/` directory (Native Markdown).
*   **Mechanism:** The daemon drops "Signal Skeletons" into `wiki/_ingest/` and spawns a `wiki_agent` tmux session to weave the new knowledge into existing Markdown files.
*   **Purpose:** Human-readable, auto-maintaining architectural memory.

## 4. The Native Parquet Engine (The Subconscious)
*   **Trigger:** Native ingestion during reincarnation via `session_summarizer.py` or via `aim jack-in` for external cartridges.
*   **Storage:** 
    *   **RAM:** `memory_lance` (The live, mutable pool of flight recorders and wiki updates).
    *   **ROM:** `archive/cartridges/*.parquet` (Immutable, highly-compressed skill packages).
*   **Function:** Hybrid RAG (Semantic Vectors + Tantivy FTS).
*   **Purpose:** Token-efficient, zero-latency semantic retrieval for the Conscious Agent via `aim search`.

## 5. Eternal Recall (History Search)
*   **Trigger:** The `aim_core/handoff_pulse_generator.py` script.
*   **Storage:** `archive/history/` (Markdown).
*   **Function:** The raw markdown transcript of the dying session is saved here. It acts as the master ledger.

## 6. Sovereign Synchronization (The Export Layer)
*   **Trigger:** `aim_core/sovereign_sync.py` running during `aim push`.
*   **Storage:** `archive/sync/`
*   **Function:** Translates the binary LanceDB memory into deterministic `.jsonl` files.
*   **Purpose:** Git-friendly, mergeable brain backups.
