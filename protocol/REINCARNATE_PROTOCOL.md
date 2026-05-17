# A.I.M. Reincarnate Protocol

This document formalizes the exact sequence of events that occur during an A.I.M. `/reincarnate` sequence. This protocol exists to prevent the context window bloat (Amnesia Problem and API 400/429 errors) while preserving absolute epistemic continuity across agent lifetimes.

---

## The 5-Phase Reincarnation Pipeline

### Phase 1: The Manual Gameplan (Operator / Live Agent)
Before reincarnation is ever triggered, the outgoing agent **must** execute its final cognitive task: distilling its active state into `continuity/REINCARNATION_GAMEPLAN.md`.
- **Purpose:** To provide the incoming, blank-slate agent with immediate directives, warnings (e.g., "Do not over-engineer this"), and context on what was just completed.
- **Enforcement:** The native `aim_reincarnate.py` script enforces a 5-minute staleness check. If the Gameplan has not been written or updated recently, the script will mechanically block the handoff to prevent amnesia.

### Phase 2: The Signal Skeleton Extraction (`handoff_pulse_generator.py`)
Once the Reincarnate script is fired, the system bypasses the active context window and directly reads the raw `.jsonl` flight recorder from the Gemini CLI's hidden cache.
- **The Scrub:** It surgically strips out massive, multi-megabyte JSON payloads, raw search results, and tool responses. 
- **The Skeleton:** It preserves only the pure conversational text, the agent's internal `<thoughts>`, and the names/intents of the tools executed.
- **Output:** This noise-reduced "Signal Skeleton" is converted to standard Markdown and saved permanently to `/archive/history/[TIMESTAMP]_[SESSION_ID].md`. It also writes a rolling delta to `continuity/LAST_SESSION_FLIGHT_RECORDER.md`.

### Phase 3: The Subconscious Scribe (`session_summarizer.py`)
The system cannot feed the entire raw history (which may be tens of thousands of lines) directly into the permanent memory wiki.
- **The Trigger (Direct Python Handoff):** To guarantee execution and bypass the fragile Gemini CLI `SessionEnd` hook, `aim_reincarnate.py` directly spawns the summarizer as a detached background daemon (`subprocess.Popen` with the `--bg` flag) the exact moment the Signal Skeleton is generated.
- **The Daemon:** The `session_summarizer.py` script wakes up in the background and reads the newly generated Markdown Signal Skeleton.
- **Chunking:** If the session is massive, it chunks the transcript by conversational turns to avoid overwhelming the LLM API.
- **LLM Extraction:** It passes these chunks to an LLM using the strict `EXTRACTOR_SYSTEM` prompt, instructing it to ignore conversational fluff and output *only 5-7 concise bullet points* containing core architectural decisions, major bug fixes, or newly established patterns.
- **The Ingest Drop:** These highly distilled, hyper-dense bullet points are saved as small `.md` files and dropped into the `/memory-wiki/_ingest/` folder.

### Phase 4: Persistent Memory Weaving (`wiki_tools.py`)
The tiny summary files sitting in `_ingest/` must be integrated into the permanent knowledge base.
- **The Wiki Agent:** A dedicated, ephemeral `wiki_agent` is spawned in a background `tmux` session.
- **The Task:** It wakes up, reads the bullet points in `_ingest/`, and intelligently weaves those facts into the permanent Obsidian wiki files (e.g., `index.md`, `log.md`, `LoCoMo-Character-Profiles.md`).
- **Cleanup:** Once a chunk is woven into the wiki, the agent deletes that chunk from the `_ingest/` directory to keep it clean. It then gracefully exits.

### Phase 5: The Teleport (`aim_reincarnate.py`)
While Phases 3 and 4 handle long-term memory in the background, Phase 5 handles the immediate tactical handoff.
- **Sync:** The script synchronizes remote GitHub issues into `continuity/ISSUE_TRACKER.md`.
- **The Spawn:** It creates a brand-new, clean `tmux` session (`aim_reincarnation_[TIMESTAMP]`).
- **The Injection:** It pipes a strict wake-up prompt into the new agent's shell, commanding it to immediately read the `REINCARNATION_GAMEPLAN.md` and the `ISSUE_TRACKER.md`.
- **Termination:** The script prompts the operator to press Enter, which gracefully kills the bloated, outgoing agent, leaving only the fresh agent running.
