# Development Standards

## Execution Reliability & Subshell Protocol
Always use direct script paths (e.g., `bash scripts/aim_push.sh`) to bypass shell alias resolution issues, especially within isolated worktrees and subshells. This resolves environment-specific "command not found" errors:
- `python3 scripts/aim_cli.py`
- `bash ../../scripts/aim_push.sh`
- Use explicit relative pathing (e.g., `python3 ../../scripts/aim_init.py`) when operating inside deep directory structures like `workspace/`.
- **Dynamic Pathing for Skills:** Use dynamic recursive directory crawlers to find the project root rather than relying on brittle `__file__` relative pathing (e.g., when the CLI extracts a skill to a cache directory).

## Surgical GitOps Isolation
- **Branch Strategy:** Execute fixes within dedicated Git Worktrees (e.g., `workspace/issue-348`).
- **Staging:** Enforce surgical staging (`git add <file>`) to prevent artifact leakage.
- **Validation:** Verify changes via `pytest` within the project virtual environment before pushing.
- **Deployment:** Use the atomic `aim push` protocol to maintain `main` branch integrity.

## Infrastructure Initialization
- **Planning Artifacts:** As of Issue #348, `scripts/aim_init.py` automatically generates the `planning-artifacts/` directory. All design documents and architectural RFCs should reside here.
- **Framework Hygiene:** New core directories must include a `.gitkeep` file to ensure they are tracked by git even when empty. Changes for Issue #348 were verified and pushed to the `fix/issue-348` branch.
