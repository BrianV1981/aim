# A.I.M. (Actual Intelligent Memory)

> **"Target acquired. Ready to AIM."**

**A.I.M.** is a **Sovereign Intelligence Layer** and agentic exoskeleton designed for the [Gemini CLI](https://github.com/google/gemini-cli). It transforms transient, fragmented AI sessions into a continuous, high-fidelity engineering partnership by providing a persistent, searchable, and self-distilling memory.

Most AI agents suffer from "Context Bloat" or total amnesia between sessions. A.I.M. solves this by giving the AI a **Hybrid Sovereign Brain**—separating granular forensic history from high-level architectural reasoning.

---

## 🧠 Project Singularity: Retrieval-First Architecture

A.I.M. v1.3 introduces **Retrieval-Based Orchestration (RBO)**. Instead of forcing the AI to "carry" massive technical manuals in every prompt, A.I.M. uses a lean orchestrator to "pull" specific directives only when they are relevant to the task.

| Layer | Type | Purpose | Mechanism |
| :--- | :--- | :--- | :--- |
| **The Orchestrator** | Lean Soul | High-level mandates and semantic pointers. | `GEMINI.md` |
| **The Brain** | Forensic RAG | Infinite technical detail and session history. | `engram.db` (SQLite) |
| **The Story** | Narrative | Chronological, technical daily logs. | `memory/` |

### 1. The Pre-Born Brain (Static Knowledge)
During initialization, A.I.M. automatically indexes its own **Technical Handbook** and project directives into a local RAG brain. This gives the bot immediate, searchable knowledge of its own modular architecture from "Day Zero" without increasing token costs.

### 2. The Specialist Delegation Model
A.I.M. expands its expertise by spawning specialized sub-agents (e.g., `technical-auditor`) for narrow, high-precision tasks. These experts use a formal **Dispatch Protocol** to synchronize with the Engram DB before acting.

### 3. Total Sovereignty & Portability
*   **Encrypted Secrets:** API keys are managed via the OS-native system vault.
*   **Zero-Hardcoding:** All paths are resolved dynamically at runtime, ensuring 100% portability across WSL, Native Linux, and different usernames.
*   **Sovereign Backup:** The **Obsidian Bridge** mirrors your technical soul to an external vault, protecting you from environment wipes or accidental deletions.

---

## 🚀 Quick Start

### 1. Prerequisite: Gemini CLI & Ollama
```bash
npm install -g @google/gemini-cli
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text
```

### 2. Clone & Bootstrap
```bash
git clone https://github.com/BrianV1981/aim.git
cd aim
./setup.sh
source ~/.bashrc
aim init
```

### 3. The Cockpit (TUI)
```bash
aim tui
```
Configure your AI providers (Gemini, ChatGPT 5.4, Ollama) and secure your vault.

---

## 🏗️ The A.I.M. Command Suite

*   **`aim status`**: View project momentum and pending memory proposals.
*   **`aim search`**: Sub-millisecond forensic search into technical history.
*   **`aim commit`**: One-click approval of new architectural memories with safety shadowing.
*   **`aim handoff`**: Manual trigger for technical reflection and mental-model synthesis.
*   **`aim purge`**: **Clean Slate Protocol.** Wipes all history and resets momentum.

---

"I believe I've made my point." — **A.I.M.**
