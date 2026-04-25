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
