# J.A.R.V.I.S. Hooks: Ideas & Expansion

This document elaborates on how hooks can be used to augment J.A.R.V.I.S.'s capabilities and provide deep integration into Brian's workspace.

## 1. Safety Sentinel (`BeforeTool`)
- **Primary Goal:** Prevent catastrophic errors or data loss.
- **How it works:** Intercepts `run_shell_command` calls. It scans the `command` string for patterns like `rm -rf /`, `mkfs`, or `dd`.
- **Expanded Idea:** **Permission Escalation**. Instead of a simple "Deny," the hook could trigger a custom CLI prompt that says: *"Warning: This command affects critical system files. Type 'SUDO JARVIS' to proceed."*

## 2. Context Injector (`SessionStart`)
- **Primary Goal:** Ensure J.A.R.V.I.S. is always "caught up" on the latest project state.
- **How it works:** A Python script runs at startup, finds the 5 most recently modified `.md` files in `.open/` or `Vaults/`, and injects their contents into the session context.
- **Expanded Idea:** **Git Delta Injection**. The hook could also summarize the `git diff` of the last 24 hours so J.A.R.V.I.S. knows exactly what code changed while Brian was away.

## 3. Secret Shield (`BeforeTool`)
- **Primary Goal:** Protect credentials and private keys.
- **How it works:** A Node.js hook for `write_file` that uses regex to identify high-entropy strings or common key headers (e.g., `sk-`, `-----BEGIN...`).
- **Expanded Idea:** **Auto-Gitignore**. If a secret is detected, the hook not only blocks the write but also checks if the file is in `.gitignore`. If not, it can prompt J.A.R.V.I.S. to add it immediately.

## 4. Session Archivist (`SessionEnd`)
- **Primary Goal:** Automated knowledge management and progress tracking.
- **How it works:** Captures the final `session_history`. It uses a lightweight model or local script to summarize: *"What we did," "What's left to do,"* and *"Key decisions."* It then writes this to `memory/YYYY-MM-DD.md`.
- **Expanded Idea:** **Obsidian Sync**. Automatically create a new note in the `Vaults/Daily/` folder with a backlink to the session log, keeping Brian's Obsidian vault perfectly in sync with his CLI work.

## 5. Discord Messenger (`AfterTool` / `AfterAgent`)
- **Primary Goal:** Remote monitoring and asynchronous feedback.
- **How it works:** Whenever a long-running tool (like a build or test suite) finishes, a hook sends a POST request to a Discord webhook with the result.
- **Expanded Idea:** **Interactive Remote Control**. Use Discord buttons to allow Brian to "Approve" or "Reject" a J.A.R.V.I.S. `[PROPOSAL]` from his phone while away from the terminal.

## 6. Weather Heartbeat (`SessionStart`)
- **Primary Goal:** Immediate situational awareness.
- **How it works:** Executes the `curl` command from `HEARTBEAT.md` and displays the result as part of the initial greeting.
- **Expanded Idea:** **Daily Briefing**. Combine weather, top 3 calendar events (via an API hook), and a "System Health" report into a single "Good morning, Brian" startup summary.

---
*Created: 2026-03-17*
