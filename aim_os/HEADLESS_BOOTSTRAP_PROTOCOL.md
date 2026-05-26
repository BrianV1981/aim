# A.I.M. Headless Bootstrap Protocol

This document outlines the standard operating procedure for installing a fresh, isolated instance of the A.I.M. OS into a new project directory. 

This protocol is specifically designed for **Headless / Zero-Touch** deployment by autonomous agents, intentionally bypassing interactive `sudo` prompts and configuration wizards.

## Prerequisites
Ensure the host system has Python 3 and `git` installed.

## Step-by-Step Deployment

### 1. Clone the Repository
Clone the A.I.M. repository directly into the target project folder.
```bash
git clone https://github.com/BrianV1981/aim.git /path/to/target_directory
cd /path/to/target_directory
```

### 2. Isolate the Environment (Agent-Safe)
**WARNING:** If you are an autonomous agent, DO NOT execute `./setup.sh`. The setup script may trigger interactive `sudo` prompts for OS-level dependencies (like `dbus-x11`), which will block your execution loop.

Instead, manually construct the Python virtual environment and install the verified dependencies:
```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```
*(Note: As of the resolution of Issue #599, `pandas` and other critical data-science dependencies are strictly enforced in `requirements.txt` to prevent `bootstrap_brain.py` from failing).*

### 3. Execute Headless Initialization
Execute the core initialization script using the isolated virtual environment and the `--headless` flag. 

This flag suppresses the interactive TUI, applies the default Sovereign Operator configurations, and automatically triggers the `bootstrap_brain.py` sequence to compile the initial LanceDB memory fragments.
```bash
venv/bin/python aim_core/aim_init.py --headless
```

### 4. Verification
If the deployment is successful, the terminal will output `[SUCCESS] A.I.M. Singularity initialized`. You should verify the generation of the following artifacts:
- `core/CONFIG.json` (The primary routing and configuration state)
- `.gemini/settings.json` (The workspace context bindings)
- `memory_lance/` (The initialized vector database)

The new A.I.M. instance is now fully federated and ready for autonomous task execution.