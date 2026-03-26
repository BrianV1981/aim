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
*   **Mechanism (The True Zero-Token Reflex):** It takes the raw JSON transcript, rips out all the terminal ANSI codes and raw `stdout` dumps using pure Python. It extracts a "Signal Skeleton" (reducing token weight by up to 85%) before an LLM ever touches it.
*   **Output:** A concise, 3-sentence technical narrative of what was just accomplished, saved to `memory/hourly/`.

### Tier 2: Daily Distillation (The First Proposal)
*   **Mechanism:** Reads the last 24 hours of Tier 1 hourly logs. It explicitly identifies completed tasks and newly discovered architectural rules.
*   **Output:** Generates a **Daily Memory Proposal** (a strict Git-style diff proposing what to add/remove from your `core/MEMORY.md`). 

### Tier 3: Weekly Arc (The Second Proposal)
*   **Mechanism:** If Daily Proposals pile up, Tier 3 synthesizes 7 Daily Proposals into a broader strategic review.
*   **Output:** Generates a condensed **Weekly Memory Proposal**, dropping transient, day-to-day noise.

### Tier 4: The Apex (The Monthly Proposal)
*   **Mechanism:** If Weekly Proposals pile up, Tier 4 synthesizes 4 Weekly Proposals into the ultimate, highest-level strategic summary.
*   **Output:** Generates a definitive **Monthly Memory Proposal**.

## The Execution (`aim commit`)
The AI cannot modify its own soul. It places these proposals in `memory/proposals/` for the human operator. 

**The beauty of the system is the "Rolling Proposal."** 
You do not have to wait a month to update your memory. You can type `aim commit` at *any time* after 24 hours. The command simply grabs the *most recent, highest-tier proposal available* (whether it's a Daily, Weekly, or Monthly proposal), applies it to your `core/MEMORY.md`, and instantly deletes all underlying hourly/daily scaffolding.