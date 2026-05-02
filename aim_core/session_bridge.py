#!/usr/bin/env python3
"""
OpenCode Session Bridge — replaces session_porter.py Gemini mirroring.

Pipelines opencode CLI sessions into the local archive/raw/ directory:
  1. opencode session list  →  parse session IDs
  2. opencode export <id>   →  JSON export
  3. Write to archive/raw/session-<id>.json

Used by: daemon pre-flight, handoff pulse generator (indirectly via archive),
         and manual session bridging.
"""
import os
import re
import json
import subprocess
import sys

from config_utils import CONFIG, AIM_ROOT


OPENCODE_BIN = "opencode"

_SESSION_LINE_RE = re.compile(
    r"^(ses_\S+)\s+(.+?)\s+(\d{1,2}:\d{2}\s+[AP]M)$"
)


def _find_opencode():
    """Resolve opencode binary path, preferring the one in PATH."""
    return OPENCODE_BIN


def list_sessions():
    """
    Run 'opencode session list' and parse the table output into a list of dicts.

    Each dict: {"id": "ses_...", "title": "...", "updated": "HH:MM AM/PM"}

    Returns empty list if no sessions or command fails.
    """
    result = subprocess.run(
        [_find_opencode(), "session", "list"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(f"[BRIDGE] opencode session list failed: {result.stderr}\n")
        return []

    stdout = result.stdout.strip()
    if not stdout:
        return []

    lines = stdout.splitlines()
    sessions = []

    for line in lines:
        match = _SESSION_LINE_RE.match(line)
        if match:
            sessions.append({
                "id": match.group(1),
                "title": match.group(2).strip(),
                "updated": match.group(3),
            })

    return sessions


def export_session(session_id):
    """
    Run 'opencode export <session_id>' and return the parsed JSON dict.

    Raises RuntimeError if the subprocess fails or JSON is invalid.
    """
    result = subprocess.run(
        [_find_opencode(), "export", session_id],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"opencode export failed for {session_id}: {result.stderr.strip()}"
        )

    stdout = result.stdout.strip()
    if not stdout:
        # opencode export writes to stderr when it can't find a session
        if result.stderr.strip():
            raise RuntimeError(
                f"opencode export produced no JSON for {session_id}: {result.stderr.strip()}"
            )
        raise RuntimeError(f"opencode export produced no output for {session_id}")

    try:
        return json.loads(stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Invalid JSON from opencode export for {session_id}: {e}"
        ) from e


def bridge_to_archive(session_id, archive_dir):
    """
    Export a single session and write session-<id>.json to archive_dir.

    Skips if the file already exists (idempotent). Returns the output path.
    """
    os.makedirs(archive_dir, exist_ok=True)
    output_path = os.path.join(archive_dir, f"session-{session_id}.json")

    if os.path.exists(output_path):
        return output_path

    data = export_session(session_id)
    tmp_path = output_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, output_path)
    return output_path


def bridge_all(archive_dir=None):
    """
    Export ALL listed sessions to the archive directory.

    Returns the number of sessions successfully bridged.
    """
    if archive_dir is None:
        archive_dir = CONFIG.get("paths", {}).get(
            "opencode_export_dir",
            os.path.join(AIM_ROOT, "archive", "raw"),
        )

    sessions = list_sessions()
    count = 0
    for session in sessions:
        try:
            bridge_to_archive(session["id"], archive_dir)
            count += 1
        except RuntimeError as e:
            sys.stderr.write(f"[BRIDGE] Skipping {session['id']}: {e}\n")
    return count


def bridge_latest(archive_dir=None, count=1):
    """
    Export only the N most recent sessions (first N from list).

    Returns list of output file paths.
    """
    if archive_dir is None:
        archive_dir = CONFIG.get("paths", {}).get(
            "opencode_export_dir",
            os.path.join(AIM_ROOT, "archive", "raw"),
        )

    sessions = list_sessions()
    paths = []
    for session in sessions[:count]:
        try:
            path = bridge_to_archive(session["id"], archive_dir)
            paths.append(path)
        except RuntimeError as e:
            sys.stderr.write(f"[BRIDGE] Skipping {session['id']}: {e}\n")
    return paths


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="OpenCode Session Bridge")
    ap.add_argument(
        "--all",
        dest="bridge_all_flag",
        action="store_true",
        help="Bridge all sessions",
    )
    ap.add_argument(
        "--latest",
        type=int,
        default=0,
        metavar="N",
        help="Bridge only the N most recent sessions",
    )
    ap.add_argument(
        "--archive-dir",
        default=None,
        help="Override archive output directory",
    )
    args = ap.parse_args()

    if args.bridge_all_flag:
        n = bridge_all(archive_dir=args.archive_dir)
        print(f"[BRIDGE] Exported {n} sessions.")
    elif args.latest > 0:
        paths = bridge_latest(archive_dir=args.archive_dir, count=args.latest)
        print(f"[BRIDGE] Exported {len(paths)} sessions.")
        for p in paths:
            print(f"  {p}")
    else:
        sessions = list_sessions()
        if not sessions:
            print("[BRIDGE] No sessions found.")
        else:
            print(f"[BRIDGE] Found {len(sessions)} session(s):")
            for s in sessions:
                print(f"  {s['id']}  {s['title']}  ({s['updated']})")
