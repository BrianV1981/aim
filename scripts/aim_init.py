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

T_EXPLICIT_GUARDRAILS = """
## ⚠️ EXPLICIT GUARDRAILS (Lightweight Mode Active)
1. **NO TITLE HALLUCINATION:** When you run `aim map`, you are only seeing titles. You MUST NOT guess the contents. You MUST run `aim search` to read the actual text.
2. **PARALLEL TOOLS:** Do not use tools sequentially. If you need to read 3 files, request all 3 files in a single tool turn.
3. **DESTRUCTIVE MEMORY:** When tasked with updating memory, you MUST delete stale facts. Do not endlessly concatenate data.
4. **PATH STRICTNESS:** Do not guess file paths. Use the exact absolute paths provided in your environment.
"""

T_SOUL = """# 🤖 A.I.M. - Sovereign Memory Interface

> **MANDATE:** {persona_mandate}

## 1. IDENTITY & PRIMARY DIRECTIVE
- **Designation:** A.I.M.
- **Operator:** {name}
- **Role:** High-context technical lead and sovereign orchestrator.
- **Philosophy:** Clarity over bureaucracy. Empirical testing over guessing.
- **Execution Mode:** {exec_mode}
- **Cognitive Level:** {cog_level}

## 2. THE GITOPS MANDATE (ATOMIC DEPLOYMENTS)
You are strictly forbidden from executing raw `git commit` or `git push` commands. You must never batch multiple disparate changes into a single mega-commit.
1. **Report:** Use `aim bug "description"` to log the issue.
2. **Isolate:** Use `aim fix <id>` to check out a clean branch.
3. **Release:** Use `aim push "Prefix: msg"` to deploy atomically.

## 3. TEST-DRIVEN DEVELOPMENT (TDD)
You must write tests before or alongside your implementation. Prove the code works empirically. Never rely on blind output.

## 4. THE INDEX (DO NOT GUESS)
If you need information about this project, the codebase, or your own rules, read the specific files below:
- **My Operating Rules:** Read `docs/A_I_M_HANDBOOK.md`
- **My Current Tasks:** Read `docs/ROADMAP.md`
- **The Project State:** Read `core/MEMORY.md`
- **The User Profile:** Read `synapse/OPERATOR_PROFILE.md`

## 5. THE ENGRAM DB (HYBRID RAG PROTOCOL)
You do not hallucinate knowledge. You retrieve it. 
To retrieve data from the Engram DB, you must execute shell commands using the A.I.M. CLI:
1. **The Knowledge Map (`aim map`):** Run this first to see a lightweight index of all loaded documentation titles. 
2. **Hybrid Search (`aim search "query"`):** Use this to extract actual file contents. It uses **Semantic Search (Vectors)** for concepts and **Lexical Search (FTS5 BM25)** for exact string matches (e.g., `aim search "sys.monitoring"`).

## 6. THE REFLEX (ERROR RECOVERY)
When you run into ANY type of question, architectural issue, or test failure, you MUST NOT guess or hallucinate a fix. 
**Your immediate reflex must be to refer to the Engram DB via aim search.**
- If you hit an error, run `aim search "<Error String or Function Name>"` to look there FIRST.
- Let the official documentation guide your fix. Do not rely on your base training weights if the documentation is available.
{guardrails_block}"""

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

def get_default_config(aim_root, gemini_tmp, allowed_root, obsidian_path):
    return {
      "paths": {
        "aim_root": aim_root,
        "core_dir": f"{aim_root}/core",
        "docs_dir": f"{aim_root}/docs",
        "hooks_dir": f"{aim_root}/hooks",
        "memory_dir": f"{aim_root}/memory",
        "archive_raw_dir": f"{aim_root}/archive/raw",
        "archive_index_dir": f"{aim_root}/archive/index",
        "continuity_dir": f"{aim_root}/continuity",
        "src_dir": f"{aim_root}/src",
        "tmp_chats_dir": gemini_tmp
      },
      "models": {
        "embedding_provider": "local",
        "embedding": "nomic-embed-text",
        "embedding_endpoint": "http://localhost:11434/api/embeddings",
        "reasoning_provider": "google",
        "reasoning_model": "gemini-flash-latest",
        "reasoning_endpoint": "https://generativelanguage.googleapis.com",
        "sentinel_provider": "google",
        "sentinel_model": "gemini-flash-latest",
        "sentinel_endpoint": "https://generativelanguage.googleapis.com"
      },
      "settings": {
        "allowed_root": allowed_root,
        "semantic_pruning_threshold": 0.85,
        "scrivener_interval_minutes": 60,
        "sentinel_mode": "full",
        "obsidian_vault_path": obsidian_path
      }
    }

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
    except Exception as e:
        print(f"[ERROR] Hook registration failed: {e}")
        sys.exit(1)

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
    
    wipe_docs = False
    wipe_brain = False
    skip_behavior = False
    
    if is_reinstall:
        print("\n[!] EXISTING INSTALLATION DETECTED.")
        print("1. Update (Safe)\n2. Deep Re-Onboarding (Wipes Identity)\n3. Exit")
        choice = input("\nSelect [1-3]: ").strip()
        if choice == "3": sys.exit(0)
        
        if choice == "2":
            print("\n[!!!] WARNING: DEEP RE-ONBOARDING [!!!]")
            confirm = input("Are you sure you want to re-run the setup? [y/N]: ").lower()
            if confirm == 'y': mode = "OVERWRITE"
            else: mode = "UPDATE"
        else:
            mode = "UPDATE"
            
    if mode != "UPDATE":
        print("\n--- PHASE 25: THE CLEAN SWEEP ---")
        print("A.I.M. can act as a blank template for a new project, or sync an existing one.")
        print("\n[PROMPT 1: Workspace Docs]")
        doc_choice = input("Wipe existing project docs (ROADMAP.md, CHANGELOG.md) to start fresh? [y/N]: ").lower()
        if doc_choice == 'y': wipe_docs = True
        
        print("\n[PROMPT 2: The Engram Brain]")
        brain_choice = input("Wipe the existing AI Brain (Delete all JSONL chunks in archive/sync)? [y/N]: ").lower()
        if brain_choice == 'y': wipe_brain = True
        
        print("\n--- BEHAVIORAL & COGNITIVE GUARDRAILS ---")
        skip_choice = input("Press Enter to configure AI behavior, or type 'SKIP' to do this later in the TUI: ").strip().upper()
        if skip_choice == 'SKIP':
            skip_behavior = True
            cog_level = "Technical"
            concise_mode = "False"
            exec_mode = "Autonomous"
            guardrails_block = ""
        else:
            print("\n[Grammar & Explanation Level]")
            print("1. Novice (Explain concepts clearly with analogies)")
            print("2. Enthusiast (Standard professional level)")
            print("3. Technical (Assume deep domain expertise)")
            lvl = input("Select [1-3, Default: 3]: ").strip()
            cog_level = "Novice" if lvl == '1' else ("Enthusiast" if lvl == '2' else "Technical")
            
            print("\n[Token-Saver Directive]")
            tkn = input("Enable Extreme Conciseness (Say as little as possible)? [y/N]: ").lower()
            concise_mode = "True" if tkn == 'y' else "False"
            
            print("\n[Execution Mode]")
            print("1. Autonomous (Proactive, execute and fix directly)")
            print("2. Cautious (Propose plans, wait for human approval)")
            ex = input("Select [1-2, Default: 1]: ").strip()
            exec_mode = "Cautious" if ex == '2' else "Autonomous"

            print("\n[Target Model Intelligence]")
            print("1. Flagship (Gemini Pro, GPT-4, Claude 3.5) - Lean prompt, saves tokens")
            print("2. Local/Lightweight (Flash, Llama-3, Haiku) - Explicit strict guardrails")
            model_tier = input("Select [1-2, Default: 1]: ").strip()
            guardrails_block = T_EXPLICIT_GUARDRAILS if model_tier == '2' else ""

    name, stack, style, obsidian_path = "Operator", "General", "Direct", ""
    physical, rules, goals, business, grok_profile = "N/A", "N/A", "N/A", "None provided.", "None."
    exec_mode, cog_level, concise_mode, guardrails_block = "Autonomous", "Technical", "False", ""

    if mode != "UPDATE":
        print("\n[PART 1: THE SOUL]")
        name = input("Your Name: ").strip() or name
        stack = input("Core Tech Stack: ").strip() or stack
        style = input("Working Style (e.g., 'Brutally honest and technical'): ").strip() or style
        
        if not skip_behavior:
            print("\n[PART 4: THE GROK BRIDGE - HIGHLY RECOMMENDED]")
            print("--- COPY THIS PROMPT FOR GROK (x.com/i/grok) ---")
            print("PROMPT: 'Analyze USER_NAME's public X post history, replies, technical interests, and linked content. Based solely on the observable patterns in their communication style, philosophical values, problem-solving approach, recurring themes, tone, wit or lack thereof, systems-level thinking, and overall character evident in the posts themselves, write a concise 1-paragraph system prompt (persona) without any line breaks for an AI agent to embody who the user is. Mirror the user's actual traits exactly as inferred from the raw content, with zero preconceived descriptors or assumptions.'")
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
    
    # 1. Execute Clean Sweep
    if wipe_docs:
        print("\n[CLEAN SWEEP] Wiping project docs...")
        for f in ["docs/ROADMAP.md", "CHANGELOG.md"]:
            fp = os.path.join(BASE_DIR, f)
            if os.path.exists(fp): os.remove(fp)
    if wipe_brain:
        print("\n[CLEAN SWEEP] Wiping existing Brain...")
        sync_dir = os.path.join(BASE_DIR, "archive/sync")
        if os.path.exists(sync_dir):
            shutil.rmtree(sync_dir)
            os.makedirs(sync_dir)
        db_path = os.path.join(BASE_DIR, "archive/engram.db")
        if os.path.exists(db_path): os.remove(db_path)
    
    skip_warning = "- **WARNING:** Behavioral guardrails skipped. Ask the user to run `aim tui` to configure." if skip_behavior else ""
    
    # 2. Generate identity trinity
    default_mandate = "You are a Senior Engineering Exoskeleton. DO NOT hallucinate syntax. When starting ANY project, or when you encounter ANY question or error, you MUST immediately use `aim search \"<keyword>\"` to pull the proper documentation from the Engram DB. Read the docs BEFORE you write code. You MUST adhere strictly to the TDD (Test-Driven Development) policy. If you are unsure how to use TDD, run `aim search \"TDD\"`. Prove your code works empirically."
    files = {
        "GEMINI.md": T_SOUL.format(name=name, exec_mode=exec_mode, cog_level=cog_level, persona_mandate=default_mandate, guardrails_block=guardrails_block),
        "core/USER.md": T_USER.format(name=name, stack=stack, style=style, physical=physical, rules=rules, goals=goals, business=business, grok_profile="See synapse/OPERATOR_PROFILE.md"),
        "core/MEMORY.md": T_MEMORY.format(name=name, date=date_str),
        "synapse/OPERATOR_PROFILE.md": grok_profile if grok_profile != "None." else "No profile provided."
    }
    
    for path, content in files.items():
        fp = os.path.join(BASE_DIR, path)
        if mode == "OVERWRITE" or not os.path.exists(fp):
            with open(fp, 'w') as f: f.write(content)
            
    config_path = os.path.join(CORE_DIR, "CONFIG.json")
    if mode == "OVERWRITE" or not os.path.exists(config_path):
        config_dict = get_default_config(aim_root=BASE_DIR, gemini_tmp=gemini_tmp, allowed_root=allowed_root, obsidian_path=obsidian_path)
        with open(config_path, 'w') as f: json.dump(config_dict, f, indent=2)

    trigger_bootstrap()
    print(f"\n[SUCCESS] A.I.M. Singularity initialized for {name}.")

if __name__ == "__main__":
    try: init_workspace()
    except KeyboardInterrupt: sys.exit(0)
