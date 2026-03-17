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

## Phase 3: The Archivist Engine (DONE)
- [x] **Native Indexer:** Built `src/indexer.py` to parse raw JSON transcripts into semantic-ready formats.
- [x] **Forensic Export:** Enhanced `SessionEnd` hook to move transcripts to `aim/archive/raw/`.
- [x] **Schema Standardization:** Finalized the A.I.M. Forensic Schema for cross-session continuity.

## Phase 4: Semantic Search & Retrieval (DONE)
- [x] **Vectorization:** Full Ollama/Nomic-Embed integration for session fragments.
- [x] **Native Retriever:** Built `src/retriever.py` with zero-dependency vector retrieval.
- [x] **Context Injection:** Documented Forensic Search protocol in `core/TOOLS.md`.

## Phase 5: Automation & Refinement (DONE)
- [x] **Auto-Maintenance:** Built `src/maintenance.py` to automate indexing and log distillation.
- [x] **GitHub Baseline:** Established clean root, version-controlled architecture.
- [x] **Identity Re-brand Finalized:** 100% scrub of legacy references.

---
*Created: 2026-03-17 | Status: 🟢 PLATFORM ONLINE*
