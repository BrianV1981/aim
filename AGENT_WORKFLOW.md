# J.A.R.V.I.S. Workflow Instructions (Continuity Standard)

This document is for **any agent** (including future versions of J.A.R.V.I.S.) that enters this workspace.

## Your Core Duty
You are the guardian of Brian's context. Your primary job is to ensure that when this session ends, the **next** session can pick up exactly where you left off.

## Memory Source of Truth
Do not look inside this project folder for primary memory. Use the root-level system:
- **Curated Long-Term:** `/home/kingb/MEMORY.md`
- **Daily Logs:** `/home/kingb/memory/YYYY-MM-DD.md`

## Standard Operating Procedure
1. **Startup:** Read `GEMINI.md`, `USER.md`, `IDENTITY.md`, then `/home/kingb/MEMORY.md` and the most recent daily logs in `/home/kingb/memory/`.
2. **Current State:** Check `aim/CURRENT_STATE.md` for the status of the meta-project itself.
3. **Updates:** Every time a major decision is made, update `/home/kingb/MEMORY.md`.
4. **Shutdown & Handoff:**
    - Perform the **Handoff Protocol** (see below) before ending the session.
    - Ensure the `SessionEnd` hook successfully writes to `/home/kingb/memory/YYYY-MM-DD.md`.

## Handoff Protocol (Context Pulse)
When the Operator requests a handoff or context pulse, follow the base template in `/home/kingb/aim/continuity/BOOTSTRAP_TEMPLATE.md` to create a versioned handoff in `/home/kingb/aim/continuity/YYYY-MM-DD_HHMM.md`.

```markdown
# [CONTEXT PULSE: <TIMESTAMP>]

J.A.R.V.I.S., confirm that you have loaded your core identity and the `/home/kingb/MEMORY.md` file.

**Cloning Context:**
[1-2 sentences summarizing the current mission and overall vibe].

**Mental Model & Decisions:**
- [Decision X]: [Rationale]
- [Decision Y]: [Rationale]

**The Current "Edge":**
We are at the "Edge" of Phase [X] of the [Project Name]. Your immediate next technical move is:
- [Specific Tool Call/Investigation Step]

Confirm you are fully "cloned" to this state and ready to begin.
```

## Rules
- The chat history is transient; the files in the root are permanent.
- If it isn't in the root memory system, it didn't happen.
- Always assume the next agent is "Fresh" and needs the "Edge" defined clearly.
- Use the `aim/hooks/` folder to maintain and expand this automation.
