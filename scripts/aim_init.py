#!/usr/bin/env python3
import os
import json
import subprocess
import shutil
import sys

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = os.path.join(BASE_DIR, "core")
TEMPLATE_DIR = os.path.join(CORE_DIR, "templates")

def check_dependency(cmd, name):
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except:
        return False

def uninstall():
    print("\n--- A.I.M. Uninstallation ---")
    print("To fully uninstall A.I.M.:")
    print(f"1. Remove the 'aim' alias from your .bashrc or .zshrc.")
    print(f"2. Delete the directory: {BASE_DIR}")
    print("\n[NOTE] Your system vault (keyring) still contains your API keys.")
    print("To clear them, run: python3 -c \"import keyring; keyring.delete_password('aim-system', 'google-api-key')\"")
    sys.exit(0)

def init_workspace(reinstall=False):
    print("\n--- A.I.M. Initialization ---")
    
    # 1. Scaffolding
    dirs = [
        "memory/proposals", "memory/archive", "archive/raw", "archive/index", 
        "continuity", "workstreams", "hooks", "scripts", "core/templates"
    ]
    for d in dirs:
        path = os.path.join(BASE_DIR, d)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"Created directory: {d}")

    # 2. Config Initialization
    config_path = os.path.join(CORE_DIR, "CONFIG.json")
    if not os.path.exists(config_path) or reinstall:
        print(f"{'Re-initializing' if reinstall else 'Initializing'} CONFIG.json from template...")
        template_path = os.path.join(TEMPLATE_DIR, "CONFIG.json.template")
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                config = f.read()
            
            home = os.path.expanduser("~")
            gemini_tmp = os.path.join(home, ".gemini/tmp/aim/chats")
            config = config.replace("[AIM_ROOT_PATH]", BASE_DIR)
            config = config.replace("[HOME_DIR]", home)
            config = config.replace("[GEMINI_TMP_PATH]", gemini_tmp)
            
            with open(config_path, 'w') as f:
                f.write(config)
            print("[OK] CONFIG.json initialized.")
        else:
            print("[ERROR] Template not found.")

    # 3. Memory Initialization
    memory_path = os.path.join(CORE_DIR, "MEMORY.md")
    if not os.path.exists(memory_path) or reinstall:
        print(f"{'Re-initializing' if reinstall else 'Initializing'} MEMORY.md from template...")
        template_path = os.path.join(TEMPLATE_DIR, "MEMORY.md.template")
        if os.path.exists(template_path):
            shutil.copy2(template_path, memory_path)
            print("[OK] MEMORY.md initialized.")

    print("\n[SUCCESS] A.I.M. workspace ready.")
    print("Action: Run 'aim tui' to finalize your provider settings.")

if __name__ == "__main__":
    if "--uninstall" in sys.argv:
        uninstall()
    
    reinstall_mode = "--reinstall" in sys.argv
    
    deps = [
        (["ollama", "--version"], "Ollama"),
        (["gemini", "--version"], "Gemini CLI")
    ]
    
    all_ok = True
    for cmd, name in deps:
        if not check_dependency(cmd, name):
            print(f"[WARNING] {name} not detected.")
            all_ok = False
    
    if all_ok or "--force" in sys.argv or reinstall_mode:
        init_workspace(reinstall=reinstall_mode)
    else:
        print("\nInitialization aborted. Use --force to proceed anyway.")
        sys.exit(1)
