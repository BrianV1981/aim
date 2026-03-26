# Onboarding Identity Map

This document defines where onboarding data belongs, why it belongs there, and how A.I.M. should treat each file during ingestion.

## Design Rules

1. `GEMINI.md` or `AGENTS.md` lives at the repo root.
It is the active operating prompt for the coding agent.

2. Core identity belongs in `core/`.
This includes structured facts about the operator, durable profile information, and machine-readable runtime configuration.

3. `memory/` and `continuity/` are not identity stores.
They support memory refinement, recall, checkpoints, proposals, and continuity artifacts produced over time.

4. `synapse/` is for external expert knowledge and ingest-only reference material.
It should not be the primary home for the operator's own identity.

## File Roles

### `GEMINI.md` or `AGENTS.md`

Purpose:
The live instruction surface for the agent.

What belongs here:
- agent identity
- operator name
- execution style defaults
- retrieval mandates
- planning rules
- guardrails

What does not belong here:
- detailed operator biography
- long-form social/personality analysis
- machine configuration
- evolving memory summaries

Why:
This file should stay prompt-efficient and behavior-oriented.

### `core/OPERATOR.md`

Purpose:
Canonical structured operator identity.

What belongs here:
- legal or preferred name
- tech stack
- working style
- stable personal principles
- mission or goals
- business context
- concise factual profile fields gathered during onboarding

What does not belong here:
- shell paths
- model routing
- API endpoints
- verbose persona prose
- rolling memory summaries

Why:
`OPERATOR.md` should be the stable source of truth for factual operator metadata.

### `core/OPERATOR_PROFILE.md`

Purpose:
Narrative operator profile used to capture richer persona and behavioral inference.

What belongs here:
- Grok-derived profile text
- communication style summary
- philosophical and social archetype notes
- inferred problem-solving style
- voice and tone guidance

What does not belong here:
- hard configuration
- filesystem paths
- API keys
- generated session memory

Why:
This file complements `OPERATOR.md`.
`OPERATOR.md` is structured fact.
`OPERATOR_PROFILE.md` is richer interpretive context.

### `core/MEMORY.md`

Purpose:
Durable top-level memory anchor for A.I.M.

What belongs here:
- concise long-term state
- durable project posture
- high-signal operator/project continuity notes

What does not belong here:
- raw onboarding questionnaire dumps
- low-level runtime config
- temporary chat residue

Why:
`MEMORY.md` is a compact continuity document, not the canonical operator profile.

### `core/CONFIG.json`

Purpose:
Machine-readable runtime configuration.

What belongs here:
- path configuration
- provider/model defaults
- service endpoints
- operational settings
- allowed root
- vault locations
- pruning or maintenance thresholds

What does not belong here:
- operator biography
- persona text
- life rules in prose
- Grok profile data
- freeform notes for retrieval

Why:
`CONFIG.json` should be deterministic and operational.
If a value changes how the software runs, it belongs here.
If it changes how the agent understands the operator, it belongs in markdown identity docs instead.

## TUI Update Contract

The `aim tui` "Update Operator Profile & Behavior" flow should remain symmetric with onboarding.

It should update:
- `GEMINI.md` for execution mode, cognitive level, conciseness, and lightweight guardrails
- `core/OPERATOR.md` for structured operator facts
- `core/OPERATOR_PROFILE.md` for narrative persona text

It should not write operator identity into:
- `core/CONFIG.json`
- `memory/`
- `continuity/`

## Prompt-To-File Map

### Behavioral prompts

Prompt:
`Grammar & Explanation Level`

Destination:
`GEMINI.md` / `AGENTS.md`

Reason:
This controls agent presentation behavior, not runtime configuration.

Prompt:
`Enable Extreme Conciseness`

Destination:
`GEMINI.md` / `AGENTS.md`

Reason:
This is prompt behavior.

Prompt:
`Execution Mode`

Destination:
`GEMINI.md` / `AGENTS.md`

Reason:
This is agent operating posture.

Prompt:
`Target Model Intelligence`

Destination:
`GEMINI.md` / `AGENTS.md`

Reason:
This controls prompt guardrails and instruction strictness.

### Operator prompts

Prompt:
`Your Name`

Destination:
- `GEMINI.md` / `AGENTS.md`
- `core/OPERATOR.md`
- `core/MEMORY.md`

Reason:
The name is both prompt identity and durable operator identity.

Prompt:
`Core Tech Stack`

Destination:
`core/OPERATOR.md`

Reason:
This is stable operator metadata.

Prompt:
`Working Style`

Destination:
`core/OPERATOR.md`

Reason:
This is factual operator preference metadata.

Prompt:
`Metrics (Age/Height/Weight)`

Destination:
`core/OPERATOR.md`

Reason:
This is structured operator profile data.

Prompt:
`Life Rules/Principles`

Destination:
`core/OPERATOR.md`

Reason:
These are durable operator values.

Prompt:
`Primary Mission/Life Goal`

Destination:
`core/OPERATOR.md`

Reason:
This is stable high-level operator intent.

Prompt:
`Business Info`

Destination:
`core/OPERATOR.md`

Reason:
This is structured business context for the operator.

Prompt:
`Grok profile paste`

Destination:
`core/OPERATOR_PROFILE.md`

Reason:
This is richer narrative persona material, not structured user metadata.

### Environment prompts

Prompt:
`Obsidian Vault Path`

Destination:
`core/CONFIG.json`

Reason:
This is runtime configuration.

Prompt:
`Allowed Root`

Destination:
`core/CONFIG.json`

Reason:
This is runtime workspace policy.

## Recommended Ingestion Semantics

- Root `GEMINI.md` or `AGENTS.md`: foundational operating prompt.
- `core/*.md`: foundational identity and durable project context.
- `synapse/`: external expert knowledge, reference packs, imported doctrine, and ingest-only material.
- `memory/`: refinement outputs, proposals, archival rollups, and evolving memory products.
- `continuity/`: checkpoints, summaries, and state-transfer artifacts.

## Practical Distinction: `OPERATOR.md` vs `OPERATOR_PROFILE.md`

Use `OPERATOR.md` when the data should be:
- factual
- structured
- stable
- easy to diff
- easy to rewrite destructively

Use `OPERATOR_PROFILE.md` when the data is:
- interpretive
- narrative
- voice-oriented
- inferred from public behavior or social corpus
- helpful for stylistic alignment but not authoritative as fact

Short version:
- `OPERATOR.md` = canonical facts about the operator
- `OPERATOR_PROFILE.md` = richer persona interpretation of the operator
- `CONFIG.json` = runtime mechanics only
