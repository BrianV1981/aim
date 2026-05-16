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

## CLI Interaction & Parsing Standards
- **Tool Mapping Enforcement:** When writing agent profiles (`AGENTS.md`), explicitly map required capabilities (like search) to their underlying tools (e.g., `run_shell_command`) so the agent does not attempt to invoke non-existent tools.
- **Tool Call Extraction:** Gemini CLI outputs tool calls as part of the `gemini` message structure rather than as distinct `tool_call` messages. Runner scripts must parse the `toolCalls` list within `gemini` message objects; ignoring messages with `toolCalls` causes the runner to miss tool execution and misalign output indices. In addition, the foundation model may ignore `AGENTS.md` and require explicit tool injection in prompts.
- **Prompt Sanitization:** The Gemini CLI interprets special characters (e.g., `!`, `$`, `?`) in prompts as shell/CLI shortcuts. All prompts must be sanitized (e.g., stripped or escaped) before injection into tmux sessions to prevent crashes.
- **Streaming Artifacts:** Gemini CLI logs empty `content: ""` messages to `.jsonl` during streaming/thinking phases. Runner parsing loops MUST NOT return answers based on these empty messages, as they prematurely terminate the sequence and lead to data gaps.
