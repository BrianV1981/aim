# A.I.M. Roadmap: Project Singularity

## Goal
Transform A.I.M. into a professional-grade, self-maintaining intelligence layer that scales to hundreds of sessions while ensuring absolute system safety and zero token waste via the **Zero-Token Continuity Model**.

---

## Phase 26: The Universal Binary (Global "Clawgle" Installation) [ON HOLD]
- [ ] **The Decoupling:** Refactor A.I.M.'s Python architecture so the engine can be installed globally (e.g., `~/.local/bin/clawgle`) rather than living inside the project it is managing.
- [ ] **Dynamic Scaffolding:** Update `init` so it can be run in any empty directory to instantly scaffold a localized Engram DB and Memory pipeline for that specific project.
- [ ] **Universal GitOps:** Ensure the Semantic Release and Bug Tracker tools can be used as generic dev-ops tools across any codebase, entirely independent of the AI features.

## Phase 25: The Initialization Overhaul (Polishing & Profiling) [PLANNED]
- [ ] **The "Clean Sweep" Protocol:** Overhaul `aim init` to act as a self-cleaning template. Add a prompt: **"Fresh Brain or Sync Brain?"**
    - *Fresh Brain:* Purges all existing `archive/sync/` chunks, `CHANGELOG.md`, and project-specific docs, replacing them with blank generic templates.
    - *Sync Brain:* Keeps the JSONL files and automatically imports them to seamlessly restore the operator's brain on a new machine.
- [ ] **The Index-Style `GEMINI.md`:** Stop generating a massive wall of text. `GEMINI.md` becomes a lean "Table of Contents" that strictly points the AI to `A_I_M_HANDBOOK.md` for rules and `ROADMAP.md` for tasks.
- [ ] **Idiot-Proof Retrieval Instructions:** Explicitly document the `aim search "query"` command in `GEMINI.md`. Add the conditional directive: *"When a deep search is required, `aim map` exists,"* preventing agents from spamming the map command for simple tasks.
- [ ] **Behavioral & Cognitive Guardrails:** Add interactive prompts during `aim init` to set the agent's Execution Mode (Autonomous vs. Cautious) and Grammar/Conciseness level. Bake these directly into the root `GEMINI.md`.
- [ ] **Hybrid Retrieval (Lexical + Semantic):** Upgrade `src/retriever.py` to support exact-match keyword search (FTS) alongside the existing Vector search, solving the "variable name lookup" weakness of pure semantic RAG.
- [ ] **Grok Profiling Integration:** Provide a direct hyperlink to X.com and an optimized Grok prompt during initialization. Save the resulting profile to `synapse/OPERATOR_PROFILE.md` so the personal context lives in the Engram DB, not the root prompt.

## Phase 24: The Contractor Protocol (Memory Isolation) [COMPLETED]
- [x] **The Panopticon Archive:** Ensure `session_porter.py` faithfully mirrors 100% of all JSON transcripts (both Prime Architect and subagents) to `archive/raw/` to preserve historical truth.
- [x] **The Contractor Tag:** Institute a programmatic `[EPHEMERAL]` tag or header logic for any subagent that is dispatched.
- [x] **The Tier 1 Bouncer:** Update `tier1_hourly_summarizer.py` and `indexer.py` to parse incoming JSONs for the subagent tag. If found, the scripts skip the file, preventing contractor noise from polluting the `memory/hourly` logs and the `engram.db`.

## Phase 23: The GitOps Bridge (Issue-Driven Architecture) [COMPLETED]
- [x] **Native Issue Tracking (`aim bug`):** Integrate GitHub CLI (`gh`) to allow A.I.M. to automatically create highly-structured bug tickets directly from the terminal, attaching the `FALLBACK_TAIL.md` for zero-friction stack traces.
- [x] **Branch-to-Issue Binding (`aim fix <id>`):** Automate the TDD loop. A.I.M. checks out a specific fix branch and pulls the issue context into the active session.
- [x] **Semantic Release Pipeline:** 
    - *Concept:* Implement an automated Changelog generator (based on the "Keep a Changelog" and Conventional Commits standards).
    - *Mechanism:* Update `aim push` to parse structured commit messages and automatically generate/update a human-readable `CHANGELOG.md` with version numbers, feature additions, and bug fixes.
    - *Goal:* Turn GitHub Issues and the `CHANGELOG.md` into the formal, public System of Record for the exoskeleton's evolution.

## Phase 22: CLI Agnosticism (The Codex Port) [BRAINSTORMING]
- [ ] **The Universal Adapter Layer:** Refactor A.I.M. to be fully agnostic of the underlying CLI (Gemini CLI vs. Codex CLI).
- [ ] **Native Hook Translation:**
    - *Context Injector:* Map the `BeforeModel` logic to Codex's `UserPromptSubmit` hook to seamlessly inject the Two-Brain state (`CURRENT_PULSE.md` + `FALLBACK_TAIL.md`).
    - *Failsafe Snapshot:* Map the `AfterTool` logic to Codex's `agent-turn-complete` hook to continually write the Dead Man's Switch (`FALLBACK_TAIL.md`).
    - *Clean Shutdown:* Bind the Distiller (`aim handoff`) to Codex's `Stop` hook to automatically generate the `CURRENT_PULSE.md` on agent exit.
- [ ] **Log Parsing Engine:** Write a new parser for `extract_signal.py` that reads Codex's specific transcript format (e.g., `~/.codex/memories`) to extract the intent/thought skeleton.
- [ ] **Dynamic Soul Generation:** Update `aim init` to generate an `AGENTS.md` (Codex) or `GEMINI.md` (Gemini CLI) based on the user's environment.
- [ ] **Config Wiring:** Update `aim init` to conditionally write A.I.M. hook mappings into `~/.codex/hooks.json`.

## Phase 21: The Cascading Memory Engine (Self-Cleaning Distillation) [COMPLETED]
- [x] **The Significance Filter (Hourly):** Restore the 5-line delta logic to trigger the background extraction script automatically.
- [x] **Literal Naming Schema:** Rename the Scholastic Hierarchy to literal functional names (e.g., `tier1_hourly_summarizer.py`, `tier2_daily_summarizer.py`, `tier4_memory_proposer.py`) to demystify the architecture.
- [x] **Delta Pruning Prompts:** Rewrite the AI prompts for Tiers 2, 3, and 4 to actively compare incoming logs against `core/MEMORY.md`, identifying stale facts to remove and new facts to add.
- [x] **Automatic Garbage Collection:** 
    - *Mechanism:* Tie the deletion of lower-tier logs to the successful generation/approval of upper-tier logs.
    - *Goal:* Ensure the `memory/` folder physically cannot bloat. Once 24 hourly logs are rolled into a Daily Report, the hourlies are deleted. Once 7 Dailies are rolled into a Weekly Arc, the Dailies are deleted.
- [x] **The Dual-Target Pulse (Obsidian Native):** 
    - *Concept:* Keep the AI's context lean while preserving a rich history for human visualization in Obsidian.
    - *Mechanism:* `aim handoff` will generate two copies: a single `CURRENT_PULSE.md` for the AI, and a timestamped copy in `memory/pulses/` for Obsidian.
    - *Formatting:* The AI will output Obsidian-native markdown, including YAML frontmatter, tags (e.g., `#bugfix`), and explicit wikilinks (e.g., `[[src/main.py]]`) to construct a visual graph.
- [x] **Obsidian Failsafe Sync:** Ensure the clean `.md` output of this cascading system is perfectly mapped for local vault backup via Obsidian.

## Phase 20: The "Two-Brain" Separation (Working vs. Durable Memory) [COMPLETED]
- [ ] **Decouple the Pipelines:** Radically separate the fast, short-term continuity engine from the slow, long-term memory refinement pipeline.
- [ ] **The Failsafe Context Tail (`FALLBACK_TAIL.md`):**
    - *Concept:* A Zero-Token "Dead Man's Switch" for continuity.
    - *Mechanism:* Update `failsafe_context_snapshot.py` (the `AfterTool` hook) to extract the last 5-10 turns of the raw JSON transcript and overwrite a single `continuity/FALLBACK_TAIL.md` file after *every single tool call*.
    - *Goal:* Provide perfect, free situational awareness if `/handoff` fails or the terminal crashes.
- [ ] **The Single Pulse (`CURRENT_PULSE.md`):**
    - *Concept:* Eliminate timestamped continuity folder bloat.
    - *Mechanism:* `aim handoff` and `aim pulse` will overwrite one single file (`continuity/CURRENT_PULSE.md`). Stop generating `REPORT_*.md` files.
- [ ] **Dual-Injection Onboarding:**
    - *Mechanism:* Update `context_injector.py` to read *both* `CURRENT_PULSE.md` (for high-level strategic intent) and `FALLBACK_TAIL.md` (for exact tactical reality of the last 5 turns) and inject them at session start.
- [ ] **Asynchronous Memory Refinement:**
    - *Concept:* Relegate the "Scholastic Hierarchy" (Librarian/Chancellor/Dean) to a background data-processing pipeline triggered by `aim memory` or `aim clean`.
    - *Mechanism:* This pipeline processes raw transcripts -> daily logs (`memory/YYYY-MM-DD.md`) -> memory proposals -> `core/MEMORY.md`, completely independently of the fast continuity system.

## Phase 19: Universal Sovereignty & MCP [COMPLETED]
- [x] **Universal Hub Overhaul:** Implementation of Frontier OAuth, Multi-Provider TUI, and Cognitive Health Checks.
- [x] **MCP Server Implementation:** Built a Model Context Protocol server so A.I.M.'s Engram DB can be used in Cursor, VS Code, and Claude Desktop.
- [x] **Sovereign Sync:** Implement compressed-chunk Git synchronization for sharing brains via GitHub without merge conflicts.
- [x] **"Index-First" Retrieval Protocol:**
    - *Concept:* Transition from "Injection-First" to "Selection-First" memory access.
    - *Mechanism:* Instead of searching the DB blindly, the agent is first provided with a surgical **Index of Keys** (Milestone titles, Phase names, File symbols) via `aim map`.
    - *Workflow:* 1. List Index (`aim map`) -> 2. Select Relevant Keys -> 3. Surgical Recall (`aim search "Key"`).
    - *Goal:* Scale A.I.M. to massive ecosystem-level projects (10,000+ fragments) without ever hitting the context wall or bloating the first prompt.

## Phase 18: The Scholastic Memory Model [COMPLETED]
- [x] **Signal-First Refinement:** Reduced session noise by 92% via `extract_signal.py`.
- [x] **Scholastic Tiers:** Implemented hierarchical synthesis chain (Librarian, Chancellor, Fellow, Dean).
- [x] **Cognitive Gating:** Added TUI-level controls for per-tier model and provider selection.
- [x] **Synapse Exchange:** Built the portable brain import/export system (`.aim` packs).
- [x] **Adaptive Chunking:** Finalized the recursive windowing logic for 1,000+ turn sessions.

## Phase 17: Multi-Agent Concurrency & Zero-Token Momentum [COMPLETED]
- [x] **Porter-Processor Scrivener:** Implemented local transcript mirroring for multi-agent safety.
- [x] **Synapse Synergy:** Established the recursive intake pipeline for massive knowledge ingestion.
- [x] **One-Time Bootloading:** Refactor `context_injector.py` to only perform a single injection of project state at session start.
- [x] **Librarian Refinement:** Pivot the Distiller to generate Pulses optimized for start-of-session onboarding.

## Phase 16: The RBO Prototype (End Game Architecture) [COMPLETED]
- [x] **Project Singularity:** Transitioned from context-heavy to retrieval-native soul.
- [x] **Invisible Infrastructure:** Radical simplification of workspace via Engram DB offloading.
- [x] **The Pre-Born Brain:** Implemented automatic foundation indexing during `aim init`.
- [x] **Pre-Compression Shield:** Hardened history archival against context window summarization.

*Last Updated: 2026-03-21*
