#!/home/kingb/aim/venv/bin/python3
import os
import json
import questionary
import keyring
import sys
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
    ptype = questionary.select(
        "Select Type:",
        choices=["google (Gemini Cloud)", "local (Ollama/LocalAI)", "openai-compat (Other AI Clouds)"]
    ).ask()
    
    if not ptype: return
    
    actual_type = "google" if "google" in ptype else ("local" if "local" in ptype else "openai-compat")
    config['models'][provider_key] = actual_type

    # STEP 2: ENDPOINT (If not Google)
    if actual_type != "google":
        rprint(Panel(f"[bold blue]STEP 2: API ENDPOINT[/bold blue]\nThe URL of your AI service.\n[dim]Local Default: http://localhost:11434[/dim]"))
        default_url = "http://localhost:11434" if actual_type == "local" else "https://api.example.com/v1"
        url = questionary.text("Enter API Endpoint URL:", default=config['models'].get(endpoint_key, default_url)).ask()
        if url: config['models'][endpoint_key] = url.strip()

    # STEP 3: MODEL NAME
    rprint(Panel(f"[bold blue]STEP {3 if actual_type != 'google' else 2}: MODEL NAME[/bold blue]\nWhich specific model should we use?"))
    default_model = "nomic-embed-text" if is_memory else "llama3"
    if actual_type == "google": default_model = "models/gemini-embedding-2-preview" if is_memory else "gemini-flash-latest"
    
    model = questionary.text("Enter Model Name:", default=config['models'].get(model_key, default_model)).ask()
    if model: config['models'][model_key] = model.strip()

    # STEP 4: API KEY (If needed)
    if actual_type != "local":
        rprint(Panel(
            f"[bold blue]STEP {4 if actual_type != 'google' else 3}: SECURE SYSTEM VAULT[/bold blue]\n\n"
            f"Please enter your API Key. It will be stored in your computer's \n"
            f"encrypted secure vault, NOT in a plaintext file.",
            border_style="green"
        ))
        key_name = "google-api-key" if actual_type == "google" else vault_key
        key = questionary.password(f"Paste your {actual_type} API Key:").ask()
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
            "What would you like to configure?",
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
