<div align="center">

# A.I.M. (Actual Intelligent Memory)
**"Sovereign Intelligence. Technical Continuity. Project Singularity."**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/github/v/release/BrianV1981/aim)]()
[![Platform](https://img.shields.io/badge/Platform-Gemini%20CLI-0088cc.svg)]()
[![CI/CD Status](https://img.shields.io/github/actions/workflow/status/BrianV1981/aim/test.yml?branch=main&label=tests&logo=github)](https://github.com/BrianV1981/aim/actions)
[![Sponsor](https://img.shields.io/badge/Sponsor-Buy_Me_A_Coffee-FF813F?logo=buy-me-a-coffee)](https://buymeacoffee.com/BrianV1981)

**A.I.M.** is a professional-grade **Engineering Exoskeleton** and **High-Fidelity Memory Layer** designed for the modern AI coding era. It cures the "Amnesia Problem" of autonomous agents by giving them a localized, self-cleaning, hybrid brain.

> 📖 **Full Documentation:** [Read the Official GitHub Wiki](https://github.com/BrianV1981/aim/wiki)
> 🛠️ **Engineers:** Hate biological metaphors? [Read the brutal, metaphor-free Technical Spec here](docs/TECHNICAL_SPEC.md).

</div>

---

## 🛑 The Problem: The 50-Turn Spaghetti Code
If you let an AI agent code autonomously, it is brilliant for the first 10 turns. By turn 50, its context window is overflowing, it forgets your architectural rules, it hallucinates file paths, and your repository degrades into unmaintainable spaghetti code.

## 🚀 The Solution: A Sovereign Exoskeleton
A.I.M. wraps around your CLI agent (Gemini/Codex) and physically forces it to act like a disciplined Principal Engineer. It externalizes the agent's memory into a local SQLite database, automates its Git lifecycle, and prunes its thoughts while you sleep.

---

## 🧠 The Biological Architecture (v1.7)
A.I.M. does not use a standard RAG pipeline. It models its architecture entirely on human memory systems—separating autonomic reflexes from short-term processing and deep subconscious recall.

### 1. The Autonomic Nervous System (The Python Engine)
Just like a human breathes without thinking, A.I.M. relies on invisible, autonomic Python scripts (`failsafe_context_snapshot.py`). These scripts silently index data, capture checkpoints, and scrub secrets in the background, requiring **zero context tokens** and zero conscious thought from the AI.

### 2. The Conscious Mind (The Cascading Sieve)
Throughout the day, humans absorb massive amounts of noisy data. We naturally filter this noise before sleeping. A.I.M. replicates this using a 4-Tier "Rolling Proposal" hierarchy:

| Tier | Title | Biological Equivalent |
| :--- | :--- | :--- |
| **Tier 1 (Hourly)** | **The Harvester** | Short-term buffering. A 100% free Python script strips the chaotic terminal noise into a clean JSON skeleton. |
| **Tier 2 (Daily)** | **Daily Distiller**| REM Sleep. Squashes the daily logs and generates the first **Memory Proposal**. |
| **Tier 3 (Weekly)** | **Weekly Arc** | Deep consolidation. Reviews 7 Daily Proposals and generates a condensed **Weekly Proposal**. |
| **Tier 4 (Apex)** | **The Proposer** | Core personality shifts. Synthesizes everything into a **Monthly Proposal** for the agent's fundamental `MEMORY.md`. |

> ⏱️ **The Interval Dial & The Rolling Proposal:** You do not have to wait a month to update your memory. You can run `aim commit` at any time after 24 hours. A.I.M. will simply grab the highest-tier proposal currently available, apply it to the database, and permanently delete the underlying scaffolding.

### 3. The Subconscious (Hybrid RAG)
The permanent architectural memory is stored in the **Engram DB**.
**The "Photograph" Effect:** Human memory is flawed. If someone asks, "Do you remember that time?" (Semantic Search), you might genuinely draw a blank. But if they show you a specific photograph (Exact Keyword), your brain is jarred and the entire memory floods back. A.I.M. uses **Hybrid Retrieval**. It searches for abstract "vibes" using dense Vector Embeddings, but pairs that with **FTS5 Lexical Matching**. Hitting the database with an exact variable name (the photograph) instantly jars the AI's full context back to life.

---

## 🔥 Killer Features

### 🔀 Modular Cognitive Routing (The Frankenstein Brain)
A.I.M. allows you to stitch together different LLMs for different cognitive functions using the **Universal Hub (`aim tui`)**. You can route the 4 tiers of the subconscious to completely different API providers (Google, OpenAI, Anthropic, OpenRouter, or Local Ollama).
*   **The Frontal Lobe:** Keep a flagship model (**Gemini 3.1 Pro** or **Claude 3.5**) as your main coding agent for maximum logic and reasoning.
*   **The Muscle:** Offload the massive, tedious background tasks (like the Tier 2 Daily Distiller) to incredibly fast, cheap models like **Gemini Flash** or **Haiku**. 
*   **The Free Offline Brain:** You can even route the background memory pipeline to a **Local Ollama (Llama-3)** instance running on your GPU. A.I.M. automatically injects **Explicit Guardrails** into local models to prevent hallucination, giving you flagship intelligence at the terminal with $0 API costs for background memory management.

### 🔌 The DataJack Protocol ("I Know Kung Fu")
A.I.M. allows you to instantly share knowledge without burning CPU cycles on embeddings. You can package 10,000 pages of Python documentation into a single `.engram` cartridge. When another developer runs `aim jack-in python.engram`, it executes a secure, parameterized SQLite data insertion directly into their database. The agent wakes up 3 seconds later with flawless, pre-calculated semantic recall of the entire language. *(Zero embedding calls. One person pays the compute tax once — the entire community inherits perfect recall forever).*

```text
> aim jack-in python314.engram
[1/2] Unpacking cartridge...
[2/2] Downloading Math (Nomic Embeddings) into Subconscious...
[SUCCESS] I know Kung Fu. (503 knowledge sessions injected in 3.1s)
```

### 🐙 The GitOps Bridge
A.I.M. refuses to let your AI create messy Git histories. It features a natively integrated, autonomous deployment suite:
- **`aim bug "desc"`**: Uses the `gh` CLI to instantly generate a bug ticket, attaching the agent's crash stack trace.
- **`aim fix <id>`**: Forces the AI into a clean, isolated branch (`fix/issue-x`) for strict TDD isolation.
- **`aim push "msg"`**: Parses Conventional Commits (`Feature:`, `Fix:`), calculates SemVer version bumps, and auto-generates your `CHANGELOG.md`.

### 🛡️ The Context Collapse Shield & Subagent Bouncer
When the Gemini CLI hits 50% capacity, it automatically summarizes your history to save context. This summarization is lossy and causes the agent to forget specific code paths. A.I.M. intercepts this lifecycle, running a pre-compression hook that extracts your raw JSON into a condensed "Signal Skeleton" (reducing token weight by up to 85%), ensuring the AI retains flawless tactical memory even after the CLI collapses its context window. Furthermore, if you spin up a temporary subagent, A.I.M.'s "Bouncer" script detects the `[EPHEMERAL]` tag and permanently bans the subagent's frantic noise from polluting your long-term database.

### 🌐 Universal IDE Support (MCP)
A.I.M. isn't locked to the terminal. The built-in **Model Context Protocol (MCP) Server** exposes the Engram DB to your IDE. You can natively query your project's historical memory directly inside **Cursor**, **VS Code**, or **Claude Desktop**.

---

## 🛠️ The Command Suite
- `aim init` : Launch the dynamic setup wizard (Clean Sweep & Cognitive Guardrails).
- `aim tui` : The Cockpit. Configure multi-provider LLM routing and safety guardrails.
- `aim search` : Sub-millisecond Hybrid semantic/lexical search.
- `aim jack-in` : Instantly download a `.engram` knowledge cartridge.
- `aim status` : View project momentum and the current "Technical Edge."
- `aim health` : Instant, zero-token diagnostic check of the brain pipeline.
- `aim update` : Safe, one-command update to pull the latest A.I.M. code without losing your local memory.

---

## 📖 The Master Schema
For a deep dive into the architecture, the 4-Tier distillation algorithms, and the Sovereign Sync protocols, read the official constitution:
👉 **[The A.I.M. Technical Handbook](docs/A_I_M_HANDBOOK.md)**

---

## 🏗️ Sovereign Installation (Native Linux / WSL)

A.I.M. requires a hardened environment to operate autonomously. For the complete, detailed deployment manual (including Obsidian Vault setup), read the [Getting Started Guide](docs/GETTING_STARTED.md).

### 1. Environment Hardening
Remove restricted utilities and install native permissions for Python and SQLite:
```bash
sudo snap remove curl
sudo apt update && sudo apt install -y curl git python3-venv libfuse2t64 xdg-utils
```

### 2. The AI Runtimes (Gemini & Ollama)
Ensure Node.js v20+ is installed before pulling the CLI:
```bash
# Install NVM and Node 20
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install 20 && nvm use 20

# Install the Primary Frontal Lobe
npm install -g @google/gemini-cli
gemini login  # CRITICAL: Authenticate before proceeding!

# Install the Subconscious Engine (Ollama Embeddings)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text
```

### 3. Exoskeleton Bootstrap
Clone the architecture and execute the Clean Sweep initialization:
```bash
git clone https://github.com/BrianV1981/aim.git
cd aim
./setup.sh
source ~/.bashrc
aim init
```

---

> *"I built A.I.M. because every other memory framework failed to meet my expectations. Like most things in life: if you want it done right, you usually have to do it yourself."* — **Brian Vasquez**
