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
    
    # Brain Summary Table
    table = Table(title="The A.I.M. Hybrid Brain", show_header=True, header_style="bold magenta")
    table.add_column("System Layer", style="dim")
    table.add_column("Provider", style="yellow")
    table.add_column("Active Model", style="green")
    
    table.add_row(
        "Memory (Embeddings)", 
        config['models'].get('embedding_provider', 'local').upper(),
        config['models'].get('embedding', 'nomic-embed-text')
    )
    table.add_row(
        "Reasoning (Thinking)", 
        config['models'].get('reasoning_provider', 'google').upper(),
        config['models'].get('reasoning_model', 'gemini-flash-latest')
    )
    
    rprint(table)
    
    # Settings Summary
    table_ops = Table(show_header=False, box=None)
    table_ops.add_row("[dim]Host Interface:[/dim]", f"[bold]{config['settings'].get('host_interface', 'gemini').upper()}[/bold]")
    table_ops.add_row("[dim]Sentinel Mode:[/dim]", f"[bold]{config['settings'].get('sentinel_mode', 'full').upper()}[/bold]")
    table_ops.add_row("[dim]Interval:[/dim]", f"{config['settings'].get('scrivener_interval_minutes', 30)} mins")
    
    rprint(table_ops)
    rprint("-" * 40)

def setup_provider_wizard(config, layer_type):
    """Step-by-step wizard to configure a provider."""
    is_memory = (layer_type == "memory")
    provider_key = 'embedding_provider' if is_memory else 'reasoning_provider'
    model_key = 'embedding' if is_memory else 'reasoning_model'
    endpoint_key = 'embedding_endpoint' if is_memory else 'reasoning_endpoint'
    vault_key = 'embedding-api-key' if is_memory else 'reasoning-api-key'

    rprint(Panel(f"[bold blue]STEP 1: SELECT PROVIDER TYPE[/bold blue]\nWhere should the {layer_type} logic run?"))
    choices = ["google (Gemini Cloud)", "local (Ollama/LocalAI)", "openai-compat (Universal Adapter)"]
    if not is_memory: choices.insert(2, "codex (ChatGPT Cloud)")

    ptype = questionary.select("Select Type:", choices=choices).ask()
    if not ptype: return
    
    actual_type = "google" if "google" in ptype else ("local" if "local" in ptype else ("codex" if "codex" in ptype else "openai-compat"))
    config['models'][provider_key] = actual_type

    # STEP 2: ENDPOINT
    if actual_type not in ["google", "codex"]:
        rprint(Panel(f"[bold blue]STEP 2: API ENDPOINT[/bold blue]\nURL of your AI service."))
        default_url = "http://localhost:11434" if actual_type == "local" else "https://api.example.com/v1"
        url = questionary.text("Enter URL:", default=config['models'].get(endpoint_key, default_url)).ask()
        if url: config['models'][endpoint_key] = url.strip()

    # STEP 3: MODEL NAME
    rprint(Panel(f"[bold blue]STEP 3: MODEL NAME[/bold blue]\nSpecific model identifier."))
    default_model = "nomic-embed-text" if is_memory else "llama3"
    if actual_type == "google": default_model = "models/gemini-embedding-2-preview" if is_memory else "gemini-flash-latest"
    elif actual_type == "codex": default_model = "gpt-4o"
    
    model = questionary.text("Enter Model Name:", default=config['models'].get(model_key, default_model)).ask()
    if model: config['models'][model_key] = model.strip()

    # STEP 4: AUTH
    if actual_type == "local":
        if questionary.confirm("Does this local provider require an API Key/Signin?", default=False).ask():
            auth_choice = questionary.select("Method:", choices=["OAuth (ollama signin)", "Manual Key"]).ask()
            if "OAuth" in auth_choice: subprocess.run(["ollama", "signin"])
            else:
                key = questionary.password("Paste Key:").ask()
                if key: keyring.set_password("aim-system", vault_key, key.strip())
    elif actual_type == "codex":
        if questionary.confirm("Run 'codex login' now?", default=True).ask(): subprocess.run(["codex", "login"])
    else:
        key_name = "google-api-key" if actual_type == "google" else vault_key
        key = questionary.password(f"Paste {actual_type} Key:").ask()
        if key: keyring.set_password("aim-system", key_name, key.strip())

    save_config(config)
    input("\nConfiguration saved. Press Enter...")

def manage_safety(config):
    rprint(Panel("[bold blue]SAFETY SENTINEL SETTINGS[/bold blue]"))
    mode = questionary.select(
        "Select Sentinel Strictness:",
        choices=[
            "Full (AI Intent Audit + Path Protection)",
            "Light (Path Protection Only - No AI)",
            "Disabled (NOT RECOMMENDED)"
        ]
    ).ask()
    
    if "Full" in mode: config['settings']['sentinel_mode'] = "full"
    elif "Light" in mode: config['settings']['sentinel_mode'] = "path-only"
    else: config['settings']['sentinel_mode'] = "disabled"
    
    save_config(config)
    rprint(f"[green]Safety mode updated to {config['settings']['sentinel_mode']}[/green]")
    input("\nPress Enter...")

def manage_host(config):
    rprint(Panel("[bold blue]HOST INTERFACE SETTINGS[/bold blue]\nWhich CLI are you using A.I.M. with?"))
    host = questionary.select(
        "Select Host CLI:",
        choices=["gemini (Default)", "codex (ChatGPT)", "claude (Anthropic)", "other"]
    ).ask()
    
    config['settings']['host_interface'] = host.split(" ")[0].lower()
    save_config(config)
    rprint(f"[green]Host interface set to {config['settings']['host_interface']}[/green]")
    input("\nPress Enter...")

def config_menu():
    config = load_config()
    while True:
        display_dashboard(config)
        choice = questionary.select(
            "Main Menu:",
            choices=[
                "Configure Memory Layer (Embeddings)",
                "Configure Reasoning Layer (AI Summaries)",
                "Configure Safety Sentinel (Guardrails)",
                "Configure Host Interface (Gemini/Codex/Claude)",
                "Update Distillation Interval",
                "Exit"
            ]
        ).ask()

        if "Memory" in choice: setup_provider_wizard(config, "memory")
        elif "Reasoning" in choice: setup_provider_wizard(config, "reasoning")
        elif "Safety" in choice: manage_safety(config)
        elif "Host" in choice: manage_host(config)
        elif "Interval" in choice:
            interval = questionary.text("Interval (mins):", default=str(config['settings'].get('scrivener_interval_minutes', 30))).ask()
            if interval.isdigit(): config['settings']['scrivener_interval_minutes'] = int(interval); save_config(config)
        elif "Exit" in choice or choice is None: break

if __name__ == "__main__":
    try: config_menu()
    except KeyboardInterrupt: sys.exit(0)
