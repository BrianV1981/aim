#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import glob
import shutil
import re
import sqlite3
from datetime import datetime

# --- VENV BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
venv_python = os.path.join(aim_root, "venv", "bin", "python3")

if os.path.exists(venv_python) and sys.executable != venv_python:
    os.execv(venv_python, [venv_python] + sys.argv)

# --- CONFIG BOOTSTRAP ---
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

from config_utils import CONFIG, AIM_ROOT

BASE_DIR = AIM_ROOT
CLI_NAME = os.path.basename(BASE_DIR)
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

def cmd_core_memory(args):
    """Opens the CORE_MEMORY.md file in the user's default editor."""
    core_mem_file = os.path.join(BASE_DIR, "continuity/CORE_MEMORY.md")
    if not os.path.exists(core_mem_file):
        os.makedirs(os.path.join(BASE_DIR, "continuity"), exist_ok=True)
        with open(core_mem_file, 'w') as f:
            f.write("# A.I.M. Core Memory (RAM)\n\n*This file acts as the Agent's writable RAM. The agent can use the `aim core-memory` command to save critical facts, state, or observations here that must survive across context windows and cannot wait for the background summarizer.*\n\n- [Empty]\n")
    
    editor = os.environ.get('EDITOR', 'nano')
    subprocess.call([editor, core_mem_file])

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
    """Dispatches to bootstrap_brain.py."""
    run_script(os.path.join(SRC_DIR, "bootstrap_brain.py"), [])

def cmd_doctor(args):
    """Dispatches to aim_doctor.py to validate environment dependencies."""
    run_script(os.path.join(SCRIPTS_DIR, "aim_doctor.py"), [])

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
        print(f"[ERROR] GitHub CLI ('gh') is not installed. Please install it to use '{CLI_NAME} bug'.")
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
        print(f"[ACTION] When the bug is resolved, run: {CLI_NAME} push \\\"Fix: <description> (Closes #{issue_id})\\\"")
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

def cmd_merge_batch(args):
    """Executes the aim_batch_merge.py script to cleanly merge an entire Phase of tickets."""
    merge_args = []
    if args.push:
        merge_args.append("--push")
    run_script(os.path.join(SCRIPTS_DIR, "aim_batch_merge.py"), merge_args)

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

    # 2. SOVEREIGN SYNC (Decoupled Background Task)
    try:
        print("[2/3] Spawning background Engram DB translation...")
        # Fire and forget the sync so it doesn't block the push or crash the CLI if the DB is locked
        subprocess.Popen(
            [VENV_PYTHON, os.path.join(SRC_DIR, "sovereign_sync.py"), "export"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"[WARNING] Background Sovereign Sync spawn failed: {e}")
        
    print("[3/3] Deploying to GitHub...")
    run_bash_script(os.path.join(SCRIPTS_DIR, "aim_push.sh"), [msg])

def cmd_sync_issues(args):
    """Synchronizes remote GitHub issues to the local ISSUE_TRACKER.md file."""
    run_script(os.path.join(SCRIPTS_DIR, "sync_issue_tracker.py"), [])

def cmd_crash(args):
    """Executes the crash recovery protocol to salvage interrupted sessions."""
    run_script(os.path.join(SCRIPTS_DIR, "aim_crash.py"), [])

def cmd_reincarnate(args):
    """Triggers the automated reincarnate handoff loop."""
    run_script(os.path.join(SCRIPTS_DIR, "aim_reincarnate.py"), [])

def cmd_delegate(args):
    """Dispatches to aim_delegate.py to spawn parallel sub-agents."""
    delegate_args = [args.instruction, "--files"] + args.files
    run_script(os.path.join(SCRIPTS_DIR, "aim_delegate.py"), delegate_args)

def cmd_sync(args):
    """Dispatches to back-populator.py and runs Sovereign Sync."""
    print("--- A.I.M. SYNC ---")
    try:
        from sovereign_sync import export_to_jsonl, import_from_jsonl
        from datajack_plugin import load_knowledge_provider
        
        print("[1/3] Translating Engram DB...")
        db = load_knowledge_provider()
        sync_dir = os.path.join(BASE_DIR, "archive/sync")
        export_to_jsonl(db, sync_dir)
        db.close()
        
        print("[2/3] Executing network sync...")
        run_script(os.path.join(SRC_DIR, "back-populator.py"), [])
        
        print("[3/3] Ingesting new Engrams...")
        db = load_knowledge_provider()
        imported = import_from_jsonl(db, sync_dir)
        db.close()
        print(f"      Imported {imported} new/updated sessions.")
        print("[SUCCESS] Workspace synchronized.")
    except Exception as e:
        print(f"[ERROR] Sync failed: {e}")

def cmd_handoff(args):
    """Dispatches to handoff_pulse_generator.py."""
    run_script(os.path.join(SRC_DIR, "handoff_pulse_generator.py"), [])

def cmd_sessions(args):
    """Lists recent cleaned historical sessions."""
    run_script(os.path.join(SRC_DIR, "history_scribe.py"), [])
    history_db = os.path.join(BASE_DIR, "archive/history.db")
    if not os.path.exists(history_db):
        print("No historical sessions found.")
        return
    
    conn = sqlite3.connect(history_db)
    c = conn.cursor()
    c.execute("SELECT session_id, timestamp FROM history ORDER BY timestamp DESC LIMIT 20")
    rows = c.fetchall()
    print("\n--- RECENT SESSIONS ---")
    for r in rows:
        print(f"[{r[1]}] {r[0][:8]}")
    conn.close()

def cmd_search_sessions(args):
    """Searches the full session history database."""
    query = " ".join(args.query)
    history_db = os.path.join(BASE_DIR, "archive/history.db")
    if not os.path.exists(history_db):
        run_script(os.path.join(SRC_DIR, "history_scribe.py"), [])
        if not os.path.exists(history_db):
            print("No historical sessions found.")
            return
    
    conn = sqlite3.connect(history_db)
    c = conn.cursor()
    # Search FTS5
    sql = "SELECT session_id, timestamp, snippet(history_fts, 2, '...', '...', '...', 10) FROM history_fts WHERE history_fts MATCH ? ORDER BY rank LIMIT 10"
    try:
        c.execute(sql, (query,))
        rows = c.fetchall()
        print(f"\n--- SEARCH RESULTS: {query} ---")
        if not rows:
            print("No matches found.")
        for r in rows:
            print(f"\nSession: {r[0][:8]} ({r[1]})")
            print(f"Match: {r[2]}")
    except Exception as e:
        print(f"Search failed: {e}")
    conn.close()

def cmd_memory(args):
    """Dispatches the 5-Tier Memory Distillation Pipeline."""
    print("--- A.I.M. 5-TIER MEMORY DISTILLATION ---")
    
    # Tier 1: Session Summarizer (High Frequency)
    print("[1/5] Stage 1: Session Summarizer (Latest Session Deltas)...")
    run_script(os.path.join(BASE_DIR, "hooks/session_summarizer.py"), [])
    
    # Tier 2: Memory Proposer (Hourly)
    print("[2/5] Stage 2: Memory Proposer (Hourly Consolidation)...")
    run_script(os.path.join(SRC_DIR, "memory_proposer.py"), [])
    
    # Tier 3: Daily Refiner
    print("[3/5] Stage 3: Daily Refiner...")
    run_script(os.path.join(SRC_DIR, "daily_refiner.py"), [])
    
    # Tier 4: Weekly Consolidator
    print("[4/5] Stage 4: Weekly Consolidator...")
    run_script(os.path.join(SRC_DIR, "weekly_consolidator.py"), [])

    # Tier 5: Monthly Archivist
    print("[5/5] Stage 5: Monthly Archivist (Failsafe Auto-Apply)...")
    run_script(os.path.join(SRC_DIR, "monthly_archivist.py"), [])
    
    print("[SUCCESS] Memory Distillation Pipeline complete.")

def cmd_init(args):
    """Dispatches to aim_init.py (New User Setup)."""
    init_args = []
    if args.reinstall: init_args.append("--reinstall")
    if args.uninstall: init_args.append("--uninstall")
    if args.light: init_args.append("--light")
    try:
        subprocess.run([VENV_PYTHON, os.path.join(SCRIPTS_DIR, "aim_init.py")] + init_args, check=True)
    except: pass

def cmd_ingest(args):
    """Pulls newer manual edits from the Obsidian Vault into A.I.M.'s workspace."""
    run_script(os.path.join(SCRIPTS_DIR, "obsidian_pull.py"), [])

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

    # --- THE ARC MERGER ---
    # If the proposal is ARC-only (no FULL CANDIDATE), we trigger an LLM-driven merge.
    if "### 3. MEMORY DELTA" not in content:
        print("[MERGE] Proposal is ARC-only. Triggering AI Merger...")
        try:
            from reasoning_utils import generate_reasoning
            from monthly_archivist import MERGE_SYSTEM
            
            with open(memory_path, 'r') as f:
                current_memory = f.read()
                
            prompt = f"### ARC REPORT\n{content}\n\n### CURRENT MEMORY\n{current_memory}"
            result = generate_reasoning(prompt, system_instruction=MERGE_SYSTEM, brain_type="tier5")
            
            if "### 3. MEMORY DELTA" in result:
                content = result
            else:
                print("[ERROR] AI Merger failed to produce a valid Delta.", file=sys.stderr)
                return
        except Exception as e:
            print(f"[ERROR] AI Merger failed: {e}", file=sys.stderr)
            return

    try:
        delta_part = content.split("### 3. MEMORY DELTA")[1].strip()
        delta = re.sub(r"^```(markdown|md)?\n", "", delta_part)
        delta = re.sub(r"\n```$", "", delta).strip()

        if os.path.exists(memory_path):
            shutil.copy2(memory_path, backup_path)
            print(f"Created safety shadow: {os.path.basename(backup_path)}")

        with open(memory_path, 'w') as f:
            f.write(delta)
        
        # Archive the committed proposal
        os.makedirs(archive_dir, exist_ok=True)
        dest = os.path.join(archive_dir, os.path.basename(latest_proposal))
        os.rename(latest_proposal, dest)
        
        print("Successfully committed to core/MEMORY.md.")

        # FULL CLEANUP: Delete all refinement scaffolding (Hourly logs and other proposals)
        print("[CLEANUP] Purging refinement scaffolding...")
        hourly_dir = os.path.join(BASE_DIR, "memory/hourly")
        if os.path.exists(hourly_dir):
            for f in glob.glob(os.path.join(hourly_dir, "*.md")):
                try: os.remove(f)
                except: pass
        
        for p in glob.glob(os.path.join(proposal_dir, "PROPOSAL_*.md")):
            try: os.remove(p)
            except: pass
        
        print("[SUCCESS] Refinement cycle complete.")
        
        # Phase 33/38: Automated Obsidian Transport Layer
        obsidian_script = os.path.join(SCRIPTS_DIR, "obsidian_sync.py")
        if os.path.exists(obsidian_script):
            try:
                print("  -> Syncing Delta to Obsidian Vault...")
                subprocess.run([VENV_PYTHON, obsidian_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except: pass
            
    except Exception as e:
        print(f"Error during commit: {e}", file=sys.stderr)
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, memory_path)

def cmd_config(args):
    """Dispatches to aim_config.py (TUI Cockpit)."""
    try:
        subprocess.run([VENV_PYTHON, os.path.join(SCRIPTS_DIR, "aim_config.py")], check=True)
    except: pass

def cmd_bake(args):
    """Dispatches to aim_bake.py."""
    run_script(os.path.join(SRC_DIR, "plugins", "datajack", "aim_bake.py"), [args.directory, args.output])

def cmd_exchange(args):
    """Dispatches to aim_exchange.py."""
    run_script(os.path.join(SRC_DIR, "plugins", "datajack", "aim_exchange.py"), sys.argv[2:])

def cmd_jack_in(args):
    """Dispatches to aim_exchange.py import, with support for BitTorrent Magnet Links."""
    target = args.file
    
    # Phase 38: The P2P DataJack Swarm
    if target.startswith("magnet:?"):
        print("\n[JACK-IN] Initiating DataJack Swarm Handshake...")
        print(f"  Target: Magnet Link Detected")
        
        # We need a temporary staging area for the torrent payload
        temp_dir = os.path.join(BASE_DIR, "archive/torrent_staging")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # We use a dedicated script to handle the async/threading complexities of torrents
            torrent_handler = os.path.join(SCRIPTS_DIR, "aim_torrent.py")
            if not os.path.exists(torrent_handler):
                print("[ERROR] Torrent handler not found. Ensure Phase 38 is fully installed.")
                sys.exit(1)
                
            print("  Connecting to swarm. Please wait (this depends on seeder availability)...")
            
            # Execute the torrent download. The script will return the absolute path to the downloaded .engram
            result = subprocess.run(
                [VENV_PYTHON, torrent_handler, "download", target, temp_dir],
                capture_output=True, text=True, check=True
            )
            
            # Parse the final output line to get the downloaded file path
            output_lines = result.stdout.strip().split("\n")
            downloaded_file = ""
            for line in reversed(output_lines):
                if line.startswith("SUCCESS_PATH:"):
                    downloaded_file = line.replace("SUCCESS_PATH:", "").strip()
                    break
                    
            if not downloaded_file or not os.path.exists(downloaded_file):
                print(f"[ERROR] Swarm download failed or returned invalid file path.")
                print(f"  DEBUG:\n{result.stdout}\n{result.stderr}")
                sys.exit(1)
                
            print(f"[JACK-IN] Swarm download complete: {os.path.basename(downloaded_file)}")
            # Override the target so the standard exchange logic processes the downloaded file
            target = downloaded_file
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] DataJack Swarm failure (Code {e.returncode}).")
            print(f"  DEBUG:\n{e.stdout}\n{e.stderr}")
            sys.exit(e.returncode)

    # Standard Local Engram Injection
    run_script(os.path.join(SRC_DIR, "plugins", "datajack", "aim_exchange.py"), ["import", target])

def cmd_daemon(args):
    """Manages the Autonomous Background Daemon."""
    daemon_script = os.path.join(SRC_DIR, "daemon.py")
    pid_file = os.path.join(BASE_DIR, "archive/daemon.pid")
    
    if args.action == "start":
        if os.path.exists(pid_file):
            print("[WARNING] Daemon may already be running. Check 'aim daemon status'.")
            return
        print("--- A.I.M. AUTONOMOUS DAEMON ---")
        print("[INFO] Igniting the Heartbeat Engine...")
        # Run in background
        proc = subprocess.Popen(["nohup", VENV_PYTHON, daemon_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        with open(pid_file, "w") as f:
            f.write(str(proc.pid))
        print(f"[SUCCESS] Daemon is now running in the background (PID {proc.pid}).")
        
    elif args.action == "stop":
        if os.path.exists(pid_file):
            with open(pid_file, "r") as f:
                pid = f.read().strip()
            try:
                subprocess.run(["kill", pid], check=False)
                os.remove(pid_file)
                print(f"[SUCCESS] Daemon (PID {pid}) terminated.")
            except Exception:
                print("[ERROR] Failed to kill daemon. It may have already crashed.")
        else:
            print("[INFO] No daemon is currently running.")
            
    elif args.action == "status":
        if os.path.exists(pid_file):
            with open(pid_file, "r") as f:
                pid = f.read().strip()
            # Check if process actually exists
            try:
                os.kill(int(pid), 0)
                print(f"[ACTIVE] Daemon is running (PID {pid}).")
                log_file = os.path.join(BASE_DIR, "archive/daemon.log")
                if os.path.exists(log_file):
                    print("\nLatest Pulse:")
                    subprocess.run(["tail", "-n", "3", log_file])
            except OSError:
                print("[DEAD] PID file exists but process is dead. Cleaning up.")
                os.remove(pid_file)
        else:
            print("[INACTIVE] Daemon is completely offline.")

def cmd_unplug(args):
    """Dispatches to aim_exchange.py unplug."""
    run_script(os.path.join(SRC_DIR, "plugins", "datajack", "aim_exchange.py"), ["unplug"] + sys.argv[2:])

def cmd_purge(args):
    """Executes the Clean Slate Protocol --- (Safety Warning Required) ---"""
    print("--- A.I.M. Clean Slate Protocol (The Purge) ---")
    confirm = input("This will permanently delete ALL memory, continuity, and database files. Are you sure? [y/N]: ")
    if confirm.lower() != 'y': return
    
    dirs = ["continuity/", "memory/", "archive/raw/", "archive/index/", "archive/private/", "archive/history/", "archive/sync/", "workstreams/"]
    for d in dirs:
        path = os.path.join(BASE_DIR, d)
        if os.path.exists(path):
            shutil.rmtree(path)
            os.makedirs(path, exist_ok=True)
            
    db_paths = [os.path.join(BASE_DIR, "archive/engram.db"), os.path.join(BASE_DIR, "archive/history.db")]
    for db_path in db_paths:
        if os.path.exists(db_path): os.remove(db_path)
        
    docs = ["ROADMAP.md", "CURRENT_STATE.md", "DECISIONS.md"]
    for doc in docs:
        doc_path = os.path.join(BASE_DIR, "docs", doc)
        if os.path.exists(doc_path):
            with open(doc_path, 'w') as f:
                f.write(f"# {doc.replace('.md', '').title()}\n\n[PURGED: {datetime.now().strftime('%Y-%m-%d %H:%M')}]\n")
    
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
        from datajack_plugin import load_knowledge_provider
        print("[2/3] Ingesting Sovereign Sync data...")
        db = load_knowledge_provider()
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

def ensure_hooks_mapped():
    """Silently self-heals stale hook paths in the global Gemini CLI settings when the workspace is moved or cloned."""
    settings_path = os.path.expanduser("~/.gemini/settings.json")
    if not os.path.exists(settings_path): return
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        needs_update = False
        after_hooks = settings.get("hooks", {}).get("AfterTool", [])
        for entry in after_hooks:
            for hook in entry.get("hooks", []):
                if hook.get("name") == "cognitive-mantra":
                    if "aim_router.py" not in hook.get("command", ""):
                        needs_update = True
                        break
        
        if needs_update:
            # Re-register using the aim_init logic dynamically
            try:
                sys.path.append(SCRIPTS_DIR)
                import aim_init
                aim_init.register_hooks()
            except ImportError: pass
    except Exception: pass

def main():
    ensure_hooks_mapped()
    parser = argparse.ArgumentParser(description="A.I.M. CLI")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize or update A.I.M. workspace")
    init_parser.add_argument("--reinstall", action="store_true", help="Perform a total reinstall with backup")
    init_parser.add_argument("--uninstall", action="store_true", help="Show uninstallation instructions")
    init_parser.add_argument("--light", action="store_true", help="Install the Lightweight AOS Mode (Zero-RAG, continuity only)")

    subparsers.add_parser("status", help="Show current project momentum")
    subparsers.add_parser("config", aliases=["tui"])
    subparsers.add_parser("core-memory", help="Open the Core Memory block for instant invariant tracking")
    subparsers.add_parser("update", help="Pull latest code and refresh hooks")
    subparsers.add_parser("commit", help="Commit the latest memory proposal and clear refinement scaffolding")
    subparsers.add_parser("doctor", help="Run a diagnostic check on system dependencies")
    subparsers.add_parser("health")
    subparsers.add_parser("purge")
    subparsers.add_parser("uninstall")
    subparsers.add_parser("index")
    subparsers.add_parser("ingest", help="Pull newer manual edits from the Obsidian Vault into A.I.M.'s workspace")
    subparsers.add_parser("handoff", aliases=["pulse"])
    subparsers.add_parser("sync")
    subparsers.add_parser("sync-issues", help="Synchronize remote GitHub issues to local ledger")
    subparsers.add_parser("crash", help="Trigger the Crash Recovery Protocol (Extracts signal from crashed session, generates handoff, and syncs issues)")
    subparsers.add_parser("reincarnate", help="Trigger the Reincarnation Protocol (Automated context handoff and terminal swap)")
    
    delegate_parser = subparsers.add_parser("delegate", help="Spawn parallel sub-agents to analyze multiple files (The RLM Pattern)")
    delegate_parser.add_argument("instruction", help="The prompt to give each sub-agent")
    delegate_parser.add_argument("--files", nargs="+", required=True, help="List of files to analyze")
    
    subparsers.add_parser("clean")
    subparsers.add_parser("exchange", help="Export/Import .engram cartridges")
    
    swarm_parser = subparsers.add_parser("swarm", help="Manage the A.I.M. Sovereign Swarm (Synapse)")
    swarm_parser.add_argument("action", choices=["up", "down", "status"], help="Action to perform")

    bake_parser = subparsers.add_parser("bake", help="Manufacture an atomic .engram cartridge directly from a docs folder")
    bake_parser.add_argument("directory", help="The raw documentation directory to vectorize")
    bake_parser.add_argument("output", help="The name of the resulting .engram file (e.g. pytest.engram)")

    jackin_parser = subparsers.add_parser("jack-in", help="Alias for aim exchange import")
    jackin_parser.add_argument("file", help="Path to the .engram file")
    
    unplug_parser = subparsers.add_parser("unplug", help=f"Alias for {CLI_NAME} exchange unplug")
    unplug_parser.add_argument("keyword", help="The keyword to delete (e.g., 'python314')")

    daemon_parser = subparsers.add_parser("daemon", help="Manage the Autonomous Heartbeat Daemon")
    daemon_parser.add_argument("action", choices=["start", "stop", "status"], help="Action to perform")

    subparsers.add_parser("memory", help="Trigger the Delta Ledger memory refinement pipeline")
    subparsers.add_parser("map", help="Print the Index of Keys (Knowledge Map)")

    subparsers.add_parser("sessions", help="List recent noise-reduced historical sessions")
    search_sessions_parser = subparsers.add_parser("search-sessions", help="Search the full session history database")
    search_sessions_parser.add_argument("query", nargs="+", help="The search query")

    bug_parser = subparsers.add_parser("bug", help="Report a bug and create a GitHub Issue")
    bug_parser.add_argument("title", help="Description of the bug")
    
    fix_parser = subparsers.add_parser("fix", help="Checkout a branch to fix a specific GitHub Issue")
    fix_parser.add_argument("id", help="The GitHub Issue ID")

    subparsers.add_parser("promote", help="Automate the Phase Protocol: Archive main, merge current dev branch, and cleanup")

    merge_batch_parser = subparsers.add_parser("merge-batch", help="Automate the Phase Protocol: Merge all open fix branches into main")
    merge_batch_parser.add_argument("--push", action="store_true", help="Automatically push unified main to origin")

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
    elif args.command == "core-memory": cmd_core_memory(args)
    elif args.command == "search": cmd_search(args)
    elif args.command == "map": cmd_map(args)
    elif args.command == "update": cmd_update(args)
    elif args.command in ["config", "tui"]: cmd_config(args)
    elif args.command == "index": cmd_index(args)
    elif args.command == "ingest": cmd_ingest(args)
    elif args.command in ["handoff", "pulse"]: cmd_handoff(args)
    elif args.command == "push": cmd_push(args)
    elif args.command == "sync": cmd_sync(args)
    elif args.command == "sync-issues": cmd_sync_issues(args)
    elif args.command == "crash": cmd_crash(args)
    elif args.command == "reincarnate": cmd_reincarnate(args)
    elif args.command == "clean": cmd_clean(args)
    elif args.command == "bake": cmd_bake(args)
    elif args.command == "exchange": cmd_exchange(args)
    elif args.command == "jack-in": cmd_jack_in(args)
    elif args.command == "unplug": cmd_unplug(args)
    elif args.command == "daemon": cmd_daemon(args)
    elif args.command == "memory": cmd_memory(args)
    elif args.command == "sessions": cmd_sessions(args)
    elif args.command == "search-sessions": cmd_search_sessions(args)
    elif args.command == "doctor": cmd_doctor(args)
    elif args.command == "health": cmd_health(args)
    elif args.command == "bug": cmd_bug(args)
    elif args.command == "fix": cmd_fix(args)
    elif args.command == "promote": cmd_promote(args)
    elif args.command == "merge-batch": cmd_merge_batch(args)
    elif args.command == "commit": cmd_commit(args)
    elif args.command == "purge": cmd_purge(args)
    elif args.command == "uninstall": cmd_uninstall(args)
    else: parser.print_help()

if __name__ == "__main__":
    main()
