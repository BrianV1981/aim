# A.I.M. Roadmap: Reliability & Scaling

## Goal
Transform A.I.M. into a professional-grade, self-maintaining intelligence layer that scales to hundreds of sessions while ensuring absolute system safety and zero token waste.

## Phase 12: Reliability & Scalability (Red Team Response) [URGENT / TOP PRIORITY]
- [ ] **Unified Forensic Database (SQLite):** Consolidate `archive/index/*.fragments.json` into a single `forensic.db`. Replace O(N) file-scanning with near-instant SQL indexing.
- [ ] **Flywheel Concurrency Locking:** Implement `.aim.lock` advisory locking in `session_summarizer.py` to prevent race conditions during rapid session termination.
- [ ] **Dynamic Privacy Hardening:** Upgrade `scripts/telemetry_scrubber.py` to automatically ingest the current username and vault-stored keys at runtime (Zero hardcoded paths).
- [ ] **Commit Safety Shadowing:** Automatically generate `MEMORY.md.bak` during the `aim commit` process to allow for instant rollback.
- [ ] **Proposal Syntax Validation (Linter):** Implement automated regex verification of the `### 3. MEMORY DELTA` header before committing to prevent model-generated corruption of core rules.

## Phase 13: Productization & Distribution [IN PROGRESS]
- [x] **Automated Onboarding (`aim init`):** A guided installer for clean workspace scaffolding.
- [x] **Repo Protection:** Established robust `.gitignore` to keep personal memories sovereign.
- [x] **Bootstrapping Templates:** Created generic templates for Core Memory and Configuration.
- [x] **A.I.M. Cockpit (TUI):** Visual management of providers and the System Vault.
- [ ] **Dependency Standardization:** Create `requirements.txt` and a final `setup.sh` wrapper.

---

## Phase 6: Gemini-Native Transition [COMPLETED]
- [x] **Google Embedding Migration:** Initial SDK integration.
- [x] **The Flash Distiller:** Upgraded to Gemini Flash.
- [x] **The Chronicles:** Established archival narrative.

## Phase 7: Security & Safety Guardrails [COMPLETED]
- [x] **Secret Shield:** Scans for high-entropy strings.
- [x] **Safety Sentinel:** Intercepts state-altering commands.
- [x] **Workspace Guardrail:** Enforced "A.I.M. Territory" path logic.

## Phase 8: Semantic Awareness & Project Expansion [COMPLETED]
- [x] **Multi-Project Context:** Directory-based `CONTEXT.md` loading.
- [x] **Advanced Forensic Search:** Upgraded retriever with `--context` and `--session` filters.
- [x] **Foundational Embedding Provider:** Locked local Nomic/Ollama as the immutable brain coordinate system.

## Phase 9: Sovereign Hardening & Secret Management [COMPLETED]
- [x] **Native Keyring Migration:** Secrets moved to System Vault.
- [x] **Telemetry Anonymization:** Integrated sequential scrubbing into the flywheel.
- [x] **Zero-Burn Obsidian Sync:** Mirroring daily logs to external vault.

## Phase 11: Toward Project Singularity (Audit Strategy)
- [ ] **Pillar A: The Heartbeat:** [ON HOLD] Decommissioned prototype to save tokens.
- [x] **Pillar B: Shadow Memory:** Versioned snapshot system.
- [x] **Pillar C: Semantic Intent Guardrails:** LLM-backed verification in Sentinel.

---

## 🧪 Phase 14: Future Research & Expansion Ideas
- [ ] **The "Chameleon" Persona:** Expand `CONTEXT.md` to support directory-based persona overrides.
- [ ] **The "Mirror" Tool (`aim diff`):** Command to compare Context Pulses to visualize momentum.

---
*Last Updated: 2026-03-18*
