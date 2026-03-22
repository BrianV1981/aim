# A.I.M. Hooks Index

This index tracks all active and proposed hooks for the A.I.M. workspace. Hooks are categorized by their lifecycle event and intended purpose.

## Active Hooks
- **[context_injector.py](./context_injector.py) (`SessionStart`):** Dual-Injection Onboarding. Injects the `CURRENT_PULSE.md` (Strategy) and `FALLBACK_TAIL.md` (Tactics).
- **[safety_sentinel.py](./safety_sentinel.py) (`BeforeTool`):** Semantic Intent Guardrail that intercepts dangerous shell commands using LLM verification.
- **[secret_shield.py](./secret_shield.py) (`BeforeTool`):** Prevents secret/credential leaks during file writes.
- **[workspace_guardrail.py](./workspace_guardrail.py) (`BeforeTool`):** Hard-scopes A.I.M. activity to the authorized `allowed_root` with deep-scan path protection.
- **[tier1_hourly_summarizer.py](./tier1_hourly_summarizer.py) (`SessionEnd`):** The first stage of the Durable Memory pipeline. Compresses raw JSON into structured hourly logs.
- **[failsafe_context_snapshot.py](./failsafe_context_snapshot.py) (`AfterTool`):** The "Dead Man's Switch". Maintains a rolling 10-turn snapshot of the session in `FALLBACK_TAIL.md` and triggers the Hourly Summarizer if the 5-line significance filter is passed.
- **[pre_compress_checkpoint.py](./pre_compress_checkpoint.py) (`PreCompress`):** Hardened history archival shield against context window summarization.

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
