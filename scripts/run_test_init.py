#!/usr/bin/env python3
import subprocess
import os
import sys

# --- CONFIG ---
SANDBOX_DIR = os.path.expanduser("~/aim_test_sandbox")
INIT_SCRIPT = os.path.join(SANDBOX_DIR, "scripts/aim_init.py")

def run_test():
    print(f"--- Running Installer Simulation in {SANDBOX_DIR} ---")
    
    # Simulate user inputs
    inputs = [
        "Test User",           # Name
        "Rust, Solana",        # Tech Stack
        "Practical and Direct", # Style
        "/home/kingb/test_vault", # Obsidian
        "/home/kingb/aim_test_sandbox" # Safety Root
    ]
    input_str = "\n".join(inputs) + "\n"
    
    try:
        # We use sys.executable to ensure we use the same python
        process = subprocess.Popen(
            [sys.executable, INIT_SCRIPT],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=SANDBOX_DIR
        )
        stdout, stderr = process.communicate(input=input_str)
        
        print("\n--- STDOUT ---")
        print(stdout)
        
        if stderr:
            print("\n--- STDERR ---")
            print(stderr)
            
        print("\n--- AUDIT: VERIFYING FILES ---")
        targets = ["core/USER.md", "core/MEMORY.md", "docs/ROADMAP.md", "core/CONFIG.json"]
        for t in targets:
            path = os.path.join(SANDBOX_DIR, t)
            if os.path.exists(path):
                print(f"[PASS] Created: {t}")
                if t.startswith("docs/"):
                    with open(path, 'r') as f:
                        if "RAG STATUS" in f.read():
                            print(f"  -> [PASS] Disclaimer found in {t}")
            else:
                print(f"[FAIL] Missing: {t}")

    except Exception as e:
        print(f"Simulation failed: {e}")

if __name__ == "__main__":
    run_test()
