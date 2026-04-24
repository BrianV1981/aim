# A.I.M. Continuity Subsystem (Working Memory)

This directory is the immediate "Working Memory" of the A.I.M. exoskeleton. It exists to solve the fundamental problem of long-horizon LLM sessions: **Context Collapse**.

## The Problem: The 40% Rule
Token consumption is not linear; it is cumulative. As a session drags on, the active context window fills with thousands of lines of terminal output, failed debugging attempts, and "thrashing." 

If an agent's context window reaches 50% capacity, its "attention weights" become hopelessly diluted by its own past. Attempting to force an agent to compress its own sprawling 1-million-token history down to 10% causes severe hallucinations. The agent will lose track of the architecture and forget variable names. 

*An agent at 30% capacity is a genius. The same agent forced to compress from 50% down to 15% is lobotomized.*

## The Solution: The Sprint Cycle & Relay Baton
A.I.M. is designed to be operated in tight, focused "Sprint Cycles." You do not build a whole app in one terminal session. You use one agent to map the code, then you kill it. You spin up a new agent to execute the code.

This directory contains the **Relay Batons** passed between those agents:

### 1. `LAST_SESSION_CLEAN.md` (The Noise Filter)
When a session ends, you do not pass the raw, 500,000-character JSON chat transcript to the next agent. That is raw noise. 
Instead, the native `scripts/extract_signal.py` script parses the JSON. Using purely deterministic Python (no LLMs), it mathematically strips out all JSON brackets, base64 tool signatures, and conversational fluff. It creates a tight, pristine Markdown document that is often **80% smaller** than the original file. This is the clean narrative of exactly what the last agent did.

### 2.  (The Tactical Handoff)
Before an agent dies, it (or the `aim handoff` command) synthesizes its final state into this document. This is the explicit "To-Do" list and situational awareness brief for the incoming agent.

## The Universal Continuity Mandate
Every A.I.M. agent—from the default bootstrap template to highly specialized personas (like the Python Specialist)—is hardcoded with the **Universal Continuity Mandate** in its `GEMINI.md` file. 

When a new agent spins up, it is explicitly ordered to read the `LAST_SESSION_CLEAN.md` and  before it writes a single line of code. This ensures the new, "fresh" agent inherits the epistemic certainty of the previous agent, without inheriting the massive token weight of the previous agent's struggle.