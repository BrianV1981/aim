# Gameplan: Transitioning to the Persistent LLM Wiki Architecture

## The Problem
The current A.I.M. memory system is fractured. `core/MEMORY.md` is deprecated, stagnant, and the old 5-Tier Cascading Memory was removed. The Reincarnation loop successfully generates a clean session transcript (`archive/history/`), but the critical final step fails:
1. The transcript is passed to `session_summarizer.py`, which futilely tries to rewrite the deprecated `MEMORY.md`.
2. The transcript is *never* embedded/ingested into the `archive/project_core.db` for the Hybrid RAG search to use.
3. The LLM Wiki (Issue #264) was built but never initialized in the workspace, meaning there is no `memory-wiki/` directory to hold synthesized project lore.

## The Objective
We need to completely rip out the `MEMORY.md` dependency, initialize the Persistent LLM Wiki, and rewire the Reincarnation loop so that session logs are both vectorized (for RAG) and synthesized (for the Wiki).

## Execution Steps

### 1. Initialize the Persistent LLM Wiki
- **Action:** Create the `memory-wiki/` directory structure (`memory-wiki/_ingest/`, `memory-wiki/index.md`, `memory-wiki/log.md`).
- **Action:** Generate the `memory-wiki/WIKI_SCHEMA.md` system prompt so the Subconscious Daemon knows how to format the project lore.

### 2. Deprecate and Remove `core/MEMORY.md`
- **Action:** Delete `core/MEMORY.md`.
- **Action:** Remove any references to `core/MEMORY.md` from `GEMINI.md` and instruct the Conscious Agent to read `memory-wiki/index.md` instead.
- **Action:** Update the Conscious Agent's rules to drop new findings into `memory-wiki/_ingest/` rather than trying to edit memory directly.

### 3. Rewire the Reincarnation Pipeline (`handoff_pulse_generator.py`)
- **Action:** Modify `handoff_pulse_generator.py` so that when a session ends, it does TWO things with the clean flight recorder markdown:
  - **A. Vector Ingestion:** It automatically triggers an indexer to embed the markdown into `archive/project_core.db` so the Hybrid RAG search can find it later.
  - **B. Wiki Ingestion (The Drop Zone):** It drops a summary or the flight recorder itself into `memory-wiki/_ingest/` for the Subconscious Daemon to synthesize.

### 4. Obsidian Integration & The Dual-Search Architecture
The new system will operate on a "Dual-Search" architecture to maximize speed and semantic understanding:
- **Obsidian Native Sync:** The entire `memory-wiki/` directory is purely native Markdown. This means you can open the `memory-wiki/` folder directly as an Obsidian Vault. Any changes made by the Subconscious Daemon will instantly appear in your Obsidian knowledge graph.
- **Fast Lexical Search (`aim wiki search`):** We will keep the `wiki_tools.py` logic which builds an *in-memory* SQLite FTS5 database on the fly. This provides 0ms latency exact-keyword searches of the markdown files without needing to re-index them.
- **Deep Semantic Search (`aim search`):** To ensure the Conscious Agent can "feel" the architectural decisions via vector embeddings, the synthesized `memory-wiki/*.md` files MUST also be ingested into the `archive/project_core.db` vector store. We will update the background indexer to scan the `memory-wiki/` directory alongside the `archive/history/` directory.
- **Action:** Rip out the monolithic logic that tries to rewrite `MEMORY.md`.
- **Action:** Convert it into a clean pipeline trigger that:
  1. Embeds the raw history into `project_core.db`.
  2. Drops a synthesized "Signal Skeleton" into `memory-wiki/_ingest/`.
  3. Executes `aim wiki process` (or pings the daemon webhook) to have the secondary LLM synthesize the new lore into the `memory-wiki/` markdown files.

### 5. Manual & Automatic Triggers
- **Action:** Ensure `aim wiki process` works flawlessly when called manually via the CLI (for when the user drops PDFs or notes into `_ingest/`).
- **Action:** Ensure it fires automatically at the very end of the `/reincarnate` sequence.

## The End State
When you run `/reincarnate`:
1. The dying agent generates a clean Markdown log of the session.
2. That log is mathematically embedded into the SQLite `project_core.db` for instant Hybrid RAG search retrieval.
3. The core takeaways are dropped into `memory-wiki/_ingest/`.
4. A background (Subconscious) LLM wakes up, reads the ingest folder, updates `memory-wiki/index.md` with the new lore, and goes back to sleep.
5. The new agent wakes up with perfect, zero-latency access to both the raw vector history and the highly synthesized Wiki lore.