#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import glob
import shutil
import re
from datetime import datetime

# --- CONFIG BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

from config_utils import CONFIG, AIM_ROOT

BASE_DIR = AIM_ROOT
VENV_PYTHON = os.path.join(BASE_DIR, "venv/bin/python3")
SRC_DIR = os.path.join(BASE_DIR, "src")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

def run_script(script_path, args):
    """Executes an A.I.M. script with the provided arguments."""
    cmd = [VENV_PYTHON, script_path] + args
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{' '.join(cmd)}' failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)

def run_bash_script(script_path, args):
    """Executes a bash script with the provided arguments."""
    cmd = ["bash", script_path] + args
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Bash script '{' '.join(cmd)}' failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)

def cmd_status(args):
    """Displays the current A.I.M. operational pulse."""
    status_file = os.path.join(BASE_DIR, "continuity/CURRENT_PULSE.md")
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            print(f.read())
    else:
        print("Error: CURRENT_PULSE.md not found. Run 'aim handoff' to generate.", file=sys.stderr)

def cmd_search(args):
    """Dispatches to retriever.py."""
    query = " ".join(args.query)
    retriever_args = [query]
    if args.top_k: retriever_args += ["--top-k", str(args.top_k)]
    if args.full: retriever_args += ["--full"]
    if args.context is not None: retriever_args += ["--context", str(args.context)]
    if args.session: retriever_args += ["--session", args.session]
    run_script(os.path.join(SRC_DIR, "retriever.py"), retriever_args)

def cmd_map(args):
    """Prints the surgical Index of Keys."""
    run_script(os.path.join(SRC_DIR, "retriever.py"), ["--map"])

def cmd_index(args):
    """Dispatches to indexer.py."""
    run_script(os.path.join(SRC_DIR, "indexer.py"), [])

def cmd_health(args):
    """Dispatches to heartbeat.py."""
    run_script(os.path.join(SRC_DIR, "heartbeat.py"), [])

def cmd_bug(args):
    """Creates a highly-structured GitHub Issue using the gh CLI."""
    print("--- A.I.M. ISSUE TRACKER ---")
    title = args.title
    tail_path = os.path.join(BASE_DIR, "continuity/FALLBACK_TAIL.md")
    
    body = f"## Description\n{title}\n\n## Context Tail (Last 10 Turns)\n"
    if os.path.exists(tail_path):
        with open(tail_path, 'r') as f:
            body += f"<details>\n<summary>View Stack Trace</summary>\n\n```markdown\n{f.read()}\n```\n</details>"
    else:
        body += "No FALLBACK_TAIL.md found."
        
    try:
        print("[1/1] Dispatching to GitHub CLI...")
        subprocess.run(["gh", "issue", "create", "--title", title, "--body", body, "--label", "bug"], check=True)
        print("[SUCCESS] Bug ticket created. Run 'aim fix <id>' to branch out.")
    except FileNotFoundError:
        print("[ERROR] GitHub CLI ('gh') is not installed. Please install it to use 'aim bug'.")
    except Exception as e:
        print(f"[ERROR] Failed to create issue: {e}")

def cmd_fix(args):
    """Checks out a new branch for a specific GitHub Issue ID."""
    issue_id = args.id
    branch_name = f"fix/issue-{issue_id}"
    print(f"--- A.I.M. ISSUE RESOLUTION (Issue #{issue_id}) ---")
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        print(f"[SUCCESS] Branched out to {branch_name}")
        print(f"[ACTION] When the bug is resolved, run: aim push \"Fix: <description> (Closes #{issue_id})\"")
    except Exception as e:
        print(f"[ERROR] Failed to branch: {e}")

def cmd_promote(args):
    """Automates the Phase Protocol: Archives main, merges current dev branch, and cleans up."""
    print("--- A.I.M. PHASE PROMOTION ---")
    try:
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)
        current_branch = result.stdout.strip()
        
        if current_branch == "main":
            print("[ERROR] You are already on 'main'. Please run 'aim promote' from your dev branch.")
            return
            
        print(f"[1/5] Preparing to promote '{current_branch}' to main...")
        
        # 1. Fetch latest
        subprocess.run(["git", "fetch", "origin"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 2. Archive current main
        date_str = datetime.now().strftime("%Y%m%d-%H%M")
        archive_branch = f"archive-{current_branch}-{date_str}"
        print(f"[2/5] Backing up current 'main' to '{archive_branch}'...")
        subprocess.run(["git", "checkout", "main"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "checkout", "-b", archive_branch], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "push", "-u", "origin", archive_branch], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 3. Merge dev branch into main
        print(f"[3/5] Merging '{current_branch}' into main...")
        subprocess.run(["git", "checkout", "main"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "merge", current_branch, "--no-edit"], check=True)
        
        # 4. Push main
        print(f"[4/5] Deploying new baseline to GitHub...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        # 5. Cleanup
        print(f"[5/5] Cleaning up local workspace...")
        subprocess.run(["git", "branch", "-d", current_branch], check=True)
        
        print("\n[SUCCESS] Promotion complete. You are now on a clean 'main' branch.")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Git operation failed. Promotion aborted. Please check your git status.")
    except Exception as e:
        print(f"\n[ERROR] Failed to promote: {e}")

def cmd_push(args):
    """Dispatches to aim_push.sh with Sovereign Sync and Semantic Release."""
    msg = args.message
    
    # 1. SEMANTIC RELEASE PIPELINE (Phase 23)
    print("--- A.I.M. SEMANTIC RELEASE ---")
    version_file = os.path.join(BASE_DIR, "VERSION")
    changelog_file = os.path.join(BASE_DIR, "CHANGELOG.md")
    
    try:
        current_version = "v1.0.0"
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                current_version = f.read().strip()
                
        # Fallback if the old date-based versioning is in place
        if len(current_version.split('.')) != 3 or "202" in current_version:
            current_version = "v1.5.0"
            
        major, minor, patch = map(int, current_version.replace('v', '').split('.'))
        
        bump_type = "none"
        if msg.startswith("BREAKING CHANGE:"): bump_type = "major"
        elif msg.startswith("Feature:") or msg.startswith("feat:"): bump_type = "minor"
        elif msg.startswith("Fix:") or msg.startswith("fix:"): bump_type = "patch"
        
        if bump_type == "major":
            major += 1; minor = 0; patch = 0
        elif bump_type == "minor":
            minor += 1; patch = 0
        elif bump_type == "patch":
            patch += 1
            
        new_version = f"v{major}.{minor}.{patch}"
        
        if bump_type != "none":
            print(f"[1/3] Bumping version: {current_version} -> {new_version}")
            with open(version_file, 'w') as f: f.write(new_version)
            
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_entry = f"## [{new_version}] - {date_str}\n- {msg}\n\n"
            
            if not os.path.exists(changelog_file):
                with open(changelog_file, 'w') as f:
                    f.write(f"# Changelog\n\n{log_entry}")
            else:
                with open(changelog_file, 'r') as f: content = f.read()
                content = content.replace("# Changelog\n", f"# Changelog\n\n{log_entry}")
                with open(changelog_file, 'w') as f: f.write(content)
        else:
            print(f"[1/3] No semantic prefix found (Feature/Fix/BREAKING CHANGE). Version remains {new_version}.")
    except Exception as e:
        print(f"[WARNING] Semantic Release failed: {e}")

    # 2. SOVEREIGN SYNC
    try:
        from sovereign_sync import export_to_jsonl
        from forensic_utils import ForensicDB
        print("[2/3] Translating Engram DB for Git sync...")
        db = ForensicDB()
        sync_dir = os.path.join(BASE_DIR, "archive/sync")
        exported = export_to_jsonl(db, sync_dir)
        db.close()
        print(f"      Exported {exported} sessions to {sync_dir}")
    except Exception as e:
        print(f"[WARNING] Sovereign Sync export failed: {e}")
        
    print("[3/3] Deploying to GitHub...")
    run_bash_script(os.path.join(SCRIPTS_DIR, "aim_push.sh"), [msg])

def cmd_sync(args):
    """Dispatches to back-populator.py and runs Sovereign Sync."""
    print("--- A.I.M. SYNC ---")
    try:
        from sovereign_sync import export_to_jsonl, import_from_jsonl
        from forensic_utils import ForensicDB
        
        print("[1/3] Translating Engram DB...")
        db = ForensicDB()
        sync_dir = os.path.join(BASE_DIR, "archive/sync")
        export_to_jsonl(db, sync_dir)
        db.close()
        
        print("[2/3] Executing network sync...")
        run_script(os.path.join(SRC_DIR, "back-populator.py"), [])
        
        print("[3/3] Ingesting new Engrams...")
        db = ForensicDB()
        imported = import_from_jsonl(db, sync_dir)
        db.close()
        print(f"      Imported {imported} new/updated sessions.")
        print("[SUCCESS] Workspace synchronized.")
    except Exception as e:
        print(f"[ERROR] Sync failed: {e}")

def cmd_handoff(args):
    """Dispatches to handoff_pulse_generator.py."""
    run_script(os.path.join(SRC_DIR, "handoff_pulse_generator.py"), [])
...
def cmd_memory(args):
    """Dispatches the complete asynchronous memory refinement pipeline."""
    print("--- A.I.M. ASYNC MEMORY REFINEMENT ---")
    print("[1/4] Processing session logs (Tier 1)...")
    run_script(os.path.join(BASE_DIR, "hooks/tier1_hourly_summarizer.py"), [])
    print("[2/4] Synthesizing Daily Report (Tier 2)...")
    run_script(os.path.join(SRC_DIR, "tier2_daily_summarizer.py"), [])
    print("[3/4] Synthesizing Weekly Arc (Tier 3)...")
    run_script(os.path.join(SRC_DIR, "tier3_weekly_summarizer.py"), [])
    print("[4/4] Generating Core Memory Proposals (Tier 4)...")
    run_script(os.path.join(SRC_DIR, "tier4_memory_proposer.py"), [])
    print("[SUCCESS] Full Memory Pipeline complete.")

def cmd_init(args):
    """Dispatches to aim_init.py (New User Setup)."""
    init_args = []
    if args.reinstall: init_args.append("--reinstall")
    if args.uninstall: init_args.append("--uninstall")
    try:
        subprocess.run([VENV_PYTHON, os.path.join(SCRIPTS_DIR, "aim_init.py")] + init_args, check=True)
    except: pass

def cmd_commit(args):
    """Applies the latest versioned distillation proposal to core/MEMORY.md."""
    proposal_dir = os.path.join(BASE_DIR, "memory/proposals")
    archive_dir = os.path.join(BASE_DIR, "memory/archive")
    memory_path = os.path.join(BASE_DIR, "core/MEMORY.md")
    backup_path = f"{memory_path}.bak"
    
    if not os.path.exists(proposal_dir):
        print("Error: No proposals folder found.", file=sys.stderr)
        return

    proposals = glob.glob(os.path.join(proposal_dir, "PROPOSAL_*.md"))
    if not proposals:
        print("Error: No pending proposals found.", file=sys.stderr)
        return

    proposals.sort(reverse=True)
    latest_proposal = proposals[0]
    
    print(f"Committing latest proposal: {os.path.basename(latest_proposal)}")

    with open(latest_proposal, 'r') as f:
        content = f.read()

    if "### 3. MEMORY DELTA" not in content:
        print("Error: Proposal is missing the '### 3. MEMORY DELTA' header.", file=sys.stderr)
        return

    try:
        delta_part = content.split("### 3. MEMORY DELTA")[1].strip()
        if not delta_part:
            print("Error: MEMORY DELTA section is empty.", file=sys.stderr)
            return
            
        delta = re.sub(r"^```(markdown|md)?\n", "", delta_part)
        delta = re.sub(r"\n```$", "", delta).strip()

        if os.path.exists(memory_path):
            shutil.copy2(memory_path, backup_path)
            print(f"Created safety shadow: {os.path.basename(backup_path)}")

        with open(memory_path, 'w') as f:
            f.write(delta)
        
        # Archive
        os.makedirs(archive_dir, exist_ok=True)
        for p in proposals:
            dest = os.path.join(archive_dir, os.path.basename(p))
            os.rename(p, dest)
        
        print("Successfully committed to core/MEMORY.md.")
    except Exception as e:
        print(f"Error during commit: {e}", file=sys.stderr)
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, memory_path)

def cmd_config(args):
    """Dispatches to aim_config.py (TUI Cockpit)."""
    try:
        subprocess.run([VENV_PYTHON, os.path.join(SCRIPTS_DIR, "aim_config.py")], check=True)
    except: pass

def cmd_purge(args):
    """Executes the Clean Slate Protocol."""
    print("--- A.I.M. Clean Slate Protocol (The Purge) ---")
    
    dirs = ["continuity/", "memory/", "archive/raw/", "archive/index/", "archive/private/", "workstreams/"]
    for d in dirs:
        path = os.path.join(BASE_DIR, d)
        if os.path.exists(path):
            shutil.rmtree(path)
            os.makedirs(path, exist_ok=True)
            
    db_path = os.path.join(BASE_DIR, "archive/engram.db")
    if os.path.exists(db_path): os.remove(db_path)
        
    docs = ["ROADMAP.md", "CURRENT_STATE.md", "DECISIONS.md"]
    for doc in docs:
        doc_path = os.path.join(BASE_DIR, "docs", doc)
        if os.path.exists(doc_path):
            with open(doc_path, 'w') as f:
                f.write(f"# {doc.replace('.md', '').title()}\n\n[PURGED: {datetime.now().strftime('%Y-%m-%d %H:%M')}]\n")
    
    project_path = os.path.join(BASE_DIR, "projects/example-project/")
    if os.path.exists(project_path):
        for f in os.listdir(project_path):
            fp = os.path.join(project_path, f)
            if os.path.isfile(fp): os.remove(fp)
            elif os.path.isdir(fp): shutil.rmtree(fp)

    print("\n[SUCCESS] A.I.M. has been purged.")

def cmd_uninstall(args):
    """Interactive uninstaller."""
    print("\n--- A.I.M. UNINSTALLER ---")
    confirm = input("\nRemove A.I.M. from your system? [y/N]: ").lower()
    if confirm != 'y': return

    print("\n1. Software Only\n2. Total Purge")
    choice = input("\nSelect [1-2]: ").strip()
    
    if choice == '2':
        for item in os.listdir(BASE_DIR):
            p = os.path.join(BASE_DIR, item)
            if os.path.isfile(p): os.unlink(p)
            elif os.path.isdir(p): shutil.rmtree(p)
    else:
        dirs = ["scripts/", "src/", "hooks/", "venv/", "archive/experimental/"]
        for d in dirs:
            p = os.path.join(BASE_DIR, d)
            if os.path.exists(p): shutil.rmtree(p)
        for f in ["setup.sh", "requirements.txt", "LICENSE"]:
            p = os.path.join(BASE_DIR, f)
            if os.path.exists(p): os.remove(p)

    print("\n[SUCCESS] A.I.M. removed.")

def cmd_update(args):
    """Safely pulls latest code, ingests sync data, and re-registers hooks."""
    print("--- A.I.M. SOVEREIGN UPDATE ---")
    
    # 1. Pull from Git
    try:
        print("[1/3] Syncing with GitHub...")
        subprocess.run(["git", "stash"], check=False)
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        subprocess.run(["git", "stash", "pop"], check=False)
    except Exception as e:
        print(f"[ERROR] Git sync failed: {e}")
        return

    # 2. Ingest Sovereign Sync data
    try:
        from sovereign_sync import import_from_jsonl
        from forensic_utils import ForensicDB
        print("[2/3] Ingesting Sovereign Sync data...")
        db = ForensicDB()
        sync_dir = os.path.join(BASE_DIR, "archive/sync")
        imported = import_from_jsonl(db, sync_dir)
        db.close()
        print(f"      Imported {imported} sessions from JSONL.")
    except ImportError:
        print("[2/3] Sovereign Sync module not found. Skipping ingestion.")
    except Exception as e:
        print(f"[WARNING] Sovereign Sync import failed: {e}")

    # 3. Refresh Hooks (Interactive)
    try:
        print("[3/3] Triggering A.I.M. Initializer...")
        subprocess.run([VENV_PYTHON, os.path.join(SCRIPTS_DIR, "aim_init.py")], check=True)
        print("[SUCCESS] Core engine and TUI updated.")
    except Exception as e:
        print(f"[ERROR] Update process failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="A.I.M. CLI")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize or update A.I.M. workspace")
    init_parser.add_argument("--reinstall", action="store_true", help="Perform a total reinstall with backup")
    init_parser.add_argument("--uninstall", action="store_true", help="Show uninstallation instructions")

    subparsers.add_parser("status", help="Show current project momentum")
    subparsers.add_parser("config", aliases=["tui"])
    subparsers.add_parser("update", help="Pull latest code and refresh hooks")
    subparsers.add_parser("commit")
    subparsers.add_parser("health")
    subparsers.add_parser("purge")
    subparsers.add_parser("uninstall")
    subparsers.add_parser("index")
    subparsers.add_parser("handoff", aliases=["pulse"])
    subparsers.add_parser("sync")
    subparsers.add_parser("clean")
    subparsers.add_parser("memory", help="Trigger asynchronous memory refinement pipeline")
    subparsers.add_parser("map", help="Print the Index of Keys (Knowledge Map)")

    bug_parser = subparsers.add_parser("bug", help="Report a bug and create a GitHub Issue")
    bug_parser.add_argument("title", help="Description of the bug")
    
    fix_parser = subparsers.add_parser("fix", help="Checkout a branch to fix a specific GitHub Issue")
    fix_parser.add_argument("id", help="The GitHub Issue ID")

    subparsers.add_parser("promote", help="Automate the Phase Protocol: Archive main, merge current dev branch, and cleanup")

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query", nargs="+")
    search_parser.add_argument("--top-k", type=int)
    search_parser.add_argument("--full", action="store_true")
    search_parser.add_argument("--context", type=int, nargs='?', const=2000)
    search_parser.add_argument("--session", type=str)

    push_parser = subparsers.add_parser("push")
    push_parser.add_argument("message")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    known = list(subparsers.choices.keys())
    if sys.argv[1] not in known and sys.argv[1] not in ["-h", "--help", "pulse", "tui"]:
        args = parser.parse_args(["search"] + sys.argv[1:])
    else:
        args = parser.parse_args()

    if args.command == "init": cmd_init(args)
    elif args.command == "status": cmd_status(args)
    elif args.command == "search": cmd_search(args)
    elif args.command == "map": cmd_map(args)
    elif args.command == "update": cmd_update(args)
    elif args.command in ["config", "tui"]: cmd_config(args)
    elif args.command == "index": cmd_index(args)
    elif args.command in ["handoff", "pulse"]: cmd_handoff(args)
    elif args.command == "push": cmd_push(args)
    elif args.command == "sync": cmd_sync(args)
    elif args.command == "clean": cmd_clean(args)
    elif args.command == "memory": cmd_memory(args)
    elif args.command == "health": cmd_health(args)
    elif args.command == "bug": cmd_bug(args)
    elif args.command == "fix": cmd_fix(args)
    elif args.command == "promote": cmd_promote(args)
    elif args.command == "commit": cmd_commit(args)
    elif args.command == "purge": cmd_purge(args)
    elif args.command == "uninstall": cmd_uninstall(args)
    else: parser.print_help()

if __name__ == "__main__":
    main()
