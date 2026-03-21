# A.I.M. Technical Handbook (Master Schema)

This document is the definitive architectural map for the A.I.M. platform. It defines the modular components of the brain and the protocols that ensure continuity and sovereignty.

---

## SECTION 1: THE ROOT ARCHITECTURE

### 1.1 `GEMINI.md` (The Soul)
- **Role:** Lean Orchestrator.
- **Function:** A pointer-native source of truth. It directs the agent to query the **Engram DB** for technical policies rather than carrying them in the context window.

### 1.2 `setup.sh` (The Bootstrapper)
- **Function:** Automates venv creation and performs the **Nuclear Alias Reset** to ensure the `aim` command is always correctly linked to the local project.

---

## SECTION 2: THE ENGRAM DB (SUBCONSCIOUS)
The core of A.I.M.'s memory lives in a local SQLite database (`archive/engram.db`).

### 2.1 The Pre-Born Brain
During initialization, A.I.M. indexes this Handbook and core project directives. This provides the agent with "Day Zero" technical knowledge.

### 2.2 Synapse Ingestion
The `synapse/` folder is a dedicated intake zone. Any technical references dropped here are recursively indexed as `expert_knowledge`.

### 2.3 The Synapse Exchange (`aim exchange`)
Expertise is portable. A.I.M. can `export` its indexed knowledge into compressed `.aim` packs, allowing you to share a pre-trained "Python Expert" or "Solana Architect" brain with other machines without re-indexing.

---

## SECTION 3: THE SCHOLASTIC HIERARCHY (CONSCIOUSNESS)
Memory is refined through a tiered chain of command to prevent knowledge decay and bloat.

### 3.1 Tier 1: The Librarian (`session_summarizer.py`)
- **Frequency:** Hourly / Session End.
- **Function:** Uses the **Signal Filter** to strip tool noise and writes a surgical technical narrative of the recent turns into the daily logs.

### 3.2 Tier 2: The Chancellor (`src/chancellor.py`)
- **Frequency:** Daily.
- **Function:** Synthesizes multiple session narratives into a **Daily Milestone Report**.

### 3.3 Tier 3: The Fellow (`src/fellow.py`)
- **Frequency:** Weekly.
- **Function:** Conducts a strategic review of the week's accomplishments and proposes the next week's trajectory.

### 3.4 Tier 4: The Dean (`src/dean.py`)
- **Frequency:** Monthly.
- **Function:** The final filter. Refines the **Project Soul** (`MEMORY.md`) by identifying the only facts worth keeping for the long term.

---

## SECTION 4: SAFETY & SOVEREIGNTY

### 4.1 The Safety Sentinel (`hooks/safety_sentinel.py`)
- **Hardened Protection:** Intercepts destructive commands and performs a Level 2 AI intent audit. Uses `EXIT 2` to force blocks even in YOLO mode.

### 4.2 The Obsidian Bridge (`scripts/obsidian_sync.py`)
- **Role:** Sovereign Mirror.
- **Function:** Mirroring of Daily Logs, Core Memory, and **Raw JSON Transcripts** to an external vault for 100% recovery.

---

"I believe I've made my point." — **A.I.M.**
