# A.I.M. Hooks Index

This index tracks all active and proposed hooks for the A.I.M. workspace. Hooks are categorized by their lifecycle event and intended purpose.

## Active Hooks
- **[session_summarizer.py](./session_summarizer.py) (`SessionEnd`):** The core of the Persistent LLM Wiki architecture. Compresses raw JSONL transcripts into structured markdown and triggers the Subconscious Daemon.
- **[cognitive_mantra.py](./cognitive_mantra.py) (`AfterTool`):** The Anti-Drift Shield. Monitors autonomous tool execution and forces a hard `<MANTRA>` generation reset every 50 steps to preserve context weight.

## Proposed Hook Concepts (Intelligence Level 2+)
1. **Forensic Context Bridge (`SessionStart`)**: Automatic semantic retrieval of historical context.
2. **Semantic Commit Reviewer (`BeforeTool`)**: AI-generated commit messages based on architectural impact.
3. **Proactive Documentation Auditor (`AfterTool`)**: Real-time sync between code changes and documentation.
4. **Context Budget Watcher (`AfterAgent`)**: API quota monitoring and usage optimization.
5. **Autonomous Testing Sentinel (`AfterTool`)**: Automated test execution after code modifications.
6. **Dependency & Security Pulse (`SessionStart`)**: Automated tech stack vulnerability checks.
7. **Keyring Integrity Check (`SessionStart`)**: Proactive verification of sovereign secrets.

---
*Last Updated: 2026-04-24*
