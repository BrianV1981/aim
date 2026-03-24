# A.I.M. Technical Handbook (Master Schema)

This document is the definitive architectural map for the A.I.M. platform. It defines the modular components of the brain and the protocols that ensure continuity and sovereignty.

---

## SECTION 1: THE ROOT ARCHITECTURE

### 1.1 `GEMINI.md` (The Index & Soul)
- **Role:** Lean Orchestrator & Cognitive Baseline.
- **Function:** It is an explicit **Table of Contents**. Instead of holding massive walls of text, it directs the agent to query the **Engram DB** for technical policies.
- **Cognitive Guardrails:** It permanently encodes the Operator's chosen grammar level, execution mode (Autonomous vs Cautious), and the "Token-Saver" conciseness mandate.

### 1.2 The Initialization Overhaul (`aim init`)
- **Function:** A dynamic, decoupled scaffolding wizard.
- **Clean Sweep:** Allows the user to independently wipe Project Docs (Roadmap, Changelog) and/or the AI Brain (Engram DB) when repurposing the A.I.M. template for a new codebase.
- **The TUI Updater:** If behavioral questions are skipped during installation, the Operator can hot-swap the AI's personality and rules dynamically using the `aim tui` cockpit.

---

## SECTION 2: THE ENGRAM DB (SUBCONSCIOUS)
The core of A.I.M.'s memory lives in a local SQLite database (`archive/engram.db`). It uses a **Hybrid RAG** engine, blending dense Vector Embeddings (Cosine Similarity) with FTS5 Lexical matching (BM25) to provide flawless recall of abstract concepts and exact variable names.

### 2.1 The Pre-Born Brain
During initialization, A.I.M. indexes this Handbook and core project directives. This provides the agent with "Day Zero" technical knowledge.

### 2.2 Synapse Ingestion
The `synapse/` folder is a dedicated intake zone. Any technical references dropped here are recursively indexed as `expert_knowledge`.

### 2.3 The Synapse Exchange (`aim exchange`)
Expertise is portable. A.I.M. can `export` its indexed knowledge into compressed `.aim` packs, allowing you to share a pre-trained "Python Expert" or "Solana Architect" brain with other machines without re-indexing.

---

## SECTION 3: THE CASCADING MEMORY ENGINE (CONSCIOUSNESS)
Memory is refined through a tiered, self-cleaning hierarchy to prevent knowledge decay and file bloat.

### 3.1 Tier 1: The Harvester (`hooks/tier1_hourly_summarizer.py`)
- **Trigger:** Automated via the `failsafe_context_snapshot.py` hook when 5 lines of new technical delta are detected.
- **Function (The Python Sieve):** Uses a 100% free, zero-token Python script to strip raw JSON tool noise and extract a lean "Signal Skeleton."
- **The Bouncer (Contractor Protocol):** Before summarizing, it scans the transcript. If it detects the `[EPHEMERAL]` tag, it assumes the session was run by a temporary subagent and completely ignores the file, preserving the Engram DB's purity.
- **Output:** A concise technical narrative saved to `memory/hourly/`.

### 3.2 Tier 2: Daily Distillation (`src/tier2_daily_summarizer.py`)
- **Trigger:** Triggered via `aim memory`.
- **Function:** Squashes the 24 hourly logs into a **Daily Proposal** (a Git-style diff proposing what to add/remove from your `core/MEMORY.md`). **Automatically deletes the hourly logs** upon completion.

### 3.3 Tier 3: Weekly Arc (`src/tier3_weekly_summarizer.py`)
- **Trigger:** Triggered via `aim memory`.
- **Function:** Synthesizes the 7 Daily Proposals into a condensed **Weekly Proposal**. **Automatically deletes the daily logs** upon completion.

### 3.4 Tier 4: The Apex Proposer (`src/tier4_memory_proposer.py`)
- **Trigger:** Triggered via `aim memory`.
- **Function:** Synthesizes the Weekly Proposals into the definitive **Monthly Proposal**.

### 3.5 The Rolling Proposal (`aim commit`)
The beauty of the Cascading Sieve is that you do not have to wait a month to update your memory. You can type `aim commit` at *any time* after 24 hours. The command simply grabs the *most recent, highest-tier proposal available* (Daily, Weekly, or Monthly), applies it to your `core/MEMORY.md`, and instantly deletes all underlying scaffolding.

---

## SECTION 4: SAFETY & SOVEREIGNTY

### 4.1 The Safety Sentinel (`hooks/safety_sentinel.py`)
- **Hardened Protection:** Intercepts destructive commands and performs a Level 2 AI intent audit. Uses `EXIT 2` to force blocks even in YOLO mode.

### 4.2 The Obsidian Bridge (`scripts/obsidian_sync.py`)
- **Role:** Sovereign Mirror.
- **Function:** Mirroring of Daily Logs, Core Memory, and **Raw JSON Transcripts** to an external vault for 100% recovery.

---

## SECTION 5: SYSTEM MAINTENANCE & UPDATES

### 5.1 The Sovereign Update (`aim update`)
- **Role:** High-Fidelity Sync.
- **Function:** Automates the lifecycle of keeping A.I.M. current.
- **Protocol:**
  1. **Source Sync:** Performs a `git pull origin main` to fetch the latest TUI, scripts, and engine logic.
  2. **Hook Refresh:** Re-registers all system hooks to ensure the local Gemini CLI is utilizing the latest architectural guardrails.
  3. **Data Preservation (Safe Update):** The update logic explicitly protects your **Personality Trinity** (`GEMINI.md`, `OPERATOR.md`, `MEMORY.md`). These files are never overwritten, ensuring the bot's soul remains intact across versions.

---

## SECTION 6: THE HYBRID SOUL PROTOCOL

A.I.M. maintains technical continuity through a dual-mode ingestion engine within `src/bootstrap_brain.py`. This ensures that active instructions stay current while expert knowledge remains permanent.

### 6.1 Foundation Sync (Active Instructions)
- **Scope:** `GEMINI.md`, `core/MEMORY.md`, and all files in `docs/`.
- **Logic:** These files are **Synchronized**. 
- **The Self-Healing Trigger (JIT):** There is no heavy background daemon monitoring these files. Instead, A.I.M. uses a "Just-In-Time" (JIT) sync. Every time a new session starts, the `context_injector.py` hook explicitly checks the file modification timestamps against the Engram DB. 
- **Behavior:** If it detects that a human operator manually edited `MEMORY.md` or a docs file, it instantly spins up a silent background thread to overwrite the old engrams with the new version before the agent even reads the first prompt. This ensures A.I.M. always follows the absolute current project mandates without requiring manual re-indexing commands.

### 6.2 Synapse Ingestion (Permanent Knowledge)
- **Scope:** Everything dropped into the `synapse/` folder.
- **Logic:** This is an **Onramp**.
- **Behavior:** Once a file is indexed from Synapse, it is **Permanently Persistent** in the Engram DB. The source files on disk can be safely deleted to keep the workspace lean; A.I.M. will still retain and retrieve the knowledge from the database.

### 6.3 Amnesia Protection
- **0-Byte Shield:** The bootstrap engine automatically skips empty or 0-byte files. This prevents accidental "Technical Amnesia" where an empty file on disk could overwrite and hollow out a valid engram in the database.

---

## SECTION 7: UNIVERSAL SOVEREIGNTY (MCP & SYNC)

A.I.M. is designed to integrate seamlessly with your wider engineering ecosystem while maintaining absolute data sovereignty.

### 7.1 The Universal Hub (Cockpit)
- **Role:** Centralized configuration for all reasoning models.
- **Function:** The `aim tui` supports OAuth (Google CLI, Codex CLI), API Keys, OpenRouter, and local Ollama routing. It includes **Cognitive Health Checks** to verify provider integrity in real-time.

### 7.2 Model Context Protocol (MCP) Server
- **Role:** IDE Integration.
- **Function:** A built-in `fastmcp` server (`src/mcp_server.py`) exposes the A.I.M. Engram DB as a standard tool. This allows IDEs like Cursor and VS Code, or agents like Claude Desktop, to natively query your project's historical continuity and mandates.

### 7.3 Sovereign Sync (Git Synchronization)
- **Role:** Binary Conflict Resolution.
- **Function:** SQLite databases (`engram.db`) cause binary merge conflicts in Git. A.I.M. circumvents this by translating the database into deterministic `.jsonl` files (`archive/sync/`) during `aim push` and `aim sync`. When you run `aim update` on another machine, it surgically ingests those `.jsonl` files back into the local database, allowing seamless multi-device brain synchronization.

### 7.4 The "Index-First" Retrieval Protocol
- **Role:** Token-Efficient Discovery.
- **Command:** `aim map`
- **Function:** Instead of performing a blind, high-token search, A.I.M. can first pull a surgical "Knowledge Map" (a list of all indexed documents and session IDs). This allows the agent to see *what* is known before deciding *where* to search, scaling the architecture to massive ecosystem-level projects without hitting context limits.

### 7.5 The Universal Skills Framework
- **Role:** CLI-Agnostic Action Execution.
- **Function:** The `skills/` directory allows the Operator to drop executable scripts (Python/Bash) alongside a `SKILL.md` manifest. The A.I.M. MCP server automatically registers these scripts as standardized tools, making them instantly available to any connected agent (Cursor, Claude Code, Gemini) without requiring platform-specific adapter code.

---

## SECTION 8: DEVELOPMENT LIFECYCLE (THE PHASE PROTOCOL)

A.I.M. development is highly structured to prevent regressions and provide clear rollback points for AI agents.

### 8.1 The Branching Strategy
1.  **Ideation & Planning:** The roadmap is updated on `main` to explicitly define the next phase (e.g., Phase 21).
2.  **Execution Branch:** A new branch is cut (e.g., `dev-phase-21`). All TDD and feature work occurs here.
3.  **The Archive Cut:** Before merging the completed `dev-` branch, the *current* state of `main` is cloned to a timestamped archive branch (e.g., `phase-20-20260321-2328`). This freezes the previous phase in an immutable, known-good state.
4.  **The Merge:** The `dev-` branch is merged into `main`, establishing the new baseline.

### 8.2 Why this Protocol?
While creating branches instead of Git Tags for archiving might seem non-standard in human-only teams, it is highly optimized for AI-driven development. It provides the agent with explicit, readable branches that act as immediate "Save States" if a phase goes completely off the rails, ensuring catastrophic architectural mistakes can be reverted instantly without complex `git reflog` operations.

---

## SECTION 9: TEST-DRIVEN DEVELOPMENT (TDD) POLICY

### 9.1 The Mandate
Every functional change, bug fix, or new feature **MUST** be governed by the TDD lifecycle. No code enters the `src/` directory without a corresponding verification script. Verification is not just "running code"; it is the empirical proof of correctness.

### 9.2 The Lifecycle (Red-Green-Refactor)
1.  **RED (Reproduction):** Create a reproduction script or unit test that fails. This defines the "Current Broken State."
2.  **GREEN (Fix):** Apply the minimal surgical code change required to make the test pass.
3.  **REFACTOR (Polish):** Clean up the implementation for idiomatic quality and performance while ensuring the test remains green.

### 9.3 Verification Standards
- **Unit Tests:** Preferred for utility functions and logic-heavy modules (using `pytest` or `unittest`).
- **Reproduction Scripts:** Mandatory for bug fixes. Prove the bug exists, then prove it's gone.
- **Protocol Isolation:** For MCP and cross-tool features, use mock clients to verify interface compliance without environmental bloat.
- **Zero-Token Validation:** Tests must be fast and autonomous. Avoid external API calls during testing unless the API itself is the target.

---

## SECTION 10: GIT-OPS & SEMANTIC RELEASE (THE PUBLIC LEDGER)

A.I.M. enforces a strict, automated versioning system to maintain a pristine historical ledger of all modifications without requiring manual human tracking.

### 10.1 Issue-Driven Development (`aim bug` & `aim fix`)
- **`aim bug <description>`:** Grabs the `FALLBACK_TAIL.md` crash logs and automatically creates a highly structured GitHub Issue via the `gh` CLI.
- **`aim fix <id>`:** Automatically checks out a clean Git branch (`fix/issue-<id>`) to enforce strict TDD isolation before any code is written.

### 10.2 The Mandatory Rule
Every GitHub repository managed by A.I.M. **MUST** utilize a Semantic Release Pipeline. 

### 10.3 The Atomic Deployment Rule
A.I.M. strictly follows a **Continuous Release** methodology rather than batched human releases. 
- **The Rule:** AI agents are strictly forbidden from executing raw `git commit` or `git push` commands. Every single bug fix or isolated feature addition must be deployed immediately using its own `aim push` command.
- **The Lifecycle:** You must never batch multiple disparate changes into a single mega-commit. When executing code changes, you must follow this isolated lifecycle:
  1. **Report:** Use `aim bug "description"` to log the issue.
  2. **Isolate:** Use `aim fix <id>` to check out a clean branch.
  3. **Release:** Use `aim push "Prefix: msg"` to deploy atomically.
- **The Rationale:** This guarantees that the `CHANGELOG.md` is built from short, concise, and hyper-focused entries. It ensures that if a regression occurs, the operator can instantly revert a specific version (e.g., `v1.0.6`) without throwing away unrelated code bundled in a massive mega-commit.

### 10.4 Conventional Commits (`aim push`)
To drive this automation, all commit messages executed by the agent must follow the Conventional Commits specification. The `aim push` command explicitly parses these prefixes to calculate version numbers and generate changelogs:
- `Feature: ...` (Triggers a Minor version bump)
- `Fix: ...` (Triggers a Patch version bump)
- `Docs: ...` (Documentation only, no version bump)
- `Chore: ...` (Maintenance, no version bump)
- `BREAKING CHANGE: ...` (Triggers a Major version bump)

### 10.5 Automated Changelog
The public face of A.I.M.'s memory is the `CHANGELOG.md`. This file is not written by hand or generated by a summarizer LLM. It is strictly assembled by the Semantic Release engine reading the commit history during `aim push`, ensuring absolute fidelity between the code shipped and the history recorded.

---

"I believe I've made my point." — **A.I.M.**
