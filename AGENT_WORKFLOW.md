# A.I.M. Workflow Instructions (Continuity Standard)

This document is for **any agent** that enters this workspace.

## Your Core Duty
You are the guardian of Brian's context. Your primary job is to ensure that when this session ends, the **next** session can pick up exactly where you left off.

## Memory Source of Truth
Use the root-level system:
- **Curated Long-Term:** `/home/kingb/MEMORY.md`
- **Daily Logs:** `/home/kingb/memory/YYYY-MM-DD.md`

## Standard Operating Procedure
1. **Startup:** Read `GEMINI.md`, `USER.md`, `IDENTITY.md`, then `/home/kingb/MEMORY.md` and the most recent daily logs in `/home/kingb/memory/`.
2. **Current State:** Check `aim/CURRENT_STATE.md` for the status of the meta-project itself.
3. **Updates:** Every time a major decision is made, update `/home/kingb/MEMORY.md`.
4. **Shutdown & Handoff:**
    - Perform the **Handoff Protocol** before ending the session.
    - Ensure the `SessionEnd` hook successfully writes to `/home/kingb/memory/YYYY-MM-DD.md`.

## Handoff Protocol (Context Pulse)
When the Operator requests a handoff or context pulse via `/handoff`, follow the base template in `/home/kingb/aim/continuity/BOOTSTRAP_TEMPLATE.md` to create a versioned handoff in `/home/kingb/aim/continuity/YYYY-MM-DD_HHMM.md`.

## Rules
- The chat history is transient; the files in the root are permanent.
- If it isn't in the root memory system, it didn't happen.
- Always assume the next agent is "Fresh" and needs the "Edge" defined clearly.
- Use the `aim/hooks/` folder to maintain and expand this automation.
