# Memory Brain Overhaul Gameplan

## Purpose
This document captures the intended redesign of A.I.M.'s memory refinement pipeline before more incremental iteration obscures the target architecture again.

The goal is not to rewrite the entire brain. The goal is to:
- start memory refinement much earlier
- make each tier produce auditable deltas instead of opaque prose-only proposals
- clarify naming so the system is understandable to operators
- preserve the current working continuity pipeline while upgrading the memory pipeline around it

## Current Problem
The current system has a few structural weaknesses:
- memory refinement begins too late
- waiting 24 hours before meaningful `MEMORY.md` proposals is too slow
- higher tiers are forced to reason over prose-heavy proposals instead of explicit add/remove/change ledgers
- the naming scheme is partly literal and partly scholastic, which creates conceptual drift
- the TUI does not yet expose the cadence and role boundaries that the architecture actually wants

## Target Architecture

### Core Principle
Refinement should start early, but durable memory should remain conservative.

That means:
- summaries happen frequently
- memory delta proposals happen frequently
- committable `MEMORY.md` candidates must appear much earlier than they do today
- higher-trust full `MEMORY.md` rewrites still happen at stronger upper tiers
- operators can manually commit strong proposals whenever they want

### Proposed Pipeline

#### Stage 0: Session Signal Preparation
- Input: pre-pruned session histories / extracted signal
- Job: produce compact raw material for the first summarizer
- Notes:
  - this remains upstream infrastructure
  - no naming overhaul is needed here

#### Stage 1: High-Frequency Session Summarizer
- Suggested cadence: every 30 minutes
- Target frequency: 48 times per day
- Input:
  - pre-pruned session history
  - current `core/MEMORY.md`
  - optionally current continuity state for situational alignment
- Output:
  - a tight narrative summary
  - highlighted pivots, milestones, and candidate durable facts
- Purpose:
  - compress recent work into something a higher tier can actually reason over
  - identify what may deserve promotion into durable memory

#### Stage 2: Frequent Memory Delta Proposer
- Suggested cadence: hourly by default, customizable later
- Original aspiration: more frequent than daily, much earlier than the current 24-hour wait
- Input:
  - multiple Stage 1 summaries
  - current `core/MEMORY.md`
- Output:
  - a full committable `MEMORY.md` candidate
  - an explicit change ledger
- Purpose:
  - convert narrative summaries into actionable memory deltas
  - give the operator something meaningful to commit before a full day passes
  - support the real operator behavior of running `aim commit` every few hours, not only once per day

#### Stage 3: Higher-Order Consolidator
- Suggested cadence: daily
- Input:
  - all Stage 2 proposals in the window
  - all Stage 2 change ledgers
  - current `core/MEMORY.md`
- Output:
  - a stronger consolidated full `MEMORY.md` candidate
  - a merged add/remove/modify ledger with rationale
- Purpose:
  - collapse repeated truths
  - reject noise
  - reconcile conflicting lower-tier proposals

#### Stage 4: Apex Memory Refiner
- Suggested cadence: weekly or monthly
- Input:
  - higher-order consolidated proposals
  - higher-order change ledgers
  - current `core/MEMORY.md`
- Output:
  - a full rewritten `MEMORY.md` candidate
  - a final rationale for the proposed durable-memory change
- Purpose:
  - produce the cleanest possible durable-memory candidate
  - serve as the highest-trust commit source

## Required Artifact Schema
Every proposal-producing stage should emit more than prose.

Lower tiers should not only say "here is a better memory." They should also say exactly what changed.

### Required Sections
Each proposal artifact should include:
- `Candidate MEMORY.md`
- `Summary`
- `Candidate Durable Facts`
- `Proposed Adds`
- `Proposed Removes`
- `Proposed Modifications`
- `Rationale`
- `Confidence` (optional but useful)

### Why This Matters
Without an explicit ledger, higher tiers are forced to diff AI prose against AI prose, which is unstable and hard to audit.

With an explicit ledger, higher tiers can:
- merge repeated adds
- discard weak removals
- compare rationale
- reconcile conflicting changes
- produce a more trustworthy final proposal

Without a full candidate `MEMORY.md`, early proposals are also not directly committable by the current `aim commit` pipeline. That matters because operators will reasonably want to run `aim commit` every few hours, not just after a full-day or full-week cycle.

## Durable Memory Doctrine

### What Should Happen Early
- session summarization
- candidate durable fact extraction
- memory delta proposals
- full but lower-trust committable `MEMORY.md` candidates

### What Should Happen Later
- stronger full `MEMORY.md` rewrites
- aggressive pruning
- apex consolidation

### Commit Doctrine
The system should not require a full 24-hour wait before `MEMORY.md` can improve.

Operators should be able to:
- review a strong early proposal
- run `aim commit`
- promote a meaningful update sooner

Higher tiers then continue refining and compressing over longer windows.

This means the system should treat early proposals as valid commit candidates, not just intermediate internal scaffolding.

## Commit Strategy Decision

### Decision
The preferred direction is now an AI-assisted commit path, and the old proposal model should be decommissioned.

Instead of forcing lower proposal tiers to repeatedly rewrite full `MEMORY.md` candidates, the system should allow lower tiers to emit structured deltas and rationale, and let `aim commit` perform the final synthesis when the operator explicitly chooses to promote memory.

This is now the chosen architecture because it is the cleaner and more efficient design. The old approach was a design flaw that became obvious once the real commit behavior and operator usage pattern were examined closely.

### Why This Won
- repeated full-memory rewrites at lower tiers are wasteful
- lower tiers are better used for extraction, pruning, and structured recommendation
- `aim commit` is the natural place to spend tokens, because it is the intentional moment of memory promotion
- operators want to commit early and often, but not necessarily force every background tier to regenerate the whole memory file every time
- this removes the need for bulky proposal artifacts whose only purpose was to satisfy a flawed dumb commit pipeline

### New Commit Doctrine
`aim commit` should eventually support an AI merge path:
- read current `core/MEMORY.md`
- read one or more proposal ledgers
- synthesize the next `MEMORY.md`
- preserve backup/rollback behavior
- emit a concise summary of what was added, removed, and modified

### Changelog Impact
If `aim commit` becomes the intelligent merger, the old assumption that each lower tier must generate its own full memory rewrite becomes unnecessary.

That means the memory proposal system should shift away from "every stage writes a full replacement body" and toward "stages produce auditable deltas, and commit performs the final merge."

### Decommission Decision
The old "every proposal tier writes a full replacement body" model should not be preserved as a long-term compatibility target.

It should be treated as the retired architecture.

The goal is not to support both systems forever. The goal is to replace the flawed one with the cleaner one:
- lower tiers produce deltas and rationale
- `aim commit` performs the final merge into `core/MEMORY.md`

## Naming Overhaul

## Naming Problem
The current naming is mixed:
- the files are literal (`tier1_hourly_summarizer.py`, `tier2_daily_summarizer.py`)
- the config/runtime keys are scholastic (`librarian`, `chancellor`, `fellow`, `dean`)
- some docs already drift toward literal descriptors

This creates unnecessary translation overhead.

## Naming Goals
New names should be:
- explicit enough for first-time operators
- compatible with the broader brain vocabulary (`engram`, `synapse`)
- stable enough to survive future feature growth

## Recommended Strategy
Do the rename in two phases:

### Phase A: User-Facing Labels First
- update TUI labels
- update handbook/docs wording
- keep existing internal keys temporarily for compatibility

### Phase B: Internal Key Migration
- add config migration for old names
- rename internal routing keys only after the operator-facing model is stable

This reduces risk and avoids breaking existing `CONFIG.json` installs prematurely.

## Naming Options

### Option 1: Fully Literal
- `Session Summarizer`
- `Memory Delta Proposer`
- `Memory Consolidator`
- `Apex Memory Refiner`

Pros:
- highest clarity
- easiest for new users

Cons:
- least flavorful

### Option 2: Brain-Themed Explicit
- `Cortex`
- `Hippocampus`
- `Thalamus`
- `Engram Refiner`

Pros:
- fits the existing brain vocabulary better than the scholastic names
- feels more native to A.I.M.'s identity

Cons:
- some names may still require explanation

### Option 3: Hybrid Recommended
- `Session Summarizer`
- `Librarian`
- `Consolidator`
- `Dean`

Pros:
- preserves a little personality
- makes the first and most frequently touched stages much clearer

Cons:
- still mixed

## Recommendation
If the rename happens, the best long-term direction is probably brain-themed but explicit.

A strong candidate set would be:
- `Session Summarizer`
- `Memory Delta Proposer`
- `Memory Consolidator`
- `Engram Refiner`

This is less whimsical than the scholastic chain, but much more understandable.

If a more branded brain-lexicon version is desired later, it should be introduced only after the behavior and cadence are stable.

## TUI Requirements
The TUI should eventually expose:
- per-stage provider / model selection
- per-stage cadence / duration
- enable / disable toggles
- health visibility for continuity and memory artifacts

The specialist-tier screen should be expanded so each stage has:
- an LLM/provider section
- a cadence section

## Health and Bootstrap Requirements
The continuity layer is foundational. The system is degraded if continuity artifacts are missing.

Minimum expectations:
- `continuity/CURRENT_PULSE.md` always exists after init/bootstrap/clean wipe
- `continuity/FALLBACK_TAIL.md` exists and remains readable
- TUI health checks surface missing or stale continuity artifacts as real failures

## Implementation Order

### Step 1
Lock the architecture:
- confirm stage count
- confirm cadence defaults
- confirm artifact schema
- confirm naming direction

### Step 2
Update docs and roadmap language so the names and purpose stop drifting.

### Step 3
Add config support for:
- per-stage cadence
- per-stage provider/model routing
- new stage wiring for the faster proposal layer

### Step 4
Implement the artifact split:
- narrative summaries
- memory delta proposals with ledgers

### Step 5
Update TUI controls and health checks.

### Step 6
Only after the above is stable, migrate internal naming keys if still desired.

## Practical Guidance
- Do not make the first narrative summarizer rewrite full `MEMORY.md`.
- Make proposal-producing tiers prioritize structured delta ledgers with rationale.
- Treat `aim commit` as the likely final synthesis layer for applying those deltas into `core/MEMORY.md`.
- Do not carry the old full-body proposal system forward longer than needed to complete the migration.
- Treat early memory proposals as operator-usable outputs, not just hidden internal scaffolding.
- Favor clarity over mythology when naming runtime components.

## Summary
This overhaul is not a total rewrite. It is a schema and cadence upgrade.

The two most important changes are:
- begin meaningful memory refinement much earlier than 24 hours
- require explicit add/remove/modify ledgers at each proposal tier, with `aim commit` evolving into the intelligent merge point

If those two changes are implemented cleanly, the rest of the system becomes much easier to reason about, tune, and trust.
