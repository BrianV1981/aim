# Issue Archive

Historical record of resolved issues and their technical impact.

| Issue ID | Title | Resolution | Date |
| :--- | :--- | :--- | :--- |
| #348 | Planning Artifacts Init | Modified `scripts/aim_init.py` to ensure `planning-artifacts/` and `.gitkeep` are generated; verified with TDD and pushed to branch `fix/issue-348`. | 2026-04-21 |
| #350 | 429 Loop Panic | Identified hour-long "Thinking" hang on 429 errors; implemented Model-Lock and forced Transparency Mandate. | 2026-04-21 |
| #25736 | Gemini CLI Hang (Official) | Filed upstream report documenting a critical hour-long hang caused by failure in retry logic during 429 events for Ultra subscribers. | 2026-04-21 |

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
