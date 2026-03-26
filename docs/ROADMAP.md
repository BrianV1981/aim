# A.I.M. Roadmap: Project Singularity

## Goal
Transform A.I.M. into a professional-grade, self-maintaining intelligence layer that scales to hundreds of sessions while ensuring absolute system safety and zero token waste via the **Zero-Token Continuity Model**.

---

## Phase 39: The Sovereign Comlink (Full Two-Way Remote CLI) [PLANNED]
- [ ] **Native Discord/Telegram Integration:** Build a secure, persistent bot daemon that connects A.I.M. directly to a private Discord server or Telegram chat.
- [ ] **Remote Conversational Interface:** Allow the Operator to have full, two-way conversational interactions with the A.I.M. exoskeleton from their phone, exactly as if they were sitting at the Gemini CLI terminal. 
- [ ] **Remote Shell Execution:** When commanded via Discord, the agent must be able to natively execute `aim` commands, run `pytest`, and manipulate the local host filesystem, streaming the results and thoughts back to the chat application.

## Phase 38: The P2P DataJack Swarm (Decentralized Knowledge) [PLANNED]
- [ ] **Frictionless Magnet Loading:** Upgrade `aim jack-in` to natively accept magnet links (e.g., `aim jack-in "magnet:?xt=..."`). The CLI should handle the P2P handshake, download the `.engram` into memory, inject the vectors into SQLite, and self-clean without requiring the user to install a 3rd-party torrent client.
- [ ] **Native Python Torrent Engine:** Integrate a lightweight P2P library (like `libtorrent` via Python bindings) directly into the A.I.M. dependency stack.
- [ ] **Opt-In Background Seeding:** Add a configuration toggle in `aim tui` to enable background seeding. When active, the `aim daemon` will silently seed the operator's local `.engram` cartridges to the swarm, ensuring the survival of valuable community heuristics.

## Phase 37: The Matrix Swarm (Dynamic Aliasing) [COMPLETED]
- [x] **Portable Multi-Instance Routing:** Refactored `setup.sh` to dynamically capture the `basename` of the installation directory and bind the CLI alias to that specific folder name (e.g., `aim-backend`, `aim-frontend`).
- [x] **Namespace Segregation:** Operators can now run dozens of completely isolated A.I.M. exoskeletons in parallel across different project folders with zero alias collisions, enabling a true "Swarm" of specialized Matrix Agents.

## Phase 36: The DataJack Foundry (Atomic Cartridge Pipeline) [COMPLETED]
- [ ] **Export MCP Bug Fix:** Repair `skills/export_datajack_cartridge.py` to properly handle raw string arguments vs JSON payloads, preventing the `JSONDecodeError` that currently breaks the skill.
- [ ] **The "Factory Floor" Protocol (`aim bake`):** Formalize the process of manufacturing atomic `.engram` cartridges without hacking the active database. Build a new command: `aim bake <raw_docs_dir> <cartridge_name.engram>`.
    - **Namespace Isolation:** The command must spin up a temporary, isolated SQLite database (e.g., `/tmp/aim_factory/factory.db`) so it NEVER touches or corrupts the operator's active `archive/engram.db` or `archive/sync/` files.
    - **Targeted Ingestion:** It points the embedding logic strictly at the target `<raw_docs_dir>` and vectorizes only those files into the temporary database.
    - **Direct Export:** It runs the DataJack export protocol directly against the temporary database, spitting out the pristine atomic `.engram` file into the project root.
    - **Self-Cleaning:** It instantly deletes the temporary database and cache, leaving zero cross-contamination.
- [ ] **Cartridge Manifests:** Ensure exported cartridges embed metadata about what they contain (e.g., "Django Docs 5.0", "Pytest 8.0") so operators aren't guessing what is inside an atomic engram.

## Phase 35: The Heuristic Engram (Troubleshooting Matrices) [PLANNED]
- [ ] **Forum & Issue Ingestion Pipeline:** Build a specialized scraper/ingestion pipeline to pull resolved public troubleshooting threads (e.g., from StackOverflow, Python developer forums, and closed GitHub repository issues) into the `synapse/` folder.
- [ ] **Generalized Debugging Cartridges:** Compile a generalized `python_troubleshooting.engram`. This avoids the "benchmark cheating" perception of hyper-specific docs, instead giving the agent a generalized database of human debugging heuristics, edge-case resolutions, and historical GitHub bug reports.
- [ ] **Heuristic Search Mandate:** Update the `GEMINI.md` standard operating procedures so the agent natively queries the troubleshooting engram when it encounters an obscure error code that isn't covered in the official textbooks.

## Phase 34: Open-Source Maturity & Packaging [COMPLETED]
- [ ] **Dependency Audit:** Verify that `fastmcp`, the `ollama` client (if used natively), and any implicit vector math dependencies are explicitly declared in `requirements.txt`.
- [ ] **Directory Manifests:** Add a `README.md` to `continuity/`, `workspace/`, `scripts/`, `src/`, and `archive/` defining their exact architectural purpose and boundaries so new contributors aren't guessing.
- [ ] **CI/CD Hardening:** Ensure `.github/workflows/test.yml` is fully wired to run `pytest` on every push to catch UI/CLI parsing regressions before they hit the `main` branch.
- [ ] **Known Issues Documentation:** Add a "First Run / Known Issues" section to the Installation Guide setting honest expectations about the TUI's sensitivity to upstream API changes.
- [ ] **v2 Packaging Spec:** Research migrating the tool from the `setup.sh` alias approach to a standard `pyproject.toml` / `pipx` installation path to allow for package manager auto-completion and standard Python distribution.

## Phase 33: The Cognitive Mantra Protocol (Anti-Drift Shield) [COMPLETED]
- [ ] **Dual-Mode Attention Reset Hook:** Build `hooks/cognitive_mantra.py` to mathematically counter the "Lost in the Middle" context degradation in long-horizon LLM sessions.
- [ ] **Dynamic Tool Tracking:** Implement a state mechanism that counts autonomous *tool calls* (steps) rather than operator interactions, ensuring the AI stays leashed during long background execution loops.
- [ ] **The Subconscious Whisper (Every 25 Steps):** Inject silent, zero-output reminders of core TDD/GitOps guardrails into the system payload to reset attention weights, utilizing API Context Caching for near-zero cost.
- [ ] **The Conscious Mantra (Every 50 Steps):** Force the LLM to actively output its absolute core mandates (from `GEMINI.md`) inside a `<MANTRA>` block, using autoregressive generation to completely wash away "vibe coding drift."

## Phase 32: The Memory Brain Overhaul (Delta Ledgers & Synthesis) [PLANNED]
- [ ] **Reference Spec:** See `MEMORY_BRAIN_OVERHAUL_GAMEPLAN.md` for the target cadence and artifact schema.
- [ ] **Step 1 - Architecture Lock:** Transition the memory pipeline from "Full State Overwrites" to an "Event Sourcing / Delta Ledger" model. Lower tiers will no longer blindly rewrite the entire `MEMORY.md` file.
- [ ] **Step 2 - The Artifact Split:** Implement the physical split between *Narrative Summaries* (The Librarian/Scribe) and explicit *Memory Delta Proposals* (Adds, Removes, Modifications, Rationale).
- [ ] **Step 3 - The Intelligent Merge (`aim commit`):** Evolve the `aim commit` command from a dumb file-replacer into an AI-assisted synthesis tool that intelligently merges Delta Ledgers into the core `MEMORY.md` upon Operator approval.
- [ ] **Step 4 - Config & Cadence Routing:** Update `core/CONFIG.json` to support per-stage cadence (e.g., 30-min summaries, hourly deltas, daily consolidations) and per-stage provider routing, shifting away from hardcoded intervals.
- [ ] **Step 5 - TUI Expansion:** Expose the new cadence controls, tier routing, and explicit Health Visibility for continuity artifacts (`CURRENT_PULSE.md` and `FALLBACK_TAIL.md`) directly in the `aim tui`.
- [ ] **Step 6 - Semantic Naming Migration:** Once the behavior is stable, execute Phase A (User-Facing Labels) to migrate TUI labels from scholastic terms (Librarian/Chancellor) to literal functional names (Session Summarizer, Memory Delta Proposer).

## Phase 31: Identity Canonicalization (`OPERATOR.md`) [COMPLETED]
- [x] **Canonical Operator Record:** Replace `core/USER.md` with `core/OPERATOR.md` so the file name matches the actual doctrine: the user is the operator.
- [x] **Core Identity Consolidation:** Keep structured operator identity and narrative operator persona in `core/`, not `synapse/`.
- [x] **Onboarding Mapping:** Document the identity split and onboarding destinations so `OPERATOR.md`, `OPERATOR_PROFILE.md`, `MEMORY.md`, and `CONFIG.json` have clear boundaries.

## Phase 30: The Autonomous Daemon (State Machine Logic) [COMPLETED]
- [x] **The Background Daemon:** Build `src/daemon.py`, a persistent 24/7 background process (the "ghost in the machine") that acts as the ultimate heartbeat loop for the exoskeleton.
- [x] **Environmental Polling (The Senses):** Before waking up the AI, the Daemon runs a strict `If/Then` diagnostic matrix:
    - *The Combat Loop:* Runs `pytest`. If tests are failing, the Daemon wakes the AI with an urgent prompt to fix the build.
    - *The Looting Loop:* Checks `gh issue list`. If there are open bugs, it directs the AI to isolate a branch and patch them.
    - *The Nav Loop:* Checks `git status`. If there are uncommitted files, it commands the AI to finish its current thought and push.
    - *The Buff Loop:* If the environment is completely green, it commands the AI to read `ROADMAP.md` and start the next phase.
- [x] **Daemon TUI Controls:** Add a "Manage Autonomous Daemon" menu to `aim tui` to allow the operator to set sleep intervals, toggle diagnostic checks, or kill the background process.

## Phase 29: The Universal Skills Framework (MCP-Driven Actions) [COMPLETED]
- [x] **The Skills Directory:** Create a `skills/` folder where operators can drop executable Python/Bash scripts paired with a `SKILL.md` manifest.
- [x] **MCP Tool Translation:** Update the `fastmcp` server (`src/mcp_server.py`) to automatically read the `skills/` directory and expose every script as an official MCP Tool.
- [x] **CLI-Agnostic Execution:** Because skills are routed through the standardized MCP protocol, Gemini CLI, Claude Code, and Codex will all natively inherit the ability to trigger these custom actions without needing CLI-specific adapter code.
- [x] **Phase 29.5 (The Skill Sandbox):** Implement bubblewrap (`bwrap`) to enforce a read-only filesystem, kill network access, and apply a 60-second hard timeout for absolute RCE protection.

## Phase 28: Auto-Memory Distillation (Total Autonomy) [COMPLETED]
- [x] **Autonomous Core Commits:** Remove the human "airgap" for core memory updates. Allow the system to automatically run `aim commit` at a designated tier.
- [x] **TUI Toggle:** Add a configuration slider in the `aim tui` to select the auto-commit frequency (e.g., Off, Daily, Weekly, Monthly).
- [x] **The Monthly Default:** Turn T4 (Monthly) Auto-Commit ON by default. This guarantees that even if the operator ignores the memory pipeline, the agent acts as a living organism, slowly and methodically evolving its fundamental `MEMORY.md` over time.

## Phase 26: The Security Audit & Hardening [COMPLETED]
- [x] **Hook Resilience:** Fixed unclosed `stdin` pipes in the failsafe hook and enforced a strict fail-closed (deny) policy in the `safety_sentinel.py` LLM audit.
- [x] **Regex False-Positive Mitigation:** Tightened generic JSON key-value scanning in `secret_shield.py` and restricted IP address scraping boundaries to prevent breaking SemVer strings.
- [x] **Path Escapes:** Secured `workspace_guardrail.py` to correctly resolve `../` relative path escapes against the current working directory.
- [x] **Environment Stability:** Refactored `aim_init.py` to use safe JSON serialization (`json.dumps`) instead of fragile string formatting, fixed `NameError` traps, and added OS-level package checks (`dbus-x11`) to the installation script.
- [x] **GitOps Safety:** Update `aim_push.sh` to prevent `git add .` from indiscriminately staging untracked temp files or debug artifacts.
- [x] **DRY Refactoring:** Extract duplicated `commit_proposal()` logic from the deep restore scripts into a shared utility, and fix chronological sorting bugs.

## Phase 25: The Initialization Overhaul (Polishing & Profiling) [COMPLETED]
- [x] **The "Clean Sweep" Protocol (Decoupled):** Overhaul `aim init` to separate the workspace from the brain:
    - *Prompt 1 (Workspace):* "Keep project docs or start fresh?" (Wipes `ROADMAP.md`, `CHANGELOG.md` if fresh).
    - *Prompt 2 (Brain):* "Sync existing Brain or wipe memory?" (Imports or deletes `archive/sync/` JSONL files). This allows users to start a new codebase but plug in an experienced, pre-trained AI brain.
- [x] **The Index-Style `GEMINI.md`:** Stop generating a massive wall of text. `GEMINI.md` becomes a lean "Table of Contents" that strictly points the AI to `A_I_M_HANDBOOK.md` for rules and `ROADMAP.md` for tasks.
- [x] **Idiot-Proof Retrieval Instructions:** Explicitly document the `aim search "query"` command in `GEMINI.md`. Add the conditional directive: *"When a deep search is required, `aim map` exists,"* preventing agents from spamming the map command for simple tasks.
- [x] **Behavioral & Cognitive Guardrails:** Add interactive prompts during `aim init` to set the agent's Execution Mode (Autonomous vs. Cautious) and Grammar/Conciseness level.
- [x] **TUI Onboarding Updater:** Allow users to "Skip" the behavioral questions during init. If skipped, inject a note into `GEMINI.md` directing them to run `aim tui`. Add a new menu in `aim tui` to dynamically update the Operator Profile and Behavioral Guardrails at any time without re-running `setup.sh`.
- [x] **Hybrid Retrieval (Lexical + Semantic):** Upgrade `src/retriever.py` to support exact-match keyword search (FTS) alongside the existing Vector search, solving the "variable name lookup" weakness of pure semantic RAG.
- [x] **Grok Profiling Integration:** Provide a direct hyperlink to X.com and an optimized Grok prompt during initialization. Save the resulting profile to `core/OPERATOR_PROFILE.md` so operator identity remains part of the foundation knowledge rather than ingest-only synapse data.

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

## Phase 22: CLI Agnosticism (The Codex Port) [COMPLETED]
- [x] **The Universal Adapter Layer:** Refactor A.I.M. to be fully agnostic of the underlying CLI (Gemini CLI vs. Codex CLI).
- [x] **Native Hook Translation:** 
    - *Context Injector:* Map the `SessionStart` logic to Codex's `UserPromptSubmit` hook to seamlessly inject the Two-Brain state (`CURRENT_PULSE.md` + `FALLBACK_TAIL.md`).
    - *Failsafe Snapshot:* Map the `AfterTool` logic to Codex's `agent-turn-complete` hook to continually write the Dead Man's Switch (`FALLBACK_TAIL.md`).
- [x] **The Dual-Soul Repository:** Ship the standalone Codex repository with `AGENTS.md` and default fallback paths configured for `~/.codex/memories`.
- [x] **The First Public DataJack Release:** Generate and release `python314.engram` as the first public DataJack cartridge to seed the ecosystem.
    - *Clean Shutdown:* Bind the Distiller (`aim handoff`) to Codex's `Stop` hook to automatically generate the `CURRENT_PULSE.md` on agent exit.
- [x] **Log Parsing Engine:** Write a new parser for `extract_signal.py` that reads Codex's specific transcript format (e.g., `~/.codex/memories`) to extract the intent/thought skeleton.
- [x] **Dynamic Soul Generation:** Update `aim init` to generate an `AGENTS.md` (Codex) or `GEMINI.md` (Gemini CLI) based on the user's environment.
- [x] **Config Wiring:** Update `aim init` to conditionally write A.I.M. hook mappings into `~/.codex/hooks.json`.

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

## Phase 27: CLI Agnosticism Expansion (The Big 3) [ON HOLD]
- [ON HOLD] **Claude Code Integration:** Map A.I.M.'s hook and transcription lifecycle to the newly released Anthropic Claude Code CLI.
- [IN PROGRESS] **Codex Hardening:** Finalize the Codex JSONL parsing logic to ensure `extract_signal.py` perfectly handles Codex's native `agent-turn-complete` history.
- [ ] **Ollama CLI Routing:** Build a lightweight interceptor for the standard Ollama CLI to allow offline-only hackers to utilize the Engram DB.

*Last Updated: 2026-03-21*
