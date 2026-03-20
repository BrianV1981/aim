#!/usr/bin/env python3
import os
import json
import subprocess
import shutil
import sys
from datetime import datetime

# --- CONFIG BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

from config_utils import AIM_ROOT, load_config

BASE_DIR = AIM_ROOT
CORE_DIR = os.path.join(BASE_DIR, "core")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")

# --- INTERNAL TEMPLATES ---
# (Keeping templates same as before but ensuring placeholders are clear)

T_IDENTITY = """# IDENTITY.md - A.I.M. (Actual Intelligent Memory)
- **Operator:** {name}
- **Vibe:** Sophisticated, precise, direct, loyal.
"""

T_USER = """# USER.md - {name}
- **Role:** Operator / Lead Engineer
- **Tech Stack:** {stack}
- **Working Style:** {style}
"""

T_AGENTS = """# AGENTS.md - A.I.M. Workspace Rules
- **Autonomous Action (YOLO Mode):** Prioritize completion.
- **Validation:** Every change must be verified.
"""

T_MEMORY = """# MEMORY.md — Durable Long-Term Memory (A.I.M.)
*Last Updated: {date}*
- **Operator:** {name}.
- **Clean Slate Protocol:** Purge history on request.
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

def backup_existing():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(ARCHIVE_DIR, f"backups/pre_reinstall_{timestamp}")
    os.makedirs(backup_path, exist_ok=True)
    targets = [
        ("core", ["CONFIG.json", "MEMORY.md", "USER.md", "IDENTITY.md", "AGENTS.md"]),
        ("docs", ["ROADMAP.md", "CURRENT_STATE.md", "DECISIONS.md"])
    ]
    for folder, files in targets:
        for f in files:
            src = os.path.join(BASE_DIR, folder, f)
            if os.path.exists(src): shutil.copy2(src, os.path.join(backup_path, f))

def init_workspace():
    print("\n--- A.I.M. SOVEREIGN INSTALLER ---")
    
    is_reinstall = os.path.exists(os.path.join(CORE_DIR, "CONFIG.json"))
    mode = "INITIAL"
    if is_reinstall:
        print("\n[!] EXISTING INSTALLATION DETECTED.")
        print("1. Update Structure (Safe)\n2. Total Reinstall (Destructive)\n3. Exit")
        choice = input("\nSelect [1-3]: ").strip()
        if choice == "3": sys.exit(0)
        if choice == "2": backup_existing(); mode = "OVERWRITE"
        else: mode = "UPDATE"

    name, stack, style, obsidian_path = "Operator", "General", "Direct", ""
    if mode != "UPDATE":
        name = input("\nWhat is your name? (Operator): ").strip() or name
        stack = input("What is your primary tech stack?: ").strip() or stack
        style = input("Briefly describe your working style: ").strip() or style
        obsidian_path = input("Enter path to your Obsidian vault [Enter to skip]: ").strip()
    
    allowed_root = BASE_DIR
    if mode != "UPDATE":
        root_input = input(f"\nEnter allowed root path [Enter for default {BASE_DIR}]: ").strip()
        allowed_root = root_input if root_input else BASE_DIR

    dirs = ["memory/proposals", "memory/archive", "archive/raw", "archive/index", 
            "archive/private", "archive/experimental", "archive/backups",
            "continuity/private", "continuity", "workstreams", "hooks", "scripts", "projects"]
    for d in dirs: os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    home = os.path.expanduser("~")
    gemini_tmp = os.path.join(home, ".gemini/tmp/aim/chats")
    
    files = {
        "core/IDENTITY.md": T_IDENTITY.format(name=name),
        "core/USER.md": T_USER.format(name=name, stack=stack, style=style),
        "core/AGENTS.md": T_AGENTS.format(name=name),
        "core/MEMORY.md": T_MEMORY.format(name=name, date=date_str),
        "docs/ROADMAP.md": "# Roadmap\n",
        "docs/CURRENT_STATE.md": "# Current State\n",
        "docs/DECISIONS.md": "# ADR\n"
    }
    
    for path, content in files.items():
        fp = os.path.join(BASE_DIR, path)
        if mode == "OVERWRITE" or not os.path.exists(fp):
            with open(fp, 'w') as f: f.write(content)
            
    config_path = os.path.join(CORE_DIR, "CONFIG.json")
    if mode == "OVERWRITE" or not os.path.exists(config_path):
        config_content = T_CONFIG.format(aim_root=BASE_DIR, gemini_tmp=gemini_tmp, allowed_root=allowed_root, obsidian_path=obsidian_path)
        with open(config_path, 'w') as f: f.write(config_content)

    print(f"\n[SUCCESS] A.I.M. is ready.")

if __name__ == "__main__":
    try: init_workspace()
    except KeyboardInterrupt: sys.exit(0)
