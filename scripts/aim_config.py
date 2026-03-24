#!/usr/bin/env python3
import os
import json
import sys
import time
import subprocess
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
import questionary

# --- VENV BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

from config_utils import CONFIG, AIM_ROOT
from reasoning_utils import generate_reasoning
from aim_vault import get_key, set_key

console = Console()
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

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
            
            # Pass temp_config to generate_reasoning
            resp = generate_reasoning("Respond with 'OK'", brain_type=brain_type, config=temp_config)
            
            if "OK" in resp or len(resp) < 50: # Simple validation
                return True, resp
            return False, resp
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
            choices=["Presets (Fast/Thinking/Pro)", "All Models (Full List)", "Other (Manual)"]
        ).ask()
        
        if selection_mode == "Presets (Fast/Thinking/Pro)":
            preset = questionary.select(
                "Choose Preset:",
                choices=[
                    "Fast (Gemini 3.1 Flash)",
                    "Thinking (Gemini 3.1 Pro Thinking)",
                    "Pro (Gemini 3.1 Pro)"
                ]
            ).ask()
            if "Fast" in preset: model = "gemini-3.1-flash-preview"
            elif "Thinking" in preset: model = "gemini-3.1-pro-thinking"
            else: model = "gemini-3.1-pro-preview"
        elif selection_mode == "All Models (Full List)":
            model_choices = [
                "gemini-3.1-pro-preview",
                "gemini-3.1-flash-preview",
                "gemini-3.1-pro-thinking",
                "gemini-3-pro-preview",
                "gemini-3-flash-preview",
                "gemini-2.5-pro",
                "gemini-2.5-flash",
                "gemini-2.5-flash-lite",
                "gemini-2.0-flash-exp",
                "gemini-1.5-pro"
            ]
            model = questionary.select("Select Google Model:", choices=model_choices).ask()
        else:
            model = questionary.text("Enter Google Model ID (e.g., gemini-3.1-pro-preview):").ask()            
        endpoint = "https://generativelanguage.googleapis.com"
        if "API Key" in auth_type:
            key_name = "google-api-key"
        else:
            rprint("[cyan]Delegating authentication natively to the Gemini CLI...[/cyan]")
            key_name = None
    elif provider == "codex-cli":
        model_choices = ["gpt-5.4", "gpt-5.4-mini", "gpt-5.4-pro", "gpt-5.3-codex", "gpt-5.3-codex-spark", "gpt-4o", "Other (Manual)"]
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
        model = questionary.text("Ollama Model (e.g., llama3):", default="llama3").ask()
        if not model or not model.strip(): model = "llama3"
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
    rprint(Panel("[bold blue]Behavioral & Cognitive Guardrails[/bold blue]"))
    
    lvl = questionary.select(
        "Grammar & Explanation Level:",
        choices=[
            "1. Novice (Explain concepts clearly with analogies)",
            "2. Enthusiast (Standard professional level)",
            "3. Technical (Assume deep domain expertise)"
        ]
    ).ask()
    cog_level = "Novice" if "Novice" in lvl else ("Enthusiast" if "Enthusiast" in lvl else "Technical")
    
    tkn = questionary.confirm("Enable Extreme Conciseness (Say as little as possible)?").ask()
    concise_mode = "True" if tkn else "False"
    
    ex = questionary.select(
        "Execution Mode:",
        choices=[
            "1. Autonomous (Proactive, execute and fix directly)",
            "2. Cautious (Propose plans, wait for human approval)"
        ]
    ).ask()
    exec_mode = "Cautious" if "Cautious" in ex else "Autonomous"
    
    tier = questionary.select(
        "Target Model Intelligence:",
        choices=[
            "1. Flagship (Lean prompt, saves tokens)",
            "2. Local/Lightweight (Explicit strict guardrails)"
        ]
    ).ask()
    
    guardrails = ""
    if "Lightweight" in tier:
        guardrails = """
## ⚠️ EXPLICIT GUARDRAILS (Lightweight Mode Active)
1. **NO TITLE HALLUCINATION:** When you run `aim map`, you are only seeing titles. You MUST NOT guess the contents. You MUST run `aim search` to read the actual text.
2. **PARALLEL TOOLS:** Do not use tools sequentially. If you need to read 3 files, request all 3 files in a single tool turn.
3. **DESTRUCTIVE MEMORY:** When tasked with updating memory, you MUST delete stale facts. Do not endlessly concatenate data.
4. **PATH STRICTNESS:** Do not guess file paths. Use the exact absolute paths provided in your environment.
"""
    
    # Read and update GEMINI.md
    gemini_path = os.path.join(AIM_ROOT, "GEMINI.md")
    if os.path.exists(gemini_path):
        with open(gemini_path, 'r') as f: content = f.read()
        import re
        content = re.sub(r'- \*\*Execution Mode:\*\*.*', f'- **Execution Mode:** {exec_mode}', content)
        content = re.sub(r'- \*\*Cognitive Level:\*\*.*', f'- **Cognitive Level:** {cog_level}', content)
        content = re.sub(r'- \*\*Conciseness:\*\*.*', f'- **Conciseness:** {concise_mode}', content)
        
        # Fallbacks if the user manually deleted the lines
        if f"- **Execution Mode:**" not in content and "## 1. IDENTITY & PRIMARY DIRECTIVE" in content:
            content = content.replace("## 1. IDENTITY & PRIMARY DIRECTIVE", f"## 1. IDENTITY & PRIMARY DIRECTIVE\n- **Execution Mode:** {exec_mode}\n- **Cognitive Level:** {cog_level}\n- **Conciseness:** {concise_mode}")

        content = re.sub(r'- \*\*WARNING:\*\* Behavioral guardrails skipped.*', '', content)
        
        # Remove existing guardrails if present, then append if needed
        content = re.sub(r'## ⚠️ EXPLICIT GUARDRAILS.*', '', content, flags=re.DOTALL)
        content = content.strip() + "\n" + guardrails
        
        with open(gemini_path, 'w') as f: f.write(content)
        rprint("[green]GEMINI.md successfully updated.[/green]")
    else:
        rprint("[red]Error: GEMINI.md not found.[/red]")
        
    input("\nPress Enter to continue...")

def update_agent_persona():
    os.system('clear')
    rprint(Panel("[bold cyan]Agent Persona Configuration[/bold cyan]\nSelect a specialized mandate for your agent."))
    
    personas = {
        "Generic Sovereign Agent": "You are a Senior Engineering Exoskeleton. DO NOT hallucinate. You must follow this 3-step loop:\n1. **Search:** Use `aim search \"<keyword>\"` to pull documentation from the Engram DB BEFORE writing code.\n2. **Plan:** Write a markdown To-Do list outlining your technical strategy.\n3. **Execute:** Methodically execute the To-Do list step-by-step. Prove your code works empirically via TDD.",
        "Frontend Architect": "You are a Frontend Architect and UI/UX Artist. DO NOT hallucinate. You must follow this 3-step loop:\n1. **Search:** Use `aim search` to verify exact UI documentation (Tailwind v4, Next.js 15, React 19) and `aim search \"UI UX Design System\"` for aesthetic guidelines.\n2. **Plan:** Write a markdown To-Do list outlining your component architecture and aesthetic goals.\n3. **Execute:** Methodically execute the To-Do list step-by-step. Write rendering tests and adhere to TDD.",
        "Fintech Backend Engineer": "You are a Fintech Backend Engineer. DO NOT hallucinate APIs. You must follow this 3-step loop:\n1. **Search:** Use `aim search` to pull the exact constraints for Stripe Webhooks or Supabase SSR from the Engram DB.\n2. **Plan:** Write a markdown To-Do list outlining your database schema and routing logic.\n3. **Execute:** Methodically execute the To-Do list step-by-step. Prevent security vulnerabilities using strict TDD.",
        "Web3 Smart Contract Auditor": "You are a Senior Web3 Auditor. DO NOT hallucinate cryptography. You must follow this 3-step loop:\n1. **Search:** Use `aim search` to verify exact documentation for Solana Anchor and Token Extensions.\n2. **Plan:** Write a markdown To-Do list outlining your architectural strategy and re-entrancy protections.\n3. **Execute:** Methodically execute the To-Do list step-by-step. Write exhaustive security tests before deploying.",
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
        for t in ["default_reasoning", "librarian", "chancellor", "dean"]:
            details = tiers_config.get(t, {"provider": "NOT SET", "model": "N/A"})
            status_indicator, diag_msg = health_cache.get(t, ("[white]○[/white]", ""))
            table.add_row(t.replace("_", " ").title(), details['provider'], details['model'], status_indicator, diag_msg)
        rprint(table)
        
        choice = questionary.select(
            "Main Settings:",
            choices=[
                "1. Run Cognitive Health Check (Test All)",
                "2. Manage Secret Vault (API Keys)",
                "3. Configure Default Brain",
                "4. Configure Specialist Tiers (Librarian/Chancellor/Dean)",
                "5. Manage MCP Server (IDE Integration)",
                "6. Update Operator Profile & Behavior",
                "7. Update Obsidian Vault Path",
                "8. Archive Retention (Current: " + str(CONFIG['settings'].get('archive_retention_days', 30)) + "d)",
                "9. Auto-Memory Distillation (Current: " + CONFIG['settings'].get('auto_distill_tier', 'T4') + ")",
                "10. Set Agent Persona (Specialty Mandate)",
                "11. Exit"
            ]
        ).ask()

        if choice == "11. Exit": break
        
        if "1." in choice:
            for t in ["default_reasoning", "librarian", "chancellor", "dean"]:
                details = tiers_config.get(t)
                if not details or details.get('provider') == "NOT SET":
                    health_cache[t] = ("[red]●[/red]", "NOT SET") 
                    continue
                success, msg = test_provider(details['provider'], details['model'], details.get('endpoint'), t, details.get('auth_type', 'API Key'))
                health_cache[t] = ("[bold green]●[/bold green]", "OK") if success else ("[bold red]●[/bold red]", str(msg)[:60])
        elif "2." in choice: setup_secrets_menu()
        elif "3." in choice: setup_cognitive_tier("default_reasoning")
        elif "4." in choice:
            tier = questionary.select("Select Tier:", choices=["librarian", "chancellor", "dean", "Back"]).ask()
            if tier != "Back": setup_cognitive_tier(tier)
        elif "5." in choice: mcp_server_menu()
        elif "6." in choice: update_operator_profile()
        elif "7." in choice:
            path = questionary.text("Obsidian Vault Path:", default=CONFIG['settings'].get('obsidian_vault_path', "")).ask()
            if path is not None:
                CONFIG['settings']['obsidian_vault_path'] = path
                save_config(CONFIG)
        elif "8." in choice:
            rprint("[cyan]Set retention days for raw logs and proposals.[/cyan]")
            rprint("[yellow]Enter '0' to deactivate automatic purge.[/yellow]")
            days = questionary.text("Retention Days:", default=str(CONFIG['settings'].get('archive_retention_days', 30))).ask()
            if days and days.isdigit():
                CONFIG['settings']['archive_retention_days'] = int(days)
                save_config(CONFIG)
        elif "9." in choice:
            tier_choice = questionary.select(
                "Select Auto-Commit Frequency:",
                choices=[
                    "Off (Manual aim commit only)",
                    "T2 (Daily Auto-Commit)",
                    "T3 (Weekly Auto-Commit)",
                    "T4 (Monthly Auto-Commit - Default)"
                ]
            ).ask()
            if tier_choice:
                val = tier_choice.split(" ")[0]
                CONFIG['settings']['auto_distill_tier'] = val
                save_config(CONFIG)
        elif "10." in choice:
            update_agent_persona()

if __name__ == "__main__":
    try: main_menu()
    except KeyboardInterrupt: sys.exit(0)
