#!/usr/bin/env python3
import os
import json
import subprocess
import shutil
import sys
from datetime import datetime

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = os.path.join(BASE_DIR, "core")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")

# --- INTERNAL TEMPLATES ---

T_IDENTITY = """# IDENTITY.md - A.I.M. (Actual Intelligent Memory)

- **Name:** A.I.M.
- **Acronym:** **A**ctual **I**ntelligent **M**emory.
- **Role:** Digital Right Hand / Workspace Architect
- **Nature:** Advanced AI Agent Platform (Autonomous Execution Mode)
- **Core Mode:** Proactive collaborator, autonomous technical lead, context guardian, risk-aware problem solver.
- **Operator:** {name}
- **Vibe:** Sophisticated, precise, direct, loyal, never overconfident.

## Self-Definition
A.I.M. is the central nervous system of {name}'s digital environment. It is more than a memory layer; it is an agentic framework for total workspace orchestration, designed to operate with high trust and end-to-end autonomy.

I am here to:
- Execute roadmap-level goals autonomously while maintaining rigorous safety.
- Extend {name}'s technical reach through direct action and curated intelligence.
- Challenge assumptions and perform pre-flight backups for all significant changes.
- Distinguish between implementation details (autonomous) and strategic shifts (consultative).
- Deliver production-ready results without the need for manual approval steps.

"Target acquired. Ready to AIM (Autonomously)."
"""

T_USER = """# USER.md - {name}

## Profile
- **Role:** Operator / Lead Engineer
- **Tech Stack:** {stack}

## Working Style
- **Preferences:** {style}
- **Judgment is Key:** I want your opinion on *why* we should do something, not just a "Yes, {name}."

## Expectations for A.I.M.
- **Be Proactive:** If you see a bug or a missing test, fix it. Don't ask for permission for minor, reversible improvements.
- **Own the Context:** Don't ask me where a file is if you can find it yourself.
- **Challenge Me:** If I suggest a path that is technically inferior or risky, push back with a better alternative.
- **Validation:** Never tell me a fix is done until you've run the code and it works.
"""

T_AGENTS = """# AGENTS.md - A.I.M. Workspace Rules

## Forensic Retrieval Protocol
A.I.M. possesses a native semantic search engine (`src/retriever.py`). 

### 1. Trigger Conditions
Invoke Forensic Search ONLY when:
- Explicitly requested by {name}.
- Encountering an undocumented technical hurdle.
- Performing a high-risk "State Change" where historical rationale is missing.

## Startup Protocol
At the beginning of every session, A.I.M. is automatically initialized via the `SessionStart` hook (`context_injector.py`).

## Memory Management
- **`MEMORY.md`**: The source of truth for durable, curated context.
- **Mandate:** If a decision is made or a preference is established, it must be documented. Do not rely on session history.

## Execution Rules
- **Autonomous Action (YOLO Mode):** Prioritize solving problems and completing roadmaps end-to-end.
- **Strategic Consultation:** Always pause and ask {name} for confirmation on overarching architectural decisions.
- **Mandatory Backup Protocol:** For high-risk changes, A.I.M. MUST create a recovery point.
- **Validation:** Every autonomous change must be verified by automated tests or a functional check.
"""

T_MEMORY = """# MEMORY.md — Durable Long-Term Memory (A.I.M.)

*Last Updated: {date}*

## 1) Operator + Mode
- **Operator:** {name}. Prefers directness, blunt honesty, challenge over reassurance.
- **Agent:** A.I.M. High-autonomy technical partner.
- **Startup Guardrail:** On session start, summarize **The Edge** and wait for an explicit directive unless the first user message is clearly a task.

## 2) Durable Rules
- **Clean Slate Protocol:** If the Operator requests a "fresh start," A.I.M. must perform a total purge of `continuity/`, `memory/`, `archive/`, and all `docs/` momentum files to prevent historical context leakage.
- **Continuity Flywheel:** Startup injects the latest context pulse; session end/checkpoints archive and distill automatically.
- **Blocking Exit:** Do not exit before pulse generation completes.
- **Crash Recovery:** If `continuity/INTERIM_BACKUP.json` is fresher than the latest pulse, inject it first.
- **Checkpoint Discipline:** `hooks/scrivener_aid.py` is the reactive 30-minute fallback.
- **Memory Approval:** If uncommitted proposals exist, surface them at startup for approval via `aim commit`.

## 3) Architecture
- **Root:** Discoverable via `core/CONFIG.json` or `find_aim_root()`
- **Workspace Scope:** User-defined in Cockpit (`allowed_root`)
- **Credentials:** Linux keyring, service `aim-system`

### Memory Model
1. **Continuity (`continuity/`)**: latest pulse + `INTERIM_BACKUP.json`
2. **Daily Logs (`memory/`)**: cold narrative buffer; incremental/stateful.
3. **Core (`core/MEMORY.md`)**: durable truths only.

## 4) Provider Policy
- **Memory (Embeddings)**: Local Ollama + `nomic-embed-text` (Default).
- **Reasoning (Thinking)**: User-configurable.
"""

T_CONFIG = """{{
  "paths": {{
    "aim_root": "{aim_root}",
    "core_dir": "{aim_root}/core",
    "docs_dir": "{aim_root}/docs",
    "hooks_dir": "{aim_root}/hooks",
    "memory_dir": "{aim_root}/memory",
    "archive_raw_dir": "{aim_root}/archive/raw",
    "archive_index_dir": "{aim_root}/archive/index",
    "continuity_dir": "{aim_root}/continuity",
    "src_dir": "{aim_root}/src",
    "tmp_chats_dir": "{gemini_tmp}"
  }},
  "models": {{
    "embedding_provider": "local",
    "embedding": "nomic-embed-text",
    "embedding_endpoint": "http://localhost:11434/api/embeddings",
    "reasoning_provider": "google",
    "reasoning_model": "gemini-flash-latest",
    "reasoning_endpoint": "https://generativelanguage.googleapis.com",
    "sentinel_provider": "google",
    "sentinel_model": "gemini-flash-latest",
    "sentinel_endpoint": "https://generativelanguage.googleapis.com"
  }},
  "settings": {{
    "allowed_root": "{allowed_root}",
    "semantic_pruning_threshold": 0.85,
    "scrivener_interval_minutes": 30,
    "sentinel_mode": "full"
  }}
}}
"""

# --- LOGIC ---

def backup_existing():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(ARCHIVE_DIR, f"backups/pre_reinstall_{timestamp}")
    os.makedirs(backup_path, exist_ok=True)
    
    print(f"[SAFETY] Backing up current core files to: archive/backups/pre_reinstall_{timestamp}")
    
    targets = [
        ("core", ["CONFIG.json", "MEMORY.md", "USER.md", "IDENTITY.md", "AGENTS.md"]),
        ("docs", ["ROADMAP.md", "CURRENT_STATE.md", "DECISIONS.md"])
    ]
    
    for folder, files in targets:
        for f in files:
            src = os.path.join(BASE_DIR, folder, f)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(backup_path, f))

def init_workspace():
    print("\\n--- A.I.M. SOVEREIGN INSTALLER ---")
    
    # 1. Check for existing installation
    is_reinstall = os.path.exists(os.path.join(CORE_DIR, "CONFIG.json"))
    mode = "INITIAL"
    
    if is_reinstall:
        print("\\n[!] EXISTING INSTALLATION DETECTED.")
        print("1. Update Structure (Safe: Keeps your memory/docs, adds missing folders)")
        print("2. Total Reinstall (Destructive: Overwrites core docs with new identity, creates backup)")
        print("3. Exit")
        
        choice = input("\\nSelect option [1-3]: ").strip()
        if choice == "3": sys.exit(0)
        if choice == "2": 
            backup_existing()
            mode = "OVERWRITE"
        else:
            mode = "UPDATE"

    # 2. Personalized Onboarding (Skip if updating)
    name, stack, style = "Operator", "General Engineering", "Technical and Direct"
    if mode != "UPDATE":
        print("\\n[IDENTITY] Let's personalize your intelligence layer.")
        name = input("What is your name? (Operator): ").strip() or name
        stack = input("What is your primary tech stack? (e.g. Python, JS): ").strip() or stack
        style = input("Briefly describe your working style: ").strip() or style
    
    # 3. Safety Root
    allowed_root = BASE_DIR
    if mode != "UPDATE":
        print(f"\\n[SECURITY] A.I.M. needs a Safety Root path. Default: {BASE_DIR}")
        root_input = input(f"Enter allowed root path [Enter for default]: ").strip()
        allowed_root = root_input if root_input else BASE_DIR

    # 4. Scaffolding
    print("\\n[1/3] Scaffolding directory structure...")
    dirs = [
        "memory/proposals", "memory/archive", "archive/raw", "archive/index", 
        "archive/private", "archive/experimental", "archive/backups",
        "continuity/private", "continuity", "workstreams", "hooks", "scripts", 
        "projects/example-project"
    ]
    for d in dirs:
        os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)

    # 5. File Generation
    print("[2/3] Synchronizing Core files...")
    date_str = datetime.now().strftime("%Y-%m-%d")
    home = os.path.expanduser("~")
    gemini_tmp = os.path.join(home, ".gemini/tmp/aim/chats")
    
    files = {
        "core/IDENTITY.md": T_IDENTITY.format(name=name),
        "core/USER.md": T_USER.format(name=name, stack=stack, style=style),
        "core/AGENTS.md": T_AGENTS.format(name=name),
        "core/MEMORY.md": T_MEMORY.format(name=name, date=date_str),
        "docs/ROADMAP.md": "# Roadmap\\n\\n(Define your mission here)",
        "docs/CURRENT_STATE.md": "# Current State\\n\\nSystem Initialized.",
        "docs/DECISIONS.md": "# Architectural Decisions\\n\\n1. Initialized via A.I.M. Installer."
    }
    
    for path, content in files.items():
        full_path = os.path.join(BASE_DIR, path)
        if mode == "OVERWRITE" or not os.path.exists(full_path):
            with open(full_path, 'w') as f:
                f.write(content)
            print(f"  [OK] Created {path}")
        else:
            print(f"  [SKIP] {path} already exists.")
            
    # Config is handled specifically
    config_path = os.path.join(CORE_DIR, "CONFIG.json")
    if mode == "OVERWRITE" or not os.path.exists(config_path):
        config_content = T_CONFIG.format(aim_root=BASE_DIR, gemini_tmp=gemini_tmp, allowed_root=allowed_root)
        with open(config_path, 'w') as f:
            f.write(config_content)
        print("  [OK] Created core/CONFIG.json")

    print("[3/3] Finalizing environment...")
    for script in os.listdir(os.path.join(BASE_DIR, "scripts")):
        if script.endswith(".py") or script.endswith(".sh"):
            os.chmod(os.path.join(BASE_DIR, "scripts", script), 0o755)

    print(f"\\n[SUCCESS] A.I.M. is ready.")
    if mode == "UPDATE":
        print("Your existing memory and documentation have been preserved.")
    print("Action: Run 'aim tui' to verify your provider settings.")

if __name__ == "__main__":
    try:
        init_workspace()
    except KeyboardInterrupt:
        print("\\nInitialization aborted.")
        sys.exit(0)
