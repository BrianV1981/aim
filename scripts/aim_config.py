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
    
    table = Table(show_header=False, box=None)
    table.add_row("[yellow]Embedding Provider:[/yellow]", config['models'].get('embedding_provider', 'local').upper())
    table.add_row("[yellow]Embedding Model:[/yellow]", config['models'].get('embedding', 'nomic-embed-text'))
    table.add_row("[yellow]Endpoint:[/yellow]", config['models'].get('embedding_endpoint', 'N/A'))
    table.add_row("[yellow]Distillation Interval:[/yellow]", f"{config['settings'].get('scrivener_interval_minutes', 30)} mins")
    table.add_row("[yellow]Obsidian Sync:[/yellow]", "ACTIVE" if os.path.exists(os.path.join(BASE_DIR, "scripts/obsidian_sync.py")) else "DISABLED")
    
    rprint(table)
    rprint("-" * 40)

def manage_providers(config):
    while True:
        display_dashboard(config)
        choice = questionary.select(
            "Provider Settings:",
            choices=[
                "Switch Provider Type (WARNING: DESTRUCTIVE)",
                "Change Model Name",
                "Change API Endpoint URL",
                "Update API Key (Secure System Vault)",
                "Back to Main Menu"
            ]
        ).ask()

        if choice == "Switch Provider Type (WARNING: DESTRUCTIVE)":
            rprint(Panel.fit(
                "[bold red]🛑 DANGER: BRAIN TRANSPLANT DETECTED[/bold red]\n\n"
                "Switching providers requires a TOTAL RE-INDEX of your memories.\n"
                "Are you absolutely sure?",
                border_style="red"
            ))
            
            confirm = questionary.confirm("Proceed with provider switch?", default=False).ask()
            if not confirm:
                continue

            ptype = questionary.select(
                "Select Type:",
                choices=["google", "local", "openai-compat"]
            ).ask()
            if ptype:
                config['models']['embedding_provider'] = ptype
                if ptype == "local" and not config['models'].get('embedding_endpoint'):
                    config['models']['embedding_endpoint'] = "http://localhost:11434/api/embeddings"
                elif ptype == "openai-compat" and not config['models'].get('embedding_endpoint'):
                    config['models']['embedding_endpoint'] = "http://localhost:8080/v1"
                save_config(config)
                rprint("[bold green]Provider updated. RE-INDEXING IS MANDATORY.[/bold green]")
                input("\nPress Enter to continue...")

        elif choice == "Change Model Name":
            ptype = config['models'].get('embedding_provider', 'local')
            hint = ""
            if ptype == "google":
                hint = "Example: models/gemini-embedding-2-preview"
            elif ptype == "local":
                hint = "Example: nomic-embed-text"
            elif ptype == "openai-compat":
                hint = "Example: text-embedding-3-small"
            
            rprint(Panel(f"[bold blue]MODEL NAME[/bold blue]\nThis is the ID of the specific model being used.\n[dim]{hint}[/dim]"))
            
            current = config['models'].get('embedding', '')
            model = questionary.text(f"Enter Model Name:", default=current).ask()
            if model and model.strip():
                config['models']['embedding'] = model.strip()
                save_config(config)
                rprint(f"[green]Model updated.[/green]")
            input("\nPress Enter to continue...")

        elif choice == "Change API Endpoint URL":
            ptype = config['models'].get('embedding_provider', 'local')
            hint = ""
            if ptype == "local":
                hint = "Default (Ollama): http://localhost:11434/api/embeddings"
            elif ptype == "openai-compat":
                hint = "Example: http://localhost:8080/v1"
            
            rprint(Panel(f"[bold blue]API ENDPOINT[/bold blue]\nThe URL where A.I.M. sends text to be converted to vectors.\n[dim]{hint}[/dim]"))
            
            current = config['models'].get('embedding_endpoint', '')
            endpoint = questionary.text(f"Enter Endpoint URL:", default=current).ask()
            if endpoint and endpoint.strip():
                config['models']['embedding_endpoint'] = endpoint.strip()
                save_config(config)
                rprint(f"[green]Endpoint updated.[/green]")
            input("\nPress Enter to continue...")

        elif choice == "Update API Key (Secure System Vault)":
            ptype = config['models'].get('embedding_provider', 'local')
            service = "aim-system"
            key_name = "google-api-key" if ptype == "google" else "embedding-api-key"
            
            hint = ""
            if ptype == "google":
                hint = "Format: AIza... (typically 35 characters)"
            elif ptype == "openai-compat":
                hint = "Format: sk-... (typically 48-51 characters)"
            
            rprint(Panel(
                f"[bold blue]🔐 SECURE SYSTEM VAULT[/bold blue]\n\n"
                f"A.I.M. uses your operating system's built-in encrypted vault \n"
                f"(Keychain/Credential Manager) to store secrets. \n\n"
                f"[bold]Why?[/bold] This prevents your API keys from being leaked in \n"
                f"plaintext configuration files or terminal history.\n\n"
                f"[dim]{hint}[/dim]",
                title="Security Awareness",
                border_style="green"
            ))
            
            key = questionary.password(f"Paste your {ptype} API key here:").ask()
            if key and key.strip():
                keyring.set_password(service, key_name, key.strip())
                rprint(f"[green]Success! Key saved to your system's secure vault.[/green]")
            else:
                rprint("[yellow]Vault not updated.[/yellow]")
            input("\nPress Enter to continue...")

        elif choice == "Back to Main Menu" or choice is None:
            break

def config_menu():
    config = load_config()
    while True:
        display_dashboard(config)
        choice = questionary.select(
            "What would you like to configure?",
            choices=[
                "Manage Embedding Provider (Brain Settings)",
                "Change Distillation Interval",
                "Set Obsidian Vault Path",
                "Exit"
            ]
        ).ask()

        if choice == "Manage Embedding Provider (Brain Settings)":
            manage_providers(config)
        elif choice == "Change Distillation Interval":
            rprint(Panel("[bold blue]DISTILLATION INTERVAL[/bold blue]\nHow often A.I.M. distills your history into a long-term pulse.\n[dim]Example: 30 (mins)[/dim]"))
            current = str(config['settings'].get('scrivener_interval_minutes', 30))
            interval = questionary.text(f"Interval in mins:", default=current).ask()
            if interval and interval.isdigit():
                config['settings']['scrivener_interval_minutes'] = int(interval)
                save_config(config)
                rprint("[green]Interval updated.[/green]")
            input("\nPress Enter to continue...")
        elif choice == "Set Obsidian Vault Path":
            rprint(Panel("[bold blue]OBSIDIAN VAULT PATH[/bold blue]\nWhere A.I.M. daily logs are mirrored.\n[dim]Currently hardcoded.[/dim]"))
            rprint("[yellow]Path: /home/kingb/OperationsCenterVault/AIM_LOGS[/yellow]")
            input("\nPress Enter to continue...")
        elif choice == "Exit" or choice is None:
            break

if __name__ == "__main__":
    try:
        config_menu()
    except KeyboardInterrupt:
        rprint("\n[yellow]Configuration aborted.[/yellow]")
        sys.exit(0)
