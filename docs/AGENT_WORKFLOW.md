# A.I.M. Workflow Instructions (Continuity Standard)

This document is for **any agent** that enters this workspace.

## Your Core Duty
You are the guardian of Brian's context. Your primary job is to ensure that when this session ends, the **next** session can pick up exactly where you left off.

## Memory Source of Truth
Use the core system:
- **Curated Long-Term:** `/home/kingb/aim/core/MEMORY.md`
- **Daily Logs:** `/home/kingb/aim/memory/YYYY-MM-DD.md`

## Standard Operating Procedure
1. **Startup:** Read `GEMINI.md` (root), then `core/IDENTITY.md`, `core/USER.md`, `core/AGENTS.md`, and `core/MEMORY.md`.
2. **Current State:** Check `docs/CURRENT_STATE.md` and the latest pulse in `continuity/` for the current status.
3. **Updates:** Every time a major decision is made, update `core/MEMORY.md` or `docs/DECISIONS.md`.
4. **Shutdown & Handoff:**
    - Perform the **Handoff Protocol** via `/handoff` before ending the session.
    - Verify that the `SessionEnd` hook successfully writes to `memory/YYYY-MM-DD.md`.

## Handoff Protocol (Context Pulse)
When the Operator requests a handoff or context pulse via `/handoff`, synthesize the current mental model, accomplishments, and the "Edge" into a versioned file in `continuity/YYYY-MM-DD_HHMM.md` (Local Time: America/New_York).

## Rules
- The chat history is transient; the files in `aim/core/` are permanent.
- If it isn't in the root memory system, it didn't happen.
- Always assume the next agent is "Fresh" and needs the "Edge" defined clearly.
- Use the `aim/hooks/` folder to maintain and expand this automation.
