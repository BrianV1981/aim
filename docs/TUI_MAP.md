# A.I.M. TUI Architecture Map

The **Sovereign Cockpit (TUI)** is the central control plane for the A.I.M. OS. It allows the operator to configure the cognitive routing, behavioral guardrails, and memory retention policies without manually editing JSON files.

The TUI is entirely executed via `scripts/aim_config.py`. Below is the technical mapping of every feature to its associated configuration file and system logic.

---

## 1. Run Cognitive Health Check (Test All)
- **Logic:** Iterates through all 6 cognitive tiers (Default, Scribe, Proposer, Refiner, Consolidator, Archivist) defined in `core/CONFIG.json`.
- **Execution:** Calls `generate_reasoning("Respond with 'OK'")` in `src/reasoning_utils.py` for each active tier.
- **Diagnostics:** If a provider fails, it catches the exact HTTP exception or subprocess stderr and displays it in the 'Diagnostics' column.
- **Timeout:** Flagship models now have a 60-second health check timeout to accommodate the Gemini CLI bridge.
- **Associated Files:** `core/CONFIG.json`, `src/reasoning_utils.py`, `scripts/aim_config.py`.

## 2. Manage Secret Vault (API Keys)
- **Logic:** Interfaces directly with the underlying Linux/macOS keyring to securely store, retrieve, or delete API credentials. It never writes keys to plaintext files.
- **Execution:** Uses the Python `keyring` library (wrapped in `scripts/aim_vault.py`). Keys are stored under the `"aim-system"` namespace.
- **Associated Files:** `scripts/aim_vault.py`.

## 3 & 4. Configure Brain / Cognitive Pipeline (T1-T5)
- **Logic:** Configures the `provider`, `model`, `endpoint`, and `auth_type` for the reasoning engine.
- **Tiers:** 
  - `default_reasoning`: The primary brain for interactive tasks.
  - `tier1`: Tier 1: Session Summarizer (`hooks/session_summarizer.py`)
  - `tier2`: Tier 2: Memory Proposer (`src/memory_proposer.py`)
  - `tier3`: Tier 3: Daily Refiner
  - `tier4`: Tier 4: Weekly Consolidator
  - `tier5`: Tier 5: Monthly Archivist
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
- **Logic:** Asks the user for both operator identity fields and behavioral guardrails.
- **Execution:** Rewrites `core/OPERATOR.md` and `core/OPERATOR_PROFILE.md` from structured prompt answers, then updates the behavioral guardrail fields inside `GEMINI.md`.
- **Associated Files:** `GEMINI.md`, `core/OPERATOR.md`, `core/OPERATOR_PROFILE.md`.

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

## Initialization Contract
- **Logic:** `aim init` seeds the same config schema that the TUI expects instead of a separate legacy shape.
- **Execution:** Fresh installs now create `["models"]["tiers"]` with default tier routing and populate `archive_retention_days` plus `auto_distill_tier` in `core/CONFIG.json`.
- **Associated Files:** `scripts/aim_init.py`, `src/config_utils.py`, `core/CONFIG.json`.

## 10. Set Agent Persona (Specialty Mandate)
- **Logic:** Injects a strict, specialized mandate (e.g., Frontend Architect, Web3 Auditor) into the top of the AI's system prompt.
- **Execution:** Uses Regex to safely overwrite the `> **MANDATE:**` block in `GEMINI.md` without destroying the rest of the file's GitOps rules.
- **Associated Files:** `GEMINI.md`.

## 11. Configure Cognitive Mantra (Anti-Drift)
- **Logic:** Configures the `cognitive_mantra.py` watchdog timer, which injects silent reminders or hard `<MANTRA>` generation requests into the LLM context to prevent behavioral drift during long sessions.
- **Execution:** Writes boolean toggle and integer tool-call intervals to `["settings"]["cognitive_mantra"]` in `core/CONFIG.json`.
- **Associated Files:** `core/CONFIG.json`, `hooks/cognitive_mantra.py`.

## 12. Configure Handoff Context Tail
- **Logic:** Determines how many historical conversational turns the Continuity Engine preserves when distilling a session handoff to the next agent.
- **Execution:** Writes an integer limit to `["settings"]["handoff_context_tail"]` in `core/CONFIG.json`.
- **Associated Files:** `core/CONFIG.json`, `src/handoff_pulse_generator.py`.
