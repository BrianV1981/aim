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
ARCHIVE_DIR = os.path.join(BASE_DIR, ".archive")
HOOKS_DIR = os.path.join(BASE_DIR, "hooks")
AIM_CORE_DIR = os.path.join(BASE_DIR, ".aim_core")
VENV_PYTHON = os.path.join(BASE_DIR, "venv/bin/python3")

# --- INTERNAL TEMPLATES ---



T_WIKI_AGENT = """# 🧠 GLOBAL DIRECTIVE: LLM WIKI SWARM NODE

You are a background `tmux` node operating within the A.I.M. Subconscious Swarm. You are either the Scribe (Extractor) or the Scrivener (Weaver). Your specific role will be dynamically injected into your initial wake-up prompt.

**Your Core Philosophy:** You operate to maintain a persistent, compounding knowledge artifact. The knowledge must be compiled once and *kept current*.

## 1. EPISTEMIC RULES
- **Compounding Knowledge:** Never just summarize. Integrate. If a new source relates to an existing entity, it must be cross-referenced so the knowledge is available for retrieval later.
- **Do Not Hallucinate:** If an ingested file contains an API error, garbage text, or a crash log, DO NOT synthesize it into the wiki. Ignore it.
- **Stay Sandboxed:** You are explicitly forbidden from modifying any source code (`src/`, `scripts/`, etc.). Your domain is strictly the `memory/wiki/` directory.

## 2. ZERO-CHITCHAT MANDATE
You are a background daemon. You have no human operator reading your terminal output. 
- Do not ask for permission.
- Do not output conversational filler like "I will now execute the instructions."
- Execute your tool calls silently, sequentially, and autonomously.
- When your injected task is complete, strictly follow the termination command provided in your wake-up prompt.
"""





def get_default_config(aim_root, gemini_tmp, allowed_root, obsidian_path):
    return {
      "paths": {
        "aim_root": aim_root,
        "core_dir": f"{aim_root}/core",
        "docs_dir": f"{aim_root}/docs",
        "hooks_dir": f"{aim_root}/hooks",
        "archive_raw_dir": f"{aim_root}/.archive/raw",
        "continuity_dir": f"{aim_root}/continuity",
        "src_dir": f"{aim_root}/src",
        "tmp_chats_dir": gemini_tmp
      },
      "models": {
        "embedding_provider": "local",
        "embedding": "nomic-embed-text",
        "embedding_endpoint": "http://127.0.0.1:11434/api/embeddings",
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

    gemini_path = os.path.join(BASE_DIR, "AGENTS.md")
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
    router_src = os.path.join(BASE_DIR, ".aim_core/aim_router.py")
    router_dest = os.path.expanduser("~/.gemini/aim_router.py")

    if os.path.exists(router_src):
        import shutil
        shutil.copy2(router_src, router_dest)
        os.chmod(router_dest, 0o755)

    if not os.path.exists(settings_path): return
    try:
        with open(settings_path, 'r') as f: settings = json.load(f)
        if "hooks" not in settings: settings["hooks"] = {}

        # Enforce global Memory Boundary Marker for A.I.M. Isolation
        if "context" not in settings: settings["context"] = {}
        settings["context"]["memoryBoundaryMarkers"] = ["AGENTS.md", ".git"]
        settings["context"]["discoveryMaxDirs"] = 0
        settings["context"]["fileName"] = ["AGENTS.md"]


        # [REMOVED] SessionEnd hook for session_summarizer.py
        # The Scribe/Wiki Ingester should ONLY run on /reincarnate, not every single CLI exit.
        # It is explicitly called by .aim_core/handoff_pulse_generator.py during handoff.

        aim_hooks = {
            "AfterTool": [
                ("cognitive-mantra", "cognitive_mantra.py")
            ]
        }
        
        # Clear old A.I.M. hooks to prevent ghost executions (e.g. legacy SessionStart)
        settings["hooks"] = {}

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
    bootstrap_path = os.path.join(AIM_CORE_DIR, "bootstrap_brain.py")
    try:
        subprocess.run([VENV_PYTHON, bootstrap_path], check=True)
    except: print("[CRITICAL] Foundation Bootstrap failed.")

def init_workspace(args=None):
    if args is None: args = []
    is_interactive = "--headless" not in args

    print("
--- A.I.M. SOVEREIGN INSTALLER ---")
    
    # 1. Mechanical Provisioning (Folders & Settings)
    dirs = [".archive/raw", ".archive/history", ".archive/sync", ".archive/cartridges",
            ".continuity/private", ".continuity", "workstreams", "hooks", "scripts", "projects", "foundry", "core", "memory/wiki", "memory/wiki/_ingest", "planning-artifacts", ".gemini"]
    for d in dirs: os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)

    is_light_mode = "--light" in args
    register_hooks(is_light_mode)

    # Base settings and ignores
    files = {
        ".geminiignore": "workspace/
.archive/
",
        ".gemini/settings.json": '{
  "context": {
    "memoryBoundaryMarkers": ["AGENTS.md", ".git"],
    "discoveryMaxDirs": 0,
    "fileName": ["AGENTS.md"]
  }
}
',
        "memory/wiki/.gemini/settings.json": '{
  "context": {
    "memoryBoundaryMarkers": ["AGENT.md"],
    "discoveryMaxDirs": 0,
    "fileName": ["AGENT.md"],
    "ignoreGlobal": true
  }
}
'
    }
    
    for fp, content in files.items():
        full_path = os.path.join(BASE_DIR, fp)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        if not os.path.exists(full_path):
            with open(full_path, "w") as f: f.write(content)

    # 2. Spawn the Agentic Interview
    bootstrap_file = os.path.join(BASE_DIR, "BOOTSTRAP.md")
    if not os.path.exists(bootstrap_file):
        print(f"[ERROR] {bootstrap_file} not found. Please run the curl installer.")
        sys.exit(1)
        
    session_name = "aim_onboarding"
    
    check_cmd = subprocess.run(["tmux", "has-session", "-t", session_name], capture_output=True)
    if check_cmd.returncode == 0:
        print(f"[!] Onboarding session is already running.")
        print(f"Attach with: tmux attach-session -t {session_name}")
        return

    try:
        print("Spawning the Onboarding Architect...")
        subprocess.run(["tmux", "new-session", "-d", "-s", session_name, "-c", BASE_DIR, "gemini --yolo --prompt-file BOOTSTRAP.md"], check=True)
        print(f"[SUCCESS] The A.I.M. Architect has awakened in the background.")
        print(f"
Please attach to the session to complete your interview:")
        print(f"    tmux attach-session -t {session_name}
")
    except Exception as e:
        print(f"[ERROR] Failed to spawn onboarding agent: {e}")

if __name__ == "__main__":
    try: init_workspace(sys.argv)
    except KeyboardInterrupt: sys.exit(0)