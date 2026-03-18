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
    
    # Brain Summary Table
    table = Table(title="The A.I.M. Hybrid Brain", show_header=True, header_style="bold magenta")
    table.add_column("Layer", style="dim")
    table.add_column("Provider", style="yellow")
    table.add_column("Model", style="green")
    
    table.add_row(
        "Memory (Embeddings)", 
        config['models'].get('embedding_provider', 'local').upper(),
        config['models'].get('embedding', 'nomic-embed-text')
    )
    table.add_row(
        "Reasoning (Summary/Audit)", 
        config['models'].get('reasoning_provider', 'google').upper(),
        config['models'].get('reasoning_model', 'gemini-flash-latest')
    )
    
    rprint(table)
    
    # Meta Info
    rprint(f"[dim]Distillation Interval: {config['settings'].get('scrivener_interval_minutes', 30)} mins[/dim]")
    rprint(f"[dim]Obsidian Sync: {'ACTIVE' if os.path.exists(os.path.join(BASE_DIR, 'scripts/obsidian_sync.py')) else 'DISABLED'}[/dim]")
    rprint("-" * 40)

def manage_memory(config):
    """Configuration for the Embedding Layer."""
    while True:
        display_dashboard(config)
        choice = questionary.select(
            "Memory Provider Settings (Vector Indexing):",
            choices=[
                "Switch Memory Provider (WARNING: DESTRUCTIVE)",
                "Change Memory Model Name",
                "Change Memory API Endpoint",
                "Update Memory API Key (Secure System Vault)",
                "Back to Main Menu"
            ]
        ).ask()

        if choice == "Switch Memory Provider (WARNING: DESTRUCTIVE)":
            rprint(Panel.fit(
                "[bold red]🛑 DANGER: BRAIN TRANSPLANT[/bold red]\n\n"
                "Switching memory providers requires a TOTAL RE-INDEX of your archive.\n"
                "Are you absolutely sure?",
                border_style="red"
            ))
            if not questionary.confirm("Proceed?", default=False).ask(): continue
            
            ptype = questionary.select("Select Type:", choices=["google", "local", "openai-compat"]).ask()
            if ptype:
                config['models']['embedding_provider'] = ptype
                if ptype == "local": config['models']['embedding_endpoint'] = "http://localhost:11434/api/embeddings"
                save_config(config)
                rprint("[bold green]Memory Provider updated. RE-INDEXING MANDATORY.[/bold green]")
                input("\nPress Enter...")

        elif choice == "Change Memory Model Name":
            model = questionary.text("Enter Model ID (e.g. nomic-embed-text):", default=config['models'].get('embedding', '')).ask()
            if model: config['models']['embedding'] = model.strip(); save_config(config)

        elif choice == "Change Memory API Endpoint":
            url = questionary.text("Enter URL:", default=config['models'].get('embedding_endpoint', '')).ask()
            if url: config['models']['embedding_endpoint'] = url.strip(); save_config(config)

        elif choice == "Update Memory API Key (Secure System Vault)":
            ptype = config['models'].get('embedding_provider', 'local')
            key = questionary.password(f"Enter Key for {ptype}:").ask()
            if key: keyring.set_password("aim-system", "embedding-api-key", key.strip())
            input("\nPress Enter...")

        elif choice == "Back to Main Menu" or choice is None:
            break

def manage_reasoning(config):
    """Configuration for the Reasoning Layer."""
    while True:
        display_dashboard(config)
        choice = questionary.select(
            "Reasoning Provider Settings (Summaries & Safety):",
            choices=[
                "Switch Reasoning Provider (Gemini vs. Ollama)",
                "Change Reasoning Model Name",
                "Change Reasoning API Endpoint",
                "Update Reasoning API Key (Secure System Vault)",
                "Back to Main Menu"
            ]
        ).ask()

        if choice == "Switch Reasoning Provider (Gemini vs. Ollama)":
            rprint(Panel(
                "[bold blue]REASONING LOGIC[/bold blue]\n\n"
                "A.I.M. defaults to [bold green]Google (Gemini Flash)[/bold green] for reasoning because \n"
                "it is highly token-efficient and handles complex safety audits \n"
                "better than small local models.\n\n"
                "Switching to [bold]Local (Ollama)[/bold] allows for 100% offline operation \n"
                "with zero token cost."
            ))
            ptype = questionary.select("Select Type:", choices=["google", "local", "openai-compat"]).ask()
            if ptype:
                config['models']['reasoning_provider'] = ptype
                if ptype == "local": config['models']['reasoning_endpoint'] = "http://localhost:11434/api/generate"
                save_config(config)
                rprint(f"[green]Reasoning Layer switched to {ptype.upper()}.[/green]")
                input("\nPress Enter...")

        elif choice == "Change Reasoning Model Name":
            model = questionary.text("Enter Model ID (e.g. gemini-flash-latest or llama3):", default=config['models'].get('reasoning_model', '')).ask()
            if model: config['models']['reasoning_model'] = model.strip(); save_config(config)

        elif choice == "Change Reasoning API Endpoint":
            url = questionary.text("Enter URL:", default=config['models'].get('reasoning_endpoint', '')).ask()
            if url: config['models']['reasoning_endpoint'] = url.strip(); save_config(config)

        elif choice == "Update Reasoning API Key (Secure System Vault)":
            ptype = config['models'].get('reasoning_provider', 'google')
            key_name = "google-api-key" if ptype == "google" else "reasoning-api-key"
            key = questionary.password(f"Enter Key for {ptype}:").ask()
            if key: keyring.set_password("aim-system", key_name, key.strip())
            input("\nPress Enter...")

        elif choice == "Back to Main Menu" or choice is None:
            break

def config_menu():
    config = load_config()
    while True:
        display_dashboard(config)
        choice = questionary.select(
            "Main Menu:",
            choices=[
                "Manage Memory Layer (Embeddings)",
                "Manage Reasoning Layer (AI Summaries)",
                "Change Distillation Interval",
                "Exit"
            ]
        ).ask()

        if choice == "Manage Memory Layer (Embeddings)":
            manage_memory(config)
        elif choice == "Manage Reasoning Layer (AI Summaries)":
            manage_reasoning(config)
        elif choice == "Change Distillation Interval":
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
