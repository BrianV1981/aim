# A.I.M. Hooks Index

This index tracks all active and proposed hooks for the A.I.M. workspace. Hooks are categorized by their lifecycle event and intended purpose.

## Active Hooks
- **[context_injector.py](./context_injector.py) (`SessionStart`):** Injects latest context pulse, project scope, and `HEARTBEAT.md` instructions.
- **[safety_sentinel.py](./safety_sentinel.py) (`BeforeTool`):** Semantic Intent Guardrail that intercepts dangerous shell commands using LLM verification.
- **[secret_shield.py](./secret_shield.py) (`BeforeTool`):** Prevents secret/credential leaks during file writes.
- **[session_summarizer.py](./session_summarizer.py) (`SessionEnd`):** Forensic archival, SQL-backed semantic indexing, and Flash Distillation.
- **[scrivener_aid.py](./scrivener_aid.py) (Interim Pulse):** 30-minute Rolling Interim Backups and crash recovery checkpoints.
- **[workspace_guardrail.py](./workspace_guardrail.py):** Hard-scopes A.I.M. activity to the authorized `allowed_root`.

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
