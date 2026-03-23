#!/usr/bin/env python3
import sys, json, subprocess, os
from pathlib import Path

aim_root = Path(__file__).parent.parent
aim_cli = aim_root / "scripts" / "aim_cli.py"

try:
    args_json = sys.argv[1] if len(sys.argv) > 1 else "{}"
    args = json.loads(args_json)
    keyword = args.get("keyword", "expert-")
    out_name = args.get("name", "export.engram")
    
    result = subprocess.run(
        [sys.executable, str(aim_cli), "exchange", "export", keyword, "--out", out_name],
        capture_output=True,
        text=True,
        cwd=aim_root
    )
    print(json.dumps({
        "status": "Export Complete",
        "output": result.stdout.strip(),
        "error": result.stderr.strip(),
        "file": out_name
    }, indent=2))
except Exception as e:
    print(json.dumps({"error": str(e)}))