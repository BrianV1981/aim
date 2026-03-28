# A.I.M. (Actual Intelligent Memory)

**"Treat your AI like a bot, not an oracle. Built by a gamer, for the trenches."**

☕ **Support the project:** [Buy Me a Coffee](https://buymeacoffee.com/brianv1981)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-1.24.0-blue.svg)](https://github.com/BrianV1981/aim/blob/main)
[![Platform](https://img.shields.io/badge/Platform-Gemini%20CLI-0088cc.svg)](https://github.com/BrianV1981/aim/blob/main)

**A.I.M.** is an open-source engineering A.I.M. OS designed to cure the "Amnesia Problem" of autonomous AI agents.

---

## 📖 Core Documentation (For Engineers)
> *If you hate biological metaphors ("Brain", "Subconscious", "Frontal Lobe") and just want to see the exact mechanical architecture and database schemas, read these two documents:*
> 
> 🛠️ **[The Technical Specification](https://github.com/BrianV1981/aim/wiki/Technical-Specification)** — Metaphor-free engineering specs.
> 🗺️ **[The Master Schema](https://github.com/BrianV1981/aim/wiki/The-Master-Schema)** — The definitive structural map of the platform.

---

> ⚠️ **ALPHA STATUS & THE VIBE CODING ORIGIN**
>
> A.I.M. wasn't built by a machine learning researcher in Silicon Valley. It was built by a gamer who spent years writing macros and automation bots for MMOs — Asheron's Call, Star Wars Galaxies, SWTOR, and anything else with repetitive clicking or a second account that needed a buff bot.
>
> When you automate an MMO character, you learn quickly that you can't rely on "magic." You need rigid state machines, clearly defined scopes, memory limits, and watchdog timers to reset the bot when it inevitably wanders off path. A.I.M. applies this exact philosophy to LLMs. Instead of trying to build a smarter brain, A.I.M. provides the leash.
>
> **This project is radically transparent.** It is an Alpha Proof-of-Concept built entirely via "vibe coding" — using the very A.I.M. OS it provides. The commit history shows the TUI iterations, the bug storms, the live patches against real API outputs. There is no VC-funded black box here. The plumbing is being battle-tested in public, and the architecture proves that a structured AI workflow can turn a non-coder into a systems architect.

📖 **Full Documentation:** [Read the Official GitHub Wiki](https://github.com/BrianV1981/aim/wiki)
🛠️ **Engineers:** Hate biological metaphors? [Read the metaphor-free Technical Spec here](https://github.com/BrianV1981/aim/wiki/Technical-Specification).

---

## 🛑 The Problem: The 50-Turn Spaghetti Code

If you let an AI agent code autonomously, it is brilliant for the first 10 turns. By turn 50, its context window is overflowing, it forgets your architectural rules, it hallucinates file paths, and your repository degrades into unmaintainable spaghetti code.

The industry's answer is to build a bigger context window. That's giving a distractible worker a bigger desk.

A.I.M.'s answer is a strict Standard Operating Procedure, a memory sieve, and a leash.

---

## 🚀 The Solution: A Sovereign A.I.M. OS

A.I.M. wraps around your CLI agent (Gemini/Codex) and forces it to act like a disciplined Principal Engineer. It externalizes the agent's memory into a local SQLite database, automates its Git lifecycle, and prunes its thoughts while you sleep.

---

## 🧠 The Architecture (v1.24)

A.I.M. does not use a standard RAG pipeline. Its core insight is separating **what requires an LLM** from **what doesn't** — and ruthlessly offloading everything that doesn't.

### 1. The Zero-Token Python Engine (The Autonomic Layer)

This is A.I.M.'s primary architectural breakthrough, and it's what most memory frameworks miss entirely.

**The AI industry assumes memory management requires an LLM.** A.I.M. doesn't. The Tier 1 Harvester uses pure, deterministic Python — no LLM, no API calls, zero tokens — to strip raw terminal JSON noise down to a clean "Signal Skeleton," reducing token weight by up to 85% before an LLM ever touches the data.

*   **Empirical Proof (The Noise Filter):** When processing the raw, successful `matrix_pro_run1_final.json` benchmark log, the native `scripts/extract_signal.py` script reduced the file from **269,537 characters (264 KB)** of chaotic JSON down to a pristine **56,325 characters (56 KB)** of human-readable Markdown. That is a **79.1% reduction** in context weight, executed in milliseconds, for exactly $0.00.

Background scripts (`failsafe_context_snapshot.py`) silently index data, capture checkpoints, and scrub secrets. The AI doesn't think about any of this, just like you don't think about breathing.

**The Universal Hook Router:** A.I.M. employs a context-aware global router dispatch. This means you can run 5 different agents in 5 different project directories simultaneously. The router automatically detects the active terminal and routes the memory pipeline to that specific local `engram.db`, ensuring **zero cross-contamination** between concurrent workspaces.

**The Executive Guardrails (Anti-Drift):** A.I.M. actively monitors the agent's behavior via the `cognitive_mantra` hook. It tracks autonomous tool calls. At 25 actions, it injects a silent "Subconscious Whisper" to remind the agent of its mandates. At 50 actions, it forcefully halts execution and requires the agent to output a `<MANTRA>` block reciting its GitOps rules, completely washing away "Lost in the Middle" context degradation.

### 2. The Cascading Memory Engine (The Delta Ledger)

Memory is refined through a 5-Tier self-cleaning hierarchy utilizing a Delta Ledger architecture (Phase 32):

| Tier | Title | What It Does |
|---|---|---|
| **Tier 1** | **The Scribe** | Extracts high-signal technical narratives from chaotic raw chat logs. Evaluates Hindsight Pruning (The Eureka Protocol). |
| **Tier 2** | **Memory Proposer** | Reads recent Scribe narratives and proposes structured Add/Remove deltas for `MEMORY.md`. |
| **Tier 3** | **Daily Refiner** | Deduplicates and consolidates multiple hourly Tier 2 proposals into a single Daily State. |
| **Tier 4** | **Weekly Consolidator**| Distills the past 7 Daily States into high-level project milestones and architectural shifts. |
| **Tier 5** | **Monthly Archivist** | Compresses long-term stable architecture into dense, factual axioms and archives stale context. |

> ⏱️ **The Rolling Proposal:** You don't have to wait a month. Run `aim commit` at any time and A.I.M. grabs the latest Delta Ledger proposal, applies it, and syncs the exact state via the Zero-API Obsidian Transport layer.

### 3. The Subconscious (Modular Hybrid RAG)

The permanent memory lives in the **Engram DB** — a local SQLite database with two key properties:

**Hyper-Modular Infrastructure:** The Engram system is not locked to any specific embedding model. It defaults to free local `nomic-embed-text` for zero-cost offline usage, but the architecture is designed to be instantly swappable. You can wire in cutting-edge multimodal models like `gemini-embedding-2-preview` (supporting text, image, video, audio, and PDF) and rebuild your cartridges. The system is a fluid data stream, not a stone tablet.

**The Disposable Database:** The SQLite file is not the source of truth — it's a high-speed cache. The permanent memory lives in raw `.jsonl` files in `archive/sync/`. If the database ever corrupts, `aim sync` rebuilds it from scratch. The database is disposable; the text files are eternal.

**The "Photograph" Effect:** A.I.M. uses Hybrid Retrieval — dense vector embeddings for abstract "vibe" searches, paired with FTS5 lexical matching for exact variable names and error codes. When you hit the database with a specific string, the full context floods back.

---

## 🔥 Killer Features

### 🔀 Modular Cognitive Routing (The "A La Carte" Brain)

This is A.I.M.'s primary economic advantage over generic IDE wrappers.

Cursor and Claude Code force every background task — every file summary, every memory index update — through an expensive flagship model. A.I.M. decouples the "subconscious" from the "conscious mind":

- **The Frontal Lobe:** Keep a flagship model (**Gemini 3.1 Pro** or **Opus 4.6**) as your active coding agent for complex reasoning.
- **The Subconscious:** Offload the heavy, repetitive background tasks (Tier 1 Harvester, Tier 2 Distiller) to fast, inexpensive models like **Gemini Flash**, **Sonnet**, or **Haiku**.
- **The Free Offline Brain:** Route the entire background memory pipeline to a **Local Ollama (Llama-3)** instance on your GPU. A.I.M. automatically injects explicit guardrails into local models to prevent hallucination, enabling background memory management without incurring API costs.

The result: flagship intelligence at the terminal, fraction-of-a-cent models doing the filing.

### 🎯 The Matrix Agent (Plug-and-Play Specialists)

The ultimate goal of A.I.M. is not a generalist IDE. It is a **Matrix Agent**.

By combining a specific knowledge cartridge (`django_master.engram`) with a surgically constrained `GEMINI.md` and a mandated workflow (forced `pytest` execution), you don't need the smartest model in the world. You need a model that can follow directions.

You don't rely on the LLM's pre-trained weights to know the answer. You inject the exact documentation, mandate the exact testing tools, and force the agent to loop until the terminal output is green.

### 🔌 The DataJack Swarm (Phase 38 P2P BitTorrent)

Package 10,000 pages of documentation into a single `.engram` cartridge. When another developer runs the command, the built-in `aria2` daemon handshakes with the A.I.M. P2P swarm, downloads the cartridge via Magnet Link, and executes a secure, parameterized SQLite insertion directly into their local database. The agent wakes up with pre-calculated semantic recall of the entire library. Zero embedding calls. 

```bash
> aim jack-in "magnet:?xt=urn:btih:..."
[JACK-IN] Initiating DataJack Swarm Handshake...
  -> Resolving metadata (finding peers)...
  -> Downloading... 100.0%
[SUCCESS] I know Kung Fu. (503 knowledge sessions injected in 3.1s)
```
If a cartridge is highly valuable, the community naturally seeds it. If it is garbage, the swarm lets it die. A self-cleaning, censorship-resistant decentralized knowledge network.

### 🐙 The GitOps Bridge

A.I.M. forces atomic, traceable deployments:

- **`aim bug "desc"`** — Creates a structured GitHub Issue with crash logs attached.
- **`aim fix <id>`** — Checks out a clean isolated branch (`fix/issue-x`) for TDD.
- **`aim push "msg"`** — Parses Conventional Commits, calculates SemVer bumps, auto-generates `CHANGELOG.md`.

AI agents are forbidden from raw `git commit` or `git push`. Every change is tied to an issue. Every regression is instantly revertible.

### 🛡️ The Context Collapse Shield & The Eureka Protocol (Phase 39)

When the Gemini CLI prunes history, A.I.M. intercepts the event and maintains a rolling "Failsafe Snapshot" of raw JSON logs. The Signal Skeleton reduces token weight by up to 85%.

**Hindsight Pruning (The Eureka Protocol):** If the agent spends 20,000 tokens thrashing and failing to fix a bug, but finally solves it with a single line of code, A.I.M. automatically detects the "Eureka Moment." It intercepts the memory pipeline, deletes the 15 turns of useless trial-and-error, and synthesizes a single, hyper-compressed fact: *"The agent spent 20k tokens debugging X. The final solution was simply Y."* This physically prevents your context window from permanently filling up with dead ends.

### 🛑 Predictable Restraint (Anti-Rogue Execution)
A massive danger with modern, highly capable LLMs is their tendency to "auto-execute." If you spin up a standard AI agent in a repository that contains a `TODO.md` or `TASK.md` file, it will often begin autonomously editing your code the second it boots up, without waiting for your permission. A.I.M.'s rigid GitOps and behavioral hierarchy physically suppresses this instinct. The agent treats the operator as the explicit trigger, ensuring it never touches your codebase until you give the exact execution order. *(See empirical proof of this in the [Matrix vs. Base Weights Benchmark](docs/benchmarks/BENCHMARK_DJANGO_MATRIX.md)).*

### 🌐 Universal IDE Support (MCP)

The built-in MCP Server exposes the Engram DB to any connected IDE — **Cursor**, **VS Code**, or **Claude Desktop** — without any platform-specific adapter code.

---

## 🛠️ The Command Suite

- `aim init` — Setup wizard. Clean Sweep & Cognitive Guardrails.
- `aim tui` — The Cockpit. Configure multi-provider LLM routing.
- `aim search` — Sub-millisecond Hybrid semantic/lexical search.
- `aim jack-in` — Install a `.engram` knowledge cartridge.
- `aim memory` — Run the distillation pipeline.
- `aim commit` — Apply the latest memory proposal.
- `aim status` — View project momentum and current state.
- `aim health` — Zero-token diagnostic check of the brain pipeline.
- `aim update` — Safe one-command update without losing local memory.

---

## 🏗️ Installation (Linux / WSL)

> **Note:** A.I.M. currently requires Linux or WSL (Ubuntu). macOS support is on the roadmap.

### 1. Prerequisites

```bash
# Remove restricted snap utilities
sudo snap remove curl
sudo apt update && sudo apt install -y curl git python3-venv libfuse2t64 xdg-utils

# Install NVM and Node 20+
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install 20 && nvm use 20

# Install Gemini CLI and authenticate
npm install -g @google/gemini-cli
gemini login  # CRITICAL: Do this before proceeding

# Install Ollama for local embeddings
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text
```

### 2. Install A.I.M.

```bash
git clone https://github.com/BrianV1981/aim.git
cd aim
./setup.sh
source ~/.bashrc
aim init
```

### 3. Configure

```bash
aim tui  # Set your LLM providers, routing, and guardrails
```

For the complete deployment manual including Obsidian Vault setup, see the [Installation Guide](https://github.com/BrianV1981/aim/wiki/Installation-Guide).

---

## 📖 Core Documentation

- [The Master Schema](https://github.com/BrianV1981/aim/wiki/The-Master-Schema) — Full architectural map
- [Technical Specification](https://github.com/BrianV1981/aim/wiki/Technical-Specification) — Metaphor-free engineering specs
- [Benchmarks](https://github.com/BrianV1981/aim/wiki/Benchmark-Render) — Repeatable, raw-data-backed comparisons

---

> *"Alcmaeon of Croton, Praxagoras of Kos, and Herophilus of Chalcedon were three Ancient Greek philosophers interested in the relation between the head and the body. Alcmaeon argued that the brain is the seat of intelligence, connected to the extremities of the body by poroi. Praxagoras suggested that the brain controls movement in the body, and posed the existence of neurons responsible for sending brain signals through the body. Herophilus used dissection to demonstrate the existence of a nervous system distinct from the vascular system, discovered nerves connected to inner organs and muscles, and distinguished between sensory and motor nerves."*