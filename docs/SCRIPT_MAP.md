# A.I.M. Script Map

This document maps out the core Python and Shell scripts operating within the A.I.M. architecture. It breaks down the files across their respective domains: `hooks/`, `src/`, `scripts/`, and `skills/`, detailing their primary purpose, dependencies, and architectural role.

---

## 🪝 Hooks (`hooks/`)
*Hooks act as interceptors and operational guardrails, running dynamically during execution cycles to enforce safety, capture context, and update state.*

### `cognitive_mantra.py`
* **Purpose**: Tracks operational momentum by counting tool calls and enforcing cognitive limits.
* **Imports**: `subprocess`, `sys`, `os`, `json`, `config_utils.CONFIG`
* **Architecture**: Execution Hook / Throttle

### `context_injector.py`
* **Purpose**: Fetches the recent pulse and tail data, verifies self-healing sync, and dynamically injects environmental context.
* **Imports**: `sys`, `os`, `datetime`, `json`, `glob`, `math`, `forensic_utils`, `config_utils`
* **Architecture**: Context Engine / Injection Hook

### `failsafe_context_snapshot.py`
* **Purpose**: Checks task significance and triggers checkpoints/snapshots to preserve context during critical events.
* **Imports**: `sys`, `os`, `json`, `time`, `config_utils`
* **Architecture**: Safety / Snapshot Hook

### `safety_sentinel.py`
* **Purpose**: Audits the agent's intent before executing high-risk actions. Uses LLM reasoning to evaluate safety.
* **Imports**: `sys`, `os`, `json`, `re`, `glob`, `reasoning_utils.generate_reasoning`, `config_utils`
* **Architecture**: Security / Guardrail Hook

### `secret_shield.py`
* **Purpose**: Scans output and execution pathways for secrets or credentials to prevent accidental leaks.
* **Imports**: `sys`, `os`, `json`, `re`
* **Architecture**: Security / DLP Hook

### `session_summarizer.py`
* **Purpose**: Processes local transcripts, manages locks, and recursively narrates activity to produce technical narrative summaries in `memory/hourly/`.
* **Imports**: `subprocess`, `sys`, `os`, `datetime`, `json`, `time`, `shutil`, `re`, `glob`, `reasoning_utils`, `forensic_utils`, `extract_signal`
* **Architecture**: Background Task / Memory Pipeline (Tier 1)

### `workspace_guardrail.py`
* **Purpose**: Scans commands for paths to ensure modifications are restricted to safe, authorized directories.
* **Imports**: `sys`, `os`, `json`, `re`, `subprocess`, `config_utils`
* **Architecture**: Security / Filesystem Guardrail

---

## 🧠 Core System (`src/`)
*The `src/` directory contains the foundational logic, daemons, and reasoning engines that power A.I.M.*

### `back-populator.py`
* **Purpose**: Back-populates missed data or historical sessions into the primary A.I.M. index.
* **Imports**: `sys`, `os`, `datetime`, `json`, `glob`, `config_utils`
* **Architecture**: Maintenance Daemon

### `bootstrap_brain.py`
* **Purpose**: Verifies embedding engines and bootstraps the foundational system structures and initial file indexes.
* **Imports**: `sys`, `os`, `datetime`, `json`, `time`, `sqlite3`, `glob`, `forensic_utils`, `config_utils`
* **Architecture**: Initialization / Core Engine

### `config_utils.py`
* **Purpose**: Loads configuration values, merges defaults, and resolves the `AIM_ROOT` path.
* **Imports**: `sys`, `os`, `json`, `getpass`
* **Architecture**: Core Utility / Configuration

### `daily_refiner.py`
* **Purpose**: Deduplicates and consolidates multiple hourly Tier 2 memory proposals into a single Daily State.
* **Imports**: `sys`, `json`, `os`, `glob`, `datetime`, `reasoning_utils`
* **Architecture**: Memory Pipeline (Tier 3)

### `daemon.py`
* **Purpose**: The main background daemon that maintains the A.I.M. heartbeat, manages the nav/combat loops, and monitors environmental state.
* **Imports**: `sys`, `os`, `datetime`, `json`, `time`, `subprocess`
* **Architecture**: Background Daemon / Loop Orchestrator

### `forensic_utils.py`
* **Purpose**: Manages the `ForensicDB` (SQLite), handles text chunking, and interfaces with the LLM via `google.genai` to compute and retrieve embeddings.
* **Imports**: `sys`, `os`, `struct`, `json`, `sqlite3`, `math`, `google.genai`, `requests`, `keyring`, `config_utils`
* **Architecture**: Core Engine / Database & Embeddings

### `handoff_pulse_generator.py`
* **Purpose**: Generates semantic "handoff pulses" summarizing context between active sessions using `generate_reasoning`.
* **Imports**: `sys`, `os`, `datetime`, `json`, `glob`, `extract_signal`, `reasoning_utils`
* **Architecture**: Context Engine / Orchestration

### `heartbeat.py`
* **Purpose**: Assesses and prints the real-time status of the database, memory pipeline, failsafes, and sync health.
* **Imports**: `os`, `datetime`, `time`, `sqlite3`, `glob`
* **Architecture**: System Monitoring

### `maintenance.py`
* **Purpose**: Runs periodic maintenance, such as cleaning the rolling archives to manage disk space.
* **Imports**: `sys`, `os`, `time`, `glob`, `config_utils`
* **Architecture**: System Maintenance

### `mcp_server.py`
* **Purpose**: Operates the FastMCP server, exposing A.I.M. context, handling sandbox commands, and executing external skills.
* **Imports**: `sys`, `os`, `pathlib`, `shutil`, `json`, `subprocess`, `fastmcp.FastMCP`, `retriever`
* **Architecture**: Core Engine / MCP Interface

### `memory_proposer.py`
* **Purpose**: Analyzes recent session summaries and proposes structured delta updates (Adds/Removes/Modifications) for `MEMORY.md`.
* **Imports**: `sys`, `os`, `datetime`, `json`, `glob`, `reasoning_utils`
* **Architecture**: Memory Pipeline (Tier 2)

### `memory_utils.py`
* **Purpose**: Commits memory proposals and updates to long-term storage.
* **Imports**: `os`, `shutil`, `re`, `glob`
* **Architecture**: Memory Management Pipeline

### `reasoning_utils.py`
* **Purpose**: Abstraction layer for LLM API calls, routing prompts to providers like Google, OpenAI, Anthropic, Ollama, and OpenRouter.
* **Imports**: `sys`, `os`, `json`, `re`, `keyring`, `requests`, `subprocess`
* **Architecture**: Core Engine / LLM Router

### `retriever.py`
* **Purpose**: Performs vector searches across the knowledge map using cosine similarity via `ForensicDB`.
* **Imports**: `sys`, `os`, `json`, `argparse`, `hashlib`, `re`, `forensic_utils`, `config_utils`
* **Architecture**: Core Engine / RAG Pipeline

### `sovereign_sync.py`
* **Purpose**: Manages the export and import of A.I.M. data formats via JSONL (Sovereign Sync protocol).
* **Imports**: `os`, `json`, `sqlite3`, `glob`
* **Architecture**: Core Engine / Data Portability

### `weekly_consolidator.py`
* **Purpose**: Distills the past 7 Daily States into high-level project milestones and architectural shifts.
* **Imports**: `sys`, `json`, `os`, `glob`, `datetime`, `reasoning_utils`
* **Architecture**: Memory Pipeline (Tier 4)

---

## 🛠️ Scripts & CLI (`scripts/`)
*User-facing commands, initialization utilities, and operational tooling.*

### `aim_cli.py`
* **Purpose**: The primary entry point for the `aim` command. Routes subcommands (e.g., `init`, `config`, `sync`, `push`, `jack_in`).
* **Imports**: `sys`, `os`, `datetime`, `argparse`, `shutil`, `re`, `glob`, `subprocess`, `config_utils`, `sovereign_sync`, `forensic_utils`
* **Architecture**: CLI Entrypoint

### `aim_config.py`
* **Purpose**: Handles the interactive configuration wizard (`aim config`), updating personas, API keys, and operator profiles.
* **Imports**: `sys`, `os`, `json`, `time`, `re`, `requests`, `questionary`, `rich`, `aim_vault`, `config_utils`, `reasoning_utils`
* **Architecture**: CLI Configuration

### `aim_init.py`
* **Purpose**: Initializer script used during the initial setup of A.I.M.
* **Imports**: None
* **Architecture**: Setup Utility

### `aim_bake.py`
* **Purpose**: Compresses and bakes the current A.I.M. state into a portable `.zip` cartridge.
* **Imports**: `sys`, `os`, `argparse`, `json`, `tempfile`, `pathlib`, `zipfile`, `src.forensic_utils`, `src.bootstrap_brain`
* **Architecture**: CLI Utility / Portability

### `aim_exchange.py`
* **Purpose**: Manages importing, exporting, and unplugging datajack cartridges.
* **Imports**: `sys`, `os`, `datetime`, `json`, `time`, `shutil`, `zipfile`, `sovereign_sync`, `forensic_utils`
* **Architecture**: CLI Utility / Portability

### `aim_vault.py`
* **Purpose**: Interfaces with the OS keyring to securely store, retrieve, and list API keys and secrets.
* **Imports**: `sys`, `getpass`, `argparse`, `keyring`, `rich`
* **Architecture**: Security / Credential Management

### `aim_push.sh`
* **Purpose**: Auto-versioning push script orchestrated by the semantic release pipeline inside `aim_cli.py`.
* **Imports**: None
* **Architecture**: CI/CD Script

### `aim_batch_merge.py`
* **Purpose**: Automates the GitOps merge process by systematically merging all open `fix/issue-*` branches into `main` and optionally pushing to remote to auto-close GitHub issues.
* **Imports**: `os`, `subprocess`, `argparse`, `sys`
* **Architecture**: CI/CD Utility / GitOps

### `deep_forensic_restore.py`
* **Purpose**: Performs an in-depth forensic recovery to restore corrupted or lost context.
* **Imports**: `sys`, `os`, `datetime`, `json`, `time`, `re`, `glob`, `subprocess`, `config_utils`, `memory_utils`, `reasoning_utils`
* **Architecture**: Maintenance / Recovery

### `extract_signal.py`
* **Purpose**: Extracts structured signal/content from raw outputs.
* **Imports**: `sys`, `os`, `json`
* **Architecture**: Data Processing Utility

### `methodical_rebuild.py`
* **Purpose**: Methodically reconstructs system state after a catastrophic failure or reset.
* **Imports**: `sys`, `os`, `datetime`, `json`, `shutil`, `re`, `glob`, `subprocess`, `config_utils`, `memory_utils`
* **Architecture**: Maintenance / Recovery

### `obsidian_sync.py`
* **Purpose**: Synchronizes local A.I.M. data with an Obsidian vault.
* **Imports**: `os`, `datetime`, `json`, `shutil`, `glob`
* **Architecture**: Integration Utility

### `session_porter.py`
* **Purpose**: Mirrors and ports local transcripts across directory structures.
* **Imports**: `sys`, `os`, `json`, `shutil`, `glob`
* **Architecture**: Maintenance Utility

### `telemetry_scrubber.py`
* **Purpose**: Scrubs sensitive information, secrets, and usernames from log/telemetry files before export.
* **Imports**: `sys`, `os`, `re`, `getpass`, `glob`, `keyring`
* **Architecture**: Privacy Utility

### `total_reconstruction.py`
* **Purpose**: Reconstructs a full day's session combining context and scrivener notes.
* **Imports**: `sys`, `os`, `datetime`, `json`, `re`, `glob`
* **Architecture**: Maintenance / Recovery

### `verify_order.py`
* **Purpose**: Verifies that A.I.M.'s background tasks, memory chunks, and index order are sequentially sound.
* **Imports**: `sys`, `os`, `json`, `glob`, `config_utils`
* **Architecture**: System Maintenance

### `run_test_init.py`
* **Purpose**: Utility script to execute initialization tests.
* **Imports**: `sys`, `os`, `subprocess`
* **Architecture**: Testing Utility

---

## 📊 Benchmark Suite (`scripts/benchmarks/`)
*Dedicated tooling for isolating, measuring, and recovering data from A.I.M. exoskeleton benchmark tests.*

### `setup_environments.sh`
* **Purpose**: Automated 4-way benchmark setup. Spins up isolated environments (Control vs. Matrix) for evaluating the agent.
* **Imports**: None
* **Architecture**: Testing / Benchmarking

### `calculate_economics.py`
* **Purpose**: Parses raw JSON session logs to extract tokens, separates cached inputs, and calculates exact API costs for the benchmark environments.
* **Imports**: `json`, `argparse`, `pathlib`
* **Architecture**: Testing / Benchmarking

### `recover_json_logs.py`
* **Purpose**: A streamlined recovery protocol script. Bypasses workspace isolation to hunt down and copy hidden Gemini CLI session logs from `~/.gemini/tmp/<project>/chats/` into the public repository for auditing.
* **Imports**: `os`, `glob`, `time`, `shutil`, `argparse`, `pathlib`
* **Architecture**: Testing / Data Recovery

---
*Specialized external capabilities that A.I.M. can invoke dynamically.*

### `advanced_memory_search.py`
* **Purpose**: Performs an advanced semantic/vector search against the forensic database.
* **Imports**: `sys`, `os`, `pathlib`, `json`, `forensic_utils`
* **Architecture**: Skill / Retrieval

### `export_datajack_cartridge.py`
* **Purpose**: Enables the agent to autonomously export its current datajack cartridge state.
* **Imports**: `sys`, `os`, `pathlib`, `json`, `subprocess`
* **Architecture**: Skill / Portability

### `list_recent_sessions.py`
* **Purpose**: Queries the local SQLite database to list the most recent A.I.M. sessions.
* **Imports**: `sys`, `json`, `sqlite3`, `pathlib`
* **Architecture**: Skill / State Inspection

### `propose_memory_commit.py`
* **Purpose**: Skill allowing the agent to explicitly propose a long-term memory update.
* **Imports**: `sys`, `os`, `pathlib`, `json`, `subprocess`
* **Architecture**: Skill / Memory Management
