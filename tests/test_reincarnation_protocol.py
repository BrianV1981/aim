#!/usr/bin/env python3
"""TDD: Verify reincarnation protocol simplification — no REINCARNATION_CONNECT.md redundancy."""
import os, sys

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
failures = 0

# Test 1: Wake-up prompt does NOT include REINCARNATION_CONNECT.md
print("Test 1: Wake-up prompt excludes REINCARNATION_CONNECT.md (simplified protocol)")
with open(os.path.join(AIM_ROOT, "aim_core", "aim_reincarnate.py")) as f:
    content = f.read()
if "REINCARNATION_CONNECT.md" not in content:
    print("  PASS")
else:
    print("  FAIL: REINCARNATION_CONNECT.md still referenced in aim_reincarnate.py")
    failures += 1

# Test 2: AGENTS.md step 10c instructs extracting session name from stdout
print("Test 2: AGENTS.md step 10c uses stdout-based session extraction")
with open(os.path.join(AIM_ROOT, "AGENTS.md")) as f:
    content = f.read()
if "Extract the tmux session name from the script stdout output" in content:
    print("  PASS")
else:
    print("  FAIL: Missing stdout-based session extraction in AGENTS.md step 10c")
    failures += 1

# Test 3: aim_reincarnate.py no longer writes a connect file
print("Test 3: aim_reincarnate.py does not write REINCARNATION_CONNECT.md")
if "REINCARNATION_CONNECT.md" not in open(os.path.join(AIM_ROOT, "aim_core", "aim_reincarnate.py")).read():
    print("  PASS")
else:
    print("  FAIL: REINCARNATION_CONNECT.md still referenced in aim_reincarnate.py")
    failures += 1

print()
print(f"Passed: {3 - failures}/3")
sys.exit(failures)
