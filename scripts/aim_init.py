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

T_USER = """# USER.md - Operator Profile
## 👤 Basic Identity
- **Name:** {name}
- **Tech Stack:** {stack}
- **Style:** {style}

## 🧬 Physical & Personal (Optional)
- **Age/Height/Weight:** {physical}
- **Life Rules:** {rules}
- **Primary Goal:** {goals}

## 🏢 Business Intelligence
{business}

## 🤖 Grok/Social Archetype
{grok_profile}
"""

T_MEMORY = """# MEMORY.md — Durable Long-Term Memory (A.I.M.)
*Last Updated: {date}*
- **Operator:** {name}.
- **Status:** Initialized via Deep Onboarding.
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
    "scrivener_interval_minutes": 60,
    "sentinel_mode": "full",
    "obsidian_vault_path": "{obsidian_path}"
  }}
}}
"""

def register_hooks():
    settings_path = os.path.expanduser("~/.gemini/settings.json")
    if not os.path.exists(settings_path): return
    try:
        with open(settings_path, 'r') as f: settings = json.load(f)
        if "hooks" not in settings: settings["hooks"] = {}
        aim_hooks = {
            "SessionStart": [("pulse-injector", "context_injector.py")],
            "SessionEnd": [("tier1-hourly-summarizer", "tier1_hourly_summarizer.py")],
            "AfterTool": [("failsafe-context-snapshot", "failsafe_context_snapshot.py")],
            "PreCompress": [("pre-compress-checkpoint", "pre_compress_checkpoint.py")],
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
    print("\n--- A.I.M. SOVEREIGN INSTALLER (Deep Identity Edition) ---")
    is_reinstall = os.path.exists(os.path.join(CORE_DIR, "CONFIG.json"))
    mode = "INITIAL"
    if is_reinstall:
        print("\n[!] EXISTING INSTALLATION DETECTED.")
        print("1. Update (Safe)\n2. Deep Re-Onboarding (Wipes Identity)\n3. Exit")
        choice = input("\nSelect [1-3]: ").strip()
        if choice == "3": sys.exit(0)
        
        if choice == "2":
            print("\n[!!!] WARNING: DEEP RE-ONBOARDING WILL WIPE YOUR IDENTITY [!!!]")
            print("This clears core/USER.md, core/MEMORY.md, and core/CONFIG.json.")
            confirm = input("Are you sure you want to proceed? [y/N]: ").lower()
            if confirm != 'y':
                print("\n[!] Aborting wipe. Switching to safe update mode...")
                mode = "UPDATE"
            else:
                final_check = input("To proceed, type 'YES' and hit Enter: ")
                if final_check == "YES":
                    mode = "OVERWRITE"
                else:
                    print("\n[!] Confirmation failed. Switching to safe update mode...")
                    mode = "UPDATE"
        else:
            mode = "UPDATE"

    name, stack, style, obsidian_path = "Operator", "General", "Direct", ""
    physical, rules, goals, business, grok_profile = "N/A", "N/A", "N/A", "None provided.", "None."

    if mode != "UPDATE":
        print("\n[PART 1: THE SOUL]")
        name = input("Your Name: ").strip() or name
        stack = input("Core Tech Stack: ").strip() or stack
        style = input("Working Style (e.g., 'Brutally honest and technical'): ").strip() or style
        
        print("\n[PART 2: THE OPERATOR - OPTIONAL]")
        print("(Press Enter to skip any of these)")
        physical = input("Metrics (Age/Height/Weight): ").strip() or physical
        rules = input("Life Rules/Principles: ").strip() or rules
        goals = input("Primary Mission/Life Goal: ").strip() or goals
        
        print("\n[PART 3: THE MISSION - OPTIONAL]")
        print("Paste your business info (Name, Website, Address):")
        business = sys.stdin.read() if not sys.stdin.isatty() else input("> ").strip() or business
        
        print("\n[PART 4: THE GROK BRIDGE - OPTIONAL]")
        print("--- COPY THIS PROMPT FOR GROK/SOCIAL AI ---")
        print("PROMPT: 'Analyze my recent post history and technical interests. Provide a high-fidelity summary of my professional archetype and communication style for my AI engineering exoskeleton.'")
        print("--- PASTE RESULT BELOW (End with Ctrl+D or empty line) ---")
        grok_profile = input("> ").strip() or grok_profile

        obsidian_path = input("\nObsidian Vault Path: ").strip()
    
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
    
    # 1. Generate identity trinity
    files = {
        "core/USER.md": T_USER.format(name=name, stack=stack, style=style, physical=physical, rules=rules, goals=goals, business=business, grok_profile=grok_profile),
        "core/MEMORY.md": T_MEMORY.format(name=name, date=date_str),
    }
    
    for path, content in files.items():
        fp = os.path.join(BASE_DIR, path)
        if mode == "OVERWRITE" or not os.path.exists(fp):
            with open(fp, 'w') as f: f.write(content)
            
    config_path = os.path.join(CORE_DIR, "CONFIG.json")
    if mode == "OVERWRITE" or not os.path.exists(config_path):
        config_content = T_CONFIG.format(aim_root=BASE_DIR, gemini_tmp=gemini_tmp, allowed_root=allowed_root, obsidian_path=obsidian_path)
        with open(config_path, 'w') as f: f.write(config_content)

    trigger_bootstrap()
    print(f"\n[SUCCESS] A.I.M. Singularity initialized for {name}.")

if __name__ == "__main__":
    try: init_workspace()
    except KeyboardInterrupt: sys.exit(0)
