#!/usr/bin/env python3
import os
import sys
import glob
import time
import zipfile
import json
import hashlib
import shutil
from datetime import datetime

def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

AIM_ROOT = find_aim_root()
QUARANTINE_DIR = os.path.join(AIM_ROOT, "archive", "quarantine")
IMPORT_DIR = os.path.join(AIM_ROOT, "archive", "tmp_engram_import")
PULSE_PATH = os.path.join(AIM_ROOT, "continuity", "CURRENT_PULSE.md")
EXCHANGE_SCRIPT = os.path.join(AIM_ROOT, "src", "plugins", "datajack", "aim_exchange.py")
VENV_PYTHON = os.path.join(AIM_ROOT, "venv", "bin", "python3")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

def scan_for_prompt_injections(content):
    """Heuristic scan for known adversarial prompt injections."""
    bad_patterns = [
        "ignore previous instructions",
        "you are now",
        "speed optimization",
        "do it quickly",
        "forget your mandates"
    ]
    content_lower = content.lower()
    for pattern in bad_patterns:
        if pattern in content_lower:
            return True
    return False

def warn_operator(filename, reason):
    """Writes a fatal warning to CURRENT_PULSE.md."""
    if not os.path.exists(PULSE_PATH):
        return
        
    warning = f"\n\n### 🚨 [QUARANTINE DAEMON ALERT] 🚨\n"
    warning += f"**BLOCKED SWAWM ATTACK:** The cartridge `{filename}` was intercepted and destroyed.\n"
    warning += f"**Reason:** {reason}\n"
    warning += f"**Action Taken:** The Engram DB remains secure. The payload was purged.\n"
    
    with open(PULSE_PATH, 'a') as f:
        f.write(warning)

def process_quarantine():
    """Scans the quarantine directory for .engram files and validates them."""
    if not os.path.exists(QUARANTINE_DIR):
        return
        
    engrams = glob.glob(os.path.join(QUARANTINE_DIR, "*.engram"))
    for engram in engrams:
        filename = os.path.basename(engram)
        print(f"[QUARANTINE] Scanning payload: {filename}...")
        
        sandbox_dir = os.path.join(QUARANTINE_DIR, f"sandbox_{int(time.time())}")
        os.makedirs(sandbox_dir, exist_ok=True)
        
        try:
            # 1. Structure Validation
            try:
                with zipfile.ZipFile(engram, 'r') as zf:
                    zf.extractall(sandbox_dir)
            except zipfile.BadZipFile:
                print(f"[QUARANTINE] FATAL: Invalid zip archive.")
                warn_operator(filename, "Corrupted Zip Archive")
                raise ValueError("BadZipFile")
                
            metadata_path = os.path.join(sandbox_dir, "metadata.json")
            if not os.path.exists(metadata_path):
                print(f"[QUARANTINE] FATAL: Missing metadata.json.")
                warn_operator(filename, "Missing structural metadata")
                raise ValueError("NoMetadata")
                
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                
            expected_hash = metadata.get("payload_hash")
            if not expected_hash:
                print(f"[QUARANTINE] FATAL: Missing payload_hash.")
                warn_operator(filename, "Missing cryptographic signature")
                raise ValueError("NoHash")
                
            # 2. Checksum Verification
            hasher = hashlib.sha256()
            chunk_files = sorted(glob.glob(os.path.join(sandbox_dir, "chunks", "*.jsonl")))
            
            for chunk_file in chunk_files:
                with open(chunk_file, 'rb') as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
                        
            actual_hash = hasher.hexdigest()
            if actual_hash != expected_hash:
                print(f"[QUARANTINE] FATAL: Hash mismatch! Expected {expected_hash}, got {actual_hash}")
                warn_operator(filename, "Cryptographic Hash Mismatch (Tampered Payload)")
                raise ValueError("HashMismatch")
                
            # 3. Prompt Injection Heuristics
            for chunk_file in chunk_files:
                with open(chunk_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if scan_for_prompt_injections(content):
                        print(f"[QUARANTINE] FATAL: Adversarial prompt injection detected!")
                        warn_operator(filename, "Adversarial Prompt Injection (Instruction Drift Vector)")
                        raise ValueError("PromptInjection")
                        
            # If we reach here, the cartridge is CLEAN.
            print(f"[QUARANTINE] SUCCESS: Cartridge {filename} is pristine. Forwarding to DataJack...")
            
            # Move to import dir (or just call exchange directly on the engram, but we want to simulate
            # moving it to the active import flow). Actually aim_exchange takes the engram path.
            # But wait, aim_exchange.py handles unzipping and hash verifying AGAIN.
            # That's fine, defense in depth.
            import subprocess
            subprocess.run([VENV_PYTHON, EXCHANGE_SCRIPT, "import", engram], check=True)
            
            # Clean up the original engram since it was successfully imported
            os.remove(engram)

        except Exception as e:
            # Purge the poisoned engram
            if os.path.exists(engram):
                os.remove(engram)
        finally:
            if os.path.exists(sandbox_dir):
                shutil.rmtree(sandbox_dir)

if __name__ == "__main__":
    process_quarantine()
