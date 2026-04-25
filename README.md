# A.I.M. (Actual Intelligent Memory)

A.I.M. is an open-source engineering exoskeleton designed to solve context amnesia, token bloat, state loss, and drift in long-running autonomous AI coding sessions. 

It wraps around CLI agents (primarily Google's Gemini CLI) and provides a full operating system for your AI, forcing it to act like a disciplined Principal Engineer.

## 🚀 Quickstart & Installation

A.I.M. requires **Linux** or **WSL (Ubuntu)**, Node.js v20+, and the Google Gemini CLI.

### 1. The Decoupled Exoskeleton (Recommended)
This installs the A.I.M. engine globally so you can wrap it around *any* unique project without polluting your target repository.

```bash
# 1. Install the global engine
git clone https://github.com/BrianV1981/aim.git ~/.local/share/aim
cd ~/.local/share/aim
./setup.sh
source ~/.bashrc

# 2. Wrap your unique project
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

## 🔥 Core Capabilities

A.I.M. provides a massive suite of tools to control, manage, and scale your AI agents:

*   **External SQLite Memory (Hybrid RAG):** Replaces standard sliding-window context with local, high-fidelity vector databases (semantic + lexical search).
*   **Background Markdown Generation:** A deterministic Python script strips terminal noise, reducing context weight by 85%. A background daemon then weaves this into a human-readable Markdown wiki (`memory-wiki/`).
*   **GitOps Enforcement:** AI agents are forbidden from coding on `main`. They must create GitHub issues (`aim bug`), branch out into isolated worktrees (`aim fix`), use TDD, and deploy atomically (`aim push`).
*   **Interactive TUI Cockpit:** A visual terminal interface (`aim tui`) to configure LLM routing, guardrails, and context limits without editing JSON files.
*   **Cognitive Routing:** Route expensive coding tasks to flagship models (e.g., Gemini Pro) in your terminal, while offloading repetitive background tasks (like memory indexing) to free, local models (e.g., Ollama) on your GPU.
*   **P2P Knowledge Cartridges:** Package thousands of pages of documentation into pre-vectorized `.engram` files. Share and download them peer-to-peer via BitTorrent (`aim export` / `aim jack-in`) to give agents instant recall of entire frameworks without burning API tokens.
*   **Universal IDE Support (MCP):** A built-in FastMCP server exposes the memory databases to any connected IDE (Cursor, VS Code, Claude Desktop) without requiring platform-specific adapters.
*   **Crash Recovery & Handoffs:** When the context window fills up, run `aim reincarnate` to extract active context and spawn a fresh terminal session. If the CLI crashes, run `aim crash` to salvage the interrupted session.
*   **Anti-Drift Shield:** A background hook continuously tracks autonomous tool calls. Every 50 actions, it forcefully halts execution and requires the agent to recite its GitOps rules, preventing "Lost in the Middle" context degradation.
*   **Peer-to-Peer Wiki Sync (Syncthing):** Offload heavy memory compilation to a secondary server by syncing the `memory-wiki/` folder natively via Syncthing.

---

## 📖 Documentation & Philosophy

A.I.M. separates fast onboarding documentation from deep philosophical essays and architectural diagrams.

- **[The Official A.I.M. Wiki](https://github.com/BrianV1981/aim/wiki)**: The primary onboarding ramp. Includes step-by-step user guides, configuration variables, and tutorials.
- **[The A.I.M. Knowledge Base (Public Obsidian Vault)](https://github.com/BrianV1981/aim-wiki)**: A massive, decentralized digital garden containing our raw benchmark JSON logs, architectural design history, and the complete "vibe coding" origin story.

---

### 🧬 The A.I.M. Ecosystem

> ⚠️ **DISCLAIMER: WORK IN PROGRESS**
> The repositories below are experimental adaptations. **This repository (`aim`) is the primary "Soul" of the project.** The core architectural decisions, the memory logic, and the central integrations happen here first before being ported to the external adaptations.

- **[aim](https://github.com/BrianV1981/aim):** The Core Engine (Built for Gemini CLI).
- **[aim-claude](https://github.com/BrianV1981/aim-claude):** Adaptation for Anthropic's Claude Code.
- **[aim-codex](https://github.com/BrianV1981/aim-codex):** Adaptation for OpenAI's GPT Codex.
- **[aim-antigravity](https://github.com/BrianV1981/aim-antigravity):** The experimental GUI/MCP Desktop adaptation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
☕ **Support the project:** [Buy Me a Coffee](https://buymeacoffee.com/brianv1981)