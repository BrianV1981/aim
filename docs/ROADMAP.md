# A.I.M. Roadmap: Project Singularity

## Goal
Transform A.I.M. into a professional-grade, self-maintaining intelligence layer that scales to hundreds of sessions while ensuring absolute system safety and zero token waste via the **Zero-Token Continuity Model**.

---

## Phase 21: CLI Agnosticism (The Codex Port) [BRAINSTORMING]
- [ ] **The Universal Adapter Layer:** Refactor A.I.M. to be fully agnostic of the underlying CLI (Gemini CLI vs. Codex CLI).
- [ ] **Native Hook Translation:**
    - *Context Injector:* Map the `BeforeModel` logic to Codex's `UserPromptSubmit` hook to seamlessly inject the Two-Brain state (`CURRENT_PULSE.md` + `FALLBACK_TAIL.md`).
    - *Failsafe Snapshot:* Map the `AfterTool` logic to Codex's `agent-turn-complete` hook to continually write the Dead Man's Switch (`FALLBACK_TAIL.md`).
    - *Clean Shutdown:* Bind the Distiller (`aim handoff`) to Codex's `Stop` hook to automatically generate the `CURRENT_PULSE.md` on agent exit.
- [ ] **Log Parsing Engine:** Write a new parser for `extract_signal.py` that reads Codex's specific transcript format (e.g., `~/.codex/memories`) to extract the intent/thought skeleton.
- [ ] **Dynamic Soul Generation:** Update `aim init` to generate an `AGENTS.md` (Codex) or `GEMINI.md` (Gemini CLI) based on the user's environment.
- [ ] **Config Wiring:** Update `aim init` to conditionally write A.I.M. hook mappings into `~/.codex/hooks.json`.

## Phase 20: The "Two-Brain" Separation (Working vs. Durable Memory) [PLANNED]
- [ ] **Decouple the Pipelines:** Radically separate the fast, short-term continuity engine from the slow, long-term memory refinement pipeline.
- [ ] **The Failsafe Context Tail (`FALLBACK_TAIL.md`):**
    - *Concept:* A Zero-Token "Dead Man's Switch" for continuity.
    - *Mechanism:* Update `scrivener_aid.py` (the `AfterTool` hook) to extract the last 5-10 turns of the raw JSON transcript and overwrite a single `continuity/FALLBACK_TAIL.md` file after *every single tool call*.
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
