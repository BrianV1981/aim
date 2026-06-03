# Issue Tracking

Current active issues and their status within the A.I.M. ecosystem and upstream dependencies.

| Issue ID | Title | Status | Impact |
| :--- | :--- | :--- | :--- |
| #350 | 429 Loop Panic | Mitigated (Config) | Architectural failure where 429 errors trigger a 55-minute "Thinking" hang. |
| #25736 | Gemini CLI Hang (Upstream) | Open (Reported) | Official bug report in `google-gemini/gemini-cli` regarding silent rate-limit hangs for Ultra subscribers. |
| #348 | Framework Init Fix | Resolved | Modified `scripts/aim_init.py` to include `planning-artifacts` (with `.gitkeep`) in project generation; verified on branch `fix/issue-348`. |
| #610 | Redesign aim_crash.py | Open | Pending redesign of crash handler. |
| #609 | Daemon LLM Calls Leak | Open | Cosmetic issue where background daemon LLM calls leak into main session history. |
| #381 | Architectural Drift Detection | Open | Long-standing issue to implement a mechanism to detect architectural drift. |

## Integration & Synchronization Patterns
To maintain epistemic certainty across sessions, A.I.M. utilizes a two-tier synchronization strategy:

- **Automated Reporting (`aim bug`):** Technical failures, architecture critiques, and "roast" logs are synchronized to the local `continuity/ISSUE_TRACKER.md` via `python3 scripts/aim_cli.py bug`. This ensures that even "vibe-based" critiques are captured as actionable technical debt.
- **State Anchoring (`pulse`):** Mandatory execution of `python3 scripts/aim_cli.py pulse` before session termination/reincarnation to bridge local file state with the global issue tracker.

---
*Last Updated: 2026-04-22*
