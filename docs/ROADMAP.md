# A.I.M. Roadmap: Phase 6 & Beyond

## Goal
Transform A.I.M. into a self-maintaining intelligence layer that proactively distills daily work into long-term architectural memory while ensuring absolute system safety.

## Phase 6: The Gemini-Native Transition (Intelligence Level 2) [COMPLETED]
- [x] **Google Embedding Migration (`src/indexer.py`):** Swapped `nomic-embed-text` for `gemini-embedding-2-preview` (Google GenAI SDK) for world-class forensic retrieval.
- [x] **The Flash Distiller (`src/distiller.py`):** Upgraded to **Gemini Flash** for high-context architectural reflection.
- [x] **The Chronicles (`docs/CHRONICLES.md`):** Established archival narrative for "Resolved" history to keep context lean.
- [x] **Forensic CLI (`aim` alias):** Created global bash alias to run `retriever.py` from any terminal.

## Phase 7: Security & Safety Guardrails [COMPLETED]
- [x] **Secret Shield (`BeforeTool`):** Scans for API keys, private keys, and high-entropy strings before any `write_file` or `replace` operation.
- [x] **Safety Sentinel (`BeforeTool`):** Intercepts `run_shell_command` to block or flag destructive operations.
- [x] **Workspace Guardrail:** Enforce the "A.I.M. Territory" principle (ensuring A.I.M. tools only affect authorized projects).

## Phase 8: Semantic Awareness & Project Expansion [COMPLETED]
- [x] **Multi-Project Context:** Expanded `context_injector.py` to recognize and load project-specific `CONTEXT.md` files within `/home/kingb/`.
- [x] **Git Delta Injection:** Added startup hook to summarize `git status` and `git diff` for immediate technical awareness.
- [x] **Global Alias Expansion (v2):** Promoted the `aim` alias to a full CLI dispatcher (`scripts/aim_cli.py`) for project-agnostic orchestration.
- [x] **Advanced Forensic Search:** Upgraded retriever with `--context`, `--full`, and `--session` filters for agent-grade retrieval.
- [x] **Foundational Embedding Provider:** Established Ollama/Nomic as the immutable local coordinate system for forensic memory (ADR #8).

## Phase 9: Sovereign Hardening & Secret Management [COMPLETED]
- [x] **Native Keyring Migration:** Move `GOOGLE_API_KEY` from environment variables to a platform-native keyring.
- [x] **Telemetry Anonymization:** Implemented `scripts/telemetry_scrubber.py` to sanitize telemetry logs.
- [x] **Zero-Burn Obsidian Sync:** Mirroring daily logs to `OperationsCenterVault/AIM_LOGS/` automatically.
- [x] **Hardened Script Shebangs:** Finalized transition to absolute `venv` paths.

## Phase 11: Toward Project Singularity (Audit Strategy)
- [ ] **Pillar A: The Heartbeat (Real-Time Consciousness):** [ON HOLD / DECOMMISSIONED] Prototype script `src/heartbeat.py` created but deactivated to prevent token burn. Currently utilizing `scrivener_aid.py` as a reactive alternative (30-min interval during active tool use).
- [x] **Pillar B: Shadow Memory (Emergency Recovery):** Implement a versioned snapshot system for Context Pulses to ensure fallback stability if a mental model is corrupted.
- [x] **Pillar C: Semantic Intent Guardrails:** Upgraded the `safety_sentinel` to use LLM-based verification to ensure tool commands align with the Operator's current architectural intent.


## 🧪 Tentative Research & Expansion Ideas
- [ ] **The "Chameleon" Persona:** Expand `CONTEXT.md` to support directory-based persona overrides (e.g., Senior Rust Architect vs. UX Lead).
- [ ] **The "Mirror" Tool (`aim diff`):** Create a command to compare historical Context Pulses to visualize architectural momentum and evolution.
- [ ] **External Brain Sync (Obsidian):** Automated hook to export Core Memory and Daily Logs to a Markdown-based PKM vault for visual knowledge graphing.
- [ ] **Privacy Hardening (Telemetry Scrubber):** Script to sanitize `~/.gemini/telemetry.log` of sensitive project data before aggregation.

---
*Last Updated: 2026-03-18*
