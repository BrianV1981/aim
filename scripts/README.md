# A.I.M. Scripts & Tools

This directory contains the operational layer of A.I.M.

## Key Design Principles
1. **Dynamic Root Discovery:** All scripts must use the `find_aim_root()` function (or equivalent) to resolve the A.I.M. installation path at runtime. **Never hardcode `/home/user/aim`.**
2. **Portable Shebangs:** Use `#!/usr/bin/env python3`.
3. **Sovereign Execution:** Scripts should leverage the project-local `venv` for dependencies.

## Key Scripts
- `aim_cli.py`: The main entry point (`aim`). Dispatches all commands.
- `aim_config.py`: The TUI Cockpit (`aim config`) for interactive configuration.
- `aim_init.py`: Workspace scaffolding and initialization.
- `telemetry_scrubber.py`: Dynamic privacy hardening.
- `obsidian_sync.py`: Mirrors logs to an external Obsidian vault.
