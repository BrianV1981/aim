# A.I.M. (Actual Intelligent Memory)

A.I.M. is an open-source engineering exoskeleton designed to solve context amnesia, token bloat, state loss, and drift in long-running autonomous AI coding sessions. 

It wraps around CLI agents (primarily Google's Gemini CLI) and provides:
1. **External SQLite Memory:** Local, high-fidelity vector databases (Hybrid RAG) to replace standard sliding-window context.
2. **GitOps Enforcement:** AI agents are forbidden from coding on `main`. They must create GitHub issues, branch out, use TDD, and deploy atomically.
3. **Background Markdown Generation:** A deterministic Python script strips terminal noise and extracts a "Signal Skeleton", reducing context weight by 85%. A background daemon then elegantly weaves this into a human-readable Markdown wiki.
4. **Crash Recovery & Handoffs:** Automated context extraction and "reincarnation" into fresh terminal sessions when the context window fills up.

---

## 🚀 Quickstart & Installation

A.I.M. requires **Linux** or **WSL (Ubuntu)**, Node.js v20+, and the Google Gemini CLI.

### 1. The Decoupled Exoskeleton (Recommended)
This installs the A.I.M. engine globally so you can wrap it around *any* unique project without polluting your target repository.

```bash
# 1. Install prerequisites (if missing)
# nvm install 20 && nvm use 20
# npm install -g @google/gemini-cli
# gemini login

# 2. Install the global engine
git clone https://github.com/BrianV1981/aim.git ~/.local/share/aim
cd ~/.local/share/aim
./setup.sh
source ~/.bashrc

# 3. Wrap your unique project
mkdir ~/my-new-project && cd ~/my-new-project
aim init
```
*(During `aim init`, select 'y' to perform a Clean Sweep to sever git history and wipe internal docs).*

### 2. Configure Your AI Providers
Launch the interactive dashboard to set your API keys, local Ollama models, and configure the background Wiki daemon.
```bash
aim tui
```

---

## 🛠️ The Core GitOps Workflow

A.I.M. enforces a strict "Factory Floor" workflow. Do not write code on `main`. Tell your agent to execute these steps:

1. **`aim bug "desc"`** — Creates a structured GitHub Issue containing the Commander's Intent and Action Items.
2. **`aim fix <id>`** — Spawns an isolated Git Worktree (e.g., `workspace/issue-42`) where the agent can code and run tests concurrently.
3. **`aim push "msg"`** — Parses Conventional Commits, calculates SemVer bumps, auto-generates `CHANGELOG.md`, and pushes to GitHub.
4. **`aim promote`** — Merges the isolated feature into `main` and automatically deletes the temporary Worktree.

If an agent's context window gets full, tell it to run:
- **`aim reincarnate`** — Writes a handoff gameplan, kills the bloated session, and spawns a fresh terminal with perfect epistemic certainty.

---

## 📖 Documentation & Philosophy

A.I.M. separates fast onboarding documentation from deep philosophical essays and architectural diagrams.

- **[The Official A.I.M. Wiki](https://github.com/BrianV1981/aim/wiki)**: The primary onboarding ramp. Includes step-by-step user guides, configuration variables, and tutorials.
- **[The A.I.M. Knowledge Base (Public Obsidian Vault)](https://github.com/BrianV1981/aim-wiki)**: A massive, decentralized digital garden containing our raw benchmark JSON logs, architectural design history, and the complete "vibe coding" origin story.

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
☕ **Support the project:** [Buy Me a Coffee](https://buymeacoffee.com/brianv1981)