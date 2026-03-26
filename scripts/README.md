# A.I.M. User-Facing Scripts (`scripts/`)

This directory contains the primary execution scripts and CLI tools that the human Operator interacts with. 

## Key Files
*   **`aim_cli.py`**: The central nervous system of the exoskeleton. When you type `aim` (or a dynamic alias like `aim_os`) in your terminal, this is the script that catches the command and routes it to the appropriate subsystem.
*   **`aim_init.py`**: The Onboarding Wizard. Scaffolds the workspace, handles the "Clean Sweep," and injects the `GEMINI.md` system prompt.
*   **`aim_config.py`**: The Sovereign Cockpit (TUI). Provides the visual interface for configuring Cognitive Routing, API keys, and Anti-Drift hooks.
*   **`aim_bake.py`**: The DataJack Foundry. Spins up isolated `/tmp/` databases to manufacture atomic `.engram` cartridges without cross-contaminating the active workspace.