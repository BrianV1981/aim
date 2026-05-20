# The Persistent LLM Wiki (Long-Term Memory)

This document outlines the mechanics of the A.I.M. Persistent Wiki. To prevent "Context Collapse" and token burn, A.I.M. physically separates reference data (RAG Cartridges) from synthesized logic (The Wiki) and offloads wiki maintenance to an event-driven background daemon.

## 1. The Dual-Search Architecture
The Wiki operates on a Dual-Search engine to maximize speed and semantic understanding:
*   **Fast Lexical Search (`aim wiki search`):** The `wiki_tools.py` logic builds an *in-memory* Tantivy index on the fly. This provides 0ms latency exact-keyword searches of the markdown files without needing to re-index them, protecting the agent's token wallet.
*   **Deep Semantic Search (`aim search`):** To ensure the Conscious Agent can "feel" the architectural decisions via vector embeddings, the synthesized `wiki/*.md` files are ingested natively into the `memory_lance` vector store alongside raw session flight recorders.
*   **Obsidian Native Sync:** The entire `wiki/` directory is purely native Markdown. It can be opened directly as an Obsidian Vault, providing a real-time graphical representation of the project's subconscious memory.

## 2. The Golden Rule of Epistemic Certainty
A "Conscious Agent" (the agent the operator is actively using) is strictly forbidden from manually editing the markdown wiki files. Forcing the primary agent to stop, cross-reference, and format markdown files creates severe latency and token burn.
*   **To Read:** Agents query the `wiki/` folder natively or use `aim wiki search`.
*   **To Write:** Agents must dump raw text files or "Eureka" moments directly into the `wiki/_ingest/` Drop Zone and go to sleep.

## 3. Event-Driven Offloading (Direct Python Handoff)
Wiki maintenance is handled exclusively by the Subconscious Scribe in the background, triggered automatically during Reincarnation.
1.  **The Trigger:** When `/reincarnate` is executed, the dying agent triggers `aim_core/aim_reincarnate.py`.
2.  **The Background Daemon:** The script spawns the `session_summarizer.py` scribe as a detached background daemon (`--bg` flag), completely decoupled from the active CLI session.
3.  **Vector Ingestion:** The daemon natively chunks the new flight recorder using the 500-1500 char Length-Constrained Accumulator and mathematically embeds it directly into the `memory_lance` RAM pool.
4.  **Memory Distillation:** The daemon uses an LLM to extract a concise list of the session's core architectural takeaways and drops the markdown into `wiki/_ingest/`.
5.  **The Wiki Agent:** Finally, it spawns the ephemeral `wiki_agent` tmux session. This agent wakes up, reads the ingest folder, seamlessly weaves the new knowledge into the existing Markdown wiki, logs the action to `wiki/log.md`, re-embeds the updated wiki directly into `memory_lance`, and gracefully exits.
