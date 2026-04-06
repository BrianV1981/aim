#!/usr/bin/env python3
import os
import json
import sys
import time
import subprocess
import requests
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
import questionary

# --- DYNAMIC ROOT DISCOVERY ---
def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core", "CONFIG.json")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
src_dir = os.path.join(AIM_ROOT, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

from reasoning_utils import generate_reasoning
from aim_vault import get_key, set_key

CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

CONFIG = load_config()
console = Console()

tui_style = questionary.Style([
    ('qmark', 'fg:#FF9D00 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#5F819D bold'),
    ('pointer', 'fg:#FF9D00 bold'),
    ('highlighted', 'fg:#FF9D00 bold'),
    ('selected', 'fg:#5F819D'),
    ('separator', 'fg:#6C6C6C'),
    ('instruction', ''),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])

OPERATOR_TEMPLATE = """# OPERATOR.md - Operator Record
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
See core/OPERATOR_PROFILE.md
"""

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

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

def load_operator_identity_defaults():
    defaults = {
        "name": "Operator",
        "stack": "General",
        "style": "Direct",
        "physical": "N/A",
        "rules": "N/A",
        "goals": "N/A",
        "business": "None provided.",
        "grok_profile": "No profile provided."
    }

    gemini_path = os.path.join(AIM_ROOT, "GEMINI.md")
    if os.path.exists(gemini_path):
        with open(gemini_path, "r", encoding="utf-8") as f:
            gemini = f.read()
        defaults["name"] = _extract_md_field(gemini, "Operator", defaults["name"])
        defaults["exec_mode"] = _extract_md_field(gemini, "Execution Mode", "Autonomous")
        defaults["cog_level"] = _extract_md_field(gemini, "Cognitive Level", "Technical")
        defaults["concise_mode"] = _extract_md_field(gemini, "Conciseness", "False")
        defaults["lightweight_guardrails"] = "## ⚠️ EXPLICIT GUARDRAILS" in gemini
    else:
        defaults["exec_mode"] = "Autonomous"
        defaults["cog_level"] = "Technical"
        defaults["concise_mode"] = "False"
        defaults["lightweight_guardrails"] = False

    operator_path = os.path.join(AIM_ROOT, "core", "OPERATOR.md")
    if os.path.exists(operator_path):
        with open(operator_path, "r", encoding="utf-8") as f:
            operator = f.read()
        defaults["name"] = _extract_md_field(operator, "Name", defaults["name"])
        defaults["stack"] = _extract_md_field(operator, "Tech Stack", defaults["stack"])
        defaults["style"] = _extract_md_field(operator, "Style", defaults["style"])
        defaults["physical"] = _extract_md_field(operator, "Age/Height/Weight", defaults["physical"])
        defaults["rules"] = _extract_md_field(operator, "Life Rules", defaults["rules"])
        defaults["goals"] = _extract_md_field(operator, "Primary Goal", defaults["goals"])
        defaults["business"] = _extract_section(operator, "🏢 Business Intelligence", "🤖 Grok/Social Archetype", defaults["business"])

    operator_profile_path = os.path.join(AIM_ROOT, "core", "OPERATOR_PROFILE.md")
    if os.path.exists(operator_profile_path):
        with open(operator_profile_path, "r", encoding="utf-8") as f:
            defaults["grok_profile"] = f.read().strip() or defaults["grok_profile"]

    return defaults

def write_operator_documents(operator_path, operator_profile_path, values):
    operator_content = OPERATOR_TEMPLATE.format(
        name=values["name"],
        stack=values["stack"],
        style=values["style"],
        physical=values["physical"],
        rules=values["rules"],
        goals=values["goals"],
        business=values["business"]
    )
    with open(operator_path, "w", encoding="utf-8") as f:
        f.write(operator_content)
    with open(operator_profile_path, "w", encoding="utf-8") as f:
        f.write(values["grok_profile"] or "No profile provided.")

def update_gemini_behavior_file(gemini_path, exec_mode, cog_level, concise_mode, guardrails):
    if not os.path.exists(gemini_path):
        return False

    with open(gemini_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = re.sub(r'- \*\*Execution Mode:\*\*.*', f'- **Execution Mode:** {exec_mode}', content)
    content = re.sub(r'- \*\*Cognitive Level:\*\*.*', f'- **Cognitive Level:** {cog_level}', content)
    content = re.sub(r'- \*\*Conciseness:\*\*.*', f'- **Conciseness:** {concise_mode}', content)

    if "- **Execution Mode:**" not in content and "## 1. IDENTITY & PRIMARY DIRECTIVE" in content:
        content = content.replace(
            "## 1. IDENTITY & PRIMARY DIRECTIVE",
            f"## 1. IDENTITY & PRIMARY DIRECTIVE\n- **Execution Mode:** {exec_mode}\n- **Cognitive Level:** {cog_level}\n- **Conciseness:** {concise_mode}"
        )

    content = re.sub(r'- \*\*WARNING:\*\* Behavioral guardrails skipped.*', '', content)
    content = re.sub(r'## ⚠️ EXPLICIT GUARDRAILS.*', '', content, flags=re.DOTALL)
    content = content.strip() + "\n" + guardrails

    with open(gemini_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def test_provider(provider, model, endpoint, brain_type="default_reasoning", auth_type="API Key"):
    """Validates the provider configuration with a simple prompt."""
    with console.status(f"[bold blue]Testing {provider} ({model})...[/bold blue]"):
        try:
            # We create a temporary config for the test
            temp_config = CONFIG.copy()
            if 'tiers' not in temp_config['models']: temp_config['models']['tiers'] = {}
            temp_config['models']['tiers'][brain_type] = {
                "provider": provider,
                "model": model,
                "endpoint": endpoint,
                "auth_type": auth_type
            }

            # Pass temp_config to generate_reasoning. Use a 60s timeout so health checks for flagship models pass.
            resp = generate_reasoning("Respond with 'OK'", brain_type=brain_type, config=temp_config, timeout=60)            
            if "Error" in resp or "Exception" in resp:
                return False, resp
            # Strict validation: The prompt explicitly asked the model to "Respond with 'OK'".
            # We strictly look for that string to prevent short error messages from falsely passing.
            if "OK" in resp or "ok" in resp.lower() or "Ok" in resp:
                return True, resp
            return False, f"Unexpected response shape: {resp}"
        except Exception as e:
            return False, str(e)

def setup_secrets_menu():
    while True:
        os.system('clear')
        rprint(Panel("[bold cyan]A.I.M. SECRET VAULT[/bold cyan]\nSovereign Credential Management"))
        
        common_keys = [
            ("google", "google-api-key"),
            ("openrouter", "openrouter-api-key"),
            ("openai", "openai-api-key"),
            ("anthropic", "anthropic-api-key")
        ]
        
        table = Table()
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")
        
        for provider, key_name in common_keys:
            val = get_key("aim-system", key_name)
            status = "[bold green]SET[/bold green]" if val else "[red]NOT SET[/red]"
            table.add_row(provider.capitalize(), status)
        
        rprint(table)
        
        choice = questionary.select(
            "Manage Secrets:",
            choices=[f"Set {k.capitalize()} Key" for k, _ in common_keys] + ["Back"]
        ).ask()
        
        if choice == "Back": break
        
        provider = choice.split()[1].lower()
        key_name = next(kn for p, kn in common_keys if p == provider)
        set_key("aim-system", key_name)

def setup_cognitive_tier(tier_name):
    rprint(Panel(f"[bold blue]Tier Configuration: {tier_name.upper()}[/bold blue]"))
    
    provider = questionary.select(
        "Select Provider:",
        choices=["google", "openrouter", "anthropic", "codex-cli", "local (ollama)", "openai-compat"]
    ).ask()
    
    auth_type = "api_key"
    if provider in ["google", "codex-cli"]:
        auth_type = questionary.select(
            "Authentication Method:",
            choices=["API Key", "OAuth (System Default / CLI)"]
        ).ask()
    
    model = ""
    endpoint = ""
    key_name = None

    if provider == "google":
        selection_mode = questionary.select(
            "Select Mode:",
            choices=["All Models (Full List)", "Other (Manual)"]
        ).ask()
        
        if selection_mode == "All Models (Full List)":
            model_choices = [
                "gemini-3.1-pro-preview",
                "gemini-3-flash-preview",
                "gemini-2.5-pro",
                "gemini-2.5-flash",
                "gemini-2.5-flash-lite"
            ]
            model = questionary.select("Select Google Model:", choices=model_choices).ask()
        else:
            model = questionary.text("Enter Google Model ID (e.g., gemini-3.1-pro-preview):").ask()            
        endpoint = "https://generativelanguage.googleapis.com"
        if "API Key" in auth_type:
            key_name = "google-api-key"
        else:
            # REGRESSION GUARD: Do NOT trigger `subprocess.run(["gemini", "login"])` here.
            # The Gemini CLI intercepts it and traps the user in an interactive chat session,
            # requiring a double Ctrl+C to escape back to the TUI. (See Issue #24)
            rprint("[cyan]Delegating authentication natively to the Gemini CLI...[/cyan]")
            rprint("[yellow]Please ensure you are authenticated by running 'gemini login' in a separate terminal.[/yellow]")
            key_name = None
    elif provider == "codex-cli":
        model_choices = ["gpt-5.4", "gpt-5.4-mini", "gpt-5.3-codex", "gpt-5.3-codex-spark", "Other (Manual)"]
        model = questionary.select("Select Codex Model:", choices=model_choices).ask()
        if model == "Other (Manual)":
            model = questionary.text("Enter Codex Model ID (e.g., gpt-5.4):").ask()
        if "OAuth" in auth_type:
            rprint("[cyan]Triggering Codex CLI Login...[/cyan]")
            try: subprocess.run(["codex", "login"], check=True)
            except: rprint("[red]Failed to trigger 'codex login'. Is it installed?[/red]")
        else:
            key_name = "openai-api-key"
    elif provider == "openrouter":
        model_choices = [
            "anthropic/claude-3.5-sonnet", 
            "google/gemini-2.0-flash-001",
            "deepseek/deepseek-r1",
            "openai/gpt-4o",
            "meta-llama/llama-3.3-70b-instruct",
            "Other (Manual)"
        ]
        model = questionary.select("Select OpenRouter Model:", choices=model_choices).ask()
        if model == "Other (Manual)":
            model = questionary.text("Enter OpenRouter Model ID (e.g., provider/model):").ask()
        endpoint = "https://openrouter.ai/api/v1"
        key_name = "openrouter-api-key"
    elif provider == "anthropic":
        model_choices = ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229", "Other (Manual)"]
        model = questionary.select("Select Anthropic Model:", choices=model_choices).ask()
        if model == "Other (Manual)":
            model = questionary.text("Enter Anthropic Model ID:").ask()
        endpoint = "https://api.anthropic.com/v1/messages"
        key_name = "anthropic-api-key"
    elif provider == "local (ollama)":
        model = questionary.text("Ollama Model (e.g., gemma4:e4b):", default="gemma4:e4b").ask()
        if not model or not model.strip(): model = "gemma4:e4b"
        endpoint = questionary.text("Ollama Endpoint:", default="http://localhost:11434/api/generate").ask()
        if not endpoint or not endpoint.strip(): endpoint = "http://localhost:11434/api/generate"
        key_name = None
    else: # openai-compat
        model = questionary.text("Model Name:").ask()
        endpoint = questionary.text("Endpoint URL:").ask()
        key_name = "openai-api-key"

    # Verify key exists
    if key_name and not get_key("aim-system", key_name):
        rprint(f"[yellow]Warning: {key_name} is not set in the vault.[/yellow]")
        if questionary.confirm("Set it now?").ask():
            set_key("aim-system", key_name)

    # Test
    success, msg = test_provider(provider.replace(" (ollama)", ""), model, endpoint, tier_name, auth_type)
    if success:
        rprint(f"[green]Test Success: {msg}[/green]")
        if 'tiers' not in CONFIG['models']: CONFIG['models']['tiers'] = {}
        CONFIG['models']['tiers'][tier_name] = {
            "provider": provider.replace(" (ollama)", ""),
            "model": model,
            "endpoint": endpoint,
            "auth_type": auth_type
        }
        save_config(CONFIG)
    else:
        rprint(f"[red]Test Failed: {msg}[/red]")
        if questionary.confirm("Save anyway?").ask():
            if 'tiers' not in CONFIG['models']: CONFIG['models']['tiers'] = {}
            CONFIG['models']['tiers'][tier_name] = {
                "provider": provider.replace(" (ollama)", ""),
                "model": model,
                "endpoint": endpoint,
                "auth_type": auth_type
            }
            save_config(CONFIG)

def mcp_server_menu():
    while True:
        os.system('clear')
        rprint(Panel("[bold green]A.I.M. MCP SERVER CONTROL[/bold green]\nModel Context Protocol Integration"))
        
        # Check if server is running (rudimentary check via pgrep)
        try:
            subprocess.run(["pgrep", "-f", "src/mcp_server.py"], check=True, capture_output=True)
            status = "[bold green]ONLINE (Background)[/bold green]"
        except subprocess.CalledProcessError:
            status = "[bold red]OFFLINE[/bold red]"
            
        rprint(f"Server Status: {status}\n")
        rprint("[cyan]Connection String for IDEs (Cursor/VSCode):[/cyan]")
        rprint(f"[yellow]{AIM_ROOT}/venv/bin/python3 {AIM_ROOT}/src/mcp_server.py[/yellow]\n")
        
        choice = questionary.select(
            "MCP Actions:",
            choices=[
                "1. Launch MCP Inspector (Web UI Test)",
                "2. View MCP Client Setup Instructions",
                "3. Back"
            ]
        ).ask()
        
        if choice == "3. Back": break
        
        if "1." in choice:
            rprint("[cyan]Launching FastMCP Inspector... (Press Ctrl+C to exit)[/cyan]")
            fastmcp_bin = os.path.join(AIM_ROOT, "venv/bin/fastmcp")
            try:
                subprocess.run([fastmcp_bin, "inspector", os.path.join(AIM_ROOT, "src/mcp_server.py")])
            except KeyboardInterrupt: pass
        elif "2." in choice:
            rprint("\n[bold cyan]--- Claude Desktop Setup ---[/bold cyan]")
            rprint("Add the following to your claude_desktop_config.json:")
            config_example = {
                "mcpServers": {
                    "aim-engram": {
                        "command": os.path.join(AIM_ROOT, "venv/bin/python3"),
                        "args": [os.path.join(AIM_ROOT, "src/mcp_server.py")]
                    }
                }
            }
            rprint(f"[yellow]{json.dumps(config_example, indent=2)}[/yellow]")
            rprint("\n[bold cyan]--- Cursor / VS Code Setup ---[/bold cyan]")
            rprint("1. Open MCP settings in your IDE.")
            rprint("2. Add a new 'stdio' server.")
            rprint(f"3. Command: [yellow]{os.path.join(AIM_ROOT, 'venv/bin/python3')}[/yellow]")
            rprint(f"4. Args: [yellow]{os.path.join(AIM_ROOT, 'src/mcp_server.py')}[/yellow]")
            input("\nPress Enter to continue...")

def update_operator_profile():
    defaults = load_operator_identity_defaults()
    rprint(Panel("[bold blue]Operator Profile & Behavioral Guardrails[/bold blue]"))

    name = questionary.text("Operator Name:", default=defaults["name"]).ask() or defaults["name"]
    stack = questionary.text("Core Tech Stack:", default=defaults["stack"]).ask() or defaults["stack"]
    style = questionary.text("Working Style:", default=defaults["style"]).ask() or defaults["style"]
    physical = questionary.text("Metrics (Age/Height/Weight):", default=defaults["physical"]).ask() or defaults["physical"]
    rules = questionary.text("Life Rules/Principles:", default=defaults["rules"]).ask() or defaults["rules"]
    goals = questionary.text("Primary Mission/Life Goal:", default=defaults["goals"]).ask() or defaults["goals"]
    business = questionary.text("Business Info:", default=defaults["business"]).ask() or defaults["business"]
    grok_profile = questionary.text("Operator Persona / Grok Profile:", default=defaults["grok_profile"]).ask() or defaults["grok_profile"]
    
    lvl = questionary.select(
        "Grammar & Explanation Level:",
        choices=[
            "1. Novice (Explain concepts clearly with analogies)",
            "2. Enthusiast (Standard professional level)",
            "3. Technical (Assume deep domain expertise)"
        ],
        default=f"3. {defaults['cog_level']} (Assume deep domain expertise)" if defaults["cog_level"] == "Technical" else None
    ).ask()
    cog_level = "Novice" if "Novice" in lvl else ("Enthusiast" if "Enthusiast" in lvl else "Technical")
    
    tkn = questionary.confirm(
        "Enable Extreme Conciseness (Say as little as possible)?",
        default=defaults["concise_mode"] == "True"
    ).ask()
    concise_mode = "True" if tkn else "False"
    
    ex = questionary.select(
        "Execution Mode:",
        choices=[
            "1. Autonomous (Proactive, execute and fix directly)",
            "2. Cautious (Propose plans, wait for human approval)"
        ],
        default="1. Autonomous (Proactive, execute and fix directly)" if defaults["exec_mode"] == "Autonomous" else "2. Cautious (Propose plans, wait for human approval)"
    ).ask()
    exec_mode = "Cautious" if "Cautious" in ex else "Autonomous"
    
    tier = questionary.select(
        "Target Model Intelligence:",
        choices=[
            "1. Flagship (Lean prompt, saves tokens)",
            "2. Local/Lightweight (Explicit strict guardrails)"
        ],
        default="2. Local/Lightweight (Explicit strict guardrails)" if defaults["lightweight_guardrails"] else "1. Flagship (Lean prompt, saves tokens)"
    ).ask()
    
    guardrails = ""
    if "Lightweight" in tier:
        cli_name = os.path.basename(AIM_ROOT)
        guardrails = f"""
## ⚠️ EXPLICIT GUARDRAILS (Lightweight Mode Active)
1. **NO TITLE HALLUCINATION:** When you run `{cli_name} map`, you are only seeing titles. You MUST NOT guess the contents. You MUST run `{cli_name} search` to read the actual text.
2. **PARALLEL TOOLS:** Do not use tools sequentially. If you need to read 3 files, request all 3 files in a single tool turn.
3. **DESTRUCTIVE MEMORY:** When tasked with updating memory, you MUST delete stale facts. Do not endlessly concatenate data.
4. **PATH STRICTNESS:** Do not guess file paths. Use the exact absolute paths provided in your environment.
"""
    
    gemini_path = os.path.join(AIM_ROOT, "GEMINI.md")
    operator_path = os.path.join(AIM_ROOT, "core", "OPERATOR.md")
    operator_profile_path = os.path.join(AIM_ROOT, "core", "OPERATOR_PROFILE.md")

    if not update_gemini_behavior_file(gemini_path, exec_mode, cog_level, concise_mode, guardrails):
        rprint("[red]Error: GEMINI.md not found.[/red]")
    else:
        write_operator_documents(
            operator_path,
            operator_profile_path,
            {
                "name": name,
                "stack": stack,
                "style": style,
                "physical": physical,
                "rules": rules,
                "goals": goals,
                "business": business,
                "grok_profile": grok_profile
            }
        )
        rprint("[green]GEMINI.md, OPERATOR.md, and OPERATOR_PROFILE.md successfully updated.[/green]")
        
    input("\nPress Enter to continue...")

def update_agent_persona():
    os.system('clear')
    rprint(Panel("[bold cyan]Agent Persona Configuration[/bold cyan]\nSelect a specialized mandate for your agent."))
    
    cli_name = os.path.basename(AIM_ROOT)
    
    personas = {
        "Generic Sovereign Agent": f"You are a Senior Sovereign Agent. DO NOT hallucinate. You must follow this 3-step loop:\n1. **Search:** Use `{cli_name} search \"<keyword>\"` to pull documentation from the Engram DB BEFORE writing code.\n2. **Plan:** Write a markdown To-Do list outlining your technical strategy.\n3. **Execute:** Methodically execute the To-Do list step-by-step. Prove your code works empirically via TDD.",
        "Frontend Architect": f"You are a Frontend Architect and UI/UX Artist. DO NOT hallucinate. You must follow this 3-step loop:\n1. **Search:** Use `{cli_name} search` to verify exact UI documentation (Tailwind v4, Next.js 15, React 19) and `{cli_name} search \"UI UX Design System\"` for aesthetic guidelines.\n2. **Plan:** Write a markdown To-Do list outlining your component architecture and aesthetic goals.\n3. **Execute:** Methodically execute the To-Do list step-by-step. Write rendering tests and adhere to TDD.",
        "Fintech Backend Engineer": f"You are a Fintech Backend Engineer. DO NOT hallucinate APIs. You must follow this 3-step loop:\n1. **Search:** Use `{cli_name} search` to pull the exact constraints for Stripe Webhooks or Supabase SSR from the Engram DB.\n2. **Plan:** Write a markdown To-Do list outlining your database schema and routing logic.\n3. **Execute:** Methodically execute the To-Do list step-by-step. Prevent security vulnerabilities using strict TDD.",
        "Web3 Smart Contract Auditor": f"You are a Senior Web3 Auditor. DO NOT hallucinate cryptography. You must follow this 3-step loop:\n1. **Search:** Use `{cli_name} search` to verify exact documentation for Solana Anchor and Token Extensions.\n2. **Plan:** Write a markdown To-Do list outlining your architectural strategy and re-entrancy protections.\n3. **Execute:** Methodically execute the To-Do list step-by-step. Write exhaustive security tests before deploying.",
        "Custom...": ""
    }
    
    choice = questionary.select(
        "Select Persona:",
        choices=list(personas.keys()) + ["Cancel"]
    ).ask()
    
    if choice == "Cancel" or not choice:
        return
        
    mandate = personas[choice]
    if choice == "Custom...":
        mandate = questionary.text("Enter custom mandate (e.g., 'You are a Python Data Scientist...'):").ask()
        if not mandate: return

    gemini_path = os.path.join(AIM_ROOT, "GEMINI.md")
    if os.path.exists(gemini_path):
        with open(gemini_path, 'r') as f: content = f.read()
        import re
        # Safely replace the mandate block
        new_content = re.sub(r'> \*\*MANDATE:\*\*.*?(?=\n## 1\.)', f'> **MANDATE:** {mandate}\n\n', content, flags=re.DOTALL)
        if new_content == content:
            rprint("[yellow]Could not find standard MANDATE block. Appending to top.[/yellow]")
            new_content = f"> **MANDATE:** {mandate}\n\n" + content
            
        with open(gemini_path, 'w') as f: f.write(new_content)
        rprint(f"[green]Persona updated to: {choice}[/green]")
    else:
        rprint("[red]Error: GEMINI.md not found.[/red]")
    
    input("\nPress Enter to continue...")

def configure_cognitive_mantra():
    """Configures the Anti-Drift Shield (Cognitive Mantra) thresholds."""
    if 'cognitive_mantra' not in CONFIG['settings']:
        CONFIG['settings']['cognitive_mantra'] = {"enabled": True, "whisper_interval": 25, "mantra_interval": 50}
    
    current = CONFIG['settings']['cognitive_mantra']
    
    rprint("\n[cyan]--- Cognitive Mantra (Anti-Drift Shield) ---[/cyan]")
    rprint("This background hook tracks autonomous tool calls to prevent 'Lost in the Middle' context collapse.")
    rprint("The [yellow]Whisper[/yellow] is a silent reminder injected into the context window.")
    rprint("The [red]Mantra[/red] halts the agent and forces it to physically recite its system rules.")
    
    enabled = questionary.confirm("Enable Cognitive Mantra?", default=current.get("enabled", True)).ask()
    
    if enabled:
        whisper = questionary.text(
            "Subconscious Whisper Interval (Tool Calls):", 
            default=str(current.get("whisper_interval", 25))
        ).ask()
        
        mantra = questionary.text(
            "Full Mantra Recital Interval (Tool Calls):", 
            default=str(current.get("mantra_interval", 50))
        ).ask()
        
        if whisper and whisper.isdigit() and mantra and mantra.isdigit():
            CONFIG['settings']['cognitive_mantra'] = {
                "enabled": True,
                "whisper_interval": int(whisper),
                "mantra_interval": int(mantra)
            }
            save_config(CONFIG)
            rprint("[bold green]Cognitive Mantra settings updated![/bold green]")
    else:
        CONFIG['settings']['cognitive_mantra']['enabled'] = False
        save_config(CONFIG)
        rprint("[yellow]Cognitive Mantra disabled.[/yellow]")


def main_menu():
    # Cache for health status: {tier: (status_text, timestamp)}
    health_cache = {}

    while True:
        os.system('clear')
        rprint(Panel("[bold green]A.I.M. SOVEREIGN COCKPIT v2.0[/bold green]\nCognitive Orchestration Layer"))
        
        table = Table(title="Cognitive Status & Health")
        table.add_column("Tier", style="cyan")
        table.add_column("Provider", style="magenta")
        table.add_column("Model", style="yellow")
        table.add_column("Health", justify="center")
        table.add_column("Diagnostics", style="dim")
        
        tiers_config = CONFIG.get('models', {}).get('tiers', {})
        tiers = ["default_reasoning", "tier1"]
        tier_labels = {
            "default_reasoning": "Primary Brain",
            "tier1": "Single-Shot Memory Compiler"
        }
        for t in tiers:
            details = tiers_config.get(t, {"provider": "NOT SET", "model": "N/A"})
            status_indicator, diag_msg = health_cache.get(t, ("[white]○[/white]", ""))
            table.add_row(tier_labels.get(t, t), details['provider'], details['model'], status_indicator, diag_msg)
        rprint(table)
        
        choice = questionary.select(
            "Main Settings:",
            choices=[
                "1. Run Cognitive Health Check",
                "2. Manage Secret Vault",
                "3. Configure Default Brain",
                "4. Configure Single-Shot Memory Compiler",
                "5. Manage MCP Server",
                "6. Update Operator Profile & Behavior",
                "7. Update Obsidian Vault Path",
                "8. Configure Cognitive Architecture",
                "9. Archive Retention",
                "10. Set Agent Persona",
                "11. Configure Cognitive Mantra",
                "12. Configure LAST_SESSION_FLIGHT_RECORDER.md",
                "13. Reincarnation Protocol",
                "14. BitTorrent Swarm Integration",
                "15. Exit"
            ],
            style=tui_style
        ).ask()

        if not choice or choice.startswith("15. Exit"): break
        
        if choice.startswith("1."):
            for i, t in enumerate(tiers):
                details = tiers_config.get(t)
                if not details or details.get('provider') == "NOT SET":
                    health_cache[t] = ("[red]●[/red]", "NOT SET") 
                    continue
                success, msg = test_provider(details['provider'], details['model'], details.get('endpoint'), t, details.get('auth_type', 'API Key'))
                if success:
                    health_cache[t] = ("[bold green]●[/bold green]", "OK")
                elif "[ERROR: CAPACITY_LOCKOUT]" in str(msg):
                    health_cache[t] = ("[bold yellow]⚠[/bold yellow]", "Server Capacity Exhausted (Google-side). Try again later.")
                else:
                    health_cache[t] = ("[bold red]●[/bold red]", str(msg)[:60])
                
                # Prevent API rate limits when testing multiple models back-to-back
                if i < len(tiers) - 1:
                    import time; time.sleep(2)
        elif choice.startswith("2."): setup_secrets_menu()
        elif choice.startswith("3."): setup_cognitive_tier("default_reasoning")
        elif choice.startswith("4."):
            setup_cognitive_tier("tier1")
        elif choice.startswith("5."): mcp_server_menu()
        elif choice.startswith("6."): update_operator_profile()
        elif choice.startswith("7."):
            path = questionary.text("Obsidian Vault Path:", default=CONFIG['settings'].get('obsidian_vault_path', "")).ask()
            if path is not None:
                CONFIG['settings']['obsidian_vault_path'] = path
                save_config(CONFIG)
        elif choice.startswith("8."):
            rprint("\n[cyan]--- Configure Cognitive Architecture (Decoupled Brain) ---[/cyan]")
            rprint("A.I.M. allows you to offload heavy LLM memory distillation to a second computer (Subconscious Node).")
            rprint("This keeps your primary laptop (Frontline Agent) lightning fast and saves battery/tokens,")
            rprint("while your 2nd PC does the heavy architectural distillation in the background.\n")
            mode = questionary.select(
                "Select Cognitive Architecture Mode:",
                choices=[
                    "monolithic (Default) - Your machine handles all coding and memory distillation locally.",
                    "frontline (Laptop) - Pure speed. Bypasses memory distillation and drops transcripts to your Obsidian Vault.",
                    "subconscious (Server) - Background brain. Monitors Obsidian Vault and distills memory for the frontline agent.",
                    "Cancel"
                ]
            ).ask()
            if mode and mode != "Cancel":
                val = mode.split(" ")[0]
                if val in ["frontline", "subconscious"]:
                    vault_path = CONFIG.get('settings', {}).get('obsidian_vault_path', "")
                    if not vault_path:
                        rprint("[bold red]WARNING: You must configure an Obsidian Vault Path (Menu Option 7) before enabling a decoupled mode![/bold red]")
                        import time; time.sleep(2)
                        continue
                if 'settings' not in CONFIG: CONFIG['settings'] = {}
                CONFIG['settings']['cognitive_mode'] = val
                save_config(CONFIG)
                rprint(f"[green]Cognitive Architecture set to {val.upper()}.[/green]")
                import time; time.sleep(1.5)
        elif choice.startswith("9."):
            rprint("[cyan]Set retention days for raw logs and proposals.[/cyan]")
            rprint("[yellow]Enter '0' to deactivate automatic purge.[/yellow]")
            days = questionary.text("Retention Days:", default=str(CONFIG['settings'].get('archive_retention_days', 0))).ask()
            if days and days.isdigit():
                CONFIG['settings']['archive_retention_days'] = int(days)
                save_config(CONFIG)
        elif choice.startswith("10."):
            update_agent_persona()
        elif choice.startswith("11."):
            configure_cognitive_mantra()
        elif choice.startswith("12."):
            rprint("\n[cyan]--- Configure LAST_SESSION_FLIGHT_RECORDER.md ---[/cyan]")
            rprint("This determines the maximum number of lines preserved in `LAST_SESSION_FLIGHT_RECORDER.md`.")
            rprint("Decrease this number if you frequently hit max token limits on context handoffs (e.g., 1000).")
            rprint("Increase this number (up to 1990) if your agent needs deeper historical memory of the active session.")
            rprint("Set this to [bold yellow]0[/bold yellow] to preserve the FULL session history (No truncation).")
            current_tail = str(CONFIG.get('settings', {}).get('handoff_context_lines', 0))
            tail_input = questionary.text("Flight Recorder (Max Lines Buffer, 0 for Full):", default=current_tail).ask()

            if tail_input and tail_input.isdigit():
                if 'settings' not in CONFIG:
                    CONFIG['settings'] = {}
                CONFIG['settings']['handoff_context_lines'] = int(tail_input)
                save_config(CONFIG)
                if tail_input == "0":
                    rprint("[green]LAST_SESSION_FLIGHT_RECORDER.md successfully set to FULL SESSION.[/green]")
                else:
                    rprint(f"[green]LAST_SESSION_FLIGHT_RECORDER.md successfully set to {tail_input} lines.[/green]")
                import time; time.sleep(1.5)

        elif choice.startswith("13."):
            rprint("\n[cyan]--- The Reincarnation Protocol ---[/cyan]")
            rprint("When enabled, the agent will automatically spawn a new tmux terminal and hand off its context when the context window fills.")
            current_rebirth = CONFIG.get('settings', {}).get('auto_rebirth', False)
            toggle = questionary.confirm("Enable Auto-Rebirth?", default=current_rebirth).ask()
            if toggle is not None:
                if 'settings' not in CONFIG:
                    CONFIG['settings'] = {}
                CONFIG['settings']['auto_rebirth'] = toggle
                save_config(CONFIG)
                status = "ON" if toggle else "OFF"
                rprint(f"[green]Auto-Rebirth successfully turned {status}.[/green]")
                import time; time.sleep(1.5)

        elif choice.startswith("14."):
            rprint("\n[cyan]--- BitTorrent Swarm Integration ---[/cyan]")
            rprint("When enabled, the agent will peer with the Sovereign Swarm to share and retrieve engrams.")
            if 'settings' not in CONFIG:
                CONFIG['settings'] = {}
            current_swarm = CONFIG['settings'].get('swarm_enabled', False)
            toggle = questionary.confirm("Enable Swarm Peering?", default=current_swarm).ask()
            if toggle is not None:
                CONFIG['settings']['swarm_enabled'] = toggle
                if toggle:
                    CONFIG['settings']['max_download_speed'] = questionary.text("Max Download Speed (e.g., 0 for unlimited, 5M, 500K):", default=str(CONFIG['settings'].get('max_download_speed', '0'))).ask()
                    CONFIG['settings']['seeding_ratio'] = float(questionary.text("Seeding Ratio (e.g., 1.0):", default=str(CONFIG['settings'].get('seeding_ratio', 1.0))).ask() or 1.0)
                    CONFIG['settings']['rpc_port'] = int(questionary.text("RPC Port (default: 6800):", default=str(CONFIG['settings'].get('rpc_port', 6800))).ask() or 6800)
                save_config(CONFIG)
                status = "ON" if toggle else "OFF"
                rprint(f"[green]Swarm Peering successfully turned {status}.[/green]")
                import time; time.sleep(1.5)


if __name__ == "__main__":
    try: main_menu()
    except KeyboardInterrupt: sys.exit(0)
