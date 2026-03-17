# Decisions: J.A.R.V.I.S. Workspace Architecture

## 2026-03-17: Unified Meta-Project (`aim`)
- **Decision:** Create a single project folder (`aim`) to hold both project documentation AND the hook scripts.
- **Rationale:** Keeps the logic for "How I remember" and "What I remember" in the same place. Makes the system portable and easier for a "fresh" agent to understand.
- **Status:** Implemented.

## 2026-03-17: SessionEnd as First Hook
- **Decision:** Start with a `SessionEnd` hook for the proof of concept.
- **Rationale:** Directly addresses the most painful part of AI collaboration: context loss upon disconnect. Easier to test and provides immediate value (the `HANDOFF.md`).
- **Status:** In progress.
