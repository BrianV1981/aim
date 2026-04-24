import os, sys, shutil

os.makedirs("workspace/issue-388/skills/reincarnate_temp/scripts", exist_ok=True)
shutil.copy("workspace/issue-388/skills/reincarnate.py", "workspace/issue-388/skills/reincarnate_temp/scripts/run.py")
shutil.copy("workspace/issue-388/skills/reincarnate_SKILL.md", "workspace/issue-388/skills/reincarnate_temp/SKILL.md")
shutil.make_archive("workspace/issue-388/skills/reincarnate", "zip", "workspace/issue-388/skills/reincarnate_temp")
os.rename("workspace/issue-388/skills/reincarnate.zip", "workspace/issue-388/skills/reincarnate.skill")
shutil.rmtree("workspace/issue-388/skills/reincarnate_temp")
if os.path.exists("workspace/issue-388/skills/reincarnate.py"):
    os.remove("workspace/issue-388/skills/reincarnate.py")
if os.path.exists("workspace/issue-388/skills/reincarnate_SKILL.md"):
    os.remove("workspace/issue-388/skills/reincarnate_SKILL.md")
print("Packaged reincarnate.skill")

with open("workspace/issue-388/scripts/aim_reincarnate.py", "r") as f:
    content = f.read()

content = content.replace(
    "Wake up. MANDATE: 1. Read AGENTS.md and acknowledge your core constraints. 2. Read HANDOFF.md. 3. You must read continuity/REINCARNATION_GAMEPLAN.md, continuity/CURRENT_PULSE.md, and continuity/ISSUE_TRACKER.md before taking any action or responding. (NOTE: Use run_shell_command with 'cat' to read the continuity files, as they are gitignored and your read_file tool will fail).",
    "Wake up. MANDATE: 1. Read AGENTS.md and acknowledge your core constraints. 2. Read continuity/REINCARNATION_GAMEPLAN.md and continuity/ISSUE_TRACKER.md before taking any action or responding. (NOTE: Use run_shell_command with 'cat' to read the continuity files, as they are gitignored and your read_file tool will fail)."
)
with open("workspace/issue-388/scripts/aim_reincarnate.py", "w") as f:
    f.write(content)
print("Updated aim_reincarnate.py")

with open("workspace/issue-388/scripts/aim_init.py", "r") as f:
    content = f.read()

content = content.replace("1. `HANDOFF.md` (The \"Front Door\" to the project's current state and directives).\n2. `continuity/ISSUE_TRACKER.md`", "1. `continuity/ISSUE_TRACKER.md`")
content = content.replace("**CRITICAL PROTOCOL:** You MUST read `HANDOFF.md` and `continuity/REINCARNATION_GAMEPLAN.md` sequentially", "**CRITICAL PROTOCOL:** You MUST read `continuity/REINCARNATION_GAMEPLAN.md`")
content = content.replace(", and `continuity/CURRENT_PULSE.md`", "")
content = content.replace("`continuity/CURRENT_PULSE.md`", "")

# Remove HANDOFF.md generation from init workspace
content = content.replace('        "HANDOFF.md": "# A.I.M. Continuity Handoff\\n\\n## ⚠️ CRITICAL INSTRUCTION FOR INCOMING AGENT ⚠️\\nYou are waking up in the middle of a continuous operational loop.\\nTo prevent hallucination, you must establish **Epistemic Certainty** regarding the previous agent\'s actions before you write any code.\\n\\n### The Continuity Protocol (The Reincarnation Gameplan)\\n*(NOTE: You MUST use `run_shell_command` with `cat` to read the continuity files, as they are gitignored and `read_file` will fail).*\\n\\n1. Read `continuity/REINCARNATION_GAMEPLAN.md` (The rigid executive directive passed by the previous agent).\\n2. Read `continuity/CURRENT_PULSE.md` (The explicit handoff state and project edge).\\n3. Read `continuity/ISSUE_TRACKER.md` (The local ledger of all open and closed tickets).\\n4. Do not blindly assume success. Verify the state via file reads or tests.\\n",\n', "")

with open("workspace/issue-388/scripts/aim_init.py", "w") as f:
    f.write(content)
print("Updated aim_init.py")

if os.path.exists("workspace/issue-388/AGENTS.md"):
    with open("workspace/issue-388/AGENTS.md", "r") as f:
        content = f.read()
    content = content.replace("1. `HANDOFF.md` (The \"Front Door\" to the project's current state and directives).\n2. `continuity/ISSUE_TRACKER.md`", "1. `continuity/ISSUE_TRACKER.md`")
    content = content.replace("**CRITICAL PROTOCOL:** You MUST read `HANDOFF.md` and `continuity/REINCARNATION_GAMEPLAN.md` sequentially", "**CRITICAL PROTOCOL:** You MUST read `continuity/REINCARNATION_GAMEPLAN.md`")
    content = content.replace(", and `continuity/CURRENT_PULSE.md`", "")
    content = content.replace("`continuity/CURRENT_PULSE.md`", "")
    with open("workspace/issue-388/AGENTS.md", "w") as f:
        f.write(content)
    print("Updated AGENTS.md")

if os.path.exists("workspace/issue-388/continuity/README.md"):
    with open("workspace/issue-388/continuity/README.md", "r") as f:
        content = f.read()
    content = content.replace("`REINCARNATION_GAMEPLAN.md` and `CURRENT_PULSE.md`", "`REINCARNATION_GAMEPLAN.md`")
    content = content.replace("`CURRENT_PULSE.md`", "")
    content = content.replace("`HANDOFF.md`", "")
    with open("workspace/issue-388/continuity/README.md", "w") as f:
        f.write(content)
    print("Updated continuity/README.md")
