#!/usr/bin/env python3
import os
import json
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
import questionary
import subprocess

# --- CONFIG BOOTSTRAP ---
def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        rprint("[red]Error: CONFIG.json not found. Run 'aim init' first.[/red]")
        sys.exit(1)
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def get_installed_ollama_models():
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:]
        return [line.split()[0] for line in lines if line.strip()]
    except: return []

def setup_provider_wizard(config, tier_name):
    """Configures a specific cognitive tier."""
    rprint(Panel(f"[bold blue]Tier Configuration: {tier_name.upper()}[/bold blue]"))
    
    provider = questionary.select(
        "Select Provider:",
        choices=["google", "local (ollama)", "openai-compat", "codex-cli"]
    ).ask()
    
    if provider == "google":
        model = questionary.select("Select Model:", choices=["gemini-flash-latest", "gemini-1.5-pro", "gemini-3.1-pro", "gemini-2.0-flash-exp"]).ask()
        endpoint = "https://generativelanguage.googleapis.com"
    elif provider == "local (ollama)":
        models = get_installed_ollama_models() or ["nomic-embed-text", "llama3", "mistral"]
        model = questionary.select("Select Installed Model:", choices=models).ask()
        endpoint = "http://localhost:11434/api/generate"
    elif provider == "codex-cli":
        model = "gpt-5.4"
        endpoint = "local-exec"
    else:
        model = questionary.text("Enter Model Name:").ask()
        endpoint = questionary.text("Enter Endpoint URL:").ask()

    # Save to the new tiers schema
    if 'tiers' not in config['models']: config['models']['tiers'] = {}
    config['models']['tiers'][tier_name] = {
        "provider": provider.replace(" (ollama)", ""),
        "model": model,
        "endpoint": endpoint
    }
    save_config(config)
    rprint(f"[green]{tier_name.capitalize()} tier configured successfully.[/green]")

def cognitive_tiers_menu(config):
    while True:
        table = Table(title="Cognitive Tiers & Specialists")
        table.add_column("Tier", style="cyan")
        table.add_column("Expert", style="green")
        table.add_column("Model", style="yellow")
        table.add_column("Provider", style="magenta")

        tiers = config['models'].get('tiers', {})
        for t in ["librarian", "chancellor", "fellow", "dean"]:
            details = tiers.get(t, {"model": "NOT SET", "provider": "None"})
            table.add_row(t.capitalize(), t.replace("n", "n-specialist"), details['model'], details['provider'])

        rprint(table)
        
        choice = questionary.select(
            "Configure Tier:",
            choices=["1. Librarian (Session Logging)", "2. Chancellor (Daily Sync)", "3. Fellow (Weekly Review)", "4. Dean (Monthly/Soul)", "Back to Main"]
        ).ask()

        if "Back" in choice: break
        tier_map = {"1.": "librarian", "2.": "chancellor", "3.": "fellow", "4.": "dean"}
        setup_provider_wizard(config, tier_map[choice[:2]])

def config_menu():
    config = load_config()
    while True:
        os.system('clear')
        rprint(Panel("[bold green]A.I.M. COCKPIT (Scholastic v1.5)[/bold green]\nSovereign Control Layer"))
        
        choice = questionary.select(
            "Main Settings:",
            choices=[
                "1. Global Brain (Default Reasoning)",
                "2. Cognitive Tiers (Librarian/Chancellor/Dean)",
                "3. Embedding Engine (Mandatory)",
                "4. Safety Guardrails (Sentinel)",
                "5. Obsidian Sovereign Backup",
                "6. Scrivener Interval (Current: " + str(config['settings'].get('scrivener_interval_minutes')) + "m)",
                "Exit"
            ]
        ).ask()

        if choice == "Exit": break
        
        if "1." in choice: setup_provider_wizard(config, "default_reasoning")
        elif "2." in choice: cognitive_tiers_menu(config)
        elif "3." in choice: setup_provider_wizard(config, "embedding")
        elif "5." in choice:
            rprint(Panel("[bold blue]OBSIDIAN SOVEREIGN BACKUP[/bold blue]\nMirror your technical soul to an external folder.\n\n[yellow]Performs FULL FORENSIC BACKUP:[/yellow]\n- Daily MD logs + Raw JSON transcripts"))
            current = config['settings'].get('obsidian_vault_path', "")
            path = questionary.text("Enter Vault Path:", default=current).ask()
            if path is not None:
                config['settings']['obsidian_vault_path'] = path.strip()
                save_config(config); rprint("[green]Obsidian path updated.[/green]")
                time.sleep(1)
        elif "6." in choice:
            interval = questionary.text("Pulse Interval (minutes):", default=str(config['settings'].get('scrivener_interval_minutes', 60))).ask()
            if interval and interval.isdigit(): 
                config['settings']['scrivener_interval_minutes'] = int(interval)
                save_config(config)

if __name__ == "__main__":
    try: config_menu()
    except KeyboardInterrupt: sys.exit(0)
