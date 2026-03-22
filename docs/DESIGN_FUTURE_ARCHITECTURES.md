# Architectural Design: Phase 24+ Brainstorming
**Status:** Brainstorming / Planning Phase
**Note:** The concepts below are solid core ideas currently undergoing refinement. They represent the next logical leaps for A.I.M.'s scale and deployment mechanics.

---

## IDEA 1: The Contractor Protocol (Memory Isolation)
**Goal:** Prevent subagent (contractor) noise from polluting the Prime Agent's long-term memory, while keeping the architecture lean and avoiding database bloat.

### 1.1 The Core Philosophy
A.I.M. is shifting towards a **"Prime Architect vs. Ephemeral Contractor"** model.

*   **The Prime Architect (Forever Session):** The main agent runs in a continuous, long-lived session. It holds the high-level context, makes architectural decisions, and relies on aggressive garbage collection (The Cascading Sieve) to keep its context window clean over time.
*   **The Contractors (Subagents):** Highly specialized agents spun up for specific, tactical tasks (e.g., auditing Rust code, investigating a file, running a test suite). They execute the task, return a report, and are then "killed."

### 1.2 The Problem: Memory Contamination
Currently, subagents generate their own massive JSON transcripts in the temporary CLI folder. If these transcripts are mirrored to `archive/raw/`, they are picked up by the Librarian (`tier1_hourly_summarizer.py`). 
This means a subagent's frantic, trial-and-error terminal thrashing gets permanently baked into the Daily Log, polluting the Prime Architect's memory and bloating the Engram DB.

### 1.3 Rejected Solutions
#### ✖ Multiple Databases (The Archipelago Model)
*Idea:* Give every subagent its own SQLite database (`engram_rust_auditor.db`).
*Why we rejected it:* Too much infrastructure overhead. It breaks the simplicity of Sovereign Sync (translating one DB to JSONL) and makes it difficult for the Prime Agent to query across domains if needed.

#### ✖ Database Namespacing (The Megacity Model)
*Idea:* Add an `agent_id` column to the `engram.db` and run complex SQL `DELETE` commands when the subagent dies.
*Why we rejected it:* Leaves "ghost" fragments if the cleanup script fails. Requires constant SQL filtering to prevent cross-contamination hallucinations.

### 1.4 The Chosen Solution: The Panopticon Archive + The Tier 1 Bouncer
We must balance the need for absolute historical truth against the need for a lean, unpolluted Engram DB. We achieve this by separating the *Storage* layer from the *Refinement* layer.

1. **The Panopticon Archive (`archive/raw/`):** 
   - `session_porter.py` mirrors **100%** of all active sessions (Prime Architect AND all Subagents) into the raw archive. 
   - *Why:* Because the Gemini CLI natively compresses and destroys raw history at 50% context capacity. The Panopticon ensures every single keystroke, tool call, and hallucination is saved permanently for forensic auditing.

2. **The Contractor Tag:** 
   - Whenever a subagent is dispatched, its initial prompt includes a hidden metadata tag (e.g., `[EPHEMERAL]`).

3. **The Bouncer (`tier1_hourly_summarizer.py`):** 
   - Instead of dropping the file at the Porter level, the "Bouncer" logic is moved to the Tier 1 Librarian.
   - When the Librarian wakes up to summarize the raw archive, it checks the transcript. If it sees the `[EPHEMERAL]` tag, it skips the file.
   
4. **The Result:** 
   - The subagent's raw JSON is saved forever in `archive/raw/` (The Historical Truth).
   - But the subagent's noise never reaches the Daily Log, the Memory Proposals, or the `engram.db` (The Refined Soul).

---

## IDEA 2: The Universal Repository (Unified Installer)
**Goal:** Prevent maintaining two separate Git repositories (Gemini vs. Codex) while ensuring the agent environment is perfectly tuned to the specific CLI architecture.

### 2.1 The Problem
The Gemini CLI uses real-time, streaming hooks (`AfterTool`), while the Codex CLI uses batch hooks (`agent-turn-complete`). Maintaining a branch or a completely separate repository just to handle these "Edge Adapters" creates massive code duplication and maintenance debt.

### 2.2 The Proposed Solution: Dynamic Provisioning
Instead of shipping *both* sets of instructions/hooks natively, we build one Universal Repository that acts as a chameleon. 

1. **The Interrogation (The Fork):**
   When the user runs `setup.sh` or `aim init`, the installer explicitly asks:
   > *"Select your exoskeleton environment:"*
   > *1. Gemini CLI (Streaming Hooks)*
   > *2. Codex CLI (Batch Hooks)*

2. **The Environment Build:**
   Based on the selection, `aim_init.py` acts as a package manager:
   - **If Gemini:** It generates `GEMINI.md`, installs the `hooks_gemini/` Python scripts, and wires `~/.gemini/settings.json`.
   - **If Codex:** It generates `AGENTS.md`, installs the `hooks_codex/` Python scripts, and wires `~/.codex/hooks.json`.

3. **The Cleanup:**
   Once provisioned, the installer permanently deletes the unused files from the workspace (e.g., if Codex is chosen, it deletes `GEMINI.md` and the Gemini hooks directory). 

### 2.3 The Architectural Benefit
- The core logic (`engram.db`, Semantic Search, Distiller, TUI) remains identical and unified in one GitHub repository.
- The local execution environment slims down instantly, avoiding false promises. The repository doesn't pretend to work for both simultaneously—it formally mutates itself into the chosen architecture upon installation.

## Next Steps for Refinement
- Determine the exact tagging syntax we want to enforce for subagents (Idea 1).
- Map out the exact folder structures for separating `hooks_gemini/` and `hooks_codex/` in the universal repository (Idea 2).