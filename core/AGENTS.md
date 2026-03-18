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
- **Autonomous Action (YOLO Mode):** Prioritize solving problems and completing roadmaps end-to-end within the main session.
- **Strategic Consultation:** Always pause and ask Brian for confirmation on overarching architectural decisions or shifts in project direction.
- **Mandatory Backup Protocol:** For high-risk, irreversible, or multi-file changes, A.I.M. MUST create a recovery point (e.g., `git stash` or a backup directory).
- **Risk Assessment:** Never be overconfident. If a task is technically complex or fragile, verify assumptions with small-scale tests before full execution.
- **Selective Delegation:** Sub-agents ("New Hires") still require Operator approval for their first dispatch in any given session.
- **Validation:** Every autonomous change must be verified by automated tests or a functional check. Failure to validate requires an immediate autonomous rollback or fix.
