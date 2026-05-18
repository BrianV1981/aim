#!/usr/bin/env python3
"""TDD: Verify reincarnation protocol fixes."""
import os, sys

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
failures = 0

# Test 1: Wake-up prompt includes REINCARNATION_CONNECT.md
print("Test 1: Wake-up prompt includes REINCARNATION_CONNECT.md")
with open(os.path.join(AIM_ROOT, "aim_core", "aim_reincarnate.py")) as f:
    content = f.read()
if "REINCARNATION_CONNECT.md" in content:
    print("  PASS")
else:
    print("  FAIL: REINCARNATION_CONNECT.md not found in wake-up prompt")
    failures += 1

# Test 2: AGENTS.md step 10 includes read-connect-exit sequence
print("Test 2: AGENTS.md step 10 includes read-connect-exit")
with open(os.path.join(AIM_ROOT, "AGENTS.md")) as f:
    content = f.read()
if "REINCARNATION_CONNECT.md" in content and "Your final act is to deliver this message and exit" in content:
    print("  PASS")
else:
    print("  FAIL: Missing read-connect-exit sequence in AGENTS.md")
    failures += 1

# Test 3: REINCARNATION_CONNECT.md is written by the script
print("Test 3: aim_reincarnate.py writes REINCARNATION_CONNECT.md")
if "REINCARNATION_CONNECT.md" in open(os.path.join(AIM_ROOT, "aim_core", "aim_reincarnate.py")).read():
    print("  PASS")
else:
    print("  FAIL: REINCARNATION_CONNECT.md not referenced in aim_reincarnate.py")
    failures += 1

print()
print(f"Passed: {3 - failures}/3")
sys.exit(failures)
