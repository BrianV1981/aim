# 🔄 Continuity Protocol & Session Summaries

The Continuity Protocol ensures that A.I.M. maintains a persistent state across discrete agent sessions. This page serves as a structured index of historical session summaries and key architectural shifts identified during live operations.

## 📅 Session Logs (April 2026)

### [2026-04-21] Session-c1e9d1a5 Summary
- **Framework Initialization Fix (Issue #348):** Modified `scripts/aim_init.py` to ensure the `planning-artifacts` directory is automatically generated during project initialization; changes verified and pushed to the `fix/issue-348` branch.
- **Infrastructure Critical Bug (Issue #25736):** Identified a major flaw in the agent's error-handling logic where a `429 Too Many Requests` (rate limit) error triggers an unresponsive, 1-hour "Thinking" hang instead of fail-fast notifications; filed Bug #25736 in the `google-gemini/gemini-cli` repository as a critical architectural failure and SLA violation for Ultra subscribers.
- **Model Hard-Locking Pattern:** Implemented a new configuration pattern in `~/.gemini/settings.json` by enabling `experimental.dynamicModelConfiguration` and redefining `modelChains` to strictly force `gemini-3.1-pro-preview`, preventing silent autonomous fallbacks to Flash models.
- **Rate Limit Logic:** Determined that "3% Context" UI readings refer to window capacity, whereas 429 errors are triggered by Requests Per Minute (RPM) limits caused by rapid tool-call bursts.
- **Enhanced Continuity Pattern:** Established a mandatory requirement to generate a "Handoff Pulse" and synchronize `continuity/ISSUE_TRACKER.md` before session reincarnation to ensure cross-agent state persistence and epistemic certainty.
- **Subshell Execution Protocol:** Standardized the use of explicit Python script paths (e.g., `python3 scripts/aim_cli.py`) and relative pathing to bypass unsourced aliases and "command not found" errors across isolated Git worktrees.

### [2026-04-22] Missed Session Summary
- **Reincarnation Race Condition:** Fixed a race condition where the `reincarnate` skill terminated the session before `REINCARNATION_GAMEPLAN.md` could be saved. Enforced a mandatory 2-step protocol: write the gameplan, ask for confirmation, and execute the script in a separate turn.
- **Subconscious Wiki Daemon:** Resolved an ingestion crash by ensuring the `memory-wiki/_ingest/` directory exists and is tracked via `.gitkeep`, with a patch to `hooks/session_summarizer.py` for proactive directory creation.

### [2026-04-25] Updates
- **Reincarnation Pipeline Stabilized (#416):** Removed the broken multi-turn `ask_user` reincarnation skill that caused terminal freezing. Restored `/reincarnate` as a single-turn native script (`aim_core/aim_reincarnate.py`) and added a 3-second sleep to resolve the underlying history-saving race condition.
- **Manual Gameplan Protocol:** The outgoing agent is now strictly responsible for autonomously generating `continuity/REINCARNATION_GAMEPLAN.md` using its session memory *before* triggering the teleport script.
- **Strict Epistemic Enforcement:** A 5-minute staleness check is hardcoded into the native `/reincarnate` pipeline, mechanically blocking agent handoffs if `REINCARNATION_GAMEPLAN.md` has not been recently updated.

## 📅 Session Logs (May 2026)

### [2026-05-14] Reincarnation Pipeline & Salvage Operations
- **Reincarnation Pipeline Mastery:** The workflow is strictly defined: 1. `extract_signal.py` (parse `.jsonl` signal skeleton), 2. `session_summarizer.py` (Subconscious Scribe LLM extraction: 5-7 architectural bullets), 3. `wiki_agent` (ingest summarized summaries into `index.md`/`log.md`).
- **Dead Session Salvage:** Successfully distilled a 42,302-turn deadlock (816MB of raw `.jsonl` noise) into 40 hyper-dense Markdown summary files via the Subconscious Scribe step.
- **Anti-Corruption Mandate:** The `memory-wiki/_ingest/` folder was purged of 847 unmanageable raw chunks. The system is strictly forbidden from bypassing the Subconscious Scribe summarization step in future salvage operations.
- **Data Pipeline Correction (LoCoMo-V2):** 89 missing image URLs were resolved by re-pulling the original golden source dataset. The `scripts/` directory was reorganized into a logical pipeline (`pipeline/`, `generation/`, `patching/`, `utils/`) for reproducibility.

### [2026-05-17] Reincarnation & Decoupled Architecture
- **Reincarnation Pipeline**: Decoupled `session_summarizer.py` from the brittle `SessionEnd` hook to a direct Python handoff via `Popen`.
- **Race Condition Fix**: Updated `aim_reincarnate.py` to use native CLI primer flags (`-i`) instead of `tmux load-buffer`, eliminating race conditions during wake-up prompt injection.

---
*Last Updated: 2026-05-15*
