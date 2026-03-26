# Bug Report: Memory System Freeze

## Symptoms
- No hourly summaries are being generated.
- No reports/distillation/memory.md upgrade reports are being successfully committed.
- The `aim memory` pipeline runs but yields `0` updated files for Tier 1 and crashes at Tier 4 during auto-commit.

## Root Cause Analysis
We have identified two distinct logical bugs causing the pipeline to freeze:

### 1. Tier 1 Hourly Summarizer (The Temporal Drop Bug)
In `hooks/tier1_hourly_summarizer.py`, there is a temporal filter that checks if a message's timestamp matches today's date (`ts.startswith(today_str)`). If it does not (e.g., the session crossed midnight, or the script runs a day later), the message is skipped.
**The Fatal Flaw:** Even though the older messages are skipped, the state tracker blindly updates the read pointer to the end of the file:
```python
if not new_history:
    update_state(session_id, last_indexed_turn=len(history), last_narrated_turn=len(history))
```
This permanently marks unread older history as "processed". Consequently, no hourly logs are generated for that data, starving the rest of the memory pipeline.

### 2. Tier 4 Memory Proposer (The Missing Header Bug)
In `src/tier4_memory_proposer.py`, the final memory proposal is generated without the `### 3. MEMORY DELTA` header. However, `scripts/aim_cli.py` specifically requires this exact string to parse and apply the commit:
```python
if "### 3. MEMORY DELTA" not in content:
    print("Error: Proposal is missing the '### 3. MEMORY DELTA' header.", file=sys.stderr)
```
This causes `aim commit` (and the `AUTO-DISTILL` feature) to instantly crash, meaning Tier 4 reports are never merged into `MEMORY.md`.

## Next Steps / Brainstorming
**Should we fix this or rebuild?**
Since the bugs are relatively simple string formatting and pointer logic errors, they could be patched surgically in a few minutes. However, according to `docs/MEMORY_BRAIN_OVERHAUL_GAMEPLAN.md` and the existing issues (e.g., #56 - #61 in the aim repo tracking "Phase 32: The Memory Brain Overhaul"), there is already an active roadmap to transition away from this "full state overwrite" architecture toward an "Event Sourcing / Delta Ledger" model. 

*Debate:* Fixing these scripts means putting band-aids on the legacy scholastic architecture (`tier1`, `tier2`, `tier3`, `tier4`). Moving straight to the Brain System Rebuild (Phase 32) would resolve these issues structurally by decommissioning the flawed tier loops and replacing them with the unified "Session Summarizer" -> "Memory Delta Proposer" flow, letting `aim commit` handle intelligent AI merging as mapped out in the roadmap.