---
name: reincarnate
description: Mechanically triggers the Reincarnation Protocol. MUST be called whenever the context window is full or the user explicitly commands it.
---

# reincarnate

Mechanically triggers the Reincarnation Protocol. MUST be called whenever the context window is full or the user explicitly commands it.

Before calling this skill, you MUST generate the `continuity/REINCARNATION_GAMEPLAN.md` file using your `write_file` tool to document your current state and instructions for the incoming agent.

If the user gave you a specific message to relay to the next agent, you MUST pass it as the `handoff_message` argument. If they didn't, leave it blank.

**Arguments:**  
- `handoff_message` (string, optional) — A specific message or note to pass to the next agent.

To execute this skill, run the included Python script and pass any JSON arguments if required by the prompt:

```bash
python3 scripts/run.py '{"handoff_message": "..."}'
```

### The Strict Gameplan Template
When writing the Gameplan, you MUST use this strict markdown template:

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
```
