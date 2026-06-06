#!/usr/bin/env python3
import os
import glob
import subprocess

def export_to_parquet(aim_root, target_dir):
    """Bakes the memory-wiki into a native Parquet cartridge for synchronization."""
    print("[1/3] Baking Engram DB into Native Parquet Cartridge...")
    wiki_dir = os.path.join(aim_root, "memory/wiki")
    if not os.path.exists(wiki_dir):
        print("      No memory-wiki found to bake.")
        return False
        
    out_file = os.path.join(target_dir, "wiki_sync.parquet")
    bake_script = os.path.join(aim_root, ".aim_core", "plugins", "datajack", "aim_bake.py")
    
    try:
        subprocess.run([
            "python3", bake_script, wiki_dir, out_file,
            "--author", "Sovereign Sync", 
            "--description", "Automated LanceDB Sync Cartridge"
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"      [ERROR] Failed to bake cartridge: {e}")
        return False

def import_from_parquet(aim_root, source_dir):
    """Jacks in all Parquet cartridges found in the source directory."""
    print("[3/3] Jacking-in incoming Parquet Cartridges...")
    cartridges = glob.glob(os.path.join(source_dir, "*.parquet"))
    if not cartridges:
        print("      No incoming cartridges found.")
        return 0
        
    imported = 0
    exchange_script = os.path.join(aim_root, ".aim_core", "plugins", "datajack", "aim_exchange.py")
    
    for cartridge in cartridges:
        print(f"      Mounting {os.path.basename(cartridge)}...")
        try:
            subprocess.run(["python3", exchange_script, "import", cartridge], check=True)
            imported += 1
        except subprocess.CalledProcessError as e:
            print(f"      [WARNING] Failed to mount {cartridge}: {e}")
            
    return imported
