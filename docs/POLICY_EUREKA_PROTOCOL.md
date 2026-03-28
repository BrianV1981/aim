# The Eureka Protocol (Phase 39)

> ⚠️ **AGENT INSTRUCTION: HINDSIGHT PRUNING**
> If you spend 20,000 tokens thrashing to fix a bug, and the final solution is a 1-line change, your context window is permanently polluted with dead ends. The Eureka Protocol automatically detects this and replaces the thrashing with a single, pristine solution.

## The Problem: Context Thrashing
In a long-running agentic session, trial-and-error dominates the context window. If you try 5 different ways to fix a TypeScript error before finding the right one, the next time you encounter a similar error, the LLM's attention mechanism might pull one of the *failed* attempts from earlier in the session. This is known as "Lost in the Middle" context degradation.

## The Solution: Heuristic Detection
The `session_summarizer.py` daemon now includes a heuristic called **The Eureka Protocol**. 

During the memory distillation pipeline, it evaluates the ratio of `Tokens Spent` to `Actions Executed`.
*   If an agent spends massive amounts of tokens (e.g., `> 20,000`) across multiple turns...
*   But the final resolution only involved a tiny number of actions (e.g., `< 3` file writes)...
*   The system flags a **"Eureka Moment."**

It realizes that 90% of the session history was useless thrashing.

## Hindsight Pruning & Synthesis
When a Eureka Moment is flagged, instead of feeding the entire noisy session into the Memory Pipeline to be summarized, the system takes only the final successful turns and forces the Tier 1 Brain to generate a **[EUREKA SYNTHESIS]**.

The resulting memory is hyper-compressed: *"The agent spent 20k tokens debugging X. The final solution was simply Y."*

This pristine, zero-noise fact is then written to the Engram DB, ensuring future agents never repeat the same thrashing cycle. In future iterations, this synthesis will also be used to physically rewrite the live `session.json`, granting the active agent its tokens back.