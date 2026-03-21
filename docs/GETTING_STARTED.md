# Getting Started with A.I.M.

Welcome to **Actual Intelligent Memory**, your sovereign context layer for the Gemini CLI.

## 🚀 The 3-Step Setup

### 1. Clone & Bootstrap
```bash
git clone https://github.com/BrianV1981/aim.git
cd aim
./setup.sh
```
The `setup.sh` script creates your Python virtual environment, installs dependencies, and configures the `aim` alias.

### 2. Initialize the Workspace
This script scaffolds your directory structure and prepares your configuration templates.
```bash
# source ~/.bashrc (if setup.sh added the alias)
aim init
```

### 3. Configure your "Hybrid Brain"
Launch the interactive TUI to set up your providers and secure vault.
```bash
aim tui
```

## 🔄 Staying Up to Date
A.I.M. is under active development. To pull the latest TUI features and engine improvements without losing your bot's personality or memory:

```bash
aim update
```
**Why it's Safe:**
- **Personality Lock:** It will *never* overwrite your `GEMINI.md`, `core/USER.md`, or `core/MEMORY.md`.
- **Hook Sync:** Automatically re-registers system hooks (like the Workspace Guardrail) to your global Gemini settings.
- **Git Native:** Performs a `git pull` and refreshes the virtual environment context.

---

## 🔍 Key Commands
*   **`aim update`**: Pull latest code and re-register system hooks (Safe Update).
*   **`aim status`**: See your current project momentum and pending memory proposals.
*   **`aim search "query"`**: Near-instant semantic search into your technical history using SQLite.
*   **`aim push "msg"`**: Auto-versioned deployment to GitHub with semantic timestamps.
*   **`aim commit`**: Approve architectural memory updates with safety shadowing.

"I believe I've made my point." — **A.I.M.**
