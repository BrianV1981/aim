#!/usr/bin/env python3
import os
import subprocess
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="A.I.M. Batch Merge Utility - Merges all open fix/issue-* branches into main.")
    parser.add_argument("--push", action="store_true", help="Automatically push main to origin after successful merges")
    args = parser.parse_args()

    print("--- A.I.M. BATCH MERGE AUTOMATION ---")
    
    # Get all remote branches
    res = subprocess.run(["git", "branch", "-r"], capture_output=True, text=True, check=True)
    branches = [line.strip().replace("origin/", "") for line in res.stdout.split("\n") if "origin/fix/issue-" in line]

    if not branches:
        print("No open fix/issue-* branches found on origin.")
        sys.exit(0)

    print(f"Found {len(branches)} issue branches to merge.")

    print("\n[1/3] Preparing main branch...")
    subprocess.run(["git", "checkout", "main"], check=True)
    subprocess.run(["git", "pull", "origin", "main"], check=True)

    failed_merges = []
    successful_merges = []

    print("\n[2/3] Executing sequential merges...")
    for branch in branches:
        print(f"  -> Merging {branch}...")
        try:
            # Merge the remote branch directly
            merge_res = subprocess.run(
                ["git", "merge", f"origin/{branch}", "-m", f"Merge remote-tracking branch origin/{branch}"], 
                capture_output=True, text=True
            )
            
            if merge_res.returncode == 0:
                print(f"     [SUCCESS] Merged {branch}")
                successful_merges.append(branch)
            else:
                print(f"     [ERROR] Conflict detected in {branch}. Aborting this specific merge.")
                subprocess.run(["git", "merge", "--abort"], check=False)
                failed_merges.append(branch)
        except Exception as e:
            print(f"     [FATAL] Failed to merge {branch}: {e}")
            subprocess.run(["git", "merge", "--abort"], check=False)
            failed_merges.append(branch)

    print("\n--- MERGE SUMMARY ---")
    print(f"Successfully merged: {len(successful_merges)}")
    if failed_merges:
        print(f"Failed to merge (conflicts): {len(failed_merges)}")
        for f in failed_merges:
            print(f"  - {f}")

    if successful_merges and args.push:
        print("\n[3/3] Pushing unified main branch to origin...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("[SUCCESS] All patches deployed to live repository.")
    elif successful_merges:
        print("\n[3/3] Skipped push. Run 'git push origin main' manually when ready, or use --push flag next time.")

if __name__ == "__main__":
    main()
