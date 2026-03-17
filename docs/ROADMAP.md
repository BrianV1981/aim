# J.A.R.V.I.S. Session Preservation Roadmap

## Goal
Establish a permanent, searchable, and forensic-grade record of all J.A.R.V.I.S. sessions to prevent context drift and minimize token waste.

## Phase 1: Infrastructure & Guardrails (DONE)
- [x] Create `aim` project scaffold.
- [x] Update `GEMINI.md` with "Soul" and Concurrency guardrails.
- [x] Disable automatic session deletion in `settings.json`.
- [x] Implement initial `SessionEnd` summarizer hook.

## Phase 2: Forensic Preservation (Current Focus)
- [ ] **Data Mapping:** Map the Gemini CLI internal JSON schema to the OpenClaw `.jsonl` format.
- [ ] **The "Bridge" Hook:** Update the `SessionEnd` hook to export a "Forensic Transcript" to `aim/archive/`.
- [ ] **Search Strategy:** Decide between adapting `openclaw-sessions-console` or building a dedicated Gemini indexer.

## Phase 3: Semantic Search & Retrieval
- [ ] **Vectorization:** Implement local embedding of archived sessions.
- [ ] **RAG Integration:** Allow J.A.R.V.I.S. to perform semantic lookups of past sessions during active tasks.
- [ ] **UI Integration:** Expose search results via the CLI or a local web interface.

## Phase 4: Automation & Refinement
- [ ] **Auto-Cleanup:** Distill old daily logs into the curated `MEMORY.md`.
- [ ] **Cross-Workspace Continuity:** Ensure sessions from different projects can be cross-referenced.

---
*Created: 2026-03-17*
