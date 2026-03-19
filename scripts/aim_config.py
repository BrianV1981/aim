#!/usr/bin/env python3
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

# --- DYNAMIC CONFIGURATION ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        config_path = os.path.join(current, "core/CONFIG.json")
        if os.path.exists(config_path):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = find_aim_root(os.getcwd())
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
    rprint(Panel("[bold cyan]A.I.M. COCKPIT (Gemini Exoskeleton)[/bold cyan]", expand=False))
    
    # Brain Summary Table
    table = Table(title="Sovereign Brain Configuration", show_header=True, header_style="bold magenta")
    table.add_column("Memory Layer", style="dim")
    table.add_column("Active Provider", style="yellow")
    table.add_column("Model", style="green")
    
    table.add_row(
        "Semantic Search (Memory)", 
        config['models'].get('embedding_provider', 'local').upper(),
        config['models'].get('embedding', 'nomic-embed-text')
    )
    table.add_row(
        "Reasoning (Summaries)", 
        config['models'].get('reasoning_provider', 'google').upper(),
        config['models'].get('reasoning_model', 'gemini-flash-latest')
    )
    table.add_row(
        "Sentinel (Safety)", 
        config['models'].get('sentinel_provider', 'google').upper(),
        config['models'].get('sentinel_model', 'gemini-flash-latest')
    )
    
    rprint(table)
    
    # Settings Summary
    table_ops = Table(show_header=False, box=None)
    table_ops.add_row("[dim]Safety Sentinel Mode:[/dim]", f"[bold]{config['settings'].get('sentinel_mode', 'full').upper()}[/bold]")
    table_ops.add_row("[dim]Workspace Root:[/dim]", f"[bold]{config['settings'].get('allowed_root', BASE_DIR)}[/bold]")
    table_ops.add_row("[dim]Distillation:[/dim]", f"{config['settings'].get('scrivener_interval_minutes', 30)} mins")
    
    rprint(table_ops)
    rprint("-" * 40)

def setup_provider_wizard(config, layer_type):
    """Step-by-step wizard to configure a brain layer."""
    provider_key = f'{layer_type}_provider' if layer_type != 'embedding' else 'embedding_provider'
    model_key = f'{layer_type}_model' if layer_type != 'embedding' else 'embedding'
    endpoint_key = f'{layer_type}_endpoint' if layer_type != 'embedding' else 'embedding_endpoint'
    vault_key = f'{layer_type}-api-key'

    # Special handling for older config naming
    if layer_type == 'embedding':
        vault_key = 'embedding-api-key'
    elif layer_type == 'reasoning':
        vault_key = 'reasoning-api-key'
    elif layer_type == 'sentinel':
        vault_key = 'sentinel-api-key'

    rprint(Panel(f"[bold blue]Step 1: Choose Provider for {layer_type.upper()} Brain[/bold blue]"))
    
    choices = [
        "google (Gemini Cloud - Recommended)", 
        "local (Ollama/LocalAI - High Sovereignty)", 
        "openai-compat (External Backends)"
    ]
    if layer_type != "embedding":
        choices.insert(2, "codex (ChatGPT Backend via Codex)")

    ptype = questionary.select("Select Type:", choices=choices).ask()
    if not ptype: return
    
    actual_type = "google" if "google" in ptype else ("local" if "local" in ptype else ("codex" if "codex" in ptype else "openai-compat"))
    config['models'][provider_key] = actual_type

    # API Configuration
    if actual_type not in ["google", "codex"]:
        default_url = config['models'].get(endpoint_key, "http://localhost:11434")
        url = questionary.text("API Endpoint URL:", default=default_url).ask()
        if url: config['models'][endpoint_key] = url.strip()

    # Model Selection
    rprint(Panel(f"[bold blue]Step 2: Model Selection[/bold blue]"))
    default_model = "nomic-embed-text" if layer_type == "embedding" else "gemini-flash-latest"
    current_model = config['models'].get(model_key, default_model)
    model = questionary.text("Enter Model Name:", default=current_model).ask()
    if model: config['models'][model_key] = model.strip()

    # Auth Step
    if actual_type == "local":
        if questionary.confirm("Does this local provider require login?", default=False).ask():
            key = questionary.password("Paste Key/Token:").ask()
            if key: keyring.set_password("aim-system", vault_key, key.strip())
    elif actual_type == "codex":
        if questionary.confirm("Run 'codex login' now?", default=True).ask():
            try:
                subprocess.run(["codex", "login"], check=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                rprint("[bold red]Error:[/bold red] 'codex' command not found or login failed.")
                input("\nPress Enter...")
    else:
        key_name = "google-api-key" if actual_type == "google" else vault_key
        rprint(Panel("[bold green]🔐 Secure System Vault[/bold green]\nKeys are stored in your computer's encrypted Keychain."))
        key = questionary.password(f"Enter {actual_type} API Key:").ask()
        if key: keyring.set_password("aim-system", key_name, key.strip())

    save_config(config)
    input(f"\n{layer_type.capitalize()} brain configured. Press Enter...")

def manage_safety(config):
    mode = questionary.select(
        "Sentinel Strictness:",
        choices=["Full (AI Intent + Paths)", "Light (Paths Only)", "Disabled"]
    ).ask()
    config['settings']['sentinel_mode'] = "full" if "Full" in mode else ("path-only" if "Light" in mode else "disabled")
    save_config(config)
    rprint(f"[green]Sentinel updated to {config['settings']['sentinel_mode']}[/green]")
    input("\nPress Enter...")

def config_menu():
    config = load_config()
    while True:
        display_dashboard(config)
        choice = questionary.select(
            "Main Menu:",
            choices=[
                "Configure Search Brain (Memory/Embeddings)",
                "Configure Reasoning Brain (Summaries/Distillation)",
                "Configure Safety Brain (Intent Auditing)",
                "Configure Safety Sentinel Mode (Guardrails)",
                "Set Workspace Safety Root (Allowed Paths)",
                "Update Checkpoint Interval",
                "Exit"
            ]
        ).ask()

        if "Search" in choice: setup_provider_wizard(config, "embedding")
        elif "Reasoning" in choice: setup_provider_wizard(config, "reasoning")
        elif "Safety Brain" in choice: setup_provider_wizard(config, "sentinel")
        elif "Sentinel Mode" in choice: manage_safety(config)
        elif "Workspace" in choice:
            rprint(Panel("[bold blue]WORKSPACE SAFETY ROOT[/bold blue]\nAny path outside this root will be BLOCKED by the Sentinel."))
            current = config['settings'].get('allowed_root', BASE_DIR)
            root = questionary.text("Enter Allowed Root Path:", default=current).ask()
            if root and root.strip():
                config['settings']['allowed_root'] = root.strip()
                save_config(config)
                rprint(f"[green]Safety root updated to: {root}[/green]")
            input("\nPress Enter...")
        elif "Interval" in choice:
            interval = questionary.text("Interval (mins):", default=str(config['settings'].get('scrivener_interval_minutes', 30))).ask()
            if interval.isdigit(): 
                config['settings']['scrivener_interval_minutes'] = int(interval)
                save_config(config)
        elif "Exit" in choice or choice is None: break

if __name__ == "__main__":
    try: config_menu()
    except KeyboardInterrupt: sys.exit(0)
