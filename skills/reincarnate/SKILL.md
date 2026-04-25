---
name: reincarnate
description: Mechanically triggers the Reincarnation Protocol. MUST be called whenever the context window is full or the user explicitly commands it.
---

# reincarnate

Mechanically triggers the Reincarnation Protocol. MUST be called whenever the context window is full or the user explicitly commands it.

**CRITICAL MANDATE:** 
You MUST execute the reincarnation handoff as a strict, multi-turn interactive sequence. If you attempt to write the Gameplan and run the teleport script in the same turn, the Gemini CLI will kill the session before your history is flushed to disk, corrupting the memory of the incoming agent. 

When the Operator commands you to reincarnate, you must follow this exact order:

### TURN 1: The Prompt
Use your `ask_user` tool to ask the Operator: "Do you have a handoff message for the next agent? (Leave blank to skip)". Wait for their response to finish your turn.

### TURN 2: The Gameplan Flush
Once you receive the Operator's answer, use your `write_file` tool to generate the `continuity/REINCARNATION_GAMEPLAN.md` file. You MUST include their handoff message in the file using the strict template below. 
After using the tool, your text response MUST be: **"Gameplan written and context flushed. Report back 'Proceed' when you are ready to teleport."** 
Wait for the Operator to say "Proceed" to finish your turn. This pause guarantees the JSONL history is written to disk.

### TURN 3: The Teleport
Once the Operator says "Proceed", use your `run_shell_command` tool to execute the teleport script below:

```bash
python3 aim_core/aim_reincarnate.py
```
*(Note: Because the skill archive path changed, the script to run is directly in the core package).*

---

### The Strict Gameplan Template
When writing the Gameplan in Turn 2, you MUST use this strict markdown template:

```markdown
# Reincarnation Gameplan

## Current Objective
[Briefly describe the overarching goal or issue currently being worked on.]

## Completed Steps
- [List 2-3 key actions or code changes completed in the outgoing session.]
- ...

## Unresolved Blockers / Current State
[Describe exactly where you left off. Is there a failing test? An unresolved bug? A file that needs refactoring?]

## Next Agent's First Task
[Give a specific, actionable command for the incoming agent to execute immediately upon waking up.]

## Operator Handoff Message
[Insert the message you gathered from the Operator in Turn 1 here, or remove this section if they left it blank.]
```

**CRITICAL REMINDERS FOR THE INCOMING AGENT (Include these in your mindset):**
- **The Flight Recorder:** The `continuity/private/` folder contains the "Flight Recorder" (a raw mirror of the entire previous session). If you need deep context regarding *why* a decision was made in the previous session, you can read the latest flight recorder.
- **Operator Authorization:** You MUST always report to the Operator and wait for explicit authorization before starting or beginning any new tasks/issues. Do not autonomously start executing the next epic without confirmation.
