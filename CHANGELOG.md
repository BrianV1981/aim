# Changelog

## [v1.38.1] - 2026-03-29
- Fix: Implement dynamic workspace resolution in 'find_aim_root' to prevent database contamination across simultaneous bots (Closes #189)


## [v1.38.0] - 2026-03-29
- Feature: Integrate Reincarnation Gameplan and Full History into Continuity Pipeline (Closes #185)


## [v1.37.5] - 2026-03-28
- Fix: Rewire TUI and backend logic to use handoff_context_lines instead of turns for the 1990 line limit buffer (Closes #179)


## [v1.37.4] - 2026-03-28
- Fix: Restore delta logic to properly cap LAST_SESSION_CLEAN.md at 1990 lines (Closes #178)


## [v1.37.3] - 2026-03-28
- Fix: Lock down crash recovery session targeting and handoff scope (Closes #159)


## [v1.37.2] - 2026-03-28
- Fix: Salvage V8 OOM memory leaks via aim crash Recovery Protocol (Closes #157)


## [v1.37.1] - 2026-03-28
- Fix: Increased NODE_OPTIONS heap limit and fixed retriever syntax (Closes #156)


## [v1.37.0] - 2026-03-28
- Feature: Localized Issue Ledger (Closes #154)


## [v1.36.0] - 2026-03-28
- Feature: Implemented Cartridge Integrity Checksums (SHA-256) (Closes #145)


## [v1.35.0] - 2026-03-28
- Feature: Added aim doctor for environment validation (Closes #143)


## [v1.34.0] - 2026-03-28
- Feature: Added Writable Core Memory block to onboarding sequence (Closes #138)


## [v1.33.0] - 2026-03-28
- Feature: Added the Memory Anchor to prevent distillation drift (Closes #144)


## [v1.32.0] - 2026-03-28
- Feature: Hardened Hook Router with aggressive sandboxing and error masking (Closes #131)


## [v1.31.0] - 2026-03-28
- Feature: Decoupled Sovereign Sync from aim push (Closes #130)


## [v1.30.0] - 2026-03-28
- Feature: Implemented the SafeLoad Plugin Pattern for DataJack Engine (Closes #129)


## [v1.29.1] - 2026-03-28
- Fix: Aggressive Clean Sweep in installer to prevent doc leakage (Closes #132)

