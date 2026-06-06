#!/usr/bin/env python3
import sys
import os
import shutil

def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

AIM_ROOT = find_aim_root()

def import_cartridge(cartridge_path, auto_confirm=False):
    print(f"--- A.I.M. DATAJACK: IMPORT (Native ROM) ---")
    print(f"[INFO] Mounting Parquet Cartridge: {os.path.basename(cartridge_path)}")
    
    if not os.path.exists(cartridge_path):
        print(f"[ERROR] Cartridge not found: {cartridge_path}")
        return

    if not cartridge_path.endswith(".parquet") and not cartridge_path.endswith(".engram"):
        print("[ERROR] Invalid Cartridge: Must be a .parquet file.")
        return
        
    cartridges_dir = os.path.join(AIM_ROOT, ".archive", "cartridges")
    os.makedirs(cartridges_dir, exist_ok=True)
    
    target_path = os.path.join(cartridges_dir, os.path.basename(cartridge_path))
    if target_path.endswith(".engram"):
        target_path = target_path.replace(".engram", ".parquet")
    
    try:
        shutil.copy2(cartridge_path, target_path)
        print(f"[SUCCESS] Native ROM Cartridge mounted successfully at {target_path}.")
    except Exception as e:
        print(f"[ERROR] Failed to mount cartridge: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "import":
        print("Usage: aim_exchange.py import <file.parquet>")
        sys.exit(1)
    import_cartridge(sys.argv[2])
