# Technical Intelligence

## API Rate Limit (429) Failure Mode
- **SLA Failure:** Confirmed 55-minute to 1-hour "Thinking" hang during 429 events (RPM/TPM limits) despite premium subscription status.
- **Detection:** RPM limits are decoupled from context usage percentage. A 3% context usage does not preclude a 429 hang.
- **Mitigation:** Model Hard-Lock Protocol and Transparency Mandate (forced action prompts).
- **Upstream Issue:** Identified failure of `ModelAvailabilityService` in the official Gemini CLI to notify Ultra subscribers of throttles, documented in Bug Report #25736.

## GitHub CLI (gh) Integration
- **Account Identification:** Confirmed active use of the `BrianV1981` GitHub account for programmatic issue creation and repository management.
- **Credential Awareness:** `gh auth status` displays all local host entries; `BrianV1981` is verified as the active, functional account for this environment, while others (e.g., `d3c12yp7012`) are likely stale/invalid.
- **Authentication:** Local configuration conflicts with stale credentials have been resolved.

## Direct Script Execution Pattern
- **Requirement:** Call `scripts/aim_cli.py` and `scripts/aim_push.sh` via direct paths (e.g., `python3 scripts/aim_cli.py`).
- **Reasoning:** Bypasses shell alias failures in subshells and isolated Git worktrees, ensuring tool availability.

## State Preservation (Pulse)
- Use `python3 scripts/aim_cli.py pulse` to synchronize state to `continuity/ISSUE_TRACKER.md` before reincarnation.
- Ensures branch status and pending fixes (e.g., Issue #348 verified status) are preserved across sessions.
- **Handoff Protocol:** Successor agents must inherit the hard-locked model configuration and current workstream verified status via the `HANDOFF.md` and `continuity/ISSUE_TRACKER.md` sync.
