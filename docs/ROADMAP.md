# A.I.M. Archivist Engine Roadmap

## Goal
Establish a permanent, searchable, and forensic-grade record of all **A.I.M.** sessions to prevent context drift and minimize token waste.

## Phase 1: Infrastructure & Guardrails (DONE)
- [x] Create `aim` project scaffold.
- [x] Update `GEMINI.md` with "Soul" and Concurrency guardrails.
- [x] Disable automatic session deletion in `settings.json`.
- [x] Implement initial `SessionEnd` summarizer hook.

## Phase 2: Forensic Data Discovery (DONE)
- [x] **Data Mapping:** Mapped the Gemini CLI internal JSON schema (User turns, Model thoughts, Tool calls, Tokens).
- [x] **Transcript Location:** Identified `~/.gemini/tmp/kingb/chats/` as the raw data source.
- [x] **Identity Alignment:** Scrubbed legacy branding and established A.I.M. as the primary orchestrator.

## Phase 3: The Archivist Engine (Current Focus)
- [ ] **Native Indexer:** Build a Python-based indexer in `src/` to parse raw JSON transcripts into a semantic-ready format.
- [ ] **Forensic Export:** Enhance the `SessionEnd` hook to move finalized transcripts from `tmp/` to `aim/archive/` (Forensic Preservation).
- [ ] **Schema Standardization:** Finalize the A.I.M. Forensic Schema for cross-session continuity.

## Phase 4: Semantic Search & Retrieval
- [ ] **Vectorization:** Implement local embedding of archived sessions using a lightweight model.
- [ ] **RAG Integration:** Allow A.I.M. to perform semantic lookups of past sessions during active tasks.
- [ ] **Context Injection:** Automated "Search-Before-Action" protocol for complex requests.

## Phase 5: Automation & Refinement
- [ ] **Auto-Cleanup:** Distill old daily logs into the curated `MEMORY.md`.
- [ ] **Cross-Workspace Continuity:** Ensure sessions from different projects can be cross-referenced.

---
*Last Updated: 2026-03-17*
