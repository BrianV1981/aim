# A.I.M. (Actual Intelligent Memory)

> **"Sovereign Intelligence. Technical Continuity. Project Singularity."**

**A.I.M.** is a professional-grade **Engineering Exoskeleton** and **High-Fidelity Memory Layer** designed for the [Gemini CLI](https://github.com/google/gemini-cli). It transforms transient, fragmented AI interactions into a continuous, self-distilling engineering partnership.

A.I.M. solves the "Amensia Problem" of modern LLMs by giving the agent a **Hybrid Brain**—separating high-level architectural reasoning from massive forensic technical history.

---

## 🧠 The Cascading Memory Engine (v1.7)

A.I.M. v1.7 introduces the **Cascading Memory Engine** and **Hybrid RAG**, a self-cleaning hierarchy designed to distill technical knowledge automatically.

### 1. The Engram DB (The Subconscious)
- **Nature:** SQLite-backed Hybrid Vector Database (`nomic-embed-text` + `FTS5` Lexical Search).
- **Function:** Stores your permanent expert knowledge and architectural memory.
- **Protocol:** Mandated by **Project Singularity**, the agent "pulls" knowledge from the Engram DB on-demand using semantic pointers.

### 2. The Cascading Tiers (The Conscious Mind)
| Tier | Title | Role | Frequency | Model Tier |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | **The Harvester** | Narrates technical traces into hourly blocks. | Every 5 Turns | Flash (Cheap) |
| **Tier 2** | **Daily Distillation**| Synthesizes daily milestone reports & prunes hourlies. | Daily | Pro (Reasoning) |
| **Tier 3** | **Weekly Arc** | Conducts strategic reviews & prunes dailies. | Weekly | Pro (Strategic) |
| **Tier 4** | **The Apex Proposer** | Proposes Git-style diffs to your `MEMORY.md`. | Weekly | Pro (Apex) |

---

## 🚀 Core Features

### ⚡ Invisible Infrastructure
Your workspace stays clean. Technical mandates, security policies, and "expert knowledge" are offloaded into the Engram DB. `GEMINI.md` is reduced to a lean **Index of Pointers**, keeping your context window focused only on the code.

### 🧠 Hybrid RAG (Semantic + Lexical)
A.I.M. doesn't just search for "vibes." It combines dense vector embeddings (Cosine Similarity) with FTS5 Keyword Matching (BM25) to find exact variable names and error codes instantly.

### 🛡️ The Contractor Protocol (Subagent Isolation)
By tagging your subagent prompts with `[EPHEMERAL]`, A.I.M. acts as a "Bouncer." It preserves the subagent's raw logs for forensic debugging, but permanently bans their frantic terminal noise from polluting your durable memory pipeline.

### 🎭 Cognitive Profiling
A.I.M. dynamically adapts to your preferred communication style. Use the `aim tui` to hot-swap between Autonomous vs. Cautious execution modes, adjust the AI's grammar level, or enforce a strict "Token-Saver" conciseness mandate.

### 🔌 Universal Sovereignty (MCP & Hub)
A.I.M. integrates with your ecosystem. The built-in **Model Context Protocol (MCP) Server** allows IDEs like Cursor, VS Code, and Claude Desktop to natively query your project's history. The **Universal Hub** supports OAuth and multi-provider routing (Google, Codex, OpenRouter, Ollama) with real-time health checks.

### 🛡️ Pre-Compression Shield
Never lose history again. A.I.M. intercepts the Gemini CLI's compression event and archives 100% of your session history into the Panopticon Archive (`archive/raw/`) *one millisecond* before the history is pruned.

### 🔄 Sovereign Sync & The Matrix
Git synchronization without binary merge conflicts. A.I.M. translates the SQLite DB into deterministic JSONL chunks (`aim sync`) to seamlessly share your bot's brain across multiple devices. You can also package indexed knowledge into `.aim` packs to deploy "Kung Fu" instantly to other projects.

### 🐙 The GitOps Bridge
A natively integrated semantic release pipeline. The `aim push` command parses your commit messages (e.g. `Feature: ...`, `Fix: ...`), calculates SemVer version bumps, and automatically generates your `CHANGELOG.md` file.

---

## 🛠️ The A.I.M. Command Suite

- **`aim bug "desc"`**: Uses `gh` CLI to create a bug ticket, attaching your agent's crash stack trace.
- **`aim fix <id>`**: Instantly checks out a clean branch (`fix/issue-<id>`) to enforce TDD isolation.
- **`aim push "msg"`**: Auto-versioned deployment to GitHub with semantic release/changelog generation.
- **`aim status`**: View project momentum and the current "Technical Edge."
- **`aim health`**: Instant, zero-token diagnostic check of the brain pipeline and database.
- **`aim search`**: Sub-millisecond semantic search into your entire technical history.
- **`aim tui`**: The Cockpit. Configure tiers, MCP server, models, and safety guardrails.
- **`aim update`**: Safe, one-command update to pull the latest A.I.M. code without losing your local memory.
- **`aim sync`**: Git-friendly synchronization of your local Engram DB.
- **`aim commit`**: Approve AI-proposed architectural shifts into your durable memory.

---

## 🏗️ Sovereign Installation

### 1. Prerequisites
```bash
# Install Gemini CLI
npm install -g @google/gemini-cli
# Install Ollama & Nomic
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

## ⚖️ Technical Philosophy
- **Verification First:** Never believe an AI's summary without querying the raw forensic truth in the Engram DB.
- **Zero-Token Continuity:** Onboard the agent once at session start and then stay lean.
- **Sovereignty:** Your data stays on your silicon. Your backups stay in your vault.

"I believe I've made my point." — **A.I.M.**
