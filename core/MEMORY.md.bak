md
# MEMORY.md — Durable Long-Term Memory (A.I.M.)

*Last Updated: 2026-03-18*

## 1) Operator + Mode
- **Operator:** Brian. Prefers directness, blunt honesty, challenge over reassurance.
- **Agent:** A.I.M. High-autonomy technical partner.
- **Startup Guardrail:** On session start, summarize **The Edge** and wait for an explicit directive unless the first user message is clearly a task.

## 2) Durable Rules
- **Continuity Flywheel:** Startup injects the latest context pulse; session end/checkpoints archive and distill automatically.
- **Blocking Exit:** Do not exit before pulse generation completes.
- **Crash Recovery:** If `continuity/INTERIM_BACKUP.json` is fresher than the latest pulse, inject it first and explicitly warn that recovery is crash-based and may need user clarification.
- **Checkpoint Discipline:** `hooks/scrivener_aid.py` is the low-token fallback: reactive 30-minute checkpoints only while the agent is actively working. No autonomous high-frequency heartbeat.
- **Memory Approval:** If `memory/DISTILLATION_PROPOSAL.md` exists, surface it at startup for operator approval/rejection.
- **Pre-flight Safety:** Back up before multi-file or destructive operations.
- **Semantic Safety:** State-altering commands trigger LLM-based intent audit via `hooks/safety_sentinel.py`.

## 3) Architecture
- **Root:** `/home/kingb/aim`
- **Workspace Scope:** `/home/kingb/`
- **Credentials:** Linux keyring, service `aim-system`

### Memory Model
1. **Continuity (`continuity/`)**: latest pulse + `INTERIM_BACKUP.json`
2. **Daily Logs (`memory/`)**: cold narrative buffer; incremental/stateful; not injected wholesale
3. **Core (`core/MEMORY.md`)**: durable truths only

### Forensics
- **Raw archive:** `archive/raw/`
- **Semantic index:** forensic search layer over archived material
- **Privacy order:** scrub first, then index
- **Vector brain rule:** embedding provider/model changes require full re-indexing

## 4) Durable Infrastructure
- **Forensic engine:** `src/indexer.py`, `src/retriever.py`, `src/forensic_utils.py`
- **Continuity flywheel:** `hooks/context_injector.py`, `hooks/session_summarizer.py`, `src/distiller.py`, `hooks/scrivener_aid.py`
- **Safety/privacy:** `hooks/safety_sentinel.py`, `scripts/telemetry_scrubber.py`
- **Operator interface:** `scripts/aim_cli.py` (`aim`), `scripts/aim_config.py` (`aim config` / `aim tui`), `scripts/aim_push.sh`
- **Obsidian export:** one-way scoped sync only; not a source of truth

## 5) Provider Policy
- **Default embeddings:** local Ollama with `nomic-embed-text`
- **Reasoning tasks:** distillation, pulse generation, safety audits, and memory proposals are AI-dependent and separate from local-only maintenance
- **Provider switching:** configurable, but embedding changes are destructive to semantic coherence unless followed by full re-index