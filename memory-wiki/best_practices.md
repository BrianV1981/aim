# Best Practices and Operational Standards

## Execution Reliability
- **Script Invocation:** Always use **explicit Python script paths** (e.g., `python3 scripts/aim_cli.py` or `bash scripts/aim_push.sh`) instead of bash aliases like `aim`. 
- **Subshell Alias Failures:** Aliases are frequently missing in automated subshells or isolated Git worktrees, leading to `aim: command not found` errors. 
- **Relative Path Usage:** For reliable GitOps deployments within isolated worktrees, establish the practice of using direct relative script paths (e.g., `bash ../../scripts/aim_push.sh`) to ensure execution succeeds even when aliases are unavailable.

## GitOps and Workflow Isolation
- **Branch Isolation:** Successfully isolated framework changes to specific branches (e.g., `fix/issue-348`) and verified fixes via `pytest` within temporary workspaces before atomic deployment.
- **Workspace Isolation:** Use the `workspace/` directory for isolated issue resolution. This ensures that experimental changes or branch-specific work does not pollute the primary worktree.
- **Atomic Pushes:** Utilize `scripts/aim_push.sh` for atomic, branch-based pushes to maintain `main` branch integrity.
- **Surgical Staging:** Verify surgical staging and atomic pushes within isolated worktrees (`workspace/issue-348`) to ensure only relevant files are committed.
- **GitHub CLI Patterns:** Avoid complex shell expansions within `gh issue create`. Write content to temporary files before submission to ensure consistent execution.

## Continuity and State Management
- **Continuity Sync:** Mandatory execution of `python3 scripts/aim_cli.py pulse` before session reincarnation to synchronize the local issue tracker (`continuity/ISSUE_TRACKER.md`) and preserve context for successor agents.
- **Pulse Verification:** Confirmed that `pulse` correctly generates `HANDOFF.md` and updates `continuity/ISSUE_TRACKER.md` to maintain epistemic certainty.

## Bug Reporting Strategy
- **Tone:** Use "High-Pressure Professional" technical critique for official reports.
- **Framing:** Frame failures (especially retry-logic issues and silent hangs) as SLA and UX violations (e.g., Bug Report #25736).

---
*Last Updated: 2026-04-22*
