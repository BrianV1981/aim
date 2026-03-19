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
    print(f"Checking for {name}...")
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"[OK] {name} found.")
        return True
    except:
        print(f"[ERROR] {name} not found. Please install it first.")
        return False

def init_workspace():
    print("\n--- A.I.M. Initialization ---")
    
    # 1. Scaffolding
    dirs = [
        "memory/proposals",
        "memory/archive",
        "archive/raw",
        "archive/index",
        "continuity",
        "workstreams",
        "hooks",
        "scripts"
    ]
    for d in dirs:
        path = os.path.join(BASE_DIR, d)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"Created directory: {d}")

    # 2. Config Initialization
    config_path = os.path.join(CORE_DIR, "CONFIG.json")
    if not os.path.exists(config_path):
        print("Initializing CONFIG.json from template...")
        with open(os.path.join(TEMPLATE_DIR, "CONFIG.json.template"), 'r') as f:
            config = f.read()
        
        # Simple replacements
        home = os.path.expanduser("~")
        gemini_tmp = os.path.join(home, ".gemini/tmp/aim/chats")
        config = config.replace("[AIM_ROOT_PATH]", BASE_DIR)
        config = config.replace("[HOME_DIR]", home)
        config = config.replace("[GEMINI_TMP_PATH]", gemini_tmp)
        
        with open(config_path, 'w') as f:
            f.write(config)
        print("[OK] CONFIG.json initialized.")

    # 3. Memory Initialization
    memory_path = os.path.join(CORE_DIR, "MEMORY.md")
    if not os.path.exists(memory_path):
        print("Initializing MEMORY.md from template...")
        shutil.copy2(os.path.join(TEMPLATE_DIR, "MEMORY.md.template"), memory_path)
        print("[OK] MEMORY.md initialized.")

    print("\n[SUCCESS] A.I.M. workspace initialized.")
    print("Next step: Run 'aim tui' to configure your API keys and providers.")

if __name__ == "__main__":
    deps = [
        (["ollama", "--version"], "Ollama"),
        (["gemini", "--version"], "Gemini CLI")
    ]
    all_ok = True
    for cmd, name in deps:
        if not check_dependency(cmd, name):
            all_ok = False
    
    if all_ok or "--force" in sys.argv:
        init_workspace()
    else:
        print("\nInitialization aborted due to missing dependencies.")
        sys.exit(1)
