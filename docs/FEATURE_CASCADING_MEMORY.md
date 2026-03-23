# Key Feature: The Cascading Memory Engine

**The Problem:** Unbounded context leads to AI amnesia and massive API bills. If an agent tries to remember every terminal error and `ls` command from a 50-turn session, its context window overflows, and it forgets the project's actual architectural rules.

**The Solution:** The Cascading Memory Engine. A 4-Tier, self-cleaning hierarchy that mimics the human brain's progression from short-term chaotic buffering to long-term crystalized memory.

---

## The Biological Metaphor
A.I.M. processes information exactly like a human engineer:
1. **The Autonomic Nervous System:** You don't think about breathing. A.I.M. doesn't think about saving logs. Background Python scripts intercept terminal events silently.
2. **The Conscious Mind:** During the day, you process noise. A.I.M. uses Tier 1 and Tier 2 to squash terminal noise into structured daily reports.
3. **The Subconscious:** You file away fundamental lessons to permanent memory. A.I.M. uses Tier 4 to extract permanent project rules and embed them into the SQLite database.

## The 4 Tiers of Distillation

### Tier 1: The Harvester (Hourly Buffer)
*   **Trigger:** Automatically fires on every 5th high-impact tool execution.
*   **Mechanism:** It takes the raw JSON transcript, rips out all the terminal ANSI codes and raw `stdout` dumps, and extracts a "Signal Skeleton" (reducing token weight by up to 85%).
*   **Output:** A concise, 3-sentence technical narrative of what was just accomplished, saved to `memory/hourly/`.

### Tier 2: Daily Distillation (REM Sleep)
*   **Trigger:** Manual (`aim memory`) or scheduled.
*   **Mechanism:** Squashes 24 hours of hourly logs into a single Daily Report. It explicitly identifies completed tasks and deletes them from active memory.
*   **Garbage Collection:** Once the Daily Report is generated, it automatically deletes the underlying `memory/hourly/` logs to prevent file bloat.

### Tier 3: Weekly Arc (Deep Consolidation)
*   **Mechanism:** Synthesizes 7 Daily Reports into a broader strategic review. It identifies momentum shifts and persistent blockers.
*   **Garbage Collection:** Automatically deletes the underlying `memory/daily/` logs.

### Tier 4: The Apex Proposer (Personality Shifts)
*   **Mechanism:** Acts as the final filter. It reads the Weekly Arc and compares it against the agent's fundamental `core/MEMORY.md` file. It generates a strict Git-style diff proposing permanent changes to the agent's operating rules.
*   **Approval:** The AI cannot modify its own soul. It places the proposal in `memory/proposals/` for the human operator to review and apply via `aim commit`.

## The Result
Your AI operates with infinite memory without ever hitting a context limit, because the scaffolding of its thought process is systematically destroyed the moment the final lesson is learned.