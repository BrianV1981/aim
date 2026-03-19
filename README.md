# A.I.M. (Actual Intelligent Memory)

> **"Target acquired. Ready to AIM."**

**A.I.M.** is a **Sovereign Intelligence Layer** designed to give the [Gemini CLI](https://github.com/google/gemini-cli) a permanent, high-fidelity memory without the "Token Tax." 

Most AI agents live in a state of perpetual amnesia or suffer from "Context Bloat." A.I.M. solves this by implementing a **Hybrid Sovereign Brain**—a multi-tier architecture that separates forensic recording from architectural reasoning.

---

## 🧠 Why A.I.M. is Special

### 1. The Separation of Powers
A.I.M. doesn't just "log chats." It runs a sophisticated intelligence pipeline managed by separate, specialized components:
*   **The Archivist (Python + Nomic)**: Uses **Ollama** to index every thought, tool call, and prompt locally. It is $0 cost, private, and provides near-instant recall of historical technical details via semantic search.
*   **The Librarian (GPT-5.4/Gemini)**: A high-reasoning layer that only "wakes up" during session transitions to distill messy logs into "Atomic Truths." It evolves your project's "Soul" (`core/MEMORY.md`) while keeping it ruthlessly lean.
*   **The Sentinel (AI Guardrails)**: A real-time security auditor that uses AI to ensure model-generated commands align with your technical intent.

### 2. Radical Token Efficiency
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
