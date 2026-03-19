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

---

## 🏗️ Core Dependencies
Before starting, ensure you have:
*   [Ollama](https://ollama.com/) (For local search/memory)
*   [Gemini CLI](https://github.com/google/gemini-cli) (The underlying platform)
*   [Python 3.10+](https://www.python.org/)

## 🔍 Key Commands
*   **`aim status`**: See your current project momentum and pending memory proposals.
*   **`aim search "query"`**: Near-instant semantic search into your technical history using SQLite.
*   **`aim push "msg"`**: Auto-versioned deployment to GitHub with semantic timestamps.
*   **`aim commit`**: Approve architectural memory updates with safety shadowing.

"I believe I've made my point." — **A.I.M.**
