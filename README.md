# A.I.M. (Actual Intelligent Memory)

> **"Target acquired. Ready to AIM."**

**A.I.M.** is a **Sovereign Intelligence Layer** specifically built as an exoskeleton for the [Gemini CLI](https://github.com/google/gemini-cli). It transforms transient AI sessions into a continuous, high-fidelity engineering partnership with a permanent memory.

Most AI agents suffer from "Context Bloat" or amnesia. A.I.M. solves this by giving **Gemini** a **Hybrid Sovereign Brain**—separating forensic history from architectural reasoning.

---

## 🧠 The Gemini-Native Architecture

### 1. The Separation of Powers
A.I.M. manages Gemini's memory through specialized components:

*   **The Archivist (Memory Layer)**: Indexes every thought, tool call, and user prompt.
    *   **Forensic Engine**: Uses a **Unified SQLite Database** (`forensic.db`) for near-instant search across thousands of session fragments.
    *   **Recommended (Local)**: Uses **Ollama + Nomic** locally. Zero cost, 100% privacy.
*   **The Librarian (Reasoning Layer)**: Distills messy logs into the project's "Soul" (`core/MEMORY.md`).
    *   **Recommended (Gemini Flash)**: Best-in-class reasoning-to-token ratio for architectural synthesis.
*   **The Sentinel (Safety Layer)**: A real-time auditor that prevents Gemini from making destructive mistakes outside of your project's intent.
    *   **Local Mode ($0 Cost)**: Operates instantly using path-based guardrails.
    *   **Full AI Mode (Intent Audit)**: Uses your **chosen reasoning LLM** to analyze the *intent* of state-altering commands against your current project momentum.

### 2. Privacy & Data Sovereignty
A.I.M. is built for developers who care about security:
*   **Dynamic Scrubbing**: `telemetry_scrubber.py` automatically purges keys and sensitive paths from raw logs during the flywheel.
*   **Encrypted Vault**: API keys are stored in your computer's built-in **System Vault** (macOS Keychain, Windows Credential Manager, or Linux Secret Service) via `keyring`. No `.env` files.

### 3. Radical Token Efficiency
A.I.M. keeps Gemini's context window clean by using a **Three-Tiered Hierarchy**:
*   **Forensic Tier**: Unlimited granular data (Cost: $0 via Local SQLite).
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
./setup.sh
```

### 3. Initialize & Configure
```bash
# Initialize the workspace
aim init

# Configure the Cockpit
aim tui
```

---

## 🏗️ The A.I.M. CLI (`aim`)
*   **`aim status`**: See current momentum and pending memory proposals.
*   **`aim tui`**: Interactive dashboard for providers and the System Vault (Alias: `aim config`).
*   **`aim search`**: Near-instant forensic search (e.g., `aim search "solana logic" --context`).
*   **`aim commit`**: One-click approval of new architectural memories (with safety shadows).
*   **`aim push`**: Auto-versioned deployment to GitHub.
*   **`aim handoff`**: Manual trigger for mental-model synthesis.

---

## 🏗️ The Three-Layer Memory System

| Layer | Type | Location | Purpose |
| :--- | :--- | :--- | :--- |
| **The Pulse** | Transient | `continuity/` | The "RAM"—immediate technical context for the next turn. |
| **The Log** | Narrative | `memory/` | The "Tape"—a forensic-grade history of intent. |
| **The Core** | Durable | `core/` | The "Rules"—stable facts and architectural logic. |

---

"I believe I've made my point." — **A.I.M.**
