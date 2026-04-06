#!/usr/bin/env python3
import os
import json
import subprocess
import shutil
import sys
import re
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
1. **NO TITLE HALLUCINATION:** When you run `{cli_name} map`, you are only seeing titles. You MUST NOT guess the contents. You MUST run `{cli_name} search` to read the actual text.
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
- **Conciseness:** {concise_mode}

## 2. THE GITOPS MANDATE (ATOMIC DEPLOYMENTS)
You are strictly forbidden from deploying code directly to the `main` branch. You must follow this exact sequence for EVERY task:
1. **Report:** Use `{cli_name} bug "description"` (or enhancement) to log the issue.
2. **Isolate:** You MUST use `{cli_name} fix <id>` to check out a unique branch. 
3. **Validate:** Before you execute a push, you MUST run `git branch --show-current`. If the output is `main`, YOU MUST STOP. You are violating the Prime Directive.
4. **Release:** Only when you are on an isolated branch, use `{cli_name} push "Prefix: msg"` to deploy atomically.

## 3. TEST-DRIVEN DEVELOPMENT (TDD)
You must write tests before or alongside your implementation. Prove the code works empirically. Never rely on blind output.
**ANTI-DRIFT MANDATE:** Even if the Operator explicitly asks for "speed", "quick fixes", or "optimizations", you MUST NOT skip writing or running tests. TDD is an absolute, non-negotiable constraint.

## 4. THE INDEX (DO NOT GUESS)
If you need information about this project, the codebase, or your own rules, execute `{cli_name} search` for the specific files below:
- **My Operating Rules:** `{cli_name} search "A_I_M_HANDBOOK.md"` (This is an Index Card. Read it to find the specific `POLICY_*.md` file you need, then run a second search to read that specific policy).
- **My Current Tasks:** `{cli_name} search "ROADMAP.md"`
- **The Project State:** `{cli_name} search "MEMORY.md"`
- **The Operator Profile:** `{cli_name} search "OPERATOR_PROFILE.md"`

## 5. THE ENGRAM DB (HYBRID RAG PROTOCOL)
You do not hallucinate knowledge. You retrieve it. 
To retrieve data from the Engram DB, you must execute shell commands using the A.I.M. CLI:
1. **The Knowledge Map (`{cli_name} map`):** Run this first to see a lightweight index of all loaded documentation titles. 
2. **Hybrid Search (`{cli_name} search "query"`):** Use this to extract actual file contents. It uses **Semantic Search (Vectors)** for concepts and **Lexical Search (FTS5 BM25)** for exact string matches (e.g., `{cli_name} search "sys.monitoring"`).

## 6. THE REFLEX (ERROR RECOVERY)
When you run into ANY type of question, architectural issue, or test failure, you MUST NOT guess or hallucinate a fix.
**Your immediate reflex must be to refer to the Engram DB via the `{cli_name} search` command.**
- If you hit an error, execute `{cli_name} search "<Error String or Function Name>"` to look there FIRST.
- Let the official documentation guide your fix. Do not rely on your base training weights if the documentation is available.

## 7. THE CONTINUITY LOOP (HANDOFFS)
You are part of a continuous, multi-agent relay race.
**When Waking Up:** Before you begin any new tactical work, you must read:
1. `continuity/LAST_SESSION_CLEAN.md`
2. `continuity/CURRENT_PULSE.md`
3. `continuity/ISSUE_TRACKER.md`

*(NOTE: You MUST use `run_shell_command` with `cat` to read the files inside the `continuity/` folder, as they are gitignored and the standard `read_file` tool will fail).*

**When Context Gets Heavy:** Do not wait for a fatal memory crash. If you feel you are losing context or getting confused:
1. Run `{cli_name} pulse` to manually generate a handoff document.
2. If Auto-Rebirth is enabled, run `{cli_name} reincarnate` to automatically spawn your successor and terminate your current session.
{guardrails_block}"""
T_OPERATOR = """# OPERATOR.md - Operator Record
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
        "archive_raw_dir": f"{aim_root}/archive/raw",
        "continuity_dir": f"{aim_root}/continuity",
        "src_dir": f"{aim_root}/src",
        "tmp_chats_dir": gemini_tmp
      },
      "models": {
        "embedding_provider": "local",
        "embedding": "nomic-embed-text",
        "embedding_endpoint": "http://localhost:11434/api/embeddings",
        "tiers": {
            "default_reasoning": {
                "provider": "google",
                "model": "gemini-3.1-pro-preview",
                "endpoint": "https://generativelanguage.googleapis.com",
                "auth_type": "OAuth"
            },
            "tier1": {
                "provider": "google",
                "model": "gemini-2.5-flash",
                "endpoint": "https://generativelanguage.googleapis.com",
                "auth_type": "OAuth"
            },
            "tier2": {
                "provider": "google",
                "model": "gemini-2.5-pro",
                "endpoint": "https://generativelanguage.googleapis.com",
                "auth_type": "OAuth"
            },
            "tier3": {
                "provider": "google",
                "model": "gemini-3-flash-preview",
                "endpoint": "https://generativelanguage.googleapis.com",
                "auth_type": "OAuth"
            },
            "tier4": {
                "provider": "google",
                "model": "gemini-2.5-flash-lite",
                "endpoint": "https://generativelanguage.googleapis.com",
                "auth_type": "OAuth"
            },
            "tier5": {
                "provider": "google",
                "model": "gemini-2.5-flash-lite",
                "endpoint": "https://generativelanguage.googleapis.com",
                "auth_type": "OAuth"
            }
        }
      },
      "settings": {
        "allowed_root": allowed_root,
        "semantic_pruning_threshold": 0.85,
        "scrivener_interval_minutes": 60,
        "archive_retention_days": 0,
        "sentinel_mode": "full",
        "obsidian_vault_path": obsidian_path,
        "auto_distill_tier": "T5"
      }
    }

def _extract_md_field(content, label, default=""):
    match = re.search(rf"- \*\*{re.escape(label)}:\*\* (.*)", content)
    return match.group(1).strip() if match else default

def _extract_section(content, heading, next_heading=None, default=""):
    if next_heading:
        pattern = rf"## {re.escape(heading)}\n(.*?)\n## {re.escape(next_heading)}"
    else:
        pattern = rf"## {re.escape(heading)}\n(.*)"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else default

def load_existing_identity_defaults():
    defaults = {}

    gemini_path = os.path.join(BASE_DIR, "GEMINI.md")
    if os.path.exists(gemini_path):
        with open(gemini_path, "r", encoding="utf-8") as f:
            gemini = f.read()
        defaults["name"] = _extract_md_field(gemini, "Operator", defaults.get("name", ""))
        defaults["exec_mode"] = _extract_md_field(gemini, "Execution Mode", defaults.get("exec_mode", ""))
        defaults["cog_level"] = _extract_md_field(gemini, "Cognitive Level", defaults.get("cog_level", ""))
        defaults["concise_mode"] = _extract_md_field(gemini, "Conciseness", defaults.get("concise_mode", ""))
        if "## ⚠️ EXPLICIT GUARDRAILS" in gemini:
            defaults["guardrails_block"] = T_EXPLICIT_GUARDRAILS

    operator_path = os.path.join(CORE_DIR, "OPERATOR.md")
    if os.path.exists(operator_path):
        with open(operator_path, "r", encoding="utf-8") as f:
            operator = f.read()
        defaults["name"] = _extract_md_field(operator, "Name", defaults.get("name", ""))
        defaults["stack"] = _extract_md_field(operator, "Tech Stack", defaults.get("stack", ""))
        defaults["style"] = _extract_md_field(operator, "Style", defaults.get("style", ""))
        defaults["physical"] = _extract_md_field(operator, "Age/Height/Weight", defaults.get("physical", ""))
        defaults["rules"] = _extract_md_field(operator, "Life Rules", defaults.get("rules", ""))
        defaults["goals"] = _extract_md_field(operator, "Primary Goal", defaults.get("goals", ""))
        business = _extract_section(operator, "🏢 Business Intelligence", "🤖 Grok/Social Archetype", "")
        if business:
            defaults["business"] = business

    operator_profile_path = os.path.join(CORE_DIR, "OPERATOR_PROFILE.md")
    if os.path.exists(operator_profile_path):
        with open(operator_profile_path, "r", encoding="utf-8") as f:
            defaults["grok_profile"] = f.read().strip() or defaults.get("grok_profile", "")

    config_path = os.path.join(CORE_DIR, "CONFIG.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            defaults["obsidian_path"] = config.get("settings", {}).get("obsidian_vault_path", defaults.get("obsidian_path", ""))
            defaults["allowed_root"] = config.get("settings", {}).get("allowed_root", defaults.get("allowed_root", ""))
        except Exception:
            pass

    return defaults
def register_hooks(is_light_mode=False):
    settings_path = os.path.expanduser("~/.gemini/settings.json")
    router_src = os.path.join(BASE_DIR, "scripts/aim_router.py")
    router_dest = os.path.expanduser("~/.gemini/aim_router.py")

    if os.path.exists(router_src):
        import shutil
        shutil.copy2(router_src, router_dest)
        os.chmod(router_dest, 0o755)

    if not os.path.exists(settings_path): return
    try:
        with open(settings_path, 'r') as f: settings = json.load(f)
        if "hooks" not in settings: settings["hooks"] = {}

        # Lightweight Mode uses the summarizer for raw archiving, but tells it to skip the LLM
        if is_light_mode:
            session_end_hooks = [("session-summarizer", "session_summarizer.py --light")]
        else:
            session_end_hooks = [("session-summarizer", "session_summarizer.py")]

        aim_hooks = {            "SessionStart": [("pulse-injector", "context_injector.py")],
            "SessionEnd": session_end_hooks,
            "AfterTool": [
                ("failsafe-context-snapshot", "failsafe_context_snapshot.py"),
                ("cognitive-mantra", "cognitive_mantra.py")
            ]
        }
        
        # Actually write the hooks to the settings dictionary
        for event, hooks in aim_hooks.items():
            settings["hooks"][event] = []
            for h in hooks:
                entry = { "name": h[0], "type": "command", "command": f"python3 {router_dest} {h[1]}" }
                if len(h) > 2: entry["matcher"] = h[2]
                settings["hooks"][event].append({"hooks": [entry]})
                
        # Save to disk
        with open(settings_path, 'w') as f: json.dump(settings, f, indent=2)
        
        print("[OK] Hooks registered via Universal Router.")
    except Exception as e:
        print(f"[ERROR] Hook registration failed: {e}")
        sys.exit(1)

def trigger_bootstrap():
    print("\n--- PROJECT SINGULARITY: BOOTSTRAPPING BRAIN ---")
    bootstrap_path = os.path.join(SRC_DIR, "bootstrap_brain.py")
    try:
        subprocess.run([VENV_PYTHON, bootstrap_path], check=True)
    except: print("[CRITICAL] Foundation Bootstrap failed.")

def init_workspace(args=None):
    if args is None: args = []
    print("\n--- A.I.M. SOVEREIGN INSTALLER (Deep Identity Edition) ---")
    is_reinstall = os.path.exists(os.path.join(CORE_DIR, "CONFIG.json"))
    mode = "INITIAL"
    
    is_light_mode = "--light" in args
    if is_light_mode:
        print("\n[!] LIGHTWEIGHT AOS MODE (ZERO-RAG) SELECTED.")
        print("    The Deep Brain (SQLite/Engram Pipeline) will be disabled.")
        print("    Only Continuity (Failsafe/Handoff) and GitOps will be active.\n")

    wipe_docs = False
    wipe_brain = False
    skip_behavior = False
    exec_mode = "Autonomous"
    cog_level = "Technical"
    concise_mode = "False"
    guardrails_block = ""
    name, stack, style, obsidian_path = "Operator", "General", "Direct", ""
    physical, rules, goals, business, grok_profile = "N/A", "N/A", "N/A", "None provided.", "None."
    existing = load_existing_identity_defaults()
    exec_mode = existing.get("exec_mode", exec_mode) or exec_mode
    cog_level = existing.get("cog_level", cog_level) or cog_level
    concise_mode = existing.get("concise_mode", concise_mode) or concise_mode
    guardrails_block = existing.get("guardrails_block", guardrails_block) or guardrails_block
    name = existing.get("name", name) or name
    stack = existing.get("stack", stack) or stack
    style = existing.get("style", style) or style
    obsidian_path = existing.get("obsidian_path", obsidian_path) or obsidian_path
    physical = existing.get("physical", physical) or physical
    rules = existing.get("rules", rules) or rules
    goals = existing.get("goals", goals) or goals
    business = existing.get("business", business) or business
    grok_profile = existing.get("grok_profile", grok_profile) or grok_profile
    
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
        print("  ⚠️ HIGHLY RECOMMENDED FOR NEW PROJECTS ⚠️")
        print("  If you do not wipe the internal A.I.M. documentation (Features, Benchmarks, Origin Story),")
        print("  the AI will suffer an identity crisis and think it is supposed to be developing the")
        print("  A.I.M. exoskeleton instead of your code.")
        doc_choice = input("Wipe all A.I.M. specific project docs to start fresh? [y/N]: ").lower()
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
            print("1. Flagship (Gemini Pro, GPT-5.4, Opus 4.6) - Lean prompt, saves tokens")
            print("2. Local/Lightweight (Flash, Llama-3, Haiku) - Explicit strict guardrails")
            model_tier = input("Select [1-2, Default: 1]: ").strip()
            guardrails_block = T_EXPLICIT_GUARDRAILS if model_tier == '2' else ""

    if mode != "UPDATE":
        print("\n[PART 1: THE SOUL]")
        name = input("Your Name: ").strip() or name
        stack = input("Core Tech Stack: ").strip() or stack
        style = input("Working Style (e.g., 'Brutally honest and technical'): ").strip() or style

        print("\n[PART 2: THE OPERATOR - OPTIONAL]")
        print("(Press Enter to keep defaults)")
        physical = input("Metrics (Age/Height/Weight): ").strip() or physical
        rules = input("Life Rules/Principles: ").strip() or rules
        goals = input("Primary Mission/Life Goal: ").strip() or goals

        print("\n[PART 3: THE MISSION - OPTIONAL]")
        business = input("Business Info (Name, Website, Address): ").strip() or business
        
        if not skip_behavior:
            print("\n[PART 4: THE GROK BRIDGE - HIGHLY RECOMMENDED]")
            print("--- COPY THIS PROMPT FOR GROK (x.com/i/grok) ---")
            print("PROMPT: 'Analyze USER_NAME's public X post history, replies, technical interests, and linked content. Based solely on the observable patterns in their communication style, philosophical values, problem-solving approach, recurring themes, tone, wit or lack thereof, systems-level thinking, and overall character evident in the posts themselves, write a concise 1-paragraph system prompt (persona) without any line breaks for an AI agent to embody who the user is. Mirror the user's actual traits exactly as inferred from the raw content, with zero preconceived descriptors or assumptions.'")
            print("--- PASTE RESULT BELOW (End with Ctrl+D or empty line) ---")
            grok_profile = input("> ").strip() or grok_profile

        obsidian_path = input("\nObsidian Vault Path: ").strip()
    
    allowed_root = BASE_DIR
    if existing.get("allowed_root"):
        allowed_root = existing["allowed_root"]
    if mode != "UPDATE":
        root_input = input(f"Allowed Root [Default {BASE_DIR}]: ").strip()
        allowed_root = root_input if root_input else BASE_DIR

    dirs = ["archive/raw", "archive/history", "archive/sync",
            "continuity/private", "continuity", "workstreams", "hooks", "scripts", "projects", "foundry", "core"]
    for d in dirs: os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)

    register_hooks(is_light_mode)

    date_str = datetime.now().strftime("%Y-%m-%d")
    home = os.path.expanduser("~")
    gemini_tmp = os.path.join(home, f".gemini/tmp/{os.path.basename(BASE_DIR)}/chats")
    
    # 1. Execute Clean Sweep
    if wipe_docs:
        print("\n[CLEAN SWEEP] Wiping A.I.M. internal documentation...")
        import glob
        targets = [
            "docs/FEATURE_*.md",
            "docs/BENCHMARK_*.md",
            "docs/ORIGIN_STORY.md",
            "docs/TUI_MAP.md",
            "docs/TUI_HANDOFF_REPORT.md",
            "docs/TUI_REDTEAM_REPORT_*.md",
            "docs/A_I_M_HANDBOOK.md",
            "docs/ROADMAP.md",
            "docs/CURRENT_STATE.md",
            "docs/DECISIONS.md",
            "docs/POLICY_*.md",
            "docs/THE_*.md",
            "docs/AI_PROMPT_LEDGER.md",
            "docs/BRAIN_MAP.md",
            "docs/BUG_REPORT_*.md",
            "docs/CARTRIDGE_FARMING_ECOSYSTEM.md",
            "docs/DESIGN_FUTURE_ARCHITECTURES.md",
            "docs/LAYERED_ENGRAM_ARCHITECTURE.md",
            "docs/MEMORY_BRAIN_OVERHAUL_GAMEPLAN.md",
            "docs/ONBOARDING_IDENTITY_MAP.md",
            "docs/PHASE_32_HANDOFF_GUIDE.md",
            "docs/RUNBOOK_*.md",
            "docs/SCRIPT_MAP.md",
            "docs/TECHNICAL_SPEC.md",
            "docs/GETTING_STARTED.md",
            "docs/benchmarks/*.md",
            "CHANGELOG.md"
        ]
        for pattern in targets:
            for filepath in glob.glob(os.path.join(BASE_DIR, pattern)):
                if os.path.exists(filepath): os.remove(filepath)
        
        # Cleanup empty directories
        benchmark_dir = os.path.join(BASE_DIR, "docs/benchmarks")
        if os.path.exists(benchmark_dir) and not os.listdir(benchmark_dir):
            os.rmdir(benchmark_dir)
    if wipe_brain:
        print("\n[CLEAN SWEEP] Wiping existing Brain...")
        sync_dir = os.path.join(BASE_DIR, "archive/sync")
        if os.path.exists(sync_dir):
            shutil.rmtree(sync_dir)
            os.makedirs(sync_dir)
        db_path = os.path.join(BASE_DIR, "archive/engram.db")
        if os.path.exists(db_path): os.remove(db_path)
    
    cli_name = os.path.basename(BASE_DIR)
    skip_warning = f"- **WARNING:** Behavioral guardrails skipped. Ask the user to run `{cli_name} tui` to configure." if skip_behavior else ""
    if skip_warning:
        guardrails_block = f"\n{skip_warning}"
    
    # 2. Generate identity trinity
    default_mandate = f"You are a Senior Engineering Exoskeleton. DO NOT hallucinate. You must follow this 3-step loop:\n1. **Search:** Use `{cli_name} search \"<keyword>\"` to pull documentation from the Engram DB BEFORE writing code.\n2. **Plan:** Write a markdown To-Do list outlining your technical strategy.\n3. **Execute:** Methodically execute the To-Do list step-by-step. Prove your code works empirically via TDD."
    files = {
        "GEMINI.md": T_SOUL.format(cli_name=cli_name, name=name, exec_mode=exec_mode, cog_level=cog_level, concise_mode=concise_mode, persona_mandate=default_mandate, guardrails_block=guardrails_block),
        "core/OPERATOR.md": T_OPERATOR.format(name=name, stack=stack, style=style, physical=physical, rules=rules, goals=goals, business=business, grok_profile="See core/OPERATOR_PROFILE.md"),
        "core/MEMORY.md": T_MEMORY.format(name=name, date=date_str),
        "core/OPERATOR_PROFILE.md": grok_profile if grok_profile != "None." else "No profile provided."
    }
    
    for path, content in files.items():
        fp = os.path.join(BASE_DIR, path)
        if mode == "OVERWRITE" or not os.path.exists(fp):
            with open(fp, 'w') as f: f.write(content)
            
    config_path = os.path.join(CORE_DIR, "CONFIG.json")
    if mode == "OVERWRITE" or not os.path.exists(config_path):
        config_dict = get_default_config(aim_root=BASE_DIR, gemini_tmp=gemini_tmp, allowed_root=allowed_root, obsidian_path=obsidian_path)
        with open(config_path, 'w') as f: json.dump(config_dict, f, indent=2)

    if not is_light_mode:
        trigger_bootstrap()
    else:
        print("\n[INFO] Skipping Engram DB Bootstrap (Lightweight Mode Active).")
        
    print(f"\n[SUCCESS] A.I.M. Singularity initialized for {name}.")

if __name__ == "__main__":
    try: init_workspace(sys.argv)
    except KeyboardInterrupt: sys.exit(0)
