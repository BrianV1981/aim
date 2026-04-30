# Changelog

## [v1.58.20] - 2026-04-30
- Fix: Implement Temporal Sliding Window for RAG 3.5 chunks (Closes #489)


## [v1.58.19] - 2026-04-30
- Fix: Expand context window and reduce top_k to prevent Gemma 4 context truncation (Closes #488)


## [v1.58.18] - 2026-04-30
- Fix: Implement RAG 3.5 Parent-Child COALESCE routing in search SQL (Closes #487)


## [v1.58.17] - 2026-04-30
- Fix: Isolate Track 1 RAG search to datajack_library.db to prevent log pollution (Closes #486)


## [v1.58.16] - 2026-04-30
- Fix: Increase Ollama timeout for Track 1 script to allow Gemma 4 to load (Closes #485)


## [v1.58.15] - 2026-04-29
- Fix: Track turn_id to prevent parsing trailing JSON flushes from previous answers (Closes #481)


## [v1.58.14] - 2026-04-29
- Fix: Sleep 1s before Enter key submission to prevent UI swallows (Closes #480)


## [v1.58.13] - 2026-04-29
- Fix: Extend boot sleep and fix buffer escaping to guarantee tmux paste (Closes #479)


## [v1.58.12] - 2026-04-29
- Fix: Record JSONL line count to prevent parsing stale answers on subsequent questions (Closes #478)


## [v1.58.11] - 2026-04-29
- Fix: Ensure agent uses explicit venv/python aim_cli.py path for tools in raw tmux (Closes #477)


## [v1.58.10] - 2026-04-29
- Fix: Support native Gemini CLI JSON keys in tail monitor (Closes #476)


## [v1.58.9] - 2026-04-29
- Fix: Refactor JSONL tracking to wait for active session transcript (Closes #475)


## [v1.58.8] - 2026-04-29
- Fix: Enable YOLO mode for Track 2 Agent to prevent interactive blocking (Closes #474)


## [v1.58.7] - 2026-04-29
- Fix: Implement YOLO Restraint Mandate (Closes #472)


## [v1.58.6] - 2026-04-29
- Fix: Add Reincarnate Session Wipe to LoCoMo Benchmark (Closes #469)


## [v1.58.5] - 2026-04-29
- Fix: Agent Misinterprets /reincarnate Command and Audit Ghost Sessions (Closes #470)


## [v1.58.4] - 2026-04-26
- Fix: Implement RAG 2.0 architecture based on Deep Research (Closes #446)


## [v1.58.3] - 2026-04-26
- Fix: Save automated artifact extraction script to locomo benchmark (Closes #444)


## [v1.58.2] - 2026-04-26
- Fix: Implement LoCoMo benchmark integration and packager (Closes #442)


## [v1.58.1] - 2026-04-26
- Fix: Finalize path refactoring for LongMemEval builder script (Closes #441)


## [v1.57.35] - 2026-04-25
- Fix: Prevent cognitive mantra chunking and complete Phase 29 skills repackaging (Closes #436)
## [v1.58.0] - 2026-04-25
- Feature: Implement A.I.M. LongMemEval preparation script to convert JSONL to structured Flight Recorders (Closes #437)
## [v1.57.36] - 2026-04-25
- Fix: ModuleNotFoundError when aim_core/bootstrap_brain.py is executed as an exoskeleton sub-process (Closes #438)

## [v1.57.35] - 2026-04-25
- Fix: Ensure setup.sh dynamically sets the CLI alias based on the installation folder name rather than hardcoding 'aim' (Closes #438)
- Fix: Update AGENTS.md template and daemon pulse to reference continuity/ISSUE_TRACKER.md instead of the deprecated ROADMAP.md (Closes #439)
- Fix: Allow --clean flag during headless init to trigger Clean Sweep and aim_os.engram provisioning (Closes #440)

## [v1.57.34] - 2026-04-25
- Fix: Enforce 5-minute freshness check on REINCARNATION_GAMEPLAN.md to make handoff deterministic (Closes #416)

## [v1.57.33] - 2026-04-25
- Fix: Decouple session_summarizer hook to prevent Gemini CLI timeout and crash (Closes #429)

## [v1.57.32] - 2026-04-25
- Fix: Resolve TUI cognitive check timeout caused by recursive session-summarizer hook (Closes #426)

## [v1.57.31] - 2026-04-25
- Fix: Rewrite setup.sh for idempotency and aggressively prune requirements.txt (Closes #413)

## [v1.57.30] - 2026-04-25
- Fix: Patch stale src and scripts paths in aim_reincarnate.py (Closes BrianV1981/aim#418)

## [v1.57.29] - 2026-04-25
- Fix: Redesign /reincarnate skill to enforce strict multi-turn flush (Closes BrianV1981/aim#417)

## [v1.57.28] - 2026-04-25
- Fix: Update reincarnate.skill paths to aim_core after Epic 2 restructure (Closes BrianV1981/aim#415)

## [v1.57.27] - 2026-04-24
- Fix: Clear ghost hooks during aim init to prevent stale background processes (Closes BrianV1981/aim#405)

## [v1.57.26] - 2026-04-24
- Fix: Handle aim update engine cleanly in severed projects (Closes BrianV1981/aim#402)

## [v1.57.25] - 2026-04-24
- Fix: Resolve NameError in Cognitive Health Check (Closes BrianV1981/aim#401)

## [v1.57.24] - 2026-04-24
- Fix: Reverse aim init to interactive by default with a --headless flag (Closes BrianV1981/aim#400)

## [v1.57.23] - 2026-04-24
- Fix: Add memory-wiki to Clean Sweep destruction array for true fresh starts (Closes BrianV1981/aim#398)

## [v1.57.22] - 2026-04-24
- Fix: Redesign /reincarnate to use interactive ask_user prompt to solve execution race condition natively (Closes #393)

## [v1.57.21] - 2026-04-24
- Fix: Harden Wiki Daemon ingestion pipeline and enforce strict Reincarnation Gameplan template (Closes #392)

## [v1.57.20] - 2026-04-24
- Fix: enforce 2-step reincarnation handoff & patch path bug (Closes #390)

## [v1.57.19] - 2026-04-24
- Fix: Explicit client tracking in teleport sequence to prevent autoflip failure (Closes #391)

## [v1.57.18] - 2026-04-24
- Fix: Correct .jsonl parsing in handoff pulse generator (Closes #389)

## [v1.57.17] - 2026-04-23
- Fix: Make aim init agent-friendly and headless by default (Closes #383)

## [v1.57.16] - 2026-04-23
- Fix: Update default aim_os.engram cartridge to reflect architectural changes (Closes #371)

## [v1.57.15] - 2026-04-22
- Fix: Decouple Engine Update from Project Update (Closes #369)

## [v1.57.14] - 2026-04-22
- Fix: Deprecate Whisper from Mantra and Failsafe Context Snapshot hook (Closes #368)

## [v1.57.13] - 2026-04-22
- Fix: Rename memory-wiki/AGENTS.md to AGENT.md and deploy via aim_init.py (Closes #367)

## [v1.57.12] - 2026-04-22
- Fix: Rename 'wiki' to 'memory-wiki' to resolve collision with aim.wiki (Closes #366)

## [v1.57.11] - 2026-04-22
- Fix: Safe update migration for AGENTS.md and context settings (Closes #365)

## [v1.57.10] - 2026-04-22
- Fix: Rename GEMINI.md to AGENTS.md for perfect context isolation and platform neutrality (Closes #364)

## [v1.57.9] - 2026-04-22
- Fix: Isolate workspaces using context.ignoreGlobal: true (Closes #363)

## [v1.57.8] - 2026-04-22
- Fix: Add discoveryMaxDirs 0 to prevent downward context pollution (Closes #362)

## [v1.57.7] - 2026-04-22
- Fix: Enforce global memoryBoundaryMarkers for strict agent isolation (Closes #361)

## [v1.57.6] - 2026-04-22
- Fix: Add memory-wiki/.gemini/settings.json to isolate daemon context (Closes #361)

## [v1.57.5] - 2026-04-22
- Fix: Update Subconscious Wiki Daemon to properly prompt and parse multi-file outputs (Closes #356)
- Fix: Reincarnation script waits for user prompt before killing CLI outside of tmux (Closes #327)

## [v1.57.4] - 2026-04-21
- Fix: anchor find_aim_root to setup.sh and auto-copy CONFIG.json to new worktrees (Closes #354)

## [v1.57.3] - 2026-04-21
- Fix: spawn reincarnated agent with interactive prompt and yolo mode (Closes #351) (Closes #352)

## [v1.57.2] - 2026-04-21
- Fix: Completely purge legacy tiers configuration key from framework (Closes #349)

## [v1.57.1] - 2026-04-20
- Fix: aim init leaves stale GEMINI.md and README.md (Identity Crisis) and T_SOUL template is outdated (Closes #345)

## [v1.57.0] - 2026-04-19
- Feature: Translate 'aim' prefix to local alias during DataJack ingestion (Closes #342)

## [v1.56.0] - 2026-04-19
- Feature: Overhaul Memory System - Implement Persistent LLM Wiki and Vector Ingestion (Closes #329)

## [v1.55.1] - 2026-04-18
- Fix: Mandate operator-triggered reincarnation and add TOOLS.md modular registry (Closes #320)

## [v1.55.0] - 2026-04-09
- Feature: Stateful Memory (Scratchpad) and JSON Output for aim-calc (Closes #323)

## [v1.54.0] - 2026-04-09
- Feature: Integrate Gemini CLI Native Skills for Scientific Calculator Benchmark (Closes #321)

## [v1.53.0] - 2026-04-09
- Feature: Execute Aerospace Benchmark (Closes #316)

## [v1.52.0] - 2026-04-09
- Feature: Enforce Embedding Model Compatibility in DataJack Schema (Closes #314)

## [v1.51.1] - 2026-04-09
- Fix: Repair aim_exchange.py ingestion schema and tests (Closes #309)

## [v1.51.0] - 2026-04-09
- Feature: Add forum and issue ingestion pipeline via 'aim scrape' (Closes #47)

## [v1.50.8] - 2026-04-09
- Fix: 'aim promote' fails due to incorrect repository resolution in worktrees (Closes #298)

## [v1.50.7] - 2026-04-08
- Fix: Prevent preemptive flight recorder reading (Closes #301)

## [v1.50.6] - 2026-04-08
- Fix: '/reincarnate' command hangs indefinitely, preventing session handoff (Closes #299)

## [v1.50.5] - 2026-04-08
- Fix: Meta-Bug: Strict Enforcement of Autonomous Action Guardrails (Closes #288)

## [v1.50.4] - 2026-04-08
- Fix: Relocate background hook state files to hooks/.state/ (Closes #291)

## [v1.50.3] - 2026-04-08
- Fix: Update test_aim_cli.py to utilize sys.executable for reliable venv path resolution (Closes #292)

## [v1.50.2] - 2026-04-08
- Fix: Improve readability of noise-reduced session logs (Closes #258)

## [v1.50.1] - 2026-04-07
- Fix: Implement Archipelago Federated Database Model (Closes #153)

## [v1.50.0] - 2026-04-05
- Feature: Integrate GitHub Issue Scraper into Reincarnation Pipeline (Closes #245)

## [v1.49.1] - 2026-04-05
- Fix: obsidian_sync.py now correctly syncs MD transcripts from archive/history (Closes #239)

## [v1.49.0] - 2026-04-03
- Feature: Implement two-way Obsidian Vault Sync and fix Swarm imports (Closes #180)

## [v1.48.0] - 2026-04-03
- Feature: Implement The Factory Floor Protocol (Git Worktrees) for aim fix (Closes #45)

## [v1.47.0] - 2026-04-03
- Feature: Port REINCARNATION_GAMEPLAN.md generation logic from aim-claude (Closes #224)

## [v1.46.0] - 2026-04-03
- Feature: Re-wire Obsidian Bridge to Event-Driven /reincarnation Trigger and build Subconscious Watchdog (Closes #212, Closes #215)

## [v1.45.0] - 2026-04-03
- Feature: Implement Cognitive Architecture Toggle in TUI (Closes #214)

## [v1.44.4] - 2026-04-03
- Fix: Properly map CLI arguments in cmd_bug parser to prevent interactive lock (Closes #221)

## [v1.44.3] - 2026-04-03
- Fix: Space out API calls during Cognitive Health Check to prevent 429 exhaustion (Closes #220)

## [v1.44.2] - 2026-04-03
- Fix: Disable user hooks for generate_reasoning internal API wrapper (Closes #219)

## [v1.44.1] - 2026-04-03
- Fix: Restore missing TUI menus gutted during Phase 2 (Closes #218)

## [v1.44.0] - 2026-04-02
- Feature: Formalize Commander's Intent in aim bug command (Closes #201)

## [v1.43.0] - 2026-04-02
- Feature: Integrate aim-chalkboard Swarm Post Office into workspace via gitignore (Closes #209)

## [v1.42.1] - 2026-03-30
- Fix: Implement atomic write and sync for handoff files (Closes #198)

## [v1.42.0] - 2026-03-30
- Feature: Implement AI-Driven Reincarnation Strategist for Gameplan generation (Closes #196)

## [v1.41.0] - 2026-03-29
- Feature: Finalize Waterfall Refinement Pipeline with Consume-and-Clean protocol (Closes #191)

## [v1.40.0] - 2026-03-29
- Feature: Implement ARC-only Delta Memory Pipeline and 2000-line History Splitting (Closes #190)

## [v1.39.0] - 2026-03-29
- Feature: Finalize 5-Tier Delta Memory Pipeline and Separate Historical Session Search System (Closes #190)

## [v1.38.2] - 2026-03-29
- Fix: Restore 'total_reconstruction.py' from remote agent cross-contamination (Closes #187)

## [v1.38.1] - 2026-03-29
- Fix: Implement dynamic workspace resolution in 'find_aim_root' to prevent database contamination across simultaneous bots (Closes #189)

## [v1.38.0] - 2026-03-29
- Feature: Integrate Reincarnation Gameplan and Full History into Continuity Pipeline (Closes #185)

## [v1.37.5] - 2026-03-28
- Fix: Rewire TUI and backend logic to use handoff_context_lines instead of turns for the 1990 line limit buffer (Closes #179)

## [v1.37.4] - 2026-03-28
- Fix: Restore delta logic to properly cap LAST_SESSION_FLIGHT_RECORDER.md at 1990 lines (Closes #178)

## [v1.37.3] - 2026-03-28
- Fix: Lock down crash recovery session targeting and handoff scope (Closes #159)

## [v1.37.2] - 2026-03-28
- Fix: Salvage V8 OOM memory leaks via aim crash Recovery Protocol (Closes #157)

## [v1.37.1] - 2026-03-28
- Fix: Increased NODE_OPTIONS heap limit and fixed retriever syntax (Closes #156)

## [v1.37.0] - 2026-03-28
- Feature: Localized Issue Ledger (Closes #154)

## [v1.36.0] - 2026-03-28
- Feature: Implemented Cartridge Integrity Checksums (SHA-256) (Closes #145)

## [v1.35.0] - 2026-03-28
- Feature: Added aim doctor for environment validation (Closes #143)

## [v1.34.0] - 2026-03-28
- Feature: Added Writable Core Memory block to onboarding sequence (Closes #138)

## [v1.33.0] - 2026-03-28
- Feature: Added the Memory Anchor to prevent distillation drift (Closes #144)

## [v1.32.0] - 2026-03-28
- Feature: Hardened Hook Router with aggressive sandboxing and error masking (Closes #131)

## [v1.31.0] - 2026-03-28
- Feature: Decoupled Sovereign Sync from aim push (Closes #130)

## [v1.30.0] - 2026-03-28
- Feature: Implemented the SafeLoad Plugin Pattern for DataJack Engine (Closes #129)

## [v1.29.1] - 2026-03-28
- Fix: Aggressive Clean Sweep in installer to prevent doc leakage (Closes #132)

