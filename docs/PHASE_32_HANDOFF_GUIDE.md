# Phase 32: The Brain Overhaul Execution Guide

## ⚠️ WARNING TO THE NEXT AGENT
You are stepping into a complex, highly opinionated system. Do not start writing code blindly. Read this entire document. 
The current "Long-Term Memory" pipeline (Tiers 1-4) is **broken** (See Issue #77). It suffers from temporal drift, missing headers, and relies on full-document overwrites which are fundamentally unsafe for autonomous AI.
Your sole mission in Phase 32 is to **rip out the legacy memory architecture and replace it with a hyper-frequent, event-sourced "Delta Ledger" model.** 

This guide provides the exact roadmap, context, and constraints you need to succeed.

---

## 🧠 What You Need to Know (The Context)

1. **The Continuity Layer Works Perfectly:** The immediate session-to-session memory (`src/handoff_pulse_generator.py` and `CURRENT_PULSE.md`) works flawlessly. **Do not touch it.**
2. **The Engram DB Works Perfectly:** The local SQLite vector database (`archive/engram.db`) and the semantic search pipeline (`aim search`) are robust. **Do not touch them.**
3. **The Target is the Refinement Pipeline:** The scripts we are decommissioning are the "Scholastic Tiers":
   - `hooks/tier1_hourly_summarizer.py`
   - `src/tier2_daily_summarizer.py`
   - `src/tier3_weekly_summarizer.py`
   - `src/tier4_memory_proposer.py`
4. **The Universal Hook Router is Active:** Global hooks are now managed by a dynamic router (`scripts/aim_router.py`). When testing hooks, you must use this router; do not hardcode absolute paths to local scripts in the Gemini CLI settings.
5. **The TUI is Sensitive:** The `aim tui` (`scripts/aim_config.py`) manages the configuration for these pipelines. Changes to the pipeline architecture mean you must also update the TUI to reflect the new realities (e.g., removing the Chancellor/Dean/Librarian options).

---

## 🎯 The Goal: The "Delta Ledger" Architecture

Instead of waiting 24 hours to rewrite the entire `MEMORY.md` file, the new system will:
1. Summarize chat logs frequently (e.g., every 30 minutes).
2. Look at the summary and propose **Deltas** (Additions, Deletions, Modifications) to the `MEMORY.md`.
3. Give the Operator a simple `aim commit` command that acts as an intelligent merge tool, applying those explicit Deltas to the core file.

---

## 🗺️ The Execution Roadmap (Step-by-Step)

### Step 1: Architecture Lock & Decommissioning
- [ ] Read `docs/MEMORY_BRAIN_OVERHAUL_GAMEPLAN.md` to understand the theory behind the Delta Ledger.
- [ ] **Delete** the legacy memory scripts: `tier2_daily_summarizer.py`, `tier3_weekly_summarizer.py`, and `tier4_memory_proposer.py`.
- [ ] Remove all references to `cmd_memory` running Tiers 2-4 in `scripts/aim_cli.py`.
- [ ] **Delete** the legacy `src/indexer.py` script (it dangerously dumps raw JSON sessions into the vector DB, polluting it with noise).
- [ ] Update `scripts/aim_cli.py` so the `cmd_index` function triggers `src/bootstrap_brain.py` instead of the deleted `indexer.py`.

### Step 2: Build the Session Summarizer (Stage 1)
- [ ] Rename `hooks/tier1_hourly_summarizer.py` to `hooks/session_summarizer.py` (or similar clear name).
- [ ] Update `core/CONFIG.json` and the `aim_router` hook registration in `scripts/aim_init.py` to point to this new filename.
- [ ] **Fix the Temporal Bug:** Remove the logic that filters by "today's date". The summarizer should process *all* unread messages since the `last_indexed_turn`, regardless of the timestamp.
- [ ] **Output Constraint:** Force this script to output *only* a tight narrative summary of the session. Do not have it propose memory changes yet.

### Step 3: Build the Memory Delta Proposer (Stage 2)
- [ ] Create a new script: `src/memory_delta_proposer.py`.
- [ ] This script will read the recent narrative summaries (from Stage 1) and the current `core/MEMORY.md`.
- [ ] **The Prompt Constraint:** Force the LLM to output a strict schema. It must provide:
    - Rationale for the change.
    - Proposed Adds.
    - Proposed Removes.
    - Proposed Modifications.
    - An explicit `### 3. MEMORY DELTA` block containing the full candidate text for `MEMORY.md`.
- [ ] Wire this script into the `aim memory` CLI command so the Operator can trigger it manually.

### Step 4: The Intelligent Merge (`aim commit`)
- [ ] Rewrite `cmd_commit` in `scripts/aim_cli.py`.
- [ ] Instead of blindly replacing `core/MEMORY.md` with the proposal file, it should parse the `### 3. MEMORY DELTA` block from the latest proposal in `memory/proposals/` and safely apply it.
- [ ] Ensure it creates a `.bak` backup before writing.

### Step 5: TUI Refactoring (The Cockpit)
- [ ] Open `scripts/aim_config.py`.
- [ ] Remove the scholastic terminology (`librarian`, `chancellor`, `dean`).
- [ ] Replace them with literal functional names mapping to the new pipeline:
    - `session_summarizer`
    - `delta_proposer`
    - `consolidation_agent` (if a Tier 3 is still needed for apex merging)
- [ ] Update the TUI menus so the user can assign different LLM providers to these specific new stages.

### Step 6: Test Driven Development (TDD) Mandate
- [ ] **Crucial:** Before declaring victory, you must use `unittest.mock` to test the new pipeline.
- [ ] Look at `tests/test_aim_config.py` for an example of how we mock the `generate_reasoning` subprocess.
- [ ] Write a test in `tests/test_memory_pipeline.py` that injects a fake JSON chat history into the `session_summarizer.py` and verifies that the output summary is correctly formatted.

---

## 🛠️ Tips for the Next Agent

1. **Use `aim search`:** If you don't know how `generate_reasoning` works, or how to interact with the configuration dictionary, run `aim search "generate_reasoning"` to pull the exact syntax from the Engram DB.
2. **Be Surgical:** The GitOps mandate is strict. Do not refactor unrelated code. If you are fixing the `aim commit` logic, do not touch the `aim push` logic. 
3. **Handle Timeouts:** The `aim tui` has a history of hanging when executing subprocess calls to test providers. Use the `-y` flag or ensure STDIN is not blocked if you have to write new subprocess calls.
4. **Read `docs/BRAIN_MAP.md`:** If you are confused about where a file lives or what layer of the brain it belongs to, this map is your compass.

You are building the conscious mind of this platform. Keep it simple, keep it deterministic, and prove it works before you push.