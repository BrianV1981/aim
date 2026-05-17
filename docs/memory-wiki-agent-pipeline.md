# Memory-Wiki Agent Pipeline

This document details the end-to-end execution pipeline of the A.I.M. Memory-Wiki architecture during a reincarnation cycle. It clarifies the sequence of operations, the different types of agents spawned, and the specific prompts utilized.

## Phase 1: The Trigger
The pipeline is initiated when the user executes the `/reincarnate` command.
1. `aim_core/aim_reincarnate.py` handles the immediate UI teleportation and spawns the new terminal session for the user.
2. Before the teleport finishes, it mechanically calls `aim_core/handoff_pulse_generator.py`.
3. `handoff_pulse_generator.py` prepares the `CURRENT_PULSE.md` for the new agent, archives the raw JSONL session transcript to `archive/history/`, and finally **spawns the `session_summarizer.py` daemon in the background** to handle the heavy lifting.

---

## Phase 2: Signal Extraction (The "Multiple Agents" Phase)
This is where the confusion arose regarding multiple agents running simultaneously. 

The `session_summarizer.py` script is responsible for converting a massive (e.g., 12MB) raw flight recorder into bite-sized architectural summaries. Because no LLM can process 12MB of context at once, it must break the file into 1,000-turn chunks.

For **each individual chunk**, the daemon does the following:
1. It calls `aim_core/reasoning_utils.py -> generate_reasoning()`.
2. To bypass REST API constraints and utilize the user's local authentication, `generate_reasoning()` executes a native `subprocess.run` command:
   ```bash
   gemini -p - -o json -y
   ```
3. **Crucial Point:** This command effectively spawns a headless, ephemeral Gemini CLI agent for *every single chunk*. If a session has 15 chunks, **15 separate, headless agents are sequentially spawned and destroyed.** These are the items appearing in the Gemini CLI background jobs list.

**The Prompt Provided to These Ephemeral Extraction Agents:**
> "You are the Subconscious Scribe. Analyze the following session transcript and extract the "Signal Skeleton" - the core architectural decisions, major bug fixes, newly established patterns, or important context that MUST be remembered for the future.
> OUTPUT RULES:
> - Output RAW Markdown only.
> - Do NOT output conversational fluff.
> - Be concise, direct, and factual.
> - Limit to 5-7 bullet points of the most critical takeaways."
> 
> *[Appended with the 1,000-turn chunk of the raw transcript]*

**The Output:**
The resulting markdown summaries (the "Signal Skeletons") are saved to the `memory-wiki/_ingest/` directory (e.g., `[session_id]_part1_summary.md`, `[session_id]_part2_summary.md`).

---

## Phase 3: Wiki Synthesis (The "Single Wiki Agent" Phase)
Once all 15 chunks have been extracted and saved to the `_ingest/` folder, `session_summarizer.py` moves to the next step: updating the persistent wiki.

1. It calls the `process_wiki()` function located in `aim_core/wiki_tools.py`.
2. `process_wiki()` verifies that files exist in `memory-wiki/_ingest/`.
3. It then spawns **exactly one** dedicated, detached `tmux` session named `wiki_agent_[timestamp]`.
4. Inside this single tmux session, it launches a persistent, interactive Gemini CLI agent in YOLO mode:
   ```bash
   tmux new-session -d -s wiki_agent_[timestamp] -c /home/kingb/aim/memory-wiki gemini --yolo
   ```

**The Prompt Injected into this Single Wiki Agent:**
> "Wake up. You have new session chunks waiting in the `_ingest/` directory. You MUST process them methodically ONE BY ONE: 1. Read the first chunk. 2. Weave its architectural insights into `index.md`, `log.md`, or relevant concept pages. 3. Immediately DELETE that specific chunk from `_ingest/` before moving to the next. 4. Repeat until the `_ingest/` directory is completely empty. 5. Once the directory is empty, type `/exit` to terminate this session."

**The Output:**
This single, autonomous agent methodically reads the extracted chunks, updates the markdown files in `memory-wiki/`, deletes the chunks from `_ingest/`, and then self-terminates.

---

## Phase 4: Permanent Archival
As the single Wiki Agent is working in the background, the `session_summarizer.py` script proceeds to its final, slowest step: natively embedding the raw, stripped transcript (located in `archive/history/`) directly into LanceDB using the local `nomic-embed-text` model via Ollama. 

This ensures that while the high-level architecture lives in the markdown Wiki, every granular detail is still searchable via the vector database.