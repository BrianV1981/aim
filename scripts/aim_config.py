#!/usr/bin/env python3
import os
import json
import questionary
import keyring
import sys
import subprocess
import time
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

# --- PROVIDER DATA ---
PROVIDER_MAP = {
    "Google Cloud (API Key)": {
        "id": "google",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro", "text-embedding-004"],
        "endpoint": "https://generativelanguage.googleapis.com",
        "auth": "api-key"
    },
    "Gemini CLI (OAuth)": {
        "id": "gemini-cli",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro", "Auto (Gemini 3)"],
        "endpoint": None,
        "auth": "oauth"
    },
    "ChatGPT / Codex (OAuth)": {
        "id": "codex",
        "models": ["gpt-5.4", "o3-mini", "o1-preview"],
        "endpoint": None,
        "auth": "oauth"
    },
    "OpenAI (API Key)": {
        "id": "openai-compat",
        "models": ["gpt-4o", "gpt-4-turbo", "text-embedding-3-small"],
        "endpoint": "https://api.openai.com/v1",
        "auth": "api-key"
    },
    "Ollama": {
        "id": "local",
        "models": ["llama3", "mistral", "nomic-embed-text", "phi3"],
        "endpoint": "http://localhost:11434",
        "auth": "none"
    }
}

def get_ollama_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]
            return [line.split()[0] for line in lines if line]
    except: pass
    return None

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def display_dashboard(config):
    console.clear()
    rprint(Panel.fit("[bold cyan]A.I.M. CONTROL COCKPIT[/bold cyan] v1.1", subtitle="Sovereign Intelligence Panel", border_style="bright_blue"))
    
    brain_table = Table(title="🧠 Brain Stack", show_header=True, header_style="bold magenta", expand=True)
    brain_table.add_column("System", style="dim")
    brain_table.add_column("Provider", style="yellow")
    brain_table.add_column("Active Model", style="green")
    
    brain_table.add_row("Memory (Search)", config['models'].get('embedding_provider', 'local').upper(), config['models'].get('embedding', '---'))
    brain_table.add_row("Reasoning (Log)", config['models'].get('reasoning_provider', 'google').upper(), config['models'].get('reasoning_model', '---'))
    brain_table.add_row("Safety (Sentinel)", config['models'].get('sentinel_provider', 'google').upper(), config['models'].get('sentinel_model', '---'))
    rprint(brain_table)
    
    ops_table = Table(title="⚙️ Settings", show_header=False, box=None, expand=True)
    ops_table.add_column("Key", style="dim")
    ops_table.add_column("Value")
    
    vault_path = config['settings'].get('obsidian_vault_path') or "[NOT CONFIGURED]"
    ops_table.add_row("Sentinel Mode:", f"[bold]{config['settings'].get('sentinel_mode', 'full').upper()}[/bold]")
    ops_table.add_row("Safety Root:", f"[dim]{config['settings'].get('allowed_root', BASE_DIR)}[/dim]")
    ops_table.add_row("Obsidian Vault:", f"[cyan]{vault_path}[/cyan]")
    rprint(ops_table)
    rprint("[dim]" + "="*60 + "[/dim]")

def setup_provider_wizard(config, layer_type):
    is_mem = (layer_type == "embedding")
    provider_key = 'embedding_provider' if is_mem else f'{layer_type}_provider'
    model_key = 'embedding' if is_mem else f'{layer_type}_model'
    endpoint_key = 'embedding_endpoint' if is_mem else f'{layer_type}_endpoint'
    vault_key = f'{layer_type}-api-key'

    rprint(Panel(f"[bold blue]Configure {layer_type.upper()} Layer[/bold blue]"))
    
    p_name = questionary.select("Select Provider Type:", choices=list(PROVIDER_MAP.keys()) + ["Cancel"]).ask()
    if p_name == "Cancel" or not p_name: return
    p_data = PROVIDER_MAP[p_name]
    
    model_choices = p_data["models"]
    if p_name == "Ollama":
        local_mods = get_ollama_models()
        if local_mods: model_choices = local_mods
    
    model = questionary.select(f"Select Model for {p_name}:", choices=model_choices + ["Custom / Other", "Back"]).ask()
    if model == "Back": return setup_provider_wizard(config, layer_type)
    if model == "Custom / Other":
        model = questionary.text("Enter Model Name:").ask()
    if not model: return

    url = p_data["endpoint"]
    if p_data["id"] in ["local", "openai-compat"]:
        custom_url = questionary.text(f"Endpoint URL (Default: {url}):", default=url or "").ask()
        if custom_url: url = custom_url

    config['models'][provider_key] = p_data["id"]
    config['models'][model_key] = model
    if url: config['models'][endpoint_key] = url
    elif endpoint_key in config['models']: del config['models'][endpoint_key]
    save_config(config)

    if p_data["auth"] == "api-key":
        key_name = "google-api-key" if p_data["id"] == "google" else vault_key
        rprint(f"[yellow]Requires API Key in vault: {key_name}[/yellow]")
        if questionary.confirm("Set API Key now?").ask():
            key = questionary.password("Paste Key:").ask()
            if key: keyring.set_password("aim-system", key_name, key.strip())
    elif p_data["auth"] == "oauth":
        cli_cmd = "gemini" if p_data["id"] == "gemini-cli" else "codex login"
        rprint(f"\n[bold yellow]TERMINAL HANDOFF[/bold yellow]")
        rprint(f"Launching external CLI for authentication: '{cli_cmd}'")
        rprint("[dim]A.I.M. will pause. Exit that CLI to return here.[/dim]")
        
        if questionary.confirm(f"Launch {cli_cmd} now?").ask():
            console.clear()
            try:
                subprocess.call(cli_cmd.split())
            except KeyboardInterrupt: pass
            except Exception as e:
                rprint(f"[red]Error launching CLI: {e}[/red]")
                time.sleep(2)

    rprint(f"[green]Success: {layer_type.capitalize()} configuration saved.[/green]")
    time.sleep(1)

def manage_safety(config):
    mode = questionary.select("Sentinel Strictness:", choices=["Full (AI Intent + Paths)", "Light (Paths Only)", "Disabled"]).ask()
    if not mode: return
    config['settings']['sentinel_mode'] = "full" if "Full" in mode else ("path-only" if "Light" in mode else "disabled")
    save_config(config)
    rprint(f"[green]Sentinel updated to {config['settings']['sentinel_mode']}[/green]")
    time.sleep(1)

def config_menu():
    while True:
        config = load_config()
        display_dashboard(config)
        choice = questionary.select("Main Menu:", choices=["1. Configure Memory Layer", "2. Configure Reasoning Brain", "3. Configure Safety Brain", "4. Manage Sentinel Mode", "5. Manage Obsidian Backup Path", "6. Manage Workspace Root", "7. Update Checkpoint Interval", "Exit"]).ask()
        if not choice or "Exit" in choice: break
        try:
            if "1." in choice: setup_provider_wizard(config, "embedding")
            elif "2." in choice: setup_provider_wizard(config, "reasoning")
            elif "3." in choice: setup_provider_wizard(config, "sentinel")
            elif "4." in choice: manage_safety(config)
            elif "5." in choice:
                current = config['settings'].get('obsidian_vault_path', "")
                path = questionary.text("Enter Vault Path:", default=current).ask()
                if path is not None:
                    config['settings']['obsidian_vault_path'] = path.strip()
                    save_config(config); rprint("[green]Obsidian path updated.[/green]")
                    time.sleep(1)
            elif "6." in choice:
                current = config['settings'].get('allowed_root', BASE_DIR)
                root = questionary.text("Enter Allowed Root Path:", default=current).ask()
                if root:
                    config['settings']['allowed_root'] = root.strip()
                    save_config(config); rprint("[green]Safety root updated.[/green]")
                    time.sleep(1)
            elif "7." in choice:
                interval = questionary.text("Interval (mins):", default=str(config['settings'].get('scrivener_interval_minutes', 30))).ask()
                if interval and interval.isdigit(): 
                    config['settings']['scrivener_interval_minutes'] = int(interval)
                    save_config(config)
        except KeyboardInterrupt: continue

if __name__ == "__main__":
    try: config_menu()
    except KeyboardInterrupt: sys.exit(0)
