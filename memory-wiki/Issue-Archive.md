# Issue Archive

Historical record of resolved issues and their technical impact.

| Issue ID | Title | Resolution | Date |
| :--- | :--- | :--- | :--- |
| #348 | Planning Artifacts Init | Modified `scripts/aim_init.py` to ensure `planning-artifacts/` and `.gitkeep` are generated; verified with TDD and pushed to branch `fix/issue-348`. | 2026-04-21 |
| #350 | 429 Loop Panic | Identified hour-long "Thinking" hang on 429 errors; implemented Model-Lock and forced Transparency Mandate. | 2026-04-21 |
| #25736 | Gemini CLI Hang (Official) | Filed upstream report documenting a critical hour-long hang caused by failure in retry logic during 429 events for Ultra subscribers. | 2026-04-21 |
| #413 | Idempotent Setup | Rewrote `setup.sh` to prevent duplicate environment entries and pruned `requirements.txt` to 8 core packages. | 2026-04-25 |
| #414 | Code Hardening | Eliminated `shell=True` execution and broad `except: pass` blocks across `aim_core` and `hooks/`. | 2026-04-25 |
| #416 | Reincarnation Stabilized | Reverted to single-turn `/reincarnate` and added 3-second sleep to resolve race condition. | 2026-04-25 |
| #419 | Skill Pathing Bugs | Injected dynamic `find_aim_root()` into all `.skill` archives to replace brittle relative pathing. | 2026-04-25 |
| #420 | Test Suite Regression | Identified 29 failing tests resulting from stale imports pointing to deprecated directories. | 2026-04-25 |

## Session Summaries

### Session `session-2026-04-21T05-32-c1e9d1a5` (2026-04-21)
- **Model Hard-Lock:** Modified `~/.gemini/settings.json` to enable `experimental.dynamicModelConfiguration: true` and redefined `modelConfigs.modelChains` to strictly use `gemini-3.1-pro-preview`. This forces the CLI to prompt for user action instead of silently falling back to Flash models during 429 errors.
- **Framework Update (Issue #348):** Updated `scripts/aim_init.py` to ensure the `planning-artifacts` directory is automatically generated during project initialization.
- **Issue #348 Resolved:** Successfully pushed code to branch `fix/issue-348` ensuring the `planning-artifacts` folder and its `.gitkeep` are present.
- **Official CLI Complaint (Issue #25736):** Filed a formal bug report in `google-gemini/gemini-cli` regarding a critical architectural failure where 429 Rate Limit errors trigger an unresponsive 1-hour "Thinking" loop instead of failing fast.
- **Core A.I.M. Issue (#350):** Logged internal tracking for the same 429 hang to improve local error-handling resilience.
- **Execution Resilience:** Identified that the `aim` alias may fail in subshells; agents should prefer direct script paths (e.g., `python3 scripts/aim_cli.py`) or `bash scripts/aim_push.sh` and explicit relative pathing for reliable execution.
- **GitOps Enforcement:** Adhered to isolated branch workflows for framework fixes, utilizing `aim push` for atomic deployments.
- **Continuity Sync:** Synchronized session state to `continuity/ISSUE_TRACKER.md` and generated a Handoff Pulse before reincarnation to maintain epistemic certainty.

### Session `missed_session_summary` (2026-04-22)
- **Reincarnation Skill Race Condition Fixed:** Updated the `reincarnate` skill instructions to enforce a mandatory 2-step process (write gameplan, ask confirmation, then run script) preventing termination before `REINCARNATION_GAMEPLAN.md` is saved.
- **Skill Pathing Bug Fixed:** Modified the `aim-reincarnate` skill's `run.py` to use a dynamic recursive directory crawler for finding the project root, replacing brittle relative pathing.
- **Subconscious Wiki Daemon Ingestion Fixed:** Patched `hooks/session_summarizer.py` to proactively create the `memory-wiki/_ingest/` directory using `os.makedirs` and added a `.gitkeep` to ensure it is version-controlled, resolving silent fallback summarizer crashes.

### Session `session-2026-04-25T05-42-0bb92bf9` (2026-04-25)
- **CLI Timeout Exception:** Documented a native CLI exception where the command `gemini -p  -o json -y -m gemini-3-flash-preview` timed out after 45 seconds. This reinforces the need to avoid relying on Flash models and stick to the Model Hard-Lock pattern.

### Session `session-2026-04-25T05-42-0bb92bf9` (Updates)
- **Reincarnation Pipeline Stabilized (#416):** Removed the broken multi-turn `ask_user` reincarnation skill that caused terminal freezing. Restored `/reincarnate` as a single-turn native script (`aim_core/aim_reincarnate.py`) where the active agent autonomously writes the gameplan. Added a 3-second sleep to resolve the history-saving race condition.
- **Skill Pathing Bugs Fixed (#419):** Eliminated brittle relative pathing (`parent.parent`) across all `.skill` archives by injecting a dynamic `find_aim_root()` directory crawler.
- **Security & Execution Audit (#414):** Systematically eliminated `shell=True` execution in favor of secure list-based subprocess calls with `stdin` injection, and replaced 12 silent `except: pass` blocks with explicit `sys.stderr` error logging.
- **Idempotent Setup & Dependency Diet (#413):** Rewrote `setup.sh` using `grep -q` to be non-destructive/idempotent, and pruned `requirements.txt` down to 8 core packages.
- **Test Suite Regression (#420):** Identified 29 failing tests resulting from unmapped migrations (`src/` to `aim_core/` and `.jsonl` pipeline overhauls).

### Session `session-2026-04-25T17-54-5b8abb98` (Updates)
- **Test Suite & Skill Architecture (#420):** Repaired architectural drift by updating legacy imports to `aim_core`. Upgraded `extract_signal` fixtures to use `.jsonl` and repackaged `.skill` cartridges with `__main__.py` entrypoints.
- **Memory-Wiki Restoration (#425):** Recovered the `memory-wiki` directory from backup after accidental Git deletion. Patched the `session_summarizer.py` daemon hook to fix `ModuleNotFoundError`.
- **Asynchronous Daemon Decoupling (#426, #429):** Resolved infinite loop/timeout during `aim tui` by decoupling the `SessionEnd` hook to spawn a fully detached background process (`subprocess.Popen`) respecting `AIM_INTERNAL_REASONING=1`.
- **Strict Epistemic Enforcement:** Hardcoded a 5-minute staleness check into the native `/reincarnate` pipeline, mechanically blocking agent handoffs unless `REINCARNATION_GAMEPLAN.md` has been recently updated.
- **OAuth Sandbox Fix:** Removed `GEMINI_CLI_CONFIG_DIR` from internal reasoning utilities so headless background tasks can properly load the global OAuth keychain.
- **Cognitive Routing (#428):** Updated documentation explicitly defining "Primary Brain" as a fallback engine exclusively for headless background scripts.
- **GitOps Hygiene:** Executed `aim merge-batch` to integrate 9 fix branches, permanently purged isolated `workspace/` worktrees, deleted dummy tickets, and repaired the `aim` alias to point to `aim_core`.
