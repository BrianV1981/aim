# A.I.M. TUI Architecture Map

The **Sovereign Cockpit (TUI)** is the central control plane for the A.I.M. Exoskeleton. It allows the operator to configure the cognitive routing, behavioral guardrails, and memory retention policies without manually editing JSON files.

The TUI is entirely executed via `scripts/aim_config.py`. Below is the technical mapping of every feature to its associated configuration file and system logic.

---

## 1. Run Cognitive Health Check (Test All)
- **Logic:** Iterates through all 4 cognitive tiers (Default, Librarian, Chancellor, Dean) defined in `core/CONFIG.json`.
- **Execution:** Calls `generate_reasoning("Respond with 'OK'")` in `src/reasoning_utils.py` for each active tier.
- **Diagnostics:** If a provider fails, it catches the exact HTTP exception or subprocess stderr and displays it in the 'Diagnostics' column.
- **Associated Files:** `core/CONFIG.json`, `src/reasoning_utils.py`, `scripts/aim_config.py`.

## 2. Manage Secret Vault (API Keys)
- **Logic:** Interfaces directly with the underlying Linux/macOS keyring to securely store, retrieve, or delete API credentials. It never writes keys to plaintext files.
- **Execution:** Uses the Python `keyring` library (wrapped in `scripts/aim_vault.py`). Keys are stored under the `"aim-system"` namespace.
- **Associated Files:** `scripts/aim_vault.py`.

## 3 & 4. Configure Brain / Specialist Tiers
- **Logic:** Configures the `provider`, `model`, `endpoint`, and `auth_type` for the reasoning engine.
- **Providers:** 
  - `google` (REST API or Native CLI OAuth)
  - `codex-cli` (Native Subprocess)
  - `anthropic` (REST API)
  - `local (ollama)` (Localhost POST)
  - `openrouter` (REST API)
- **Execution:** Writes the selected configuration into the `["models"]["tiers"]` dictionary inside `core/CONFIG.json`.
- **Associated Files:** `core/CONFIG.json`, `src/reasoning_utils.py`.

## 5. Manage MCP Server (IDE Integration)
- **Logic:** Checks the process tree to see if `src/mcp_server.py` is actively running in the background. Allows the user to start or kill the server.
- **Execution:** Uses `subprocess` to launch the FastMCP server, exposing the `skills/` directory and Engram DB to external IDEs (Cursor, Windsurf).
- **Associated Files:** `src/mcp_server.py`, `skills/*`.

## 6. Update Operator Profile & Behavior
- **Logic:** Asks the user for their preferred execution style (Autonomous vs Cautious), grammar level, and conciseness. 
- **Execution:** Uses Regex to search and replace the behavioral variables directly inside the active `GEMINI.md` system prompt.
- **Associated Files:** `GEMINI.md`, `core/OPERATOR.md`.

## 7. Update Obsidian Vault Path
- **Logic:** Sets the absolute path to a local Obsidian Markdown vault for Sovereign Sync.
- **Execution:** Writes the path to `["settings"]["obsidian_vault_path"]` in `core/CONFIG.json`. 
- **Associated Files:** `core/CONFIG.json`, `src/sovereign_sync.py`.

## 8. Archive Retention
- **Logic:** Configures how many days the system should keep raw JSON transcripts and old proposal markdown files before the Garbage Collector (`aim purge`) deletes them.
- **Execution:** Writes an integer to `["settings"]["archive_retention_days"]` in `core/CONFIG.json`.
- **Associated Files:** `core/CONFIG.json`, `scripts/aim_cli.py` (Purge command).

## 9. Auto-Memory Distillation
- **Logic:** Determines if the system should automatically condense its own memories (T2 Daily, T3 Weekly, T4 Monthly) without human intervention.
- **Execution:** Writes the tier string (e.g., "T4") to `["settings"]["auto_distill_tier"]` in `core/CONFIG.json`.
- **Associated Files:** `core/CONFIG.json`, `hooks/failsafe_context_snapshot.py` (Triggers the automatic distillation).

## 10. Set Agent Persona (Specialty Mandate)
- **Logic:** Injects a strict, specialized mandate (e.g., Frontend Architect, Web3 Auditor) into the top of the AI's system prompt.
- **Execution:** Uses Regex to safely overwrite the `> **MANDATE:**` block in `GEMINI.md` without destroying the rest of the file's GitOps rules.
- **Associated Files:** `GEMINI.md`.
