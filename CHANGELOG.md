# Changelog

## [v1.7.13] - 2026-03-25
- Fix: Patched export_datajack_cartridge MCP skill to gracefully handle raw CLI strings and bypassed the broken exchange subparser (Closes #29)


## [v1.7.12] - 2026-03-25
- Fix: Synchronized TUI Google model catalog exactly with the active Gemini CLI list, removing 3 Pro variants and adding 2.5 Flash Lite (Closes #27)


## [v1.7.11] - 2026-03-25
- Fix: Hardened TUI Cognitive Health Check by removing flawed length-based heuristics and enforcing strict structural validation of the expected 'OK' response (Closes #14)


## [v1.7.10] - 2026-03-25
- Fix: Overhauled Gemini CLI output parser with stack-based brace matching to correctly extract pretty-printed multi-line JSON, resolving the 'No valid JSON payload' regression (Closes #23)


## [v1.7.9] - 2026-03-25
- Fix: Replaced invalid gemini-3.1-pro model with gemini-3-pro-preview in TUI catalog and presets (Closes #26)


## [v1.7.8] - 2026-03-25
- Fix: Corrected Gemini 3 Flash model ID in TUI catalog from gemini-3-flash to gemini-3-flash-preview to resolve 404 ModelNotFoundError (Closes #25)


## [v1.7.7] - 2026-03-24
- Fix: Reverted interactive gemini login subprocess to prevent TUI chat traps and added code guardrails against future regressions (Closes #24)


## [v1.7.6] - 2026-03-24
- Fix: Hardened Gemini CLI OAuth parsing by replacing brittle regex with backward JSON line extraction, ignoring hook/keychain noise (Closes #12)


## [v1.7.5] - 2026-03-24
- Fix: Added explicit 'gemini login' trigger during TUI Google OAuth setup to mirror the Codex bridge experience (Closes #22)


## [v1.7.4] - 2026-03-24
- Fix: Trimmed down Codex TUI model catalog to only the supported gpt-5.x variants (Closes #21)


## [v1.7.3] - 2026-03-24
- Fix: Removed invalid and deprecated Google Gemini models from the TUI model catalog to prevent ModelNotFoundError exceptions (Closes #13)


## [v1.7.2] - 2026-03-24
- Fix: Extracted Codex CLI errors from stderr to unmask invalid model failures during TUI health checks (Closes #16)


## [v1.7.1] - 2026-03-24
- Fix: Added diagnostic message column to TUI health check to expose underlying API errors (Closes #1)


## [v1.7.0] - 2026-03-23
- Feature: Finalized v1.7.0 DataJack Protocol and Wiki launch


## [v1.6.0] - 2026-03-23
- Feature: Testing Semantic Release Pipeline

