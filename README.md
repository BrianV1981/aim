# A.I.M. (Actual Intelligent Memory)

> **"Target acquired. Ready to AIM."**

**A.I.M.** is a **Sovereign Intelligence Layer** specifically built as an exoskeleton for the [Gemini CLI](https://github.com/google/gemini-cli). It transforms transient AI sessions into a continuous, high-fidelity engineering partnership with a permanent memory.

Most AI agents suffer from "Context Bloat" or amnesia. A.I.M. solves this by giving **Gemini** a **Hybrid Sovereign Brain**—separating forensic history from architectural reasoning.

---

## 🧠 The Gemini-Native Architecture

### 1. The Separation of Powers
A.I.M. manages Gemini's memory through specialized components:
*   **The Archivist (Local)**: Uses **Ollama** to index every thought and tool call Gemini makes. It allows Gemini to "search its own past" via `aim search` with $0 token cost.
*   **The Librarian (GPT-5.4/Gemini)**: A high-reasoning layer that distills messy logs into the "Soul" of the project (`core/MEMORY.md`).
*   **The Sentinel**: A real-time auditor that stops Gemini from making destructive mistakes outside of your project's intent.

### 2. Radical Token Efficiency
A.I.M. keeps Gemini's context window clean by using a **Three-Tiered Hierarchy**:
*   **Forensic Tier**: Unlimited granular data (Cost: $0).
*   **Narrative Tier**: A rolling daily log of technical momentum.
*   **Durable Tier**: Foundational rules injected into every Gemini session.
This ensures Gemini stays "smart" for months without re-reading thousands of past conversations.
...

A.I.M. uses a **Three-Tiered Memory Hierarchy** to keep your context window clean:
*   **Forensic Tier**: Unlimited granular data stored in a local vector index (Cost: $0).
*   **Narrative Tier**: A rolling daily log of momentum and "The Story."
*   **Durable Tier**: Foundational rules and infrastructure injected into every session.
This ensures your agent stays "smart" for months without re-reading thousands of past tokens.

### 3. Sovereign Security
Your secrets and private paths never leave your machine. A.I.M. uses a **Sequential Flywheel**:
1.  **Scrub**: Purges API keys and home paths from raw logs.
2.  **Index**: Generates mathematical vectors locally via Nomic.
3.  **Distill**: Synthesizes the clean data for long-term memory.
All keys are stored in your **System's Secure Vault** (Keychain), never in plaintext.

---

## 🚀 Quick Start

### 1. Prerequisite: Install Gemini CLI
A.I.M. is a context layer for the [Gemini CLI](https://github.com/google/gemini-cli). You **must** have it installed first.
```bash
npm install -g @google/gemini-cli
```

### 2. Clone & Bootstrap A.I.M.
```bash
git clone https://github.com/BrianV1981/aim.git
cd aim
python3 scripts/aim_init.py
```

### 3. Configure your Brain
Launch the **Configuration Cockpit** to set your API keys and choose your providers.
```bash
# Set your alias first: alias aim='$(pwd)/scripts/aim_cli.py'
aim tui
```

---

## 🏗️ The A.I.M. CLI (`aim`)
*   **`aim init`**: Scaffolds a new workspace.
*   **`aim tui`**: Interactive dashboard for providers and the System Vault.
*   **`aim status`**: See current momentum and pending memory proposals.
*   **`aim search`**: Forensic semantic search (e.g., `aim search "solana logic" --context`).
*   **`aim commit`**: One-click approval of new architectural memories.
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
