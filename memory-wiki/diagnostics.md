# Troubleshooting and Diagnostics

## Identifying "Thinking" Hangs
If the agent has been in a "Thinking" state for more than 5 minutes without output, it is likely trapped in a `429` rate-limit loop or a retry-backoff failure.

### Diagnostic Steps
1.  **Check Pulse:** Attempt to run `python3 scripts/aim_cli.py pulse` in a separate terminal. If the project state is accessible, the issue is likely with the API/CLI session, not the local file system.
2.  **Verify Configuration:** Ensure `~/.gemini/settings.json` is configured with the [[Model-Lock-Protocol]] and **Transparency Mandate**.
3.  **Inspect Logs:** Check for `429` errors in any available terminal logs. 
4.  **Forensics:** Inspect `/home/kingb/.gemini/tmp/aim/chats/session-[ID].json` for raw API response data. This is the primary source for confirming 429 errors from the `cloudcode-pa` endpoint.

## Recovery Procedures
- **Hard Reset:** If the CLI is unresponsive, terminate the process and use `/reincarnate` to start a fresh session.
- **State Restoration:** After reincarnation, read `HANDOFF.md` and `continuity/ISSUE_TRACKER.md` to restore epistemic certainty.
- **Benchmark Cleanup:** Ensure no zombie Python processes (e.g., ghost runner scripts) or temporary tmux sessions are left running after benchmark stress tests to maintain a pristine environment.
- **Database Corruption:** The `memory_lance` database can be corrupted by incompatible compaction commands. Rebuilding from raw flight recorders is necessary when this occurs.
- **Pristine Pipeline:** A strict post-rebuild protocol must be followed: 1) Purge toxic distractor files, 2) Complete ingestion, 3) Vault the raw database (e.g., 18GB backups), 4) Perform safe compaction.
- **Diagnostic Vaulting:** Store comprehensive benchmark diagnostic reports (e.g., the "Nightmare" report) and raw evidence `.jsonl` files in the `docs/` directory with matched timestamps for cross-session analysis.

---
*Last Updated: 2026-04-22*
