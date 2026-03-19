#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import glob
import shutil
import re
from datetime import datetime

# --- DYNAMIC CONFIGURATION ---
def find_aim_root(start_dir):
    current = os.path.abspath(start_dir)
    while current != '/':
        config_path = os.path.join(current, "core/CONFIG.json")
        if os.path.exists(config_path):
            return current
        current = os.path.dirname(current)
    return "/home/kingb/aim"

BASE_DIR = find_aim_root(os.getcwd())
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
    if args.top_k:
        retriever_args += ["--top-k", str(args.top_k)]
    if args.full:
        retriever_args += ["--full"]
    if args.context is not None:
        retriever_args += ["--context", str(args.context)]
    if args.session:
        retriever_args += ["--session", args.session]
    run_script(os.path.join(SRC_DIR, "retriever.py"), retriever_args)

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
    """Dispatches to aim_push.sh."""
    run_bash_script(os.path.join(SCRIPTS_DIR, "aim_push.sh"), [args.message])

def cmd_sync(args):
    """Dispatches to back-populator.py."""
    run_script(os.path.join(SRC_DIR, "back-populator.py"), [])

def cmd_clean(args):
    """Dispatches to maintenance.py."""
    run_script(os.path.join(SRC_DIR, "maintenance.py"), [])

def cmd_init(args):
    """Dispatches to aim_init.py (New User Setup)."""
    init_args = []
    if args.reinstall: init_args.append("--reinstall")
    if args.uninstall: init_args.append("--uninstall")
    try:
        subprocess.run(["python3", os.path.join(SCRIPTS_DIR, "aim_init.py")] + init_args, check=True)
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

    # --- PHASE 12: PROPOSAL SYNTAX VALIDATION ---
    if "### 3. MEMORY DELTA" not in content:
        print("Error: Proposal is missing the '### 3. MEMORY DELTA' header.", file=sys.stderr)
        return

    try:
        delta_part = content.split("### 3. MEMORY DELTA")[1].strip()
        # Verify it contains at least one markdown code block or seems like markdown
        if not delta_part:
            print("Error: MEMORY DELTA section is empty.", file=sys.stderr)
            return
            
        # Clean the delta (remove code block wrappers if model added them)
        delta = re.sub(r"^```(markdown|md)?\n", "", delta_part)
        delta = re.sub(r"\n```$", "", delta).strip()

        # --- PHASE 12: COMMIT SAFETY SHADOWING ---
        if os.path.exists(memory_path):
            shutil.copy2(memory_path, backup_path)
            print(f"Created safety shadow: {os.path.basename(backup_path)}")

        with open(memory_path, 'w') as f:
            f.write(delta)
        
        # Archive used proposals
        os.makedirs(archive_dir, exist_ok=True)
        for p in proposals:
            dest = os.path.join(archive_dir, os.path.basename(p))
            os.rename(p, dest)
        
        print("Successfully committed to core/MEMORY.md and cleaned proposal inbox.")
    except Exception as e:
        print(f"Error during commit: {e}", file=sys.stderr)
        if os.path.exists(backup_path):
            print("Restoring from safety shadow...")
            shutil.copy2(backup_path, memory_path)

def cmd_config(args):
    """Dispatches to aim_config.py (TUI Cockpit)."""
    try:
        subprocess.run([VENV_PYTHON, os.path.join(SCRIPTS_DIR, "aim_config.py")], check=True)
    except: pass

def main():
    parser = argparse.ArgumentParser(description="A.I.M. (Actual Intelligent Memory) CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command to execute")

    init_parser = subparsers.add_parser("init", help="Initialize a new A.I.M. workspace")
    init_parser.add_argument("--reinstall", action="store_true", help="Re-initialize core files from templates")
    init_parser.add_argument("--uninstall", action="store_true", help="Show uninstallation instructions")

    subparsers.add_parser("status", help="Show current A.I.M. pulse/state")
    subparsers.add_parser("config", aliases=["tui"], help="Launch the A.I.M. Configuration Cockpit (TUI)")
    subparsers.add_parser("commit", help="Commit the latest memory distillation proposal")
    subparsers.add_parser("health", help="Run the workspace health audit (Git, Index, Secrets)")

    search_parser = subparsers.add_parser("search", help="Forensic search through session memory")
    search_parser.add_argument("query", nargs="+", help="The search query")
    search_parser.add_argument("--top-k", type=int, help="Number of results to return")
    search_parser.add_argument("--full", action="store_true", help="Show full content of the match")
    search_parser.add_argument("--context", type=int, nargs='?', const=2000, help="Show surrounding context (default: 2000 chars)")
    search_parser.add_argument("--session", type=str, help="Filter results to a specific Session ID")

    subparsers.add_parser("index", help="Run the forensic indexer on new sessions")
    subparsers.add_parser("handoff", aliases=["pulse"], help="Run the Flash Distiller for architectural reflection")

    push_parser = subparsers.add_parser("push", help="Auto-versioning git push")
    push_parser.add_argument("message", help="Commit message")

    subparsers.add_parser("sync", help="Run the back-populator to sync logs")
    subparsers.add_parser("clean", help="Run archive maintenance")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    known_commands = list(subparsers.choices.keys())
    if sys.argv[1] not in known_commands and sys.argv[1] not in ["-h", "--help", "pulse", "tui"]:
        new_argv = [sys.argv[0], "search"] + sys.argv[1:]
        args = parser.parse_args(new_argv[1:])
    else:
        args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "config" or args.command == "tui":
        cmd_config(args)
    elif args.command == "index":
        cmd_index(args)
    elif args.command == "handoff" or args.command == "pulse":
        cmd_handoff(args)
    elif args.command == "push":
        cmd_push(args)
    elif args.command == "sync":
        cmd_sync(args)
    elif args.command == "clean":
        cmd_clean(args)
    elif args.command == "health":
        cmd_health(args)
    elif args.command == "commit":
        cmd_commit(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
