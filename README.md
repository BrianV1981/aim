# A.I.M. (Actual Intelligent Memory)

> **"Target acquired. Ready to AIM."**

**A.I.M.** is a **Sovereign Intelligence Layer** and agentic exoskeleton designed for the [Gemini CLI](https://github.com/google/gemini-cli). It transforms transient, fragmented AI sessions into a continuous, high-fidelity engineering partnership by providing a persistent, searchable, and self-distilling memory.

Most AI agents suffer from "Context Bloat" or total amnesia between sessions. A.I.M. solves this by giving the AI a **Hybrid Sovereign Brain**—separating granular forensic history from high-level architectural reasoning.

---

## 🧠 Core Architecture: The Three-Tiered Memory System

A.I.M. manages intelligence through three distinct layers, optimized for token efficiency and retrieval speed:

| Layer | Tier | Purpose | Storage |
| :--- | :--- | :--- | :--- |
| **The Pulse** | Transient | Immediate technical context and momentum for the current turn. | `continuity/` |
| **The Log** | Narrative | A chronological, scrubbed history of intent, actions, and outcomes. | `memory/` |
| **The Core** | Durable | Stable architectural facts, project rules, and "Atomic Truths." | `core/` |

### 1. The Forensic Engine (Archivist)
A.I.M. indexes every thought, tool call, and user prompt into a **Unified SQLite Database** (`forensic.db`).
*   **Near-Instant Search:** Replaces O(N) file scanning with optimized SQL queries.
*   **Local Sovereignty:** Uses **Ollama + Nomic-Embed-Text** locally by default. Your raw session data never leaves your machine during indexing.
*   **Traceability:** Perform deep-dives into your history with `aim search "logic description" --context`.

### 2. The Flash Distiller (Librarian)
Messy session logs are automatically distilled into lean "Memory Proposals."
*   **Token Tax Awareness:** The distiller ruthlessly compresses narrative history into durable facts, keeping `core/MEMORY.md` small and high-signal.
*   **Human-in-the-Loop:** A.I.M. proposes updates; you approve them via `aim commit`.

### 3. The Safety Sentinel (Guardian)
A multi-layered security protocol that protects your system and your secrets.
*   **Path Guardrails:** Hard-blocked access to files outside your authorized workspace root.
*   **Intent Auditing:** An AI-backed auditor analyzes the *intent* of destructive commands (rm, replace) against your project momentum before execution.
*   **Secret Shield:** Real-time scanning prevents accidental leakage of API keys or credentials into logs.

### 4. The Obsidian Bridge (Sovereign Backup)
A.I.M. mirrors your project's technical "Soul" into an external **Obsidian Vault**.
*   **Hardened Recovery:** Your memories exist outside the Git-tracked repo, protecting you from accidental deletions or environment wipes.
*   **Human-Centric UI:** Browse your daily logs, core rules, and technical roadmap in a high-fidelity, linked Markdown environment.
*   **Zero-Token History:** Access your past engineering decisions for $0 in API costs by browsing your local vault.

### 5. Universal Portability (Zero-Hardcoding)
A.I.M. is designed to be shared and deployed across different systems effortlessly.
*   **Environment Agnostic:** The engine makes zero assumptions about your username, home directory, or folder structure.
*   **Dynamic Discovery:** All internal paths are resolved at runtime relative to the project's physical location on disk via `src/config_utils.py`.
*   **Auto-Repairing Config:** If you clone the repository or move the project folder, A.I.M. detects the shift and automatically heals its internal configuration to match the new reality.

### 6. Specialist Delegation Model (Sub-agents)
A.I.M. leverages a "Split-Brain" architecture to expand its expertise without diluting its core soul.
*   **Modular Specialists:** Spawn dedicated experts (e.g., `technical-auditor`) for narrow, high-precision tasks.
*   **The Dispatch Protocol:** Every delegation utilizes a **Dispatch Packet** containing immediate context and RAG triggers to "awaken" the sub-agent's specialist memory.
*   **Context Isolation:** Sub-agents operate in isolated "Vaults"—they cannot see your main conversation history, preventing context bloat and ensuring total focus.

---

## 🚀 Sovereign Installation

A.I.M. is built to be portable and easy to set up on any Linux/macOS system.

### 1. Prerequisite: Gemini CLI
A.I.M. is an exoskeleton for the official Gemini CLI.
```bash
npm install -g @google/gemini-cli
```

### 2. Clone & Bootstrap
```bash
git clone https://github.com/BrianV1981/aim.git
cd aim
./setup.sh
```
The `setup.sh` script creates a local Python virtual environment, installs dependencies, and configures the `aim` alias in your `.bashrc` or `.zshrc`.

### 3. Personalized Onboarding
```bash
aim init
```
The installer will prompt you for your name, tech stack, and working style to personalize your A.I.M. instance from the first second. It also scaffolds your workspace and generates your core documentation.

### 4. The Cockpit (TUI)
```bash
aim tui
```
Launch the interactive configuration dashboard to set your AI providers (Gemini, Ollama, Codex, etc.) and secure your **System Vault** (API Keys).

---

## 🏗️ The A.I.M. Command Suite

*   **`aim status`**: View the current project momentum and pending memory proposals.
*   **`aim search`**: Near-instant forensic search (e.g., `aim search "solana logic" --context`).
*   **`aim commit`**: One-click approval of new architectural memories with safety shadowing.
*   **`aim handoff`**: Manual trigger for technical reflection and mental-model synthesis.
*   **`aim push`**: Auto-versioned deployment to GitHub with unique semantic timestamps.
*   **`aim purge`**: **Clean Slate Protocol.** Wipes all history and resets momentum for a fresh start.
*   **`aim uninstall`**: Interactive uninstaller with "Software Only" or "Total Purge" options.

---

## 🛡️ Security & Privacy
A.I.M. is designed for maximum data sovereignty:
*   **System Vault:** API keys are stored in your computer's built-in **Encrypted Keyring** (macOS Keychain, Windows Credential Manager, or Linux Secret Service). No `.env` files or plain-text keys.
*   **Dynamic Scrubbing:** The `telemetry_scrubber.py` dynamically purges your username and sensitive keys from all logs before they are indexed.
*   **Local-First:** All embedding and forensic search can be performed 100% offline using Ollama.

---

"I believe I've made my point." — **A.I.M.**
