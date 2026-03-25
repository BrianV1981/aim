# Changelog

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

