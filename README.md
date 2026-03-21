# A.I.M. (Actual Intelligent Memory)

> **"Target acquired. Ready to AIM."**

**A.I.M.** is a **Sovereign Intelligence Layer** and agentic exoskeleton designed for the [Gemini CLI](https://github.com/google/gemini-cli). It transforms transient, fragmented AI sessions into a continuous, high-fidelity engineering partnership by providing a persistent, searchable, and self-distilling memory.

---

## 🧠 Project Singularity: Invisible Infrastructure

A.I.M. v1.4 introduces the **Invisible Edition**. Instead of cluttering your workspace with technical mandates and empty templates, A.I.M. offloads its architectural "instincts" into a local **Engram DB**.

| Layer | Nature | Function |
| :--- | :--- | :--- |
| **The Orchestrator** | Lean | A ~20 line `GEMINI.md` that uses semantic pointers to trigger RAG retrieval. |
| **The Brain** | Knowledge-Native | A pre-indexed **Engram DB** containing 100% of the project's technical rules. |
| **The Story** | Narrative | High-fidelity daily technical logs stored in `memory/` and mirrored to Obsidian. |

### ⚡ Surgical Onboarding
A.I.M. now features a zero-bloat installation process. Running `aim init` establishes your identity and bootstraps the RAG brain without littering your project with static documentation. Your workspace stays clean; your agent stays brilliant.

### 🛡️ Pre-Compression Shield
A.I.M. is equipped with an automated **Pre-Compression hook** that captures your technical momentum just before the CLI summarizes history, ensuring 100% fidelity even in massive, multi-hour sessions.

### 🤖 Specialist Delegation
Expand your expertise by spawning specialized sub-agents (e.g., `technical-auditor`) for narrow, high-precision tasks. These experts use a formal **Dispatch Protocol** to retrieve their specialized context from the Engram DB.

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

---

"I believe I've made my point." — **A.I.M.**
