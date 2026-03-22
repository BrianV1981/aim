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
    status_file = os.path.join(BASE_DIR, "docs/CURRENT_STATE.md")
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            print(f.read())
    else:
        print("Error: CURRENT_STATE.md not found.", file=sys.stderr)

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

def cmd_handoff(args):
    """Dispatches to distiller.py."""
    run_script(os.path.join(SRC_DIR, "distiller.py"), [])

def cmd_push(args):
    """Dispatches to aim_push.sh with Sovereign Sync."""
    try:
        from sovereign_sync import export_to_jsonl
        from forensic_utils import ForensicDB
        print("[0/2] Translating Engram DB for Git sync...")
        db = ForensicDB()
        sync_dir = os.path.join(BASE_DIR, "archive/sync")
        exported = export_to_jsonl(db, sync_dir)
        db.close()
        print(f"      Exported {exported} sessions to {sync_dir}")
    except Exception as e:
        print(f"[WARNING] Sovereign Sync export failed: {e}")
        
    run_bash_script(os.path.join(SCRIPTS_DIR, "aim_push.sh"), [args.message])

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

def cmd_clean(args):
    """Dispatches to maintenance.py."""
    run_script(os.path.join(SRC_DIR, "maintenance.py"), [])

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
    subparsers.add_parser("map", help="Print the Index of Keys (Knowledge Map)")

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
    elif args.command == "health": cmd_health(args)
    elif args.command == "commit": cmd_commit(args)
    elif args.command == "purge": cmd_purge(args)
    elif args.command == "uninstall": cmd_uninstall(args)
    else: parser.print_help()

if __name__ == "__main__":
    main()
