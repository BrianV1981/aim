# Architectural Flaw: The Monolithic Update Mechanism

## Problem Statement

The A.I.M. Swarm OS currently suffers from a critical architectural flaw regarding its `update` mechanism (`aim_cli.py update`). When A.I.M. is deployed as an exoskeleton or operating system to manage a *target* project (e.g., `aim-google`), executing a "Safe Update" fundamentally breaks the boundary between the OS Framework and the Target Payload.

The update script assumes that the root directory is both the **A.I.M. Engine repository** (`BrianV1981/aim`) AND the **Target Project repository** (e.g., `BrianV1981/aim-google`). 

When an operator runs an update to get the latest OS engine features (like a bug fix in `aim_cli.py`), the script forcibly syncs the local environment with `BrianV1981/aim`. This causes catastrophic cross-contamination:

1. **Git History Pollution:** The local project's Git history is overwritten or merged with the development history of the A.I.M. exoskeleton itself.
2. **Brain Contamination (The "Identity Crisis"):** The update script pulls down the framework's own `issues/`, `sessions/`, and internal documentation, melting them into the local ForensicDB. An agent dedicated to developing a Go CLI suddenly possesses 1,500+ memory fragments regarding how to build Python-based DataJacks.
3. **Workspace Corruption:** Essential project files can be overwritten by the framework's default templates.

## The Root Cause

The A.I.M. architecture currently tightly couples the **Engine** (the Python orchestration scripts, TUI, and SQLite database schemas) with the **Payload** (the specific project's Git history, Markdown documentation, and active session ledgers). 

Because the `setup.sh` alias and the Python scripts execute relative to the `$AIM_ROOT`, they blindly assume the `$AIM_ROOT` belongs entirely to the framework's upstream repository.

## Proposed Solution: Decoupling Engine from Payload

To allow A.I.M. to function as a true exoskeleton for external repositories, the update mechanism must be explicitly decoupled into two distinct operational vectors:

### 1. Engine Update (`aim update engine`)
This command should strictly manage the A.I.M. framework files.
- **Action:** Fetches the latest versions of `scripts/`, `core/`, `hooks/`, `setup.sh`, and `run_init.py` from `BrianV1981/aim`.
- **Constraint:** MUST NOT execute a generic `git pull` on the root directory. It should either pull updates into a sequestered `~/.aim-engine` binary path, or surgically update the Python scripts without touching `.git/`, `docs/`, `archive/`, or `engrams/`.
- **Result:** The agent gets the latest toolsets (e.g., a faster `aim_scraper.py`) without modifying the project's memory or Git history.

### 2. Project Update (`aim update project`)
This command should strictly manage the local project's momentum and memory state.
- **Action:** Executes a `git pull` from the *Target Repository's* configured remote (e.g., `origin main` for `BrianV1981/aim-google`).
- **Sync:** Re-ingests local JSONL session ledgers and processes new `.engram` cartridges found in the local workspace.
- **Result:** The agent synchronizes with the latest commits, tickets, and memories made by other human developers or Swarm agents working on the same specific project codebase.

## Implementation Roadmap

1. **Refactor `aim_cli.py update`:** Remove the hardcoded `git pull` logic.
2. **Abstract the Engine Location:** Consider moving the core A.I.M. Python scripts into a globally installed location (e.g., `~/.local/share/aim/`) rather than forcing them to live in the root of every target project workspace. The local project folder should only contain `.gemini/`, `engrams/`, and the target source code.
3. **Update `setup.sh`:** Modify the installer so it detects whether it is running inside the core framework repository (for A.I.M. development) or inside a target project repository (for Exoskeleton deployment), and configure the update paths accordingly.