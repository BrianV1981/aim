# A.I.M. Hooks Index

This index tracks all active and proposed hooks for the A.I.M. workspace. Hooks are categorized by their lifecycle event and intended purpose.

## Active Hooks
- **[context_injector.py](./context_injector.py) (`SessionStart`):** Dual-Injection Onboarding. Injects the `CURRENT_PULSE.md` (Strategy) and `FALLBACK_TAIL.md` (Tactics).
- **[tier1_hourly_summarizer.py](./tier1_hourly_summarizer.py) (`SessionEnd`):** The first stage of the Durable Memory pipeline. Compresses raw JSON into structured hourly logs.
- **[failsafe_context_snapshot.py](./failsafe_context_snapshot.py) (`AfterTool`):** The "Dead Man's Switch". Maintains a rolling 10-turn snapshot of the session in `FALLBACK_TAIL.md` and triggers the Hourly Summarizer if the 5-line significance filter is passed.
- **[cognitive_mantra.py](./cognitive_mantra.py) (`AfterTool`):** The Anti-Drift Shield. Monitors autonomous tool execution and injects subconscious reminders every 25 steps, forcing a hard `<MANTRA>` generation reset every 50 steps to preserve context weight.

## Proposed Hook Concepts (Intelligence Level 2+)
1. **Forensic Context Bridge (`SessionStart`)**: Automatic semantic retrieval of historical context.
2. **Semantic Commit Reviewer (`BeforeTool`)**: AI-generated commit messages based on architectural impact.
3. **Proactive Documentation Auditor (`AfterTool`)**: Real-time sync between code changes and documentation.
4. **Context Budget Watcher (`AfterAgent`)**: API quota monitoring and usage optimization.
5. **Autonomous Testing Sentinel (`AfterTool`)**: Automated test execution after code modifications.
6. **Dependency & Security Pulse (`SessionStart`)**: Automated tech stack vulnerability checks.
7. **Keyring Integrity Check (`SessionStart`)**: Proactive verification of sovereign secrets.

---
*Last Updated: 2026-03-19*
