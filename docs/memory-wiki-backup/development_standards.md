# Development Standards

## Execution Reliability & Subshell Protocol
Always use direct script paths (e.g., `bash scripts/aim_push.sh`) to bypass shell alias resolution issues, especially within isolated worktrees and subshells. This resolves environment-specific "command not found" errors:
- `python3 scripts/aim_cli.py`
- `bash ../../scripts/aim_push.sh`
- Use explicit relative pathing (e.g., `python3 ../../scripts/aim_init.py`) when operating inside deep directory structures like `workspace/`.

### Code Hardening (#414)
- **No Shell Execution:** Systematically avoid `shell=True` in subprocess calls. Use secure list-based subprocess execution to prevent injection vulnerabilities and state issues.
- **Explicit Error Handling:** Broad `except: pass` blocks are strictly forbidden. Implement explicit error logging directed to `stderr` to maintain visibility into failure states.

### Dynamic Pathing for Skills
- **Crawler Requirement:** Use dynamic recursive directory crawlers (e.g., `find_aim_root()`) to locate the project root rather than relying on brittle `__file__` relative pathing like `parent.parent`. This prevents failures when the CLI extracts a skill to a cache directory.
- **Skill Entrypoints:** Ensure `.skill` ZIP cartridges are correctly repackaged with a valid `__main__.py` entrypoint for native Python execution.

## Surgical GitOps Isolation
- **Branch Strategy:** Execute fixes within dedicated Git Worktrees (e.g., `workspace/issue-348`).
- **Staging:** Enforce surgical staging (`git add <file>`) to prevent artifact leakage.
- **Validation:** Verify changes via `pytest` within the project virtual environment before pushing.
- **Deployment:** Use the atomic `aim push` protocol to maintain `main` branch integrity.
- **Batch Merging & Hygiene:** When integrating multiple fix branches, use `aim merge-batch`. You must permanently purge all isolated `workspace/` Git worktrees post-merge, delete lingering test tickets, and ensure the local `~/.bashrc` `aim` alias correctly points to the `aim_core` module path.

## Infrastructure Initialization
- **Planning Artifacts:** As of Issue #348, `scripts/aim_init.py` automatically generates the `planning-artifacts/` directory. All design documents and architectural RFCs should reside here.
- **Framework Hygiene:** New core directories must include a `.gitkeep` file to ensure they are tracked by git even when empty. Changes for Issue #348 were verified and pushed to the `fix/issue-348` branch.
- **Headless Hygiene & Idempotency:** The `setup.sh` script must dynamically derive aliases based on the cloned folder name rather than hardcoding origins. Initializing headless exoskeletons must use `aim init --clean` to trigger the "Clean Sweep" protocol and cleanly provision foundational engrams (`aim_os.engram`).

## Prompt Engineering & Execution Hooks
- **Cognitive Mantra (Anti-Chunking):** Ensure prompt injections via `cognitive_mantra.py` explicitly forbid LLMs from partitioning code output (e.g., `1/2`, `2/2`). Cautious chunking causes validation failures in automated TDD environments.
