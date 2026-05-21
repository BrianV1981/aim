# Architecture Proposal: Streamlining A.I.M. Zero-Touch Installation

**Date:** May 2026
**Context:** During the autonomous provisioning of the `aim-medsdme` target workspace, several severe friction points were discovered. These friction points prevent true "Zero-Touch" headless deployments by AI agents.

This document outlines the core failures encountered and proposes a streamlined architecture for `setup.sh` and `aim_init.py`.

## 1. The Sudo Dependency Blocker
**The Flaw:** 
The `setup.sh` bash script automatically executes `sudo apt install dbus-x11 libdbus-1-dev`. When an AI agent attempts to run `./setup.sh` autonomously, the script hangs forever waiting for the user's root password in the terminal.
**The Fix:**
*   **Decouple OS Dependencies:** The `setup.sh` script should check if it is running in `--headless` mode. If so, it should skip OS-level dependency installations and strictly handle the Python `venv` and `pip install`.
*   **Dockerization / Pre-baked Environments:** Alternatively, A.I.M. should rely on a pre-configured Docker container or system image where these dependencies are guaranteed, rather than forcing the setup script to handle package manager logic.

## 2. The Path Resolution Catastrophe
**The Flaw:**
If an agent executes `/home/kingb/aim/aim_core/aim_cli.py init` while standing inside a new, empty directory (`aim-medsdme`), the `find_aim_root()` function dynamically resolves backward until it finds a `setup.sh` or `core/CONFIG.json`. It climbed out of the target directory and found the *source* repository (`aim`). This triggered a catastrophic `--clean` sweep on the global source repository instead of initializing the target workspace.
**The Fix:**
*   **Strict Path Enforcement:** `aim_init.py` must aggressively validate its target directory. It should require an explicit target path (e.g., `aim init --target .`) and immediately abort if the target path does not match the active `git` origin or lacks a `.git` folder indicating it is the intended clone.
*   **Global Binary:** The A.I.M. CLI should be installed globally (e.g., via `pipx` or a symlink in `/usr/local/bin`). Deploying a new workspace should be a command like `aim deploy /path/to/target`, allowing the globally installed binary to handle the cloning, venv creation, and initialization safely.

## 3. Bootstrapping Bloat & The OOM Crash
**The Flaw:**
The `bootstrap_brain.py` script blindly globbed entire directories (e.g., `continuity/*.md`). During initialization, it attempted to embed a 16MB `LAST_SESSION_FLIGHT_RECORDER.md` file, which slammed the local Ollama server with 11,000 simultaneous embedding requests, resulting in a `500 Internal Server Error` (OOM crash).
**The Fix:**
*   **Whitelist Over Globbing:** The initialization bootstrap must never use wildcard globs (`*.md`). It should rely on a strict whitelist of known-safe, foundational OS files (e.g., `AGENTS.md`, `README.md`, `OPERATOR_PROFILE.md`).
*   **Dynamic Cartridge Loading:** Instead of forcing the active LLM to re-embed foundational knowledge on every fresh install, the setup process should entirely bypass `bootstrap_brain.py`. It should simply download a pre-computed `aim_os.parquet` cartridge from a central server or P2P swarm and perform a zero-copy mount into the LanceDB `archive/cartridges/` directory.

## 4. Brittle Directory Dependencies
**The Flaw:**
The `aim_init.py` script crashed with a `FileNotFoundError` because it attempted to use `shutil.copy2` to move the `aim_os.parquet` file into `archive/cartridges/`, but the `dirs` array earlier in the script failed to create that specific folder.
**The Fix:**
*   **Declarative Scaffolding:** Hardcoded procedural folder creation is brittle. A.I.M. should use a declarative JSON or YAML schema that defines the exact folder and file structure of a pristine OS environment. The initializer should loop through this schema to guarantee absolute structural integrity before executing any copy commands. 

## Summary
To achieve true, frictionless sovereign deployment, A.I.M. must transition from interactive, procedural scripts to declarative, idempotent operations that assume zero human intervention.