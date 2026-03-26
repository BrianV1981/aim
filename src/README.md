# A.I.M. Core Engine (`src/`)

This directory contains the internal Python engine that powers the A.I.M. exoskeleton. These files are typically NOT invoked directly by the Operator; they are called by the `scripts/` layer, the background `daemon`, or the Gemini CLI `hooks/`.

## Key Components
*   **`reasoning_utils.py`**: The API Bridge. Handles routing payloads to Google Gemini, Anthropic, OpenRouter, Codex, or Local Ollama. It manages subprocess execution and parses stdout/stderr to protect the agent from brittle CLI outputs.
*   **`forensic_utils.py`**: The SQLite ORM. Manages the connection to the `engram.db`, handles the calculation of dense vectors (via Nomic), and executes the FTS5 Hybrid RAG searches.
*   **`mcp_server.py`**: The Universal IDE interface. Runs a FastMCP server that exposes the A.I.M. database and skills directly to Cursor, Claude Code, or VS Code.
*   **The Summarizers**: `tier2_daily_summarizer.py`, `tier3_weekly_summarizer.py`, etc. The logic for the Cascading Memory Sieve.