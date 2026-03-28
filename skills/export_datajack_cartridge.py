#!/usr/bin/env python3
import sys, json, subprocess, os
from pathlib import Path

aim_root = Path(__file__).parent.parent
aim_exchange = aim_root / "scripts" / "aim_exchange.py"

try:
    arg_input = sys.argv[1] if len(sys.argv) > 1 else "{}"
    try:
        args = json.loads(arg_input)
        if isinstance(args, dict):
            keyword = args.get("keyword", "expert-")
            out_name = args.get("name", "export.engram")
        else:
            keyword = str(args)
            out_name = sys.argv[2] if len(sys.argv) > 2 else f"{keyword}.engram"
    except (json.JSONDecodeError, TypeError, ValueError):
        # Fallback: Assume the user passed raw string arguments via CLI
        keyword = sys.argv[1]
        out_name = sys.argv[2] if len(sys.argv) > 2 else f"{keyword}.engram"
    
    if not out_name.endswith(".engram"): out_name += ".engram"
    
    result = subprocess.run(
        [sys.executable, str(aim_exchange), "export", keyword, "--out", out_name],
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