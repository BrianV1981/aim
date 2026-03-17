# J.A.R.V.I.S. Hooks Index

This index tracks all proposed and active hooks for the `/home/kingb` workspace. Hooks are categorized by their lifecycle event and intended purpose.

## Active Hooks
- *[None currently active]*

## Proposed Hook Concepts
1. **Safety Sentinel (`BeforeTool`)**: Prevents dangerous shell commands and directory deletions.
2. **Context Injector (`SessionStart`)**: Automatically loads recent notes from `.open` and `Vaults`.
3. **Secret Shield (`BeforeTool`)**: Scans for API keys and private keys before any `write_file` operation.
4. **Session Archivist (`SessionEnd`)**: Summarizes the day's work and appends it to `memory/YYYY-MM-DD.md`.
5. **Discord Messenger (`AfterTool`)**: Sends notifications for successful builds or critical errors.
6. **Weather Heartbeat (`SessionStart`)**: Automatically runs the `HEARTBEAT.md` weather check on startup.

## Roadmap
- [ ] Implement Safety Sentinel (Bash script)
- [ ] Implement Weather Heartbeat (Python script)
- [ ] Explore Obsidian `Vaults` integration via Context Injector

---
*Last Updated: 2026-03-17*
