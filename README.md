# A.I.M. (Actual Intelligent Memory)

**"Treat your AI like a bot, not an oracle."**

A.I.M. is an open-source exoskeleton designed to cure the "Amnesia Problem" of autonomous AI agents. It wraps around your CLI agent (like Gemini) and forces it to act like a disciplined Principal Engineer — externalizing memory into a local SQLite Engram DB, automating the Git lifecycle, and ruthlessly distilling your context the exact second a coding session ends.

## 🔥 Core Features

*   **The Persistent LLM Wiki (Dual-Search Brain):** A background Subconscious Daemon reads session flight recorders and seamlessly synthesizes architectural lore into a multi-file Markdown Wiki. No more monolithic `MEMORY.md` files. Just an ever-evolving, Obsidian-synced knowledge graph.
*   **The Zero-Token Python Engine (The Autonomic Layer):** Deterministic Python scripts strip raw terminal JSON noise into a clean "Signal Skeleton," reducing token weight by up to 85% before an LLM ever touches the data.
*   **The Federated Brain (Archipelago Model):** Eliminates database bottlenecks by segregating memory across purpose-built SQLite databases (`project_core.db`, `global_skills.db`, `datajack_library.db`, `subagent_ephemeral.db`).
*   **Strict GitOps Bridge (Atomic Deployments):** Forces agents to use `aim bug`, `aim fix <id>`, `aim push`, and `aim promote`. Agents are physically forbidden from raw `git commit` or pushing to `main`, ensuring every change is isolated in a Worktree and test-driven.
*   **The Obsidian Bridge & Remote Fleet:** Because the `wiki/` directory is purely native Markdown, you can open it as an Obsidian Vault. A headless A.I.M. daemon on a secondary GPU server can compile your memory and sync the updated Wiki pages back to your primary laptop in real-time.
*   **The DataJack Protocol (.engram Cartridges):** Package thousands of pages of documentation into pre-vectorized `.engram` files. Run `aim jack-in framework.engram` to instantly inject semantic recall of entire libraries without spending a single API token.
*   **Modular Cognitive Routing:** Decouple the "conscious" and "subconscious." Keep flagship models (Gemini Pro/Claude Opus) in the terminal for coding, and route background tasks (memory indexing) to free local models via Ollama.
*   **Context Collapse Shield (Failsafe Snapshot):** A rolling dead-man's switch continuously saves your last 10 turns. If the agent crashes, the context is automatically salvaged.
*   **Executive Guardrails (Anti-Drift):** The `cognitive_mantra` hook tracks autonomous tool calls. At 50 actions, it forcefully halts execution and forces the agent to recite its GitOps rules, washing away context degradation.
*   **Reincarnation & Crash Recovery:** Run `aim reincarnate` to perform an automated context handoff to a fresh agent, or `aim crash` to salvage an interrupted V8 heap and resume exactly where you left off.
*   **Strict Bug Reporting:** The `aim bug` command strictly requires explicit `--context`, `--failure`, and `--intent` flags to ensure the next "blind" agent inherits full epistemic certainty.
*   **Interactive TUI Cockpit:** A visual terminal interface (`aim tui`) to configure LLM routing, guardrails, and context limits.
*   **Universal IDE Support (MCP):** A built-in MCP server exposes the Engram DB to any connected IDE (Cursor, VS Code, Claude Desktop) without platform-specific adapters.

----------------------------------------

All comprehensive documentation, architectural maps, setup instructions, and origin stories live in the wiki. The code is the source of truth; the wiki is the map.

📖 **[READ THE OFFICIAL WIKI](https://github.com/BrianV1981/aim/wiki)**

----------------------------------------

### 🧬 The A.I.M. Ecosystem

> ⚠️ **DISCLAIMER: WORK IN PROGRESS**
> The repositories below are experimental adaptations. **This repository (`aim`) is the primary "Soul" of the project.** The core architectural decisions, the Engram DB logic, and the central integrations happen here first before being ported to the external adaptations.

- **[aim](https://github.com/BrianV1981/aim):** The Core Engine (Built for Gemini CLI).
- **[aim-claude](https://github.com/BrianV1981/aim-claude):** Adaptation for Anthropic's Claude Code.
- **[aim-codex](https://github.com/BrianV1981/aim-codex):** Adaptation for OpenAI's GPT Codex.
- **[aim-antigravity](https://github.com/BrianV1981/aim-antigravity):** The experimental GUI/MCP Desktop adaptation.

☕ [Buy Me a Coffee](https://buymeacoffee.com/brianv1981)