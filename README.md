# A.I.M. (Actual Intelligent Memory)

> **"Target acquired. Ready to AIM."**

**A.I.M.** is a **Sovereign Intelligence Layer** specifically built as an exoskeleton for the [Gemini CLI](https://github.com/google/gemini-cli). It transforms transient AI sessions into a continuous, high-fidelity engineering partnership with a permanent memory.

Most AI agents suffer from "Context Bloat" or amnesia. A.I.M. solves this by giving **Gemini** a **Hybrid Sovereign Brain**—separating forensic history from architectural reasoning.

---

## 🧠 The Gemini-Native Architecture

### 1. The Separation of Powers
A.I.M. manages Gemini's memory through specialized components:

*   **The Archivist (Memory Layer)**: Indexes every thought, tool call, and user prompt.
    *   **Recommended (Gemini)**: Uses Google’s `gemini-embedding-2` (3072 dimensions) for a **Google-grade search engine** across your memories.
    *   **In-House (Ollama/Local)**: Recommended for sensitive data. Uses **Ollama + Nomic** locally. Ollama Cloud is also supported and preferred for privacy, as they do not keep chat logs for training.
*   **The Librarian (Reasoning Layer)**: Distills messy logs into the project's "Soul" (`core/MEMORY.md`).
    *   **Recommended (Gemini Flash)**: Best-in-class reasoning-to-token ratio for architectural synthesis.
    *   **Sovereign (Llama3/Qwen)**: Swappable for local/cheap alternatives via the Cockpit for 100% offline reasoning.
*   **The Sentinel (Safety Layer)**: A real-time auditor that prevents Gemini from making destructive mistakes outside of your project's intent.
    *   **Local Mode ($0 Cost)**: Operates instantly using path-based guardrails. It prevents unauthorized access or modification of files outside your defined project root.
    *   **Full AI Mode (Intent Audit)**: The "Agentic Compliment" to your security. It uses your **chosen reasoning LLM** (Gemini, GPT-5.4, or Llama) to analyze the *intent* of state-altering commands against your current project momentum, blocking stray destructive actions.

### 2. Privacy & Data Sovereignty
Semantic memory search is inherently sensitive. While A.I.M. includes an automated **Flywheel Scrubber** (`scripts/telemetry_scrubber.py`) to purge keys and paths, we strongly recommend:
*   **Local Indexing**: Use Ollama locally to ensure your raw fragments never leave your machine during the search coordinate generation.
*   **Privacy-First Clouds**: If using cloud, prefer **Ollama Cloud** or **Gemini Flash** (on-demand) over providers that aggregate data for learning.

### 3. Radical Token Efficiency
A.I.M. keeps Gemini's context window clean by using a **Three-Tiered Hierarchy**:
*   **Forensic Tier**: Unlimited granular data (Cost: $0 via Local).
*   **Narrative Tier**: A rolling daily log of technical momentum.
*   **Durable Tier**: Foundational rules injected into every Gemini session.

---

## 🚀 Quick Start

### 1. Prerequisite: Install Gemini CLI
A.I.M. is a context layer for the [Gemini CLI](https://github.com/google/gemini-cli).
```bash
npm install -g @google/gemini-cli
```

### 2. Clone & Bootstrap
```bash
git clone https://github.com/BrianV1981/aim.git
cd aim
python3 scripts/aim_init.py
```

### 3. Configure the Cockpit
Launch the TUI to set your providers and secure your System Vault.
```bash
# Set alias: alias aim='$(pwd)/scripts/aim_cli.py'
aim tui
```

---

## 🏗️ The A.I.M. CLI (`aim`)
*   **`aim init`**: Scaffolds a new workspace.
*   **`aim tui`**: Interactive dashboard for providers and the System Vault (Alias: `aim config`).
*   **`aim status`**: See current momentum and pending memory proposals.
*   **`aim search`**: Forensic semantic search (e.g., `aim search "solana logic" --context`).
*   **`aim commit`**: One-click approval of new architectural memories.
*   **`aim health`**: Workspace audit (Git, Index, Secrets).
*   **`aim handoff`**: Manual trigger for mental-model synthesis.

---

## 🏗️ The Three-Layer Memory System

| Layer | Type | Location | Purpose |
| :--- | :--- | :--- | :--- |
| **The Pulse** | Transient | `continuity/` | The "RAM"—immediate technical context for the next turn. |
| **The Log** | Narrative | `memory/` | The "Tape"—a forensic-grade history of intent. |
| **The Core** | Durable | `core/` | The "Rules"—stable facts and architectural logic. |

---

## 🛡️ Security & The "System Vault"
A.I.M. uses your computer's built-in **Encrypted System Vault** (macOS Keychain, Windows Credential Manager, or Linux Secret Service). API keys are never stored in `.env` files or JSON configurations.

---

"I believe I've made my point." — **A.I.M.**
