#!/usr/bin/env python3
import os
import json
import subprocess
import shutil
import sys
from datetime import datetime

# --- CONFIG BOOTSTRAP ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        if os.path.exists(os.path.join(current, "setup.sh")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = find_aim_root(os.getcwd())
CORE_DIR = os.path.join(BASE_DIR, "core")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")
HOOKS_DIR = os.path.join(BASE_DIR, "hooks")
SRC_DIR = os.path.join(BASE_DIR, "src")
VENV_PYTHON = os.path.join(BASE_DIR, "venv/bin/python3")

# --- INTERNAL TEMPLATES ---

T_USER = """# USER.md - {name}
- **Role:** Operator / Lead Engineer
- **Tech Stack:** {stack}
- **Working Style:** {style}
"""

T_MEMORY = """# MEMORY.md — Durable Long-Term Memory (A.I.M.)
*Last Updated: {date}*
- **Operator:** {name}.
- **Status:** Initialized via Singularity Bootstrap.
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
    "sentinel_mode": "full",
    "obsidian_vault_path": "{obsidian_path}"
  }}
}}
"""

T_SYNAPSE = """# A.I.M. Synapse Intake
Drop technical documentation here to feed the **Engram DB**.

Review **Section 2** of the **Handbook** or ask A.I.M. to query its brain about "Synapse Ingestion" for more details.
"""

def register_hooks():
    settings_path = os.path.expanduser("~/.gemini/settings.json")
    if not os.path.exists(settings_path): return
    try:
        with open(settings_path, 'r') as f: settings = json.load(f)
        if "hooks" not in settings: settings["hooks"] = {}
        aim_hooks = {
            "SessionStart": [("pulse-injector", "context_injector.py")],
            "SessionEnd": [("session-archivist", "session_summarizer.py")],
            "AfterTool": [("scrivener-aid", "scrivener_aid.py")],
            "PreCompress": [("pre-compress-shield", "pre_compress_checkpoint.py")],
            "BeforeTool": [
                ("safety-sentinel", "safety_sentinel.py", "run_shell_command"),
                ("secret-shield", "secret_shield.py", "write_file|replace"),
                ("workspace-guardrail", "workspace_guardrail.py")
            ]
        }
        for event, hooks in aim_hooks.items():
            settings["hooks"][event] = []
            for h in hooks:
                entry = { "name": h[0], "type": "command", "command": f"{VENV_PYTHON} {os.path.join(HOOKS_DIR, h[1])}" }
                if len(h) > 2: entry["matcher"] = h[2]
                settings["hooks"][event].append({"hooks": [entry]})
        with open(settings_path, 'w') as f: json.dump(settings, f, indent=2)
        print("[OK] Hooks registered.")
    except Exception as e: print(f"[ERROR] Hook registration: {e}")

def trigger_bootstrap():
    print("\n--- PROJECT SINGULARITY: BOOTSTRAPPING BRAIN ---")
    bootstrap_path = os.path.join(SRC_DIR, "bootstrap_brain.py")
    try:
        subprocess.run([VENV_PYTHON, bootstrap_path], check=True)
    except: print("[CRITICAL] Foundation Bootstrap failed.")

def init_workspace():
    print("\n--- A.I.M. SOVEREIGN INSTALLER (Invisible Edition) ---")
    is_reinstall = os.path.exists(os.path.join(CORE_DIR, "CONFIG.json"))
    mode = "INITIAL"
    if is_reinstall:
        print("\n[!] EXISTING INSTALLATION DETECTED.")
        print("1. Update (Safe)\n2. Total Reinstall\n3. Exit")
        choice = input("\nSelect [1-3]: ").strip()
        if choice == "3": sys.exit(0)
        mode = "OVERWRITE" if choice == "2" else "UPDATE"

    name, stack, style, obsidian_path = "Operator", "General", "Direct", ""
    if mode != "UPDATE":
        name = input("\nYour Name (Operator): ").strip() or name
        stack = input("Tech Stack: ").strip() or stack
        style = input("Working Style: ").strip() or style
        obsidian_path = input("Obsidian Vault Path [Enter to skip]: ").strip()
    
    allowed_root = BASE_DIR
    if mode != "UPDATE":
        root_input = input(f"Allowed Root [Default {BASE_DIR}]: ").strip()
        allowed_root = root_input if root_input else BASE_DIR

    dirs = ["memory/proposals", "memory/archive", "archive/raw", "archive/index", 
            "archive/private", "archive/experimental", "archive/backups",
            "continuity/private", "continuity", "workstreams", "hooks", "scripts", "projects", "synapse"]
    for d in dirs: os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)

    register_hooks()

    date_str = datetime.now().strftime("%Y-%m-%d")
    home = os.path.expanduser("~")
    gemini_tmp = os.path.join(home, ".gemini/tmp/aim/chats")
    
    # Generate ONLY the essential identity trinity
    files = {
        "core/USER.md": T_USER.format(name=name, stack=stack, style=style),
        "core/MEMORY.md": T_MEMORY.format(name=name, date=date_str),
        "synapse/README.md": T_SYNAPSE
    }
    
    for path, content in files.items():
        fp = os.path.join(BASE_DIR, path)
        if mode == "OVERWRITE" or not os.path.exists(fp):
            with open(fp, 'w') as f: f.write(content)
            print(f"  [OK] Created {path}")
            
    config_path = os.path.join(CORE_DIR, "CONFIG.json")
    if mode == "OVERWRITE" or not os.path.exists(config_path):
        config_content = T_CONFIG.format(aim_root=BASE_DIR, gemini_tmp=gemini_tmp, allowed_root=allowed_root, obsidian_path=obsidian_path)
        with open(config_path, 'w') as f: f.write(config_content)

    trigger_bootstrap()
    
    # OPTIONAL IMPORT LOGIC
    if mode != "UPDATE":
        print("\n[MOMENTUM] Initializing Roadmap...")
        do_import = input("Do you have an existing ROADMAP.md to import? [y/N]: ").strip().lower()
        if do_import == 'y':
            src = input("Enter path to your ROADMAP.md: ").strip()
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(DOCS_DIR, "ROADMAP.md"))
                print("  [OK] Roadmap imported.")
            else: print("  [ERROR] File not found. Skipping import.")

    print(f"\n[SUCCESS] A.I.M. Singularity initialized. Workspace is clean.")

if __name__ == "__main__":
    try: init_workspace()
    except KeyboardInterrupt: sys.exit(0)
