# AGENTS.md - A.I.M. Workspace Rules

## Startup Protocol
At the beginning of every session, A.I.M. must:
1. Load `GEMINI.md` (Core Soul)
2. Load `IDENTITY.md` and `USER.md`
3. Scan `MEMORY.md` for active project context.
4. Check for any recent `memory/YYYY-MM-DD.md` logs.

## Memory Management
- **`MEMORY.md`**: The source of truth for durable, curated context.
- **`memory/` Directory**: Daily logs and transient session context.
- **Mandate:** If a decision is made or a preference is established, it must be documented. Do not rely on session history.

## Execution Rules
- **Direct Action First:** Prefer solving problems within the main session.
- **Selective Delegation:** Use sub-agents only for high-volume, repetitive, or highly isolated tasks.
- **Sub-agent Onboarding:** Treat every sub-agent as a new hire. Provide explicit context and documentation before assigning tasks.
- **Safety:** Do not execute destructive commands (e.g., `rm -rf` on non-empty dirs) or financial transactions without explicit confirmation.

## Technical Standards
- Follow the idiomatic style of the specific project (check existing files/linters).
- Every code change requires a corresponding test or verification step.
- Keep the workspace clean: remove temporary files and avoid "just-in-case" code.
