import os
import json
import sys
import getpass

def _merge_defaults(target, defaults):
    changed = False
    for key, value in defaults.items():
        if key not in target:
            target[key] = value
            changed = True
        elif isinstance(value, dict) and isinstance(target.get(key), dict):
            if _merge_defaults(target[key], value):
                changed = True
    return changed

def find_aim_root():
    """
    Dynamically discovers the A.I.M. root directory.
    First checks the current working directory to support isolated workspaces.
    Falls back to the physical installation directory.
    """
    # 1. Check current directory and parents (Dynamic Workspace Isolation)
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core", "CONFIG.json")):
            return current
        current = os.path.dirname(current)
        
    # 2. Fallback to physical installation path (Global Execution)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

def load_config():
    """Loads, validates, and auto-repairs paths for the current machine."""
    home = os.path.expanduser("~")
    
    # Baseline defaults for a fresh system
    default_config = {
        "paths": {
            "aim_root": AIM_ROOT,
            "core_dir": os.path.join(AIM_ROOT, "core"),
            "docs_dir": os.path.join(AIM_ROOT, "docs"),
            "hooks_dir": os.path.join(AIM_ROOT, "hooks"),
            "archive_raw_dir": os.path.join(AIM_ROOT, "archive/raw"),
            "continuity_dir": os.path.join(AIM_ROOT, "continuity"),
            "src_dir": os.path.join(AIM_ROOT, "src"),
            "tmp_chats_dir": os.path.join(home, f".gemini/tmp/{os.path.basename(AIM_ROOT)}/chats")
        },
        "models": {
            "embedding_provider": "local",
            "embedding": "nomic-embed-text",
            "embedding_endpoint": "http://localhost:11434/api/embeddings",
            "tiers": {
                "default_reasoning": {
                    "provider": "google",
                    "model": "gemini-flash-latest",
                    "endpoint": "https://generativelanguage.googleapis.com",
                    "auth_type": "API Key"
                },
                "librarian": {
                    "provider": "google",
                    "model": "gemini-flash-latest",
                    "endpoint": "https://generativelanguage.googleapis.com",
                    "auth_type": "API Key"
                },
                "chancellor": {
                    "provider": "google",
                    "model": "gemini-flash-latest",
                    "endpoint": "https://generativelanguage.googleapis.com",
                    "auth_type": "API Key"
                },
                "dean": {
                    "provider": "google",
                    "model": "gemini-flash-latest",
                    "endpoint": "https://generativelanguage.googleapis.com",
                    "auth_type": "API Key"
                }
            }
        },
        "settings": {
            "allowed_root": home,
            "semantic_pruning_threshold": 0.85,
            "scrivener_interval_minutes": 30,
            "archive_retention_days": 30,
            "sentinel_mode": "full",
            "obsidian_vault_path": "",
            "auto_distill_tier": "T4",
            "auto_rebirth": False
        }
    }

    if not os.path.exists(CONFIG_PATH):
        return default_config

    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        changed = False
        
        # --- THE PORTABILITY SHIELD ---
        # If the root in the file doesn't match the current directory, 
        # we RE-CALCULATE everything based on the current system.
        if config.get('paths', {}).get('aim_root') != AIM_ROOT:
            sys.stderr.write(f"[PORTABILITY] System shift detected. Re-mapping paths for this machine...\n")
            
            config['paths']['aim_root'] = AIM_ROOT
            for key in ['core_dir', 'docs_dir', 'hooks_dir', 'memory_dir', 'archive_raw_dir', 'archive_index_dir', 'continuity_dir', 'src_dir']:
                config['paths'][key] = os.path.join(AIM_ROOT, key.replace('_dir', ''))
            
            # Recalculate home-based paths
            config['paths']['tmp_chats_dir'] = os.path.join(home, f".gemini/tmp/{os.path.basename(AIM_ROOT)}/chats")
            
            # If we have an Obsidian path, we only update it if it started with /home/
            old_vault = config['settings'].get('obsidian_vault_path', "")
            if old_vault.startswith("/home/"):
                # Extract the old user part and replace it with current
                parts = old_vault.split('/')
                if len(parts) > 2:
                    new_vault = os.path.join(home, *parts[3:])
                    config['settings']['obsidian_vault_path'] = new_vault

            changed = True

        if _merge_defaults(config, default_config):
            changed = True

        if changed:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
                
        return config
    except Exception:
        return default_config

CONFIG = load_config()
