# A.I.M. Memory Pipeline Architecture

This document defines how information flows from a live chat into A.I.M.'s permanent architectural memory.

## 1. The Three-Tiered Storage Model
A.I.M. separates data based on its "Half-Life" and "Token Cost":

1.  **Forensic Tier (The Brain)**: Raw, scrubbed session JSONs. Indexed locally via Nomic.
    - **Purpose**: Semantic search and "trace-back" for specific technical details.
    - **Cost**: $0 (Local).
2.  **Narrative Tier (The Story)**: Daily logs (`memory/YYYY-MM-DD.md`).
    - **Purpose**: Human-readable history and project momentum.
    - **Cost**: Low (Local append).
3.  **Durable Tier (The Soul)**: Core rules and infrastructure (`core/MEMORY.md`).
    - **Purpose**: Foundational logic injected into every session start.
    - **Cost**: High (Permanent token tax).

## 2. The Flywheel Sequence
When a session ends or a checkpoint is reached, A.I.M. executes this exact sequence:

1.  **SCRUB**: `telemetry_scrubber.py` removes API keys and sensitive paths from raw logs.
2.  **INDEX**: `indexer.py` (Local) generates 768-dimension vectors for forensic search.
3.  **DISTILL**: `distiller.py` (GPT-5.4) analyzes the logs to find new "Atomic Truths."
4.  **PROPOSE**: The distiller writes a **Memory Delta** to `memory/proposals/`.

## 3. The Human-in-the-Loop Gate
To prevent "Memory Hallucination," A.I.M. does not automatically update its Core Memory. 

- **Discovery**: On session start, `context_injector.py` detects pending proposals and alerts the user.
- **Commitment**: The user reviews the proposal and runs `aim commit`.
- **Cleanup**: `aim commit` applies the update and archives the proposal to `memory/archive/`.

## 4. Token Discipline
- **Incremental Summaries**: `session_summarizer.py` only processes new messages since the last checkpoint.
- **Lean Mandate**: The distiller is prompted to keep `MEMORY.md` high-level, moving granular details to the forensic index.

"I believe I've made my point." — **A.I.M.**
