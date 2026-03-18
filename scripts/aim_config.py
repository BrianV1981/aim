#!/home/kingb/aim/venv/bin/python3
import os
import json
import questionary
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
    
    table = Table(show_header=False, box=None)
    table.add_row("[yellow]Embedding Provider:[/yellow]", config['models'].get('embedding_provider', 'local').upper())
    table.add_row("[yellow]Distillation Interval:[/yellow]", f"{config['settings'].get('scrivener_interval_minutes', 30)} mins")
    table.add_row("[yellow]Obsidian Sync:[/yellow]", "ACTIVE" if os.path.exists(os.path.join(BASE_DIR, "scripts/obsidian_sync.py")) else "DISABLED")
    table.add_row("[yellow]Workspace Root:[/yellow]", config['settings'].get('allowed_root', '/home/kingb'))
    
    rprint(table)
    rprint("-" * 40)

def config_menu():
    config = load_config()
    
    while True:
        display_dashboard(config)
        
        choice = questionary.select(
            "What would you like to configure?",
            choices=[
                "Change Embedding Provider (Google vs Local)",
                "Change Distillation Interval",
                "Set Obsidian Vault Path",
                "Update Google API Key",
                "Exit"
            ]
        ).ask()

        if choice == "Change Embedding Provider (Google vs Local)":
            provider = questionary.select(
                "Select Provider:",
                choices=["local (Ollama/Nomic)", "google (Gemini API)"]
            ).ask()
            config['models']['embedding_provider'] = "local" if "local" in provider else "google"
            save_config(config)
            rprint("[green]Provider updated. Note: You may need to run 'aim index' to re-align your brain.[/green]")
            input("\nPress Enter to continue...")

        elif choice == "Change Distillation Interval":
            interval = questionary.text(
                "Enter interval in minutes (default 30):",
                default=str(config['settings'].get('scrivener_interval_minutes', 30))
            ).ask()
            if interval.isdigit():
                config['settings']['scrivener_interval_minutes'] = int(interval)
                save_config(config)
                rprint("[green]Interval updated.[/green]")
            input("\nPress Enter to continue...")

        elif choice == "Update Google API Key":
            # Just call our existing key script
            os.system(f"{BASE_DIR}/venv/bin/python3 {BASE_DIR}/scripts/set_key.py")
            input("\nPress Enter to continue...")

        elif choice == "Set Obsidian Vault Path":
            # Placeholder for future logic if we want to change target
            rprint("[yellow]Currently hardcoded to: /home/kingb/OperationsCenterVault/AIM_LOGS[/yellow]")
            input("\nPress Enter to continue...")

        elif choice == "Exit" or choice is None:
            break

if __name__ == "__main__":
    try:
        config_menu()
    except KeyboardInterrupt:
        rprint("\n[yellow]Configuration aborted.[/yellow]")
