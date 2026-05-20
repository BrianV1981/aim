# The Codebase Map (A.I.M. v1.61.3)

This document is the literal map of every internal script running the A.I.M. OS. Use it to understand where business logic lives. All scripts have been flattened into the `aim_core/` directory to simplify the architecture.

---

## 1. Core Engines (Database, Retrieval, Config)
*The pure Python engines driving the backend architecture and LanceDB integration.*

*   **`lance_backend.py`**: The LanceDB PyArrow wrapper. Manages RAG 5.21 schema definition and vector database connectivity.
*   **`retriever.py`**: A.I.M. Autonomous Knowledge Retriever (Native LanceDB/Parquet). The Hybrid RAG search engine combining vector embeddings with Tantivy FTS.
*   **`reasoning_utils.py`**: The universal LLM client. Dynamically routes API calls based on the Tiers defined in `CONFIG.json`.
*   **`config_utils.py`**: The single source of truth for loading, validating, and auto-repairing `core/CONFIG.json` paths.
*   **`bootstrap_brain.py`**: The initialization engine. Re-indexes core documents into `memory_lance`.

---

## 2. Command Line Interface (CLI & Routing)
*The front-end commands accessible via the `aim` global alias.*

*   **`aim_cli.py`**: The central router. Parses all `aim` commands and dispatches the corresponding script.
*   **`aim_router.py`**: Handles dynamic routing algorithms.
*   **`aim_config.py`**: The Interactive TUI (Cockpit) for modifying configurations.
*   **`aim_push.sh`**: The GitOps validation wrapper enforcing branch/issue protocols and semantic versioning.
*   **`aim_batch_merge.py`**: Utility for merging multiple open `fix/issue-*` branches into main.
*   **`aim_delegate.py`**: A.I.M. Dynamic Sub-Agent Delegation protocol for distributed processing.
*   **`aim_init.py`**: The setup wizard executed upon first repository installation to build the databases, wiki, and hooks.
*   **`aim_crash.py`**: Recovery script to safely extract the signal from a corrupted V8 heap crash.

---

## 3. Lifecycle, Memory & Continuity
*Scripts that manage the agent's context, history, and autonomous operations.*

*   **`aim_reincarnate.py`**: The Context Pruning teleport script for spawning a fresh agent vessel.
*   **`handoff_pulse_generator.py`**: Generates the `CURRENT_PULSE.md` and `LAST_SESSION_FLIGHT_RECORDER.md`, and triggers vector ingestion.
*   **`extract_signal.py`**: The Zero-Token Scribe. Uses pure Python to strip 85% of JSON noise from native CLI transcripts.
*   **`session_porter.py`**: Fast mirroring of global CLI transcripts to the local raw archive.
*   **`wiki_tools.py`**: The Persistent LLM Wiki engine managing lexical search and Subconscious Daemon execution.
*   **`daemon.py`**: The overarching background service orchestrator.
*   **`maintenance.py`**: Automated janitor for purging logs and maintaining retention policies.
*   **`heartbeat.py`**: Zero-token diagnostic tool verifying system integrity.
*   **`blackbox_vault.py`**: Encrypted storage for raw JSONL sessions.
*   **`audit_tools.py`**: Audits recent history to generate Weekly Sitreps.
*   **`recall_tools.py`**: Legacy history querying fallback.

---

## 4. Connectivity, Sync & Tools
*Bridges to external services, IDEs, and the P2P Swarm.*

*   **`aim_vault.py`**: A.I.M. Secret Vault Manager for holding API keys securely without putting them in plaintext configs.
*   **`aim_calc.py`**: Agent-Native Scientific Calculator.
*   **`aim_scraper.py`**: Scrapes GitHub Issues and forums into Synapse Markdown docs.
*   **`mcp_server.py`**: Model Context Protocol server enabling external IDEs (Cursor/VS Code) to query the databases and read memories.
*   **`aim_torrent.py`**: The P2P DataJack Swarm daemon for sharing `.parquet` cartridges.
*   **`aim_swarm.py`**: Generic swarm orchestration wrapper.
*   **`sovereign_sync.py`**: Converts LanceDB tables into `.jsonl` files in `archive/sync/`.
*   **`back-populator.py`**: Rebuilds LanceDB from `.jsonl` sync files.
*   **`obsidian_sync.py`**: Outbound Obsidian Bridge. Mirrors memory to a local Obsidian Vault.
*   **`obsidian_pull.py`**: Inbound Obsidian Bridge (`aim ingest`). Pulls manual Obsidian edits back.
*   **`sync_issue_tracker.py`**: Synchronizes remote GitHub issues to `ISSUE_TRACKER.md`.
*   **`sync_mail.py`**: Synchronizer for Swarm Post Office / Unread Mail.

---

## 5. Benchmarks & Testing
*Automated, repeatable testing harnesses for the platform.*

*   **`setup_environments.sh` & `setup_standard_environments.sh`**: Creates boilerplate folders for A/B testing frameworks.
*   **`calculate_economics.py`**: Calculates benchmark economics from raw JSON logs.
*   **`recover_json_logs.py`**: A.I.M. Benchmark JSON Recovery Protocol to extract logs for proof.
*   **`run_amnesia_killer.py`**: Amnesia Killer Demo Harness.
*   **`run_vibe_killer.py`**: Vibe Killer 60-Turn Demo Harness.

---

## 6. DataJack Plugins (`aim_core/plugins/datajack/`)
*The plugin architecture for forging and inspecting immutable ROM cartridges.*

*   **`aim_bake.py`**: Compiles text directories into portable highly-compressed `.parquet` cartridges.
*   **`aim_exchange.py`**: Handles ingestion and mounting of cartridges.
*   **`forensic_utils.py`**: Contains the RAG 5.21 Length-Constrained Accumulator chunking algorithm and ingestion utilities.
*   **`quarantine_daemon.py`**: Background watchdog verifying Swarm cartridge integrity and scanning for prompt injections.