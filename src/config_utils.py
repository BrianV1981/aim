import os
import json
import sys
import getpass

def find_aim_root():
    """
    Dynamically discovers the A.I.M. root directory based on the 
    location of this script, ensuring portability across PCs.
    """
    # config_utils.py is in aim/src/, so root is two levels up
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
            "memory_dir": os.path.join(AIM_ROOT, "memory"),
            "archive_raw_dir": os.path.join(AIM_ROOT, "archive/raw"),
            "archive_index_dir": os.path.join(AIM_ROOT, "archive/index"),
            "continuity_dir": os.path.join(AIM_ROOT, "continuity"),
            "src_dir": os.path.join(AIM_ROOT, "src"),
            "tmp_chats_dir": os.path.join(home, ".gemini/tmp/aim/chats")
        },
        "models": {
            "embedding_provider": "local",
            "embedding": "nomic-embed-text",
            "embedding_endpoint": "http://localhost:11434/api/embeddings",
            "reasoning_provider": "google",
            "reasoning_model": "gemini-flash-latest",
            "sentinel_provider": "google",
            "sentinel_model": "gemini-flash-latest"
        },
        "settings": {
            "allowed_root": home,
            "semantic_pruning_threshold": 0.85,
            "scrivener_interval_minutes": 30,
            "archive_retention_days": 30,
            "sentinel_mode": "full",
            "obsidian_vault_path": ""
        }
    }

    if not os.path.exists(CONFIG_PATH):
        return default_config

    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        
        # --- THE PORTABILITY SHIELD ---
        # If the root in the file doesn't match the current directory, 
        # we RE-CALCULATE everything based on the current system.
        if config.get('paths', {}).get('aim_root') != AIM_ROOT:
            sys.stderr.write(f"[PORTABILITY] System shift detected. Re-mapping paths for this machine...\n")
            
            config['paths']['aim_root'] = AIM_ROOT
            for key in ['core_dir', 'docs_dir', 'hooks_dir', 'memory_dir', 'archive_raw_dir', 'archive_index_dir', 'continuity_dir', 'src_dir']:
                config['paths'][key] = os.path.join(AIM_ROOT, key.replace('_dir', ''))
            
            # Recalculate home-based paths
            config['paths']['tmp_chats_dir'] = os.path.join(home, ".gemini/tmp/aim/chats")
            
            # If we have an Obsidian path, we only update it if it started with /home/
            old_vault = config['settings'].get('obsidian_vault_path', "")
            if old_vault.startswith("/home/"):
                # Extract the old user part and replace it with current
                parts = old_vault.split('/')
                if len(parts) > 2:
                    new_vault = os.path.join(home, *parts[3:])
                    config['settings']['obsidian_vault_path'] = new_vault

            # Save the corrected paths to the local CONFIG.json
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)
                
        return config
    except Exception:
        return default_config

CONFIG = load_config()
