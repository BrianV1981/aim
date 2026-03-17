# Next Actions: J.A.R.V.I.S. Continuity

## Phase 1: Proof of Concept Hook (SessionEnd)
- [ ] Create `aim/hooks/session_summarizer.py`.
- [ ] Configure `~/.gemini/settings.json` to trigger the summarizer on `SessionEnd`.
- [ ] Test the hook by ending a session and checking for an updated `HANDOFF.md`.

## Phase 2: Memory Integration
- [ ] Automate daily log creation in `aim/memory/YYYY-MM-DD.md`.
- [ ] Link Obsidian `Vaults` to the `aim` system for cross-platform context.

## Phase 3: Safety & Utility
- [ ] Implement `BeforeTool` safety sentinel for `run_shell_command`.
- [ ] Implement `SessionStart` weather/health briefing.
