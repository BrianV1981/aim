#!/home/kingb/aim/venv/bin/python3
import argparse
import subprocess
import sys
import os

# --- CONFIGURATION ---
BASE_DIR = "/home/kingb/aim"
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
    run_script(os.path.join(SRC_DIR, "retriever.py"), args.query)

def cmd_index(args):
    """Dispatches to indexer.py."""
    run_script(os.path.join(SRC_DIR, "indexer.py"), [])

def cmd_pulse(args):
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

def cmd_heartbeat(args):
    """Dispatches to heartbeat.py."""
    run_script(os.path.join(SRC_DIR, "heartbeat.py"), [])

def cmd_commit(args):
    """Applies the distillation proposal to core/MEMORY.md."""
    proposal_path = os.path.join(BASE_DIR, "memory/DISTILLATION_PROPOSAL.md")
    memory_path = os.path.join(BASE_DIR, "core/MEMORY.md")
    
    if not os.path.exists(proposal_path):
        print("Error: No distillation proposal found.", file=sys.stderr)
        return

    with open(proposal_path, 'r') as f:
        content = f.read()

    # Extract the MEMORY DELTA section (assuming it is the last block)
    if "### 3. MEMORY DELTA" in content:
        delta = content.split("### 3. MEMORY DELTA")[1].strip()
        # Remove the code block backticks if present
        delta = delta.replace("```markdown", "").replace("```", "").strip()
        
        with open(memory_path, 'w') as f:
            f.write(delta)
        print("Successfully committed distillation proposal to core/MEMORY.md.")
def cmd_health(args):
    """Dispatches to heartbeat.py."""
    run_script(os.path.join(SRC_DIR, "heartbeat.py"), [])

def cmd_handoff(args):
    """Dispatches to distiller.py."""
    run_script(os.path.join(SRC_DIR, "distiller.py"), [])

def main():
    parser = argparse.ArgumentParser(description="A.I.M. (Actual Intelligent Memory) CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command to execute")

    # Status
    subparsers.add_parser("status", help="Show current A.I.M. pulse/state")

    # Commit
    subparsers.add_parser("commit", help="Commit the latest memory distillation proposal")

    # Health
    subparsers.add_parser("health", help="Run the workspace health audit (Git, Index, Secrets)")

    # Search (Default-ish)
    search_parser = subparsers.add_parser("search", help="Forensic search through session memory")
    search_parser.add_argument("query", nargs="+", help="The search query")

    # Index
    subparsers.add_parser("index", help="Run the forensic indexer on new sessions")

    # Handoff / Pulse
    subparsers.add_parser("handoff", aliases=["pulse"], help="Run the Flash Distiller for architectural reflection")

    # Push
    push_parser = subparsers.add_parser("push", help="Auto-versioning git push")
    push_parser.add_argument("message", help="Commit message")

    # Sync
    subparsers.add_parser("sync", help="Run the back-populator to sync logs")

    # Clean / Maintenance
    subparsers.add_parser("clean", help="Run archive maintenance")

    # Handle no command: default to status or help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # Check if the first argument is a known command or alias
    known_commands = list(subparsers.choices.keys())
    # Add manual aliases check if needed, but argparse handles it if passed to parse_args
    if sys.argv[1] not in known_commands and sys.argv[1] not in ["-h", "--help", "pulse"]:
        # If not a command, default to 'search'
        new_argv = [sys.argv[0], "search"] + sys.argv[1:]
        args = parser.parse_args(new_argv[1:])
    else:
        args = parser.parse_args()

    if args.command == "status":
        cmd_status(args)
    elif args.command == "search":
        cmd_search(args)
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
