#!/home/kingb/aim/venv/bin/python3
import os
import json
import questionary
import keyring
import sys
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# --- CONFIGURATION ---
BASE_DIR = "/home/kingb/aim"
CONFIG_PATH = os.path.join(BASE_DIR, "core/CONFIG.json")
console = Console()

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def display_dashboard(config):
    console.clear()
    rprint(Panel("[bold cyan]A.I.M. CONFIGURATION COCKPIT[/bold cyan]", expand=False))
    
    table = Table(title="Current 'Brain' Configuration", show_header=True, header_style="bold magenta")
    table.add_column("Layer", style="dim")
    table.add_column("Provider", style="yellow")
    table.add_column("Model", style="green")
    
    table.add_row(
        "Memory (Embeddings)", 
        config['models'].get('embedding_provider', 'local').upper(),
        config['models'].get('embedding', 'nomic-embed-text')
    )
    table.add_row(
        "Reasoning (Summaries)", 
        config['models'].get('reasoning_provider', 'google').upper(),
        config['models'].get('reasoning_model', 'gemini-flash-latest')
    )
    
    rprint(table)
    rprint(f"[dim]Distillation Interval: {config['settings'].get('scrivener_interval_minutes', 30)} mins[/dim]")
    rprint("-" * 40)

def setup_provider_wizard(config, layer_type):
    """
    Step-by-step wizard to configure a provider (Memory or Reasoning).
    """
    is_memory = (layer_type == "memory")
    provider_key = 'embedding_provider' if is_memory else 'reasoning_provider'
    model_key = 'embedding' if is_memory else 'reasoning_model'
    endpoint_key = 'embedding_endpoint' if is_memory else 'reasoning_endpoint'
    vault_key = 'embedding-api-key' if is_memory else 'reasoning-api-key'

    rprint(Panel(f"[bold blue]STEP 1: SELECT PROVIDER TYPE[/bold blue]\nWhere should the {layer_type} logic run?"))
    
    choices = [
        "google (Gemini Cloud)", 
        "local (Ollama/LocalAI)", 
        "openai-compat (Other AI Clouds)"
    ]
    if not is_memory:
        choices.insert(2, "codex (ChatGPT Cloud via Codex CLI)")

    ptype = questionary.select("Select Type:", choices=choices).ask()
    
    if not ptype: return
    
    actual_type = "google" if "google" in ptype else ("local" if "local" in ptype else ("codex" if "codex" in ptype else "openai-compat"))
    config['models'][provider_key] = actual_type

    # STEP 2: ENDPOINT (If not Google/Codex)
    if actual_type not in ["google", "codex"]:
        rprint(Panel(f"[bold blue]STEP 2: API ENDPOINT[/bold blue]\nThe URL of your AI service.\n[dim]Local Default: http://localhost:11434[/dim]"))
        default_url = "http://localhost:11434" if actual_type == "local" else "https://api.example.com/v1"
        url = questionary.text("Enter API Endpoint URL:", default=config['models'].get(endpoint_key, default_url)).ask()
        if url: config['models'][endpoint_key] = url.strip()

    # STEP 3: MODEL NAME
    rprint(Panel(f"[bold blue]STEP 3: MODEL NAME[/bold blue]\nWhich specific model should we use?"))
    default_model = "nomic-embed-text" if is_memory else "llama3"
    if actual_type == "google": 
        default_model = "models/gemini-embedding-2-preview" if is_memory else "gemini-flash-latest"
    elif actual_type == "codex":
        default_model = "gpt-4o"

    model = questionary.text("Enter Model Name:", default=config['models'].get(model_key, default_model)).ask()
    if model: config['models'][model_key] = model.strip()

    # STEP 4: AUTHENTICATION
    if actual_type == "local":
        rprint(Panel(f"[bold blue]STEP 4: AUTHENTICATION (OLLAMA)[/bold blue]\nHow should we authenticate with Ollama?"))
        auth_choice = questionary.select(
            "Select Method:",
            choices=[
                "OAuth (Run 'ollama signin' now)",
                "Manual API Key (Store in System Vault)",
                "No Auth (Local Only)"
            ]
        ).ask()

        if auth_choice == "OAuth (Run 'ollama signin' now)":
            rprint("[yellow]Launching 'ollama signin'... follow the prompts in your browser.[/yellow]")
            try:
                subprocess.run(["ollama", "signin"], check=True)
                try: keyring.delete_password("aim-system", vault_key)
                except: pass
            except Exception as e:
                rprint(f"[red]Error during signin: {e}[/red]")
        
        elif auth_choice == "Manual API Key (Store in System Vault)":
            key = questionary.password(f"Paste your Ollama Cloud API Key:").ask()
            if key:
                keyring.set_password("aim-system", vault_key, key.strip())
                rprint("[green]Key successfully vaulted![/green]")
        
        elif auth_choice == "No Auth (Local Only)":
            try: keyring.delete_password("aim-system", vault_key)
            except: pass
            rprint("[green]Authentication cleared.[/green]")

    elif actual_type == "codex":
        rprint(Panel(f"[bold blue]STEP 4: AUTHENTICATION (CODEX)[/bold blue]\nA.I.M. will use your existing ChatGPT login via the Codex CLI."))
        if questionary.confirm("Run 'codex login' now?", default=True).ask():
            try:
                subprocess.run(["codex", "login"], check=True)
            except Exception as e:
                rprint(f"[red]Error during codex login: {e}[/red]")

    elif actual_type not in ["local", "codex"]:
        rprint(Panel(
            f"[bold blue]STEP 4: SECURE SYSTEM VAULT[/bold blue]\n\n"
            f"Please enter your API Key for {actual_type}. It will be stored safely.",
            border_style="green"
        ))
        key_name = "google-api-key" if actual_type == "google" else vault_key
        key = questionary.password(f"Paste Key:").ask()
        if key: 
            keyring.set_password("aim-system", key_name, key.strip())
            rprint("[green]Key successfully vaulted![/green]")

    save_config(config)
    rprint(f"[bold green]Configuration for {layer_type} complete![/bold green]")
    if is_memory:
        rprint("[yellow]Reminder: You must run 'aim index' to re-align your brain to the new coordinates.[/yellow]")
    input("\nPress Enter to return to menu...")

def config_menu():
    config = load_config()
    while True:
        display_dashboard(config)
        choice = questionary.select(
            "Main Menu:",
            choices=[
                "Configure Memory Layer (Step-by-Step Wizard)",
                "Configure Reasoning Layer (Step-by-Step Wizard)",
                "Update Distillation Interval",
                "Exit"
            ]
        ).ask()

        if choice == "Configure Memory Layer (Step-by-Step Wizard)":
            if questionary.confirm("WARNING: Switching Memory Providers is DESTRUCTIVE. Continue?").ask():
                setup_provider_wizard(config, "memory")
        elif choice == "Configure Reasoning Layer (Step-by-Step Wizard)":
            setup_provider_wizard(config, "reasoning")
        elif choice == "Update Distillation Interval":
            interval = questionary.text("Interval (mins):", default=str(config['settings'].get('scrivener_interval_minutes', 30))).ask()
            if interval and interval.isdigit():
                config['settings']['scrivener_interval_minutes'] = int(interval)
                save_config(config)
            input("\nPress Enter...")
        elif choice == "Exit" or choice is None:
            break

if __name__ == "__main__":
    try:
        config_menu()
    except KeyboardInterrupt:
        rprint("\n[yellow]Configuration aborted.[/yellow]")
        sys.exit(0)
