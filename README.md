# A.I.M. (Actual Intelligent Memory)

**"Treat your AI like a bot, not an oracle. Built by a gamer, for the trenches."**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-1.7.0-blue.svg)](https://github.com/BrianV1981/aim/blob/main)
[![Platform](https://img.shields.io/badge/Platform-Gemini%20CLI-0088cc.svg)](https://github.com/BrianV1981/aim/blob/main)

**A.I.M.** is an open-source engineering exoskeleton designed to cure the "Amnesia Problem" of autonomous AI agents.

---

> ⚠️ **ALPHA STATUS & THE VIBE CODING ORIGIN**
>
> A.I.M. wasn't built by a machine learning researcher in Silicon Valley. It was built by a gamer who spent years writing macros and automation bots for MMOs — Asheron's Call, Star Wars Galaxies, SWTOR, and anything else with repetitive clicking or a second account that needed a buff bot.
>
> When you automate an MMO character, you learn quickly that you can't rely on "magic." You need rigid state machines, clearly defined scopes, memory limits, and watchdog timers to reset the bot when it inevitably wanders off path. A.I.M. applies this exact philosophy to LLMs. Instead of trying to build a smarter brain, A.I.M. provides the leash.
>
> **This project is radically transparent.** It is an Alpha Proof-of-Concept built entirely via "vibe coding" — using the very exoskeleton it provides. The commit history shows the TUI iterations, the bug storms, the live patches against real API outputs. There is no VC-funded black box here. The plumbing is being battle-tested in public, and the architecture proves that a structured AI workflow can turn a non-coder into a systems architect.

📖 **Full Documentation:** [Read the Official GitHub Wiki](https://github.com/BrianV1981/aim/wiki)
🛠️ **Engineers:** Hate biological metaphors? [Read the metaphor-free Technical Spec here](https://github.com/BrianV1981/aim/wiki/Technical-Specification).

---

## 🛑 The Problem: The 50-Turn Spaghetti Code

If you let an AI agent code autonomously, it is brilliant for the first 10 turns. By turn 50, its context window is overflowing, it forgets your architectural rules, it hallucinates file paths, and your repository degrades into unmaintainable spaghetti code.

The industry's answer is to build a bigger context window. That's giving a distractible worker a bigger desk.

A.I.M.'s answer is a strict Standard Operating Procedure, a memory sieve, and a leash.

---

## 🚀 The Solution: A Sovereign Exoskeleton

A.I.M. wraps around your CLI agent (Gemini/Codex) and forces it to act like a disciplined Principal Engineer. It externalizes the agent's memory into a local SQLite database, automates its Git lifecycle, and prunes its thoughts while you sleep.

---

## 🧠 The Architecture (v1.7)

A.I.M. does not use a standard RAG pipeline. Its core insight is separating **what requires an LLM** from **what doesn't** — and ruthlessly offloading everything that doesn't.

### 1. The Zero-Token Python Engine (The Autonomic Layer)

This is A.I.M.'s primary architectural breakthrough, and it's what most memory frameworks miss entirely.

**The AI industry assumes memory management requires an LLM.** A.I.M. doesn't. The Tier 1 Harvester uses pure, deterministic Python — no LLM, no API calls, zero tokens — to strip raw terminal JSON noise down to a clean "Signal Skeleton," reducing token weight by up to 85% before an LLM ever touches the data.

Background scripts (`failsafe_context_snapshot.py`) silently index data, capture checkpoints, and scrub secrets. The AI doesn't think about any of this, just like you don't think about breathing.

### 2. The Cascading Memory Engine (The Conscious Mind)

Memory is refined through a 4-Tier self-cleaning hierarchy:

| Tier | Title | What It Does |
|---|---|---|
| **Tier 1 (Hourly)** | **The Harvester** | Zero-token Python strips terminal noise into a Signal Skeleton. No LLM involved. |
| **Tier 2 (Daily)** | **Daily Distiller** | Squashes hourly logs into a Daily Proposal. Deletes the raw logs. |
| **Tier 3 (Weekly)** | **Weekly Arc** | Synthesizes 7 Daily Proposals into a strategic weekly summary. |
| **Tier 4 (Apex)** | **The Proposer** | Generates a final proposal for permanent changes to `MEMORY.md`. |

> ⏱️ **The Rolling Proposal:** You don't have to wait a month. Run `aim commit` at any time after 24 hours and A.I.M. grabs the highest-tier proposal available, applies it, and deletes the scaffolding.

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

### 🔌 The DataJack Protocol ("I Know Kung Fu")

Package 10,000 pages of documentation into a single `.engram` cartridge. When another developer runs `aim jack-in python.engram`, it executes a secure, parameterized SQLite insertion directly into their database. The agent wakes up with pre-calculated semantic recall of the entire library. Zero embedding calls. One person pays the compute tax once — the community inherits it.

```
> aim jack-in python314.engram
[1/2] Unpacking cartridge...
[2/2] Downloading Math (Nomic Embeddings) into Subconscious...
[SUCCESS] I know Kung Fu. (503 knowledge sessions injected in 3.1s)
```

### 🐙 The GitOps Bridge

A.I.M. forces atomic, traceable deployments:

- **`aim bug "desc"`** — Creates a structured GitHub Issue with crash logs attached.
- **`aim fix <id>`** — Checks out a clean isolated branch (`fix/issue-x`) for TDD.
- **`aim push "msg"`** — Parses Conventional Commits, calculates SemVer bumps, auto-generates `CHANGELOG.md`.

AI agents are forbidden from raw `git commit` or `git push`. Every change is tied to an issue. Every regression is instantly revertible.

### 🛡️ The Context Collapse Shield

When the Gemini CLI prunes history, A.I.M. intercepts the event and maintains a rolling "Failsafe Snapshot" of raw JSON logs. The Signal Skeleton reduces token weight by up to 85%, ensuring the agent retains critical architectural context even after compression. The "Bouncer" script detects `[EPHEMERAL]` tags on temporary subagents and bans their noise from the long-term database.

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

*"OpenClaw opened my eyes. But I wanted more control. Like most things in life — if you want it done to your specifications, you usually have to build it yourself."* — **Brian Vasquez, Creator of A.I.M.**