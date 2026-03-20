# A.I.M. Memory Pipeline Architecture

This document defines how information flows from a live chat into A.I.M.'s permanent architectural memory.

## 1. The Three-Tiered Storage Model
A.I.M. separates data based on its "Half-Life" and "Token Cost":

1.  **Forensic Tier (The Brain)**: Raw, scrubbed session JSONs. Indexed locally into `engram.db` (SQLite).
    - **Purpose**: Near-instant semantic search and "trace-back" for specific technical details.
    - **Cost**: $0 (Local).
2.  **Narrative Tier (The Story)**: Daily logs (`memory/YYYY-MM-DD.md`).
    - **Purpose**: Human-readable history and project momentum.
    - **Cost**: Low (Local append).
3.  **Durable Tier (The Soul)**: Core rules and infrastructure (`core/MEMORY.md`).
    - **Purpose**: Foundational logic injected into every session start.
    - **Cost**: High (Permanent token tax).

## 2. The Flywheel Sequence
When a session ends or a checkpoint is reached, A.I.M. executes this exact sequence:

1.  **SCRUB**: `telemetry_scrubber.py` dynamically removes secrets and paths.
2.  **INDEX**: `indexer.py` populates `engram.db` using local embeddings.
3.  **DISTILL**: `distiller.py` (Gemini Flash) analyzes logs for new "Atomic Truths."
4.  **PROPOSE**: The distiller writes a **Memory Delta** to `memory/proposals/`.

## 3. The Human-in-the-Loop Gate
To prevent "Memory Hallucination," A.I.M. does not automatically update its Core Memory. 

- **Discovery**: On session start, `context_injector.py` alerts the user of pending proposals.
- **Commitment**: The user reviews the proposal and runs `aim commit`.
- **Safety**: Every commit generates a `MEMORY.md.bak` shadow and validates syntax.

## 4. Concurrency & Reliability
- **Advisory Locking**: The flywheel uses `.aim.lock` to prevent race conditions during rapid session termination.
- **Path Normalization**: All pipeline components are now portable, resolving paths relative to the project root.

"I believe I've made my point." — **A.I.M.**
