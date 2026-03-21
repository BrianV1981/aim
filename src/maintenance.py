#!/usr/bin/env python3
import os
import glob
import time
import sys

# --- CONFIG BOOTSTRAP ---
def find_aim_root():
    current = os.path.dirname(os.path.abspath(__file__))
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
sys.path.append(os.path.join(AIM_ROOT, "src"))

try:
    from config_utils import CONFIG
except ImportError:
    CONFIG = {}

RAW_DIR = CONFIG.get('paths', {}).get('archive_raw_dir', os.path.join(AIM_ROOT, "archive/raw"))
MEM_ARCHIVE_DIR = os.path.join(AIM_ROOT, "memory/archive")
CONTINUITY_DIR = CONFIG.get('paths', {}).get('continuity_dir', os.path.join(AIM_ROOT, "continuity"))

def clean_rolling_archive(days=None):
    """
    Surgical cleanup of old artifacts to prevent repo bloat.
    Targets: Raw Transcripts, Old Memory Proposals, and Historical Pulses.
    """
    if days is None:
        days = CONFIG.get('settings', {}).get('archive_retention_days', 30)
    
    if days == 0:
        print("--- A.I.M. MAINTENANCE: Deactivated ---")
        print("[IDLE] Archive retention is set to 0 (Permanent). Skipping purge.")
        return

    print(f"--- A.I.M. MAINTENANCE: {days}-Day Rolling Purge ---")
    now = time.time()
    cutoff = now - (days * 86400)
    
    targets = [
        ("Raw Transcripts", os.path.join(RAW_DIR, "*.json")),
        ("Memory Proposals", os.path.join(MEM_ARCHIVE_DIR, "*.md")),
        ("Continuity Reports", os.path.join(CONTINUITY_DIR, "REPORT_*.md")),
        ("Context Pulses", os.path.join(CONTINUITY_DIR, "202*.md"))
    ]
    
    total_purged = 0
    
    for label, pattern in targets:
        files = glob.glob(pattern)
        purged_in_category = 0
        for f in files:
            # Skip .gitkeep files
            if f.endswith(".gitkeep"): continue
            
            if os.path.getmtime(f) < cutoff:
                try:
                    os.remove(f)
                    purged_in_category += 1
                except Exception as e:
                    print(f"  [ERROR] Failed to delete {os.path.basename(f)}: {e}")
        
        if purged_in_category > 0:
            print(f"[OK] Purged {purged_in_category} stale {label}.")
            total_purged += purged_in_category
        else:
            print(f"[IDLE] {label} are within the retention window.")

    if total_purged > 0:
        print(f"\n[SUCCESS] Maintenance complete. {total_purged} artifacts removed.")
    else:
        print("\n[SUCCESS] System is lean. No action required.")

if __name__ == "__main__":
    # Allow overriding days via CLI
    retention_days = 30
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        retention_days = int(sys.argv[1])
        
    clean_rolling_archive(retention_days)
