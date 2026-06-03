# A.I.M. Reincarnate Protocol

This document formalizes the exact sequence of events that occur during an A.I.M. `/reincarnate` sequence. This protocol exists to prevent context window bloat (the "Amnesia Problem" and API 400/429 errors) while preserving absolute epistemic continuity across agent lifetimes using a "Parse Once, Route Everywhere" architecture.

---

## The 5-Phase Reincarnation Pipeline

### Phase 1: The Manual Gameplan (Operator / Live Agent)
Before reincarnation is ever triggered, the outgoing agent **must** execute its final cognitive task: distilling its active state into `continuity/REINCARNATION_GAMEPLAN.md`.
- **Format:** You MUST adhere strictly to the `aim_os/GAMEPLAN_SOP.md` structure (Commander's Summary, Tactical State, Localized Directory Map, Epistemic Warnings, and Immediate Next Action).
- **Enforcement:** The native `aim_core/aim_reincarnate.py` script enforces a 5-minute staleness check. If the Gameplan has not been written or updated recently, the script will mechanically block the handoff to prevent amnesia.

### Phase 2: The Signal Skeleton Extraction (`extract_signal.py` & `handoff_pulse_generator.py`)
Once the Reincarnate script is fired, the system bypasses the active context window and directly reads the raw `.jsonl` flight recorder from the Gemini CLI's hidden cache.
- **The Scrub (`aim_core/extract_signal.py`):** It surgically strips out massive, multi-megabyte JSON payloads, raw search results, and tool responses. It preserves only the pure conversational text, the agent's internal `<thoughts>`, and the names/intents of the tools executed.
- **The Routing (`aim_core/handoff_pulse_generator.py`):** This script takes the noise-reduced "Signal Skeleton" and routes it. It saves the full transcript permanently to `archive/history/[TIMESTAMP]_[SESSION_ID].md` and writes a rolling 5-turn delta to `continuity/CURRENT_PULSE.md` for instant, token-cheap awareness.

### Phase 3: The Subconscious Scribe (`session_summarizer.py`)
The system cannot feed the entire raw history directly into the permanent memory wiki. We use a **Direct Python Handoff** to securely offload this task.
- **The Trigger:** To guarantee execution and bypass fragile CLI `SessionEnd` hooks, `aim_core/aim_reincarnate.py` directly spawns the summarizer as a detached background daemon (`subprocess.Popen` with the `--bg` flag).
- **Vector Ingestion:** The background daemon natively chunks the new flight recorder (using the 500-1500 char Length-Constrained Accumulator) and mathematically embeds it directly into the `memory_lance` RAM pool for instant Hybrid RAG retrieval.
- **LLM Extraction:** If the session is massive, it chunks the transcript and passes it to an LLM using the strict `EXTRACTOR_SYSTEM` prompt, instructing it to output *only 5-7 concise bullet points* containing core architectural decisions or major bug fixes.
- **The Ingest Drop:** These highly distilled bullet points are saved as small `.md` files and dropped into the `memory-wiki/_ingest/` folder.

### Phase 4: Persistent Memory Weaving (`wiki_tools.py`)
The tiny summary files sitting in `_ingest/` must be integrated into the permanent knowledge base.
- **The Wiki Agent:** The Subconscious Scribe daemon spawns a dedicated, ephemeral `wiki_agent` in a background `tmux` session.
- **The Task:** It wakes up, reads the bullet points in `_ingest/`, and intelligently weaves those facts into the permanent Obsidian wiki files (e.g., `index.md`, `log.md`).
- **Cleanup & Re-embedding:** Once woven, the agent deletes the chunks from `_ingest/`. Crucially, the newly updated Wiki pages are re-embedded directly into `memory_lance` so the main `aim search` command can find the new lore semantically. The `wiki_agent` then gracefully exits.

### Phase 5: The Teleport (`aim_reincarnate.py`)
While Phases 3 and 4 handle long-term memory in the background, Phase 5 handles the immediate tactical handoff.
- **Sync:** The script synchronizes remote GitHub issues into `continuity/ISSUE_TRACKER.md`.
- **The Spawn:** It creates a brand-new, clean `tmux` session (`aim_reincarnation_[TIMESTAMP]`).
- **The Injection:** It pipes a strict wake-up prompt into the new agent's shell, commanding it to immediately read the `AGENTS.md` core constraints, the `REINCARNATION_GAMEPLAN.md`, and the `ISSUE_TRACKER.md`.
- **Termination:** The script prompts the operator to press Enter, which gracefully kills the bloated, outgoing agent, leaving only the fresh agent running with perfect Epistemic Certainty.
