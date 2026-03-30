#!/usr/bin/env python3
import os
import json
import sys
import subprocess
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# --- DYNAMIC ROOT DISCOVERY ---
def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core", "CONFIG.json")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

CONFIG = load_config()
console = Console()

tui_style = questionary.Style([
    ('qmark', 'fg:#FF9D00 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#5F819D bold'),
    ('pointer', 'fg:#FF9D00 bold'),
    ('highlighted', 'fg:#FF9D00 bold'),
    ('selected', 'fg:#5F819D'),
    ('separator', 'fg:#6C6C6C'),
    ('instruction', ''),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])

def test_provider(provider, model, endpoint, tier_name, auth_type):
    return True, "OK"

def setup_cognitive_tier(tier_name):
    rprint(f"Configuring {tier_name}...")

def main_menu():
    health_cache = {}
    while True:
        console.clear()
        rprint(Panel("[bold green]A.I.M. COCKPIT (Configuration TUI)[/bold green]\n[dim]Manage your sovereign cognitive exoskeleton[/dim]"))
        
        table = Table(title="Cognitive Tier Status", show_header=True, header_style="bold magenta")
        table.add_column("Tier", style="dim")
        table.add_column("Provider")
        table.add_column("Model")
        table.add_column("Status", justify="center")
        table.add_column("Diagnostics")

        tiers_config = CONFIG.get('models', {})
        tiers = ["default_reasoning", "tier1", "tier2", "tier3", "tier4", "tier5"]
        tier_labels = {
            "default_reasoning": "Primary (Cortex)",
            "tier1": "Tier 1: Harvester",
            "tier2": "Tier 2: Proposer",
            "tier3": "Tier 3: Refiner",
            "tier4": "Tier 4: Consolidator",
            "tier5": "Tier 5: Archivist"
        }
        for t in tiers:
            details = tiers_config.get(t, {"provider": "NOT SET", "model": "N/A"})
            status_indicator, diag_msg = health_cache.get(t, ("[white]○[/white]", ""))
            table.add_row(tier_labels.get(t, t), details['provider'], details['model'], status_indicator, diag_msg)
        rprint(table)
        
        choice = questionary.select(
            "Main Settings:",
            choices=[
                "1. Run Cognitive Health Check (Test All Tiers)",
                "2. Manage Secret Vault (API Keys)",
                "3. Configure Default Brain (Primary)",
                "4. Configure Cognitive Pipeline (T1-T5)",
                "5. Manage MCP Server (IDE Integration)",
                "6. Update Operator Profile & Behavior",
                "7. Update Obsidian Vault Path",
                "8. Archive Retention (Current: " + str(CONFIG.get('settings', {}).get('archive_retention_days', 30)) + "d)",
                "9. Auto-Memory Distillation (Current: " + CONFIG.get('settings', {}).get('auto_distill_tier', 'Off') + ")",
                "10. Set Agent Persona (Specialty Mandate)",
                "11. Configure Cognitive Mantra (Anti-Drift)",
                "12. Configure Handoff Context Tail",
                "13. Configure Waterfall Pipeline (Intervals & Cleanup)",
                "14. Reincarnation Protocol (Auto-Rebirth: " + ("ON" if CONFIG.get('settings', {}).get('auto_rebirth', False) else "OFF") + ")",
                "15. Exit"
            ],
            style=tui_style
        ).ask()

        if not choice or choice == "15. Exit": break
        
        if choice.startswith("1."):
            for t in tiers:
                details = tiers_config.get(t)
                if not details or details.get('provider') == "NOT SET":
                    health_cache[t] = ("[red]●[/red]", "NOT SET") 
                    continue
                success, msg = test_provider(details['provider'], details['model'], details.get('endpoint'), t, details.get('auth_type', 'API Key'))
                if success: health_cache[t] = ("[bold green]●[/bold green]", "OK")
                else: health_cache[t] = ("[bold red]●[/bold red]", str(msg)[:60])
        
        elif choice.startswith("4."):
            tier = questionary.select("Select Tier to Configure:", choices=tiers + ["Back"]).ask()
            if tier != "Back": setup_cognitive_tier(tier)

        elif choice.startswith("12."):
            current_tail = str(CONFIG.get('settings', {}).get('handoff_context_lines', 0))
            tail_input = questionary.text("Context Tail (Max Lines, 0 for Full):", default=current_tail).ask()
            if tail_input and tail_input.isdigit():
                CONFIG.setdefault('settings', {})['handoff_context_lines'] = int(tail_input)
                save_config(CONFIG)

        elif choice.startswith("13."):
            rprint("\n[cyan]--- Configure Waterfall Refinement Pipeline ---[/cyan]")
            pipeline_config = CONFIG.get('memory_pipeline', {
                'intervals': {'tier1': 1, 'tier2': 12, 'tier3': 24, 'tier4': 72, 'tier5': 144},
                'cleanup_mode': 'archive'
            })
            
            sub_choice = questionary.select(
                "Memory Pipeline Settings:",
                choices=[
                    "Set Tier Intervals (Hours)",
                    f"Toggle Cleanup Mode (Current: {pipeline_config.get('cleanup_mode', 'archive').upper()})",
                    "Back"
                ],
                style=tui_style
            ).ask()

            if sub_choice == "Set Tier Intervals (Hours)":
                intervals = pipeline_config.get('intervals', {})
                new_intervals = {}
                for t in ['tier1', 'tier2', 'tier3', 'tier4', 'tier5']:
                    val = questionary.text(f"Interval for {t.upper()} (Hours):", default=str(intervals.get(t, 0))).ask()
                    if val and val.isdigit(): new_intervals[t] = int(val)
                    else: new_intervals[t] = intervals.get(t, 0)
                CONFIG.setdefault('memory_pipeline', {})['intervals'] = new_intervals
                save_config(CONFIG)
                rprint("[green]Intervals updated.[/green]")
                import time; time.sleep(1)

            elif sub_choice and sub_choice.startswith("Toggle"):
                current = pipeline_config.get('cleanup_mode', 'archive')
                new_mode = "delete" if current == "archive" else "archive"
                CONFIG.setdefault('memory_pipeline', {})['cleanup_mode'] = new_mode
                save_config(CONFIG)
                rprint(f"[green]Cleanup mode toggled to {new_mode.upper()}.[/green]")
                import time; time.sleep(1)

        elif choice.startswith("14."):
            current_rebirth = CONFIG.get('settings', {}).get('auto_rebirth', False)
            toggle = questionary.confirm("Enable Auto-Rebirth?", default=current_rebirth).ask()
            if toggle is not None:
                CONFIG.setdefault('settings', {})['auto_rebirth'] = toggle
                save_config(CONFIG)

if __name__ == "__main__":
    try: main_menu()
    except KeyboardInterrupt: sys.exit(0)
