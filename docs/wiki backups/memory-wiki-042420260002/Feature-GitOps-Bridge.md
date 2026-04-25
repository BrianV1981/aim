# Feature: GitOps Bridge

The GitOps Bridge ensures that all structural changes to the A.I.M. framework are handled via atomic, isolated deployments.

## Atomic Deployments
- **Isolated Worktrees:** Every fix must be developed in a dedicated worktree (`aim fix <id>`).
- **Framework Initialization:** As of April 2026, the `aim_init.py` script ensures that `planning-artifacts/` is included in the default directory structure to support rigorous pre-coding design phases.
- **Issue #348 Resolution:** Modified `scripts/aim_init.py` to ensure `planning-artifacts/` and `.gitkeep` are generated. Verified via `pytest` and pushed to the `fix/issue-348` branch.

## Command Execution
- **Direct Execution:** To avoid shell alias conflicts or "command not found" errors, deployment scripts should be executed directly (e.g., `bash scripts/aim_push.sh`).
- **Path Reliability:** Use direct relative script paths (e.g., `bash ../../scripts/aim_push.sh`) within worktrees.

---
*Last Updated: 2026-04-22*
