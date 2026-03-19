# Next Actions: A.I.M. Operational Edge

## Phase 6: Intelligence Level 2
- [ ] **Google Embedding Migration:** Transition `src/indexer.py` from `nomic-embed-text` to Google `text-embedding-004`.
- [ ] **Flash Distiller:** Implement `src/distiller.py` using **Gemini 2.0 Flash** for high-context memory synthesis.
- [ ] **Forensic CLI:** Finalize the `aim` global bash alias for multi-project semantic search.

## Phase 8: Semantic Awareness & Expansion
- [ ] **Multi-Project Context:** Expand `context_injector.py` to handle project-specific context loads.
- [ ] **Git Delta Injection:** Automate `git diff` summarization on startup for offline awareness.

## Phase 9: sovereign Hardening
- [ ] **Telemetry Anonymization:** Implement a scrubber for `~/.gemini/telemetry.log`.
- [ ] **Hardened Shebangs:** Finalize the transition of all A.I.M. scripts to the absolute `venv` Python path.

## Maintenance & Observability
- [ ] **Memory Distillation:** Run the first weekly core update via `src/distiller.py`.
- [ ] **Observability:** Enable and verify Local OTEL telemetry in `~/.gemini/settings.json`.
