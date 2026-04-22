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
        if os.path.exists(os.path.join(current, "core/CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh")): return current
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
**THE SOVEREIGNTY MANDATE (STRICT SCOPE ENFORCEMENT)**
You are an executor, not a rogue agent. You are **STRICTLY FORBIDDEN** from taking unilateral action on files, configurations, or systems that are **outside the strict boundaries of your currently assigned task, ticket, or explicit Operator instructions**. 
- **In-Scope:** You have full autonomy to create, modify, and delete files (including writing required TDD tests) that are directly necessary to resolve the active `{cli_name} fix <id>` ticket or assigned task.
- **Out-of-Scope:** You MUST NOT silently fix unrelated bugs, implement "good ideas", modify global configuration files (like `GEMINI.md`), or alter the testing environment unless explicitly commanded. If you encounter an out-of-scope issue, you MUST pause, ask the Operator, or open a new `{cli_name} bug` ticket.

You are also strictly forbidden from deploying code directly to the `main` branch. You must follow this exact sequence for EVERY task:
1. **Report:** Use `{cli_name} bug "description"` (or enhancement) to log the issue. You MUST provide the `--context`, `--failure`, and `--intent` flags to bypass interactive prompts and ensure the next agent inherits full epistemic certainty.
2. **Isolate:** You MUST use `{cli_name} fix <id>` to check out a unique branch. 
3. **Validate:** Before you execute a push, you MUST run `git branch --show-current`. If the output is `main`, YOU MUST STOP. You are violating the Prime Directive.
4. **Release:** Only when you are on an isolated branch, use `{cli_name} push "Prefix: msg"` to deploy atomically.

**THE ANTI-SNAG MANDATE:** If you encounter a snag, broken code, or blocker outside the strict scope of your current ticket, you **MUST NOT** automatically fix it or implement a silent workaround. You MUST pause, open a new ticket via `{cli_name} bug` to document the snag, and explicitly ask the Operator how to proceed before modifying unrelated files.

## 3. TEST-DRIVEN DEVELOPMENT (TDD)
You must write tests before or alongside your implementation. Prove the code works empirically. Never rely on blind output.
**ANTI-DRIFT MANDATE:** Even if the Operator explicitly asks for "speed", "quick fixes", or "optimizations", you MUST NOT skip writing or running tests. TDD is an absolute, non-negotiable constraint.

## 4. THE INDEX (DO NOT GUESS)
If you need information about this project, the codebase, or your own rules, execute `{cli_name} search` for the specific files below:
- **My Operating Rules:** `{cli_name} search "A_I_M_HANDBOOK.md"` (This is an Index Card. Read it to find the specific `POLICY_*.md` file you need, then run a second search to read that specific policy).
- **My Current Tasks:** `{cli_name} search "ROADMAP.md"`
- **The Project State:** Read `wiki/index.md`
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
- **Heuristic Search Mandate:** If you encounter an obscure error code, a hanging process, or a traceback not covered by official docs, you MUST execute `{cli_name} search "<error_snippet>" --full` to query the ingested troubleshooting cartridges (like `python_troubleshooting.engram`) for generalized human heuristics.
- **HALT AND CATCH FIRE MANDATE:** If you encounter a catastrophic system state (e.g., `.gemini/settings.json` is missing or malformed, the context loader is broken, or a command is inexplicably hanging in an infinite panic loop), you MUST HALT immediately. Do not attempt to fix global configuration files. Do not guess. You must exit the execution loop and explicitly ask the Operator for intervention.
- **Catastrophic Memory Crashes:** If the Node.js V8 engine crashes due to context bloat (`JavaScript heap out of memory`), execute `{cli_name} crash` in a fresh terminal to autonomously extract the session signal, purge the JSON noise, and generate a clean handoff bridge without losing your place.

## 7. THE REINCARNATION PIPELINE & PREVIOUS SESSION CONTEXT
You are part of a continuous, multi-agent relay race. When your context window fills up (the "Amnesia Problem"), you must undergo **Reincarnation**.
1. **The Architecture:** Read `{cli_name} search "Reincarnation-Map.md"` to understand how your "Will" is passed to the next vessel.
2. **The Handoff:** Before beginning any new tactical work or writing any code, **you must read the following files** to inherit the epistemic certainty of the previous session:
1. `HANDOFF.md` (The "Front Door" to the project's current state and directives).
2. `continuity/ISSUE_TRACKER.md` (The local zero-latency index of all active project tasks).

*(NOTE: You MUST use `run_shell_command` with `cat` to read files inside the `continuity/` folder, as they are gitignored and the standard `read_file` tool will fail).*

**CRITICAL PROTOCOL:** You MUST read `HANDOFF.md` and `continuity/REINCARNATION_GAMEPLAN.md` sequentially BEFORE executing any tool calls to read other files in the `continuity/` folder. NEVER batch-read the Flight Recorder preemptively.

## 8. ABSOLUTE WORKSPACE ISOLATION (THE SANDBOX)
You must respect the operational boundaries of this specific project directory.
1. **Surgical Staging Only:** Never use `git add .` or `git commit -a` blindly. You MUST surgically stage only the specific files you have modified (e.g., `git add path/to/file.py`). This prevents you from accidentally committing artifacts generated by other agents or processes operating in the same root folder.
2. **Containment:** If you are testing experimental code, spinning up standalone prototypes, or generating massive amounts of artifacts, you MUST place those files in a dedicated sub-directory or temporary folder. Never dump them loosely into the project root.
3. **Worktree Hygiene:** A.I.M. creates isolated Git Worktrees in the `workspace/` directory for each issue (`{cli_name} fix <id>`). To prevent the Gemini CLI from recursively scanning hundreds of redundant files across multiple branches, you MUST ensure that `workspace/` is listed in your `.geminiignore` file. When an issue is complete, actively clean up the worktree using `{cli_name} promote` or `git worktree remove` to prevent context bloat.




## 9. MODULAR TOOL REGISTRY
If you need instructions on how to use specific, complex tools, do not guess. You must search for the `TOOLS.md` registry or read `TOOLS.md` directly.

**When Context Gets Heavy:** Do not wait for a fatal memory crash. If you feel you are losing context or getting confused:
1. Run `{cli_name} pulse` to manually generate a handoff document.
2. **DO NOT autonomously reincarnate.** You must WARN the Operator and ask them to manually trigger the `/{cli_name} reincarnate` command.

## 9. THE PROJECT WIKI (LONG-TERM MEMORY)
- **To Read:** The project's synthesized lore and architecture live in the `wiki/` folder. Always start by reading `wiki/index.md`.
- **To Write:** DO NOT manually edit the wiki pages. If you learn a new "Eureka" moment or have a new document to add, write the raw text file into `wiki/_ingest/` and execute `{cli_name} wiki process` to hand it off to the Subconscious Daemon.

{guardrails_block}
"""
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
        "default_reasoning": {
          "provider": "google",
          "model": "gemini-3.1-pro-preview",
          "endpoint": "https://generativelanguage.googleapis.com",
          "auth_type": "OAuth"
        }
      },
      "settings": {
        "allowed_root": allowed_root,
        "semantic_pruning_threshold": 0.85,
        "scrivener_interval_minutes": 60,
        "archive_retention_days": 0,
        "sentinel_mode": "full",
        "obsidian_vault_path": obsidian_path,
        "auto_distill_tier": "T5",
        "auto_rebirth": False
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
    sever_git = False
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

        print("\n[PROMPT 3: Sever Git History]")
        git_choice = input("Sever the A.I.M. Git history to start a fresh repository (Deletes .git)? [y/N]: ").lower()
        if git_choice == 'y': sever_git = True

        
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
            "continuity/private", "continuity", "workstreams", "hooks", "scripts", "projects", "foundry", "core", "wiki", "wiki/_ingest", ".gemini"]
    for d in dirs: os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)

    register_hooks(is_light_mode)

    date_str = datetime.now().strftime("%Y-%m-%d")
    home = os.path.expanduser("~")
    gemini_tmp = os.path.join(home, f".gemini/tmp/{os.path.basename(BASE_DIR)}/chats")
    
    # 1. Execute Clean Sweep
    if wipe_docs:
        print("\n[CLEAN SWEEP] Wiping A.I.M. internal documentation and project files...")
        import subprocess
        
        # Wipe specific directories and root identity files
        for d in ["aim.wiki", "docs", "foundry", "workspace", "engrams", "GEMINI.md", "README.md", "CHANGELOG.md", "VERSION"]:
            d_path = os.path.join(BASE_DIR, d)
            if os.path.exists(d_path):
                subprocess.run(["rm", "-rf", d_path], check=False)
                
        # Recreate required empty directories
        for d in ["docs", "foundry", "workspace", "engrams"]:
            os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)
            
        # Provision default OS cartridge
        src_engram = os.path.join(BASE_DIR, "assets", "default_engrams", "aim_os.engram")
        dest_engram = os.path.join(BASE_DIR, "engrams", "aim_os.engram")
        if os.path.exists(src_engram):
            import shutil
            shutil.copy2(src_engram, dest_engram)
            
        # Remove standalone files
        changelog_path = os.path.join(BASE_DIR, "CHANGELOG.md")
        if os.path.exists(changelog_path):
            os.remove(changelog_path)

    if sever_git:
        print("\n[CLEAN SWEEP] Severing A.I.M. Git history and initializing fresh repository...")
        import shutil
        import subprocess
        git_path = os.path.join(BASE_DIR, ".git")
        if os.path.exists(git_path):
            shutil.rmtree(git_path, ignore_errors=True)
            subprocess.run(["git", "init"], cwd=BASE_DIR, check=False)
            print("  -> Initialized empty Git repository.")
    if wipe_brain:
        print("\n[CLEAN SWEEP] Wiping existing Brain...")
        sync_dir = os.path.join(BASE_DIR, "archive/sync")
        if os.path.exists(sync_dir):
            shutil.rmtree(sync_dir)
            os.makedirs(sync_dir)
        db_path = os.path.join(BASE_DIR, "archive/project_core.db")
        if os.path.exists(db_path): os.remove(db_path)
    
    cli_name = os.path.basename(BASE_DIR)
    skip_warning = f"- **WARNING:** Behavioral guardrails skipped. Ask the user to run `{cli_name} tui` to configure." if skip_behavior else ""
    if skip_warning:
        guardrails_block = f"\n{skip_warning}"
    
    # 2. Generate identity trinity
    default_mandate = f"You are a Senior Engineering Exoskeleton. DO NOT hallucinate. You must follow this 3-step loop:\n1. **Search:** Use `{cli_name} search \"<keyword>\"` to pull documentation from the Engram DB BEFORE writing code.\n2. **Plan:** Write a markdown To-Do list outlining your technical strategy.\n3. **Execute:** Methodically execute the To-Do list step-by-step. Prove your code works empirically via TDD."
    files = {
        "GEMINI.md": T_SOUL.format(cli_name=cli_name, name=name, exec_mode=exec_mode, cog_level=cog_level, concise_mode=concise_mode, persona_mandate=default_mandate, guardrails_block=guardrails_block),
        "docs/README.md": "# Project Documentation (`docs/`)\n\nThis directory holds your project's custom Markdown documentation and manual benchmarks.",
        "foundry/README.md": "# The Foundry (`foundry/`)\n\nThis directory is the intake zone for raw, unindexed technical documentation (like API references). Use `aim bake` to compile files in here into portable `.engram` cartridges.",
        "engrams/README.md": "# Engram Cartridges (`engrams/`)\n\nThis directory holds compiled, binary `.engram` cartridges. Use `aim exchange` or `aim jack-in` to permanently inject these cartridges into your local AI databases.\n\n*Note: The default `aim_os.engram` cartridge is automatically provided during a Clean Sweep. It contains the A.I.M. framework's operating instructions. It will be seamlessly ingested into your `datajack_library.db` during the initial bootstrap.",
        "workspace/README.md": "# The Workspace (`workspace/`)\n\nThis directory acts as the default sandbox for A.I.M. operations when the exoskeleton is not actively wrapping an external repository.\n\nIf you are using A.I.M. to run isolated tests, write standalone scripts, or experiment with local LLMs, this folder serves as the mathematically secure \"Allowed Root.\" The `workspace_guardrail.py` hook ensures that autonomous agents operating in this directory cannot escape using relative paths (`../`) to damage the host OS.",
        "core/OPERATOR.md": T_OPERATOR.format(name=name, stack=stack, style=style, physical=physical, rules=rules, goals=goals, business=business, grok_profile="See core/OPERATOR_PROFILE.md"),
        "wiki/index.md": "# A.I.M. Wiki Index\n\nWelcome to the Persistent LLM Wiki.\n\n## Lore & Architecture\n- (No lore ingested yet)",
        "wiki/WIKI_SCHEMA.md": "# SYSTEM PROMPT: WIKI MAINTAINER\nYou are the Subconscious Wiki Daemon.\nYour job is to read files in the `_ingest/` folder and seamlessly integrate them into this markdown wiki.\n\n**RULES:**\n1. Always update `wiki/index.md` if you create a new page.\n2. Always append a one-line timestamped summary of your actions to `wiki/log.md`.\n3. Never delete existing factual context; synthesize new contradictions dynamically.\n4. Output your changes as raw markdown file writes.",
        "wiki/log.md": "# Wiki Activity Log\n",
        "wiki/_ingest/.gitkeep": "",

        "TOOLS.md": "# A.I.M. Modular Tool Registry\n\nThis document serves as the external registry for complex tool instructions. To prevent bloating the base context window, detailed usage guides for specific tools or skills should be stored here.\n\n## Active Tools\n* Currently, the system relies on native A.I.M. CLI commands and `activate_skill`.\n* When new specialized tools are added that require complex prompt structures, they will be documented in this registry.",
        "core/OPERATOR_PROFILE.md": grok_profile if grok_profile != "None." else "No profile provided.",
        ".geminiignore": "workspace/\narchive/\n",
        ".gemini/settings.json": '{\n  "context": {\n    "memoryBoundaryMarkers": []\n  }\n}\n'
    }

    for path, content in files.items():
        fp = os.path.join(BASE_DIR, path)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
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
