#!/usr/bin/env python3
import os
import sys
import json
import keyring
from cryptography.fernet import Fernet
import glob

def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core", "CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
BLACKBOX_DIR = os.path.join(AIM_ROOT, "archive", ".raw_jsonl_blackbox")

def get_or_create_key():
    """
    Retrieves the Black Box encryption key from the secure OS Keyring.
    Generates a new one if it does not exist.
    """
    SERVICE = "aim-system"
    ACCOUNT = "blackbox-key"
    
    key = keyring.get_password(SERVICE, ACCOUNT)
    if not key:
        print("[VAULT] Generating new cryptographic key for the Immutable Black Box...")
        key = Fernet.generate_key().decode('utf-8')
        keyring.set_password(SERVICE, ACCOUNT, key)
    return key.encode('utf-8')

def vault_session(jsonl_path):
    """
    Encrypts an untouched, raw .jsonl session flight recorder and locks it in the Black Box.
    """
    if not os.path.exists(jsonl_path):
        return False
        
    session_id = os.path.basename(jsonl_path).replace('.jsonl', '')
    os.makedirs(BLACKBOX_DIR, exist_ok=True)
    
    vault_path = os.path.join(BLACKBOX_DIR, f"{session_id}.enc")
    
    # Idempotency check: If it's already vaulted and sizes match roughly, skip.
    # But since it's an end-of-session dump, we just overwrite the vault if the new one is bigger/newer.
    if os.path.exists(vault_path) and os.path.getmtime(vault_path) >= os.path.getmtime(jsonl_path):
        return True
        
    try:
        with open(jsonl_path, 'rb') as f:
            raw_data = f.read()
            
        fernet = Fernet(get_or_create_key())
        encrypted_data = fernet.encrypt(raw_data)
        
        with open(vault_path, 'wb') as f:
            f.write(encrypted_data)
            
        print(f"      [VAULT] Encrypted & Secured ground truth for {session_id} in Black Box.")
        return True
    except Exception as e:
        print(f"      [FATAL] Failed to vault session {session_id}: {e}")
        return False

def audit_vault(session_id):
    """
    Decrypts a vaulted session for Operator auditing. Prints to stdout.
    """
    vault_path = os.path.join(BLACKBOX_DIR, f"{session_id}.enc")
    if not os.path.exists(vault_path):
        print(f"[ERROR] Session {session_id} not found in the Black Box.")
        return
        
    try:
        with open(vault_path, 'rb') as f:
            encrypted_data = f.read()
            
        fernet = Fernet(get_or_create_key())
        decrypted_data = fernet.decrypt(encrypted_data)
        print(decrypted_data.decode('utf-8'))
    except Exception as e:
        print(f"[ERROR] Failed to decrypt vault. Key mismatch or corruption: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "audit":
        audit_vault(sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == "vault":
        vault_session(sys.argv[2])
    else:
        print("Usage: python3 blackbox_vault.py vault <path_to_jsonl>")
        print("       python3 blackbox_vault.py audit <session_id>")
