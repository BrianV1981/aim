import os
import json
import sys

def find_aim_root():
    """Dynamically discovers the A.I.M. root directory."""
    # Start from the location of this utility file (src/config_utils.py)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")

def load_config():
    """Loads the core configuration file."""
    if not os.path.exists(CONFIG_PATH):
        # Fallback defaults if config hasn't been generated yet
        home = os.path.expanduser("~")
        return {
            "paths": {
                "aim_root": AIM_ROOT,
                "tmp_chats_dir": os.path.join(home, ".gemini/tmp/aim/chats")
            },
            "settings": {
                "allowed_root": home
            }
        }
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

CONFIG = load_config()
