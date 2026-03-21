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

def test_provider(provider, model, endpoint, brain_type="default_reasoning"):
    """Validates the provider configuration with a simple prompt."""
    with console.status(f"[bold blue]Testing {provider} ({model})...[/bold blue]"):
        try:
            # We create a temporary config for the test
            temp_config = CONFIG.copy()
            if 'tiers' not in temp_config['models']: temp_config['models']['tiers'] = {}
            temp_config['models']['tiers'][brain_type] = {
                "provider": provider,
                "model": model,
                "endpoint": endpoint
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
            ("google", "gemini-api-key"),
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
            if "Fast" in preset: model = "gemini-3.1-flash"
            elif "Thinking" in preset: model = "gemini-3.1-pro-thinking"
            else: model = "gemini-3.1-pro"
        elif selection_mode == "All Models (Full List)":
            model_choices = [
                "gemini-3.1-pro", 
                "gemini-3.1-flash", 
                "gemini-3.1-pro-thinking",
                "gemini-3.1-pro-preview",
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
            model = questionary.text("Enter Google Model ID (e.g., gemini-3.1-pro):").ask()
            
        endpoint = "https://generativelanguage.googleapis.com"
        if "API Key" in auth_type:
            key_name = "gemini-api-key"
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
        model = questionary.text("Ollama Model (e.g., llama3):").ask()
        endpoint = questionary.text("Ollama Endpoint:", default="http://localhost:11434/api/generate").ask()
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
    success, msg = test_provider(provider.replace(" (ollama)", ""), model, endpoint, tier_name)
    if success:
        rprint(f"[green]Test Success: {msg}[/green]")
        if 'tiers' not in CONFIG['models']: CONFIG['models']['tiers'] = {}
        CONFIG['models']['tiers'][tier_name] = {
            "provider": provider.replace(" (ollama)", ""),
            "model": model,
            "endpoint": endpoint
        }
        save_config(CONFIG)
    else:
        rprint(f"[red]Test Failed: {msg}[/red]")
        if questionary.confirm("Save anyway?").ask():
            if 'tiers' not in CONFIG['models']: CONFIG['models']['tiers'] = {}
            CONFIG['models']['tiers'][tier_name] = {
                "provider": provider.replace(" (ollama)", ""),
                "model": model,
                "endpoint": endpoint
            }
            save_config(CONFIG)

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
        
        tiers_config = CONFIG.get('models', {}).get('tiers', {})
        for t in ["default_reasoning", "librarian", "chancellor", "dean"]:
            details = tiers_config.get(t, {"provider": "NOT SET", "model": "N/A"})
            
            # Get cached health or default
            status_indicator = health_cache.get(t, "[white]○[/white]") # Empty circle for unknown
            
            table.add_row(
                t.replace("_", " ").title(), 
                details['provider'], 
                details['model'],
                status_indicator
            )
        
        rprint(table)
        
        choice = questionary.select(
            "Main Settings:",
            choices=[
                "1. Run Cognitive Health Check (Test All)",
                "2. Manage Secret Vault (API Keys)",
                "3. Configure Default Brain",
                "4. Configure Specialist Tiers (Librarian/Chancellor/Dean)",
                "5. Update Obsidian Vault Path",
                "6. Exit"
            ]
        ).ask()

        if choice == "6. Exit": break
        
        if "1." in choice:
            for t in ["default_reasoning", "librarian", "chancellor", "dean"]:
                details = tiers_config.get(t)
                if not details or details.get('provider') == "NOT SET":
                    health_cache[t] = "[red]●[/red]" 
                    continue
                
                success, _ = test_provider(details['provider'], details['model'], details.get('endpoint'), t)
                health_cache[t] = "[bold green]●[/bold green]" if success else "[bold red]●[/bold red]"
        
        elif "2." in choice: setup_secrets_menu()
        elif "3." in choice: setup_cognitive_tier("default_reasoning")
        elif "4." in choice:
            tier = questionary.select("Select Tier:", choices=["librarian", "chancellor", "dean", "Back"]).ask()
            if tier != "Back": setup_cognitive_tier(tier)
        elif "5." in choice:
            path = questionary.text("Obsidian Vault Path:", default=CONFIG['settings'].get('obsidian_vault_path', "")).ask()
            if path is not None:
                CONFIG['settings']['obsidian_vault_path'] = path
                save_config(CONFIG)

if __name__ == "__main__":
    try: main_menu()
    except KeyboardInterrupt: sys.exit(0)
