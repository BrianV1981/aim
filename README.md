<div align="center">

# A.I.M. (Actual Intelligent Memory)
**"Sovereign Intelligence. Technical Continuity. Project Singularity."**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-1.7.0-blue.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Gemini%20CLI-0088cc.svg)]()

**A.I.M.** is a professional-grade **Engineering Exoskeleton** and **High-Fidelity Memory Layer** designed for the modern AI coding era. It cures the "Amnesia Problem" of autonomous agents by giving them a localized, self-cleaning, hybrid brain.

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
Throughout the day, humans absorb massive amounts of noisy data. We naturally filter this noise before sleeping. A.I.M. replicates this using a 4-Tier processing hierarchy:
*   **Tier 1 (The Harvester):** Short-term buffering. Narrates the chaotic terminal noise of the last hour.
*   **Tier 2 (Daily Distiller):** REM Sleep. Squashes the daily noise, deletes completed tasks, and files away important lessons.
*   **Tier 3 (Weekly Arc):** Deep consolidation. Reviews the week and drops irrelevant context.
*   **Tier 4 (The Proposer):** Core personality shifts. Proposes permanent changes to the agent's fundamental `MEMORY.md`.

### 3. The Subconscious (Hybrid RAG)
The permanent architectural memory is stored in the **Engram DB**.
**The "Photograph" Effect:** Human memory is flawed. If someone asks, "Do you remember that time?" (Semantic Search), you might genuinely draw a blank. But if they show you a specific photograph (Exact Keyword), your brain is jarred and the entire memory floods back. A.I.M. uses **Hybrid Retrieval**. It searches for abstract "vibes" using dense Vector Embeddings, but pairs that with **FTS5 Lexical Matching**. Hitting the database with an exact variable name (the photograph) instantly jars the AI's full context back to life.

---

## 🔥 Killer Features

### 🔀 Cognitive Routing (Offload the Brain Power)
Why pay flagship API prices for background tasks? A.I.M.'s built-in **Universal Hub (TUI)** allows you to route different parts of the brain to different LLMs:
*   **The Frontal Lobe:** Keep **Gemini 3.1 Pro** as your main coding agent for maximum reasoning.
*   **The Muscle:** Offload the massive, tedious background tasks (like the Tier 1 Harvester and the Indexer) to incredibly fast, cheap models like **Gemini Flash**, **Haiku**, or even a **Local Ollama Llama-3** instance running on your GPU. 
*   *Result:* You get flagship intelligence at the terminal, with a 90% reduction in API costs for the background memory pipeline.

### 🔌 The DataJack Protocol ("I Know Kung Fu")
A.I.M. allows you to instantly share knowledge without burning CPU cycles on embeddings. You can package 10,000 pages of Python documentation into a single `.engram` cartridge. When another developer runs `aim jack-in python.engram`, it executes a raw SQLite injection directly into their database. The agent wakes up 3 seconds later with flawless, pre-calculated semantic recall of the entire language.

### 🐙 The GitOps Bridge
A.I.M. refuses to let your AI create messy Git histories. It features a natively integrated, autonomous deployment suite:
- **`aim bug "desc"`**: Uses the `gh` CLI to instantly generate a bug ticket, attaching the agent's crash stack trace.
- **`aim fix <id>`**: Forces the AI into a clean, isolated branch (`fix/issue-x`) for strict TDD isolation.
- **`aim push "msg"`**: Parses Conventional Commits (`Feature:`, `Fix:`), calculates SemVer version bumps, and auto-generates your `CHANGELOG.md`.

### 🛡️ The Pre-Compression Shield & Subagent Bouncer
When the Gemini CLI hits 50% capacity, it destroys raw history. A.I.M. intercepts this event and mirrors 100% of your raw JSON logs to a local "Panopticon Archive" for absolute forensic truth. Furthermore, if you spin up a temporary subagent to do a quick task, A.I.M.'s "Bouncer" script detects the `[EPHEMERAL]` tag and permanently bans the subagent's frantic noise from polluting your long-term database.

### 🌐 Universal IDE Support (MCP)
A.I.M. isn't locked to the terminal. The built-in **Model Context Protocol (MCP) Server** exposes the Engram DB to your IDE. You can natively query your project's historical memory directly inside **Cursor**, **VS Code**, or **Claude Desktop**.

---

## 🛠️ The Command Suite
- `aim init` : Launch the dynamic setup wizard (Clean Sweep & Cognitive Guardrails).
- `aim tui` : The Cockpit. Configure multi-provider LLM routing and safety guardrails.
- `aim search` : Sub-millisecond Hybrid semantic/lexical search.
- `aim status` : View project momentum and the current "Technical Edge."
- `aim health` : Instant, zero-token diagnostic check of the brain pipeline.
- `aim update` : Safe, one-command update to pull the latest A.I.M. code without losing your local memory.

---

## 🏗️ Sovereign Installation

### 1. Prerequisites
```bash
# Install Gemini CLI
npm install -g @google/gemini-cli
# Install Ollama & Nomic (For local embeddings)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text
```

### 2. Implementation
```bash
git clone https://github.com/BrianV1981/aim.git
cd aim
./setup.sh
source ~/.bashrc
aim init
```

---

> *"Verification First. Never believe an AI's summary without querying the raw forensic truth in the Engram DB."* — **A.I.M.**
