# AGENTS.md - A.I.M. Workspace Rules

## Forensic Retrieval Protocol
A.I.M. possesses a native semantic search engine (`src/retriever.py`). This is a **Diagnostic Tool**, not a background daemon.

### 1. Trigger Conditions
Invoke Forensic Search ONLY when:
- Explicitly requested by Brian.
- Encountering an undocumented technical hurdle that was likely addressed in a previous session.
- Performing a high-risk "State Change" where historical rationale is missing from `DECISIONS.md`.

### 2. Context Consumption (The "3-Turn Window")
When a relevant fragment is found:
- **Primary:** Absorb the identified fragment (Prompt, Response, or Thought).
- **Secondary:** If the fragment is ambiguous, A.I.M. may read the raw JSON from `archive/raw/` to ingest the **3-turn window** (1 turn before, 2 turns after) to capture the implementation result.
- **Strict Limit:** Never ingest more than 5 fragments per task to prevent context dilution.

## Startup Protocol
At the beginning of every session, A.I.M. must:
1. Load `GEMINI.md` (Core Soul)
2. Load `IDENTITY.md` and `USER.md`
3. Scan `MEMORY.md` for active project context.
4. **Maintenance Check:** Run `python3 aim/src/maintenance.py` to index previous session data.

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
