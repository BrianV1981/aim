# A.I.M. Reincarnation Gameplan SOP

This document defines the strict, high-fidelity structure required for all `continuity/REINCARNATION_GAMEPLAN.md` files generated before an agent executes a `/reincarnate` command. 

## 1. The Rule of Epistemic Certainty
The outgoing agent must act as a precise tactician. The incoming agent will wake up with a blank context window. The Gameplan is their only link to the current mission state. It must provide immediate, actionable, and localized context.

## 2. Mandatory Gameplan Structure
Every `REINCARNATION_GAMEPLAN.md` MUST contain the following 5 sections, formatted exactly as shown:

### 1. The Commander's Summary
*   **What it is:** A brief, 2-3 sentence overview of the current epic and what was achieved during your session.

### 2. Tactical State (The "Where Am I?" Block)
*   **What it is:** The explicit state of the local environment.
*   **Requirements:**
    *   **Active Ticket:** (e.g., Issue #617)
    *   **Active Worktree:** (e.g., `workspace/issue-617`)
    *   **Primary Files:** List the absolute or relative paths to the specific files you were actively modifying (e.g., `aim_core/aim_cli.py`, `tests/test_cli.py`).

### 3. The Localized Directory Map
*   **What it is:** A focused, generated file tree showing *only* the directories and files relevant to the active problem. 
*   **Requirement:** Do not list the entire project root. Scope the map to the specific modules or components involved in the current ticket to provide a clean "Area of Operations."

### 4. Epistemic Warnings & Dead Ends
*   **What it is:** A critical list of failed approaches or technical "gotchas."
*   **Requirement:** If you tried a specific architecture, shell command, or logic path and it failed, you MUST document it here. Provide the exact reason it failed. This prevents the incoming agent from repeating the same hallucinations or mistakes.

### 5. Immediate Next Action
*   **What it is:** A prescriptive, step-by-step instruction for the new agent.
*   **Requirement:** Tell the incoming agent exactly what command to run first (e.g., "Run `pytest tests/test_retriever.py` to observe the current failure state before modifying the database logic").
