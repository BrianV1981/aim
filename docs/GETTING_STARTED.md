# Getting Started with A.I.M.

Welcome to **Actual Intelligent Memory**, your sovereign context layer for the Gemini CLI.

## 🚀 The 3-Step Setup

### 1. Clone the Repository
```bash
git clone https://github.com/BrianV1981/aim.git
cd aim
```

### 2. Run the Initializer
This script will check your dependencies (Ollama, Gemini CLI) and scaffold your workspace.
```bash
python3 scripts/aim_init.py
```

### 3. Configure your "Hybrid Brain"
Launch the interactive TUI to set up your providers and secure vault.
```bash
# First, source the alias (or add it to your .bashrc)
alias aim='$(pwd)/venv/bin/python3 $(pwd)/scripts/aim_cli.py'

aim tui
```

---

## 🏗️ Core Dependencies
Before starting, ensure you have:
*   [Ollama](https://ollama.com/) (For local search/memory)
*   [Gemini CLI](https://github.com/google/gemini-cli) (The underlying platform)
*   [Python 3.10+](https://www.python.org/)

## 🔍 Key Commands
*   `aim status`: See your current project momentum.
*   `aim search "query"`: Deep-dive into your technical history.
*   `aim push "msg"`: Auto-versioned deployment to GitHub.

"I believe I've made my point." — **A.I.M.**
