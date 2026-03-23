#!/usr/bin/env python3
import sys, json, subprocess, os
from pathlib import Path

aim_root = Path(__file__).parent.parent
aim_cli = aim_root / "scripts" / "aim_cli.py"

try:
    print(json.dumps({"status": "Triggering memory refinement pipeline. This may take a minute."}))
    # We call aim memory which fires Tier 2 -> 3 -> 4
    result = subprocess.run(
        [sys.executable, str(aim_cli), "memory"],
        capture_output=True,
        text=True
    )
    print(json.dumps({
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip()
    }, indent=2))
except Exception as e:
    print(json.dumps({"error": str(e)}))