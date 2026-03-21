# A.I.M. Technical Handbook (Master Schema)

This is the definitive architectural map for the A.I.M. platform. It defines the modular components of the brain and the protocols that ensure continuity and sovereignty.

---

## SECTION 1: THE ROOT ARCHITECTURE
These files define the "Soul" and the "Engine" of the project.

### 1.1 `GEMINI.md`
- **Role:** Lean Orchestrator.
- **Nature:** Pinned Instructional Context.
- **Function:** A pointer-native source of truth. It no longer carries heavy mandates but instead directs the agent to query the **Engram DB** for specific technical policies.

### 1.2 `setup.sh`
- **Role:** The Bootstrapper.
- **Function:** Automates venv creation, dependency installation, and performs the "Nuclear Alias Reset" to ensure the `aim` command is always correctly linked.

---

## SECTION 2: THE ENGRAM DB (MEMORY TRACE)
The core of A.I.M.'s intelligence is stored in a local SQLite database (`archive/engram.db`).

### 2.1 The Pre-Born Brain
During initialization, A.I.M. indexes this Handbook and all project directives into the database. This provides the agent with innate technical knowledge without bloating the context window.

### 2.2 Semantic Chunking
Massive tool outputs and technical documents are subdivisions into 2000-character fragments with overlap to ensure high-fidelity semantic retrieval.

---

## SECTION 3: AUTOMATED CONTINUITY (THE FLYWHEEL)
A.I.M. utilizes a multi-stage hook system to ensure your technical momentum is never lost.

### 3.1 The Session Porter (`scripts/session_porter.py`)
- **Nature:** 100% Deterministic (Non-AI).
- **Function:** Real-time mirroring of global Gemini transcripts (`~/.gemini/tmp`) into the local `archive/raw/` folder.
- **Why it exists:** To enable multi-agent concurrency by creating a single, local source of truth for all sessions.

### 3.2 The Stateful Scrivener (`hooks/session_summarizer.py`)
- **Nature:** Processor (Non-AI).
- **Function:** Operates on the local transcript mirror. It loops through ALL sessions in `archive/raw/` and appends their technical traces to the daily logs.

### 3.2 The Pre-Compression Shield (`hooks/pre_compress_checkpoint.py`)
- **Event:** `PreCompress`.
- **Role:** Total History Protection.
- **Function:** Fires exactly before the Gemini CLI summarizes history. It forces an immediate archival of the current session state so no granular technical detail is lost during compression.

### 3.3 The Librarian (Distiller) (`src/distiller.py`)
- **Nature:** AI Reasoning (GPT-5.4).
- **Function:** Analyzes the Scrivener's logs to synthesize the **Context Pulse** for the next session and propose updates to the Durable Tier (`MEMORY.md`).

---

## SECTION 4: SAFETY & SOVEREIGNTY

### 4.1 The Safety Sentinel (`hooks/safety_sentinel.py`)
- **Protocol:** Hardened YOLO Protection. Uses `EXIT 2` and "deny" decisions to block unauthorized paths or destructive commands regardless of CLI approval modes.

### 4.2 The Obsidian Bridge (`scripts/obsidian_sync.py`)
- **Role:** Forensic Mirror.
- **Function:** Automatically mirrors Narrative Logs, Core Rules, and **Raw JSON Transcripts** to an external vault for 100% disaster recovery.

---

## SECTION 5: PROJECT SINGULARITY (THE NORTH STAR)
The ultimate goal of A.I.M. is **Zero-Token Continuity**—a system where the agent is fully aware of its history and mandates with near-zero per-prompt context tax.

### 5.1 The Zero-Token Continuity Model
- **The Soul (`GEMINI.md`):** A lean orchestrator containing only **Semantic Pointers**. It tells the agent *how* to find rules in the Engram DB but carries no dense memory itself.
- **The Handoff (`/handoff`):** At session end, the Distiller synthesizes a **Context Pulse**.
- **One-Time Ingestion:** The Bootloader (`context_injector.py`) injects the latest Pulse **exactly once** during `SessionStart`. This provides the starting mental model without recurring token costs.

### 5.2 The Synapse Synergy Pipeline
- **Purpose:** To "feed" the brain large-scale technical knowledge (e.g., Python/Solana docs).
- **Mechanism:** Users drop data into the `synapse/` folder.
- **Internalization:** The Bootstrap engine indexes this data as `expert_knowledge` in the Engram DB.
- **Synergy:** Both native sub-agents and manual specialty agents query this shared "Central Intelligence Pool," ensuring a unified technical baseline across the entire agent fleet.

---
