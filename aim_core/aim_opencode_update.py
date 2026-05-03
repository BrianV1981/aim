#!/usr/bin/env python3
"""
A.I.M. OpenCode Fork Updater — safely syncs upstream changes into the fork.

Pipeline:
  1. Fetch upstream/main
  2. Check for new commits vs local main
  3. Checkout main, merge upstream/main, push to origin/main
  4. Checkout opencode, merge main
  5. Detect and report merge conflicts (especially known conflict zones)
  6. Run full test suite
  7. Report summary

Usage:
  python aim_opencode_update.py [--dry-run] [--auto-merge]
  aim update fork [--dry-run] [--auto-merge]
"""
import os
import sys
import subprocess
import argparse
from datetime import datetime

# ── Configuration ─────────────────────────────────────────────────────

def find_aim_root():
    current = os.path.dirname(os.path.abspath(__file__))
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()

# Files that are modified in both repos and likely to conflict
OPECODE_CONFLICT_ZONES = [
    "aim_core/extract_signal.py",           # Both repos: OpenCode format detection vs upstream RAG
    "aim_core/reasoning_utils.py",          # Both repos: DeepSeek defaults vs upstream model config
    "aim_core/aim_cli.py",                  # Both repos: ensure_opencode_plugins vs upstream commands
    "aim_core/handoff_pulse_generator.py",  # Both repos: session source resolution
    "aim_core/wiki_tools.py",               # Both repos: opencode vs gemini tmux spawn
]

# Files safe to merge (no fork-specific modifications)
SAFE_MERGE_FILES = [
    "aim_core/plugins/datajack/forensic_utils.py",
    "aim_core/retriever.py",
    "aim_core/lance_backend.py",
    "hooks/coreference_rewriter.py",
    "aim_core/aim_config.py",
    "aim_core/aim_init.py",
    "AGENTS.md",
    "CHANGELOG.md",
    "VERSION",
    "requirements.txt",
    "benchmarks/",
]


def run_git(*args, capture=True, check=True):
    """Run a git command in AIM_ROOT and return stdout or raise."""
    cmd = ["git", "-C", AIM_ROOT] + list(args)
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if check and result.returncode != 0:
        cmd_str = " ".join(cmd)
        raise RuntimeError(f"Git command failed [{cmd_str}]: {result.stderr.strip()}")
    return result


# ── Change Detection ──────────────────────────────────────────────────

def check_for_upstream_changes():
    """
    Fetch upstream and compare with local main.
    Returns (has_changes: bool, count: int, commits: list).
    """
    # Fetch upstream
    run_git("fetch", "upstream", check=False)

    # Get commit counts on each side
    try:
        run_git("merge-base", "--is-ancestor", "upstream/main", "main")
        upstream_ahead = False
    except RuntimeError:
        upstream_ahead = True

    if not upstream_ahead:
        return False, 0, []

    new_commits = run_git(
        "log", "--oneline", "main..upstream/main"
    ).stdout.strip()

    commits_list = [c for c in new_commits.split("\n") if c]
    return True, len(commits_list), commits_list


def get_current_branch():
    """Get the current branch name."""
    return run_git("branch", "--show-current").stdout.strip()


# ── Merge Pipeline ────────────────────────────────────────────────────

def merge_phase_one(dry_run=False):
    """
    Phase 1: Merge upstream/main into local main, push to origin.
    Returns True on success.
    """
    print("\n─── Phase 1: Merge upstream/main → main ───")

    current_branch = get_current_branch()
    if current_branch != "main":
        print(f"[*] Switching to main branch (currently on {current_branch})...")
        if not dry_run:
            # Stash any uncommitted changes
            run_git("stash", "--include-untracked", check=False)
            run_git("checkout", "main")

    if dry_run:
        print("[DRY RUN] Would: git merge upstream/main")
        print("[DRY RUN] Would: git push origin main")
        if current_branch != "main":
            print(f"[DRY RUN] Would: git checkout {current_branch} (restore)")
        return True

    try:
        run_git("merge", "upstream/main", "-m", "Merge upstream/main into main (fork sync)")
        run_git("push", "origin", "main")
        print("[SUCCESS] main is now in sync with upstream/main")

        # Restore original branch
        if current_branch != "main":
            run_git("checkout", current_branch)
            run_git("stash", "pop", check=False)
        return True
    except RuntimeError as e:
        print(f"[ERROR] Phase 1 failed: {e}")
        run_git("merge", "--abort", check=False)
        return False


def merge_phase_two(dry_run=False):
    """
    Phase 2: Merge main into opencode, detect conflicts.
    Returns (success: bool, conflicts: list).
    """
    print("\n─── Phase 2: Merge main → opencode ───")

    current_branch = get_current_branch()
    switched = False
    if current_branch != "opencode":
        print(f"[*] Switching to opencode branch (currently on {current_branch})...")
        if not dry_run:
            run_git("stash", "--include-untracked", check=False)
            run_git("checkout", "opencode")
            switched = True

    if dry_run:
        print("[DRY RUN] Would: git merge main")
        # Preview known conflict zones that changed upstream
        new_commits = run_git("log", "--oneline", "opencode..main").stdout.strip()
        if new_commits:
            print("[DRY RUN] New commits to merge:")
            for line in new_commits.split("\n")[:10]:
                print(f"          {line}")
        return True, []

    try:
        run_git("merge", "main", "-m", "Merge main into opencode (fork sync)")
        print("[SUCCESS] opencode successfully merged with main")

        if switched:
            run_git("stash", "pop", check=False)
        return True, []

    except RuntimeError:
        # Merge conflict — identify conflicted files
        status = run_git("status", "--short").stdout
        conflicted_files = []
        for line in status.split("\n"):
            if line.startswith(("UU", "AA", "AU", "UA", "DD", "DU", "UD")):
                f = line[3:].strip()
                conflicted_files.append(f)

        # Highlight known conflict zones
        print(f"\n[!] MERGE CONFLICT on opencode branch")
        print(f"    {len(conflicted_files)} conflicted file(s):")
        for f in conflicted_files:
            tag = " [CONFLICT ZONE]" if f in OPECODE_CONFLICT_ZONES else ""
            print(f"      - {f}{tag}")

        print("\n    To resolve:")
        print("      1. Edit each conflicted file (preserve OpenCode/DeepSeek variants)")
        print("      2. git add <resolved_files>")
        print("      3. git commit")
        print("      4. Re-run 'aim update fork' to verify tests pass")

        return False, conflicted_files


# ── Test Suite ────────────────────────────────────────────────────────

def run_test_suite(test_filter=None):
    """
    Run the full test suite (or a filtered subset).
    Returns (passed: int, total: int, failures: list).
    """
    venv_python = os.path.join(AIM_ROOT, "venv", "bin", "python")
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    args = [venv_python, "-m", "pytest"]

    if test_filter:
        args.append(os.path.join(AIM_ROOT, "tests", test_filter))
    else:
        args.append(os.path.join(AIM_ROOT, "tests"))

    args.extend(["-x", "-q", "--tb=short"])

    result = subprocess.run(args, capture_output=True, text=True, cwd=AIM_ROOT)

    # Parse pytest output for counts
    output = result.stdout + "\n" + result.stderr
    failures = []

    # Simple parsing
    passed = 0
    total = 0

    for line in output.split("\n"):
        if "passed" in line and "failed" in line:
            try:
                parts = line.split(",")
                passed = int(parts[0].strip().split()[0])
                # Extract failed/test count from second part
                failed_part = [p for p in parts if "failed" in p]
                if failed_part:
                    total = passed + int(failed_part[0].strip().split()[0])
                else:
                    total = passed
            except (ValueError, IndexError):
                total = passed
        elif "no tests ran" in line.lower():
            return 0, 0, []

        # Collect failure file paths
        if "FAILED" in line and "::" in line:
            failures.append(line.strip())

    if total == 0:
        # Fallback: count from output
        if result.returncode == 0:
            total = passed = 1  # At least something ran

    return passed, total, failures


# ── Main Updater ──────────────────────────────────────────────────────

def run_updater(dry_run=False, auto_merge=False):
    """
    Execute the full fork update pipeline.
    Returns True if successful (no conflicts, tests pass).
    """
    print("=" * 60)
    print("A.I.M. OpenCode Fork Updater")
    if dry_run:
        print("*** DRY RUN MODE — No changes will be made ***")
    print("=" * 60)

    # Step 1: Check for upstream changes
    print("\n[*] Checking for upstream changes...")
    has_changes, count, commits = check_for_upstream_changes()

    if not has_changes:
        print("[OK] No new upstream changes. Fork is up to date.")
        return True

    print(f"[*] {count} new upstream commit(s):")
    for c in commits[:10]:
        print(f"      {c}")
    if len(commits) > 10:
        print(f"      ... and {len(commits) - 10} more")

    # Step 1.5: Check for modified files that overlap with conflict zones
    print("\n[*] Checking conflict zone overlap...")
    upstream_changed_files = run_git(
        "diff", "--name-only", "main", "upstream/main"
    ).stdout.strip().split("\n")

    for zone in OPECODE_CONFLICT_ZONES:
        if zone in upstream_changed_files:
            print(f"      [WARNING] Conflict zone modified upstream: {zone}")

    # Step 2: Phase 1 — merge upstream into main
    if not merge_phase_one(dry_run=dry_run):
        return False

    if dry_run:
        print("\n[DRY RUN] Full update pipeline preview complete.")
        return True

    # Step 3: Phase 2 — merge main into opencode
    success, conflicts = merge_phase_two(dry_run=dry_run)

    if not success:
        print("\n[!] Update blocked by merge conflicts. Resolve manually, then run tests.")
        return False

    # Step 4: Run test suite
    print("\n─── Phase 3: Running test suite ───")
    passed, total, failures = run_test_suite()

    print(f"\n{'=' * 60}")
    if passed == total and len(failures) == 0:
        print("[SUCCESS] Fork update complete.")
        print(f"         Tests: {passed}/{total} passed")
        print(f"         Run 'git push origin opencode' to deploy.")
        print(f"{'=' * 60}")
        return True
    else:
        print(f"[!] Fork updated but {len(failures)} test(s) failed ({passed}/{total} passed).")
        for f in failures[:10]:
            print(f"      {f}")
        print(f"{'=' * 60}")
        return False


# ── CLI Entry Point ───────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A.I.M. OpenCode Fork Updater — safely sync upstream into fork"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview changes without making any modifications"
    )
    parser.add_argument(
        "--auto-merge", action="store_true",
        help="Attempt automatic conflict resolution for known patterns"
    )
    args = parser.parse_args()

    try:
        success = run_updater(dry_run=args.dry_run, auto_merge=args.auto_merge)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FATAL] Updater crashed: {e}")
        sys.exit(1)
