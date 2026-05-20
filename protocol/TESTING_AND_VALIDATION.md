# Testing, Validation & The TDD Reflex

This document outlines the mandatory validation protocols for all A.I.M. agents. In the A.I.M. ecosystem, code generation is meaningless without mathematical proof. 

## 1. The Vibe Coding Trap
"Vibe Coding" refers to an LLM generating code that "looks right" based purely on its pre-trained base weights or conversational momentum, without empirical validation. 
**This is strictly prohibited.** Raw flagship LLMs operating without an exoskeleton will generate code that fails under production concurrency or breaks legacy systems.

## 2. The TDD Reflex (Test-Driven Development)
A.I.M. agents must operate with a mandatory "TDD Reflex." Every architectural change, feature addition, or bug fix must be mathematically sound and verifiable.
1.  **Reproduce First:** Before modifying any core logic, the agent must write a failing test case (or execution script) that empirically reproduces the reported bug or demonstrates the missing feature.
2.  **Implement:** The agent uses its tools to implement the fix.
3.  **Validate:** The agent runs the test suite. If the test fails, the agent must diagnose the failure, adjust its approach, and try again. 
4.  **Finality:** Validation is the only path to finality. An agent must never assume success or deploy unverified changes.

## 3. The 30% Rule & Context Collapse
Long-horizon agents degrade mathematically as their context window fills. Past 30% utilization, agents lose epistemic certainty, forget instructions, and begin to hallucinate (Vibe Code).
*   **The Golden Rule:** Always spin up a new agent BEFORE compression is necessary.
*   **The Sprint:** Treat terminal sessions like sprint cycles, not marathons. When an agent has completed a distinct logical phase (or begins to thrash), it must execute `/reincarnate` to teleport its specific "Will" (via the Gameplan) to a fresh, unburdened agent vessel. This ensures Senior-level precision is maintained indefinitely.