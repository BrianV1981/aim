# Phase 45: The Quarantine Daemon (Non-Destructive Context Pruning)

> ⚠️ **STATUS: CONCEPTUAL ARCHITECTURE (BLEEDING EDGE)**
> *This document outlines a highly advanced context-management architecture designed to act as a "Non-Destructive Garbage Collector" for LLM memory arrays. We believe this pattern sits at the absolute cutting edge of agentic systems, and we are open-sourcing it for free.*

## 1. The Market Gap

As of early 2026, managing "Context Rot" is the primary bottleneck for autonomous agents.
*   **The Industry Solution:** Commercial tools like Claude Code and Roo Code rely on manual user intervention. They provide a `/rewind` command, forcing the human to realize they are in a rabbit hole and manually delete the conversation history. Once deleted, the data is gone forever.
*   **The Academic Solution:** Research frameworks like TC-RAG use "State Pops" to rewind context when the AI detects its own logical contradictions.

**The Missing Link:** No framework currently handles **User-Side Thrashing** (human flip-flopping) autonomously while maintaining **Forensic Data Safety**. 

A.I.M. solves this via the **Quarantine Daemon**.

## 2. The Problem: User-Side Thrashing

When an operator changes their mind during a build, it devastates the LLM's context window.

**The "Flip-Flop" Scenario:**
1. **User:** "Add a red button."
2. **AI:** *Writes code for a red button.*
3. **User:** "Actually, make it blue."
4. **AI:** *Rewrites code for a blue button.*
5. **User:** "Nevermind, just delete the button completely."
6. **AI:** *Deletes the button code.*

In a standard agentic CLI, the active context window is now poisoned with 6 turns of useless, contradictory logic and obsolete code blocks. The LLM continues to pay massive API token costs to "remember" a button that no longer exists, increasing the risk of future hallucinations.

## 3. The Architecture: "Ctrl+Z for AI Context"

The Quarantine Daemon operates as a background Python hook that intercepts the raw JSON chat array and performs a **Soft Delete**.

### Step 1: Heuristic Detection
The daemon monitors the user's prompts for "Reversion Semantics" (e.g., *"revert that"*, *"nevermind"*, *"actually go back to"*). When detected, it identifies that a logical side-quest has just been invalidated.

### Step 2: The Surgical Excision
Instead of forcing the LLM to write a response acknowledging the reversion, the daemon programmatically steps in. It calculates the exact conversational turn where the side-quest began, and physically slices those JSON blocks out of the active terminal session's memory array.

### Step 3: The Quarantine (Soft Delete)
Silent deletion is dangerous. If the user later decides, *"Wait, what was the hex code for that blue button we tried earlier?"*, the data must be retrievable. 

The daemon does not delete the excised JSON. Instead, it appends the raw JSON blocks to a local graveyard file: `continuity/private/PRUNED_GRAVEYARD.jsonl`.

### Step 4: Synthetic Injection
To prevent the human operator or the LLM from getting confused by the sudden jump in conversation, the daemon replaces the excised turns with a single, ultra-compressed synthetic marker:

`[SYSTEM NOTE: The previous 6 turns regarding the button UI were quarantined by the daemon to prevent context bloat. To restore this data, run 'aim unprune'.]`

## 4. The Result

By implementing the Quarantine Daemon, A.I.M. achieves two previously mutually exclusive goals:
1. **Zero Context Weight:** The AI's active token payload drops instantly. It stops hallucinating based on dead-end code blocks.
2. **100% Forensic Fidelity:** The operator loses absolutely nothing. If an old idea becomes relevant again, the `aim unprune` command instantly stitches the quarantined JSON back into the active array. 

It is a perfectly safe, automated garbage collection system for human logic.