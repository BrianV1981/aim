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

## SECTION 5: SYSTEM MAINTENANCE & UPDATES

### 5.1 The Sovereign Update (`aim update`)
- **Role:** High-Fidelity Sync.
- **Function:** Automates the lifecycle of keeping A.I.M. current.
- **Protocol:**
  1. **Source Sync:** Performs a `git pull origin main` to fetch the latest TUI, scripts, and engine logic.
  2. **Hook Refresh:** Re-registers all system hooks to ensure the local Gemini CLI is utilizing the latest architectural guardrails.
  3. **Data Preservation (Safe Update):** The update logic explicitly protects your **Personality Trinity** (`GEMINI.md`, `USER.md`, `MEMORY.md`). These files are never overwritten, ensuring the bot's soul remains intact across versions.

---

## SECTION 6: THE HYBRID SOUL PROTOCOL

A.I.M. maintains technical continuity through a dual-mode ingestion engine within `src/bootstrap_brain.py`. This ensures that active instructions stay current while expert knowledge remains permanent.

### 6.1 Foundation Sync (Active Instructions)
- **Scope:** `GEMINI.md`, `core/MEMORY.md`, and all files in `docs/`.
- **Logic:** These files are **Synchronized**. 
- **Behavior:** If a foundation file is modified on disk, its previous engram in the DB is overwritten by the new version. This ensures A.I.M. always follows the absolute current project mandates.

### 6.2 Synapse Ingestion (Permanent Knowledge)
- **Scope:** Everything dropped into the `synapse/` folder.
- **Logic:** This is an **Onramp**.
- **Behavior:** Once a file is indexed from Synapse, it is **Permanently Persistent** in the Engram DB. The source files on disk can be safely deleted to keep the workspace lean; A.I.M. will still retain and retrieve the knowledge from the database.

### 6.3 Amnesia Protection
- **0-Byte Shield:** The bootstrap engine automatically skips empty or 0-byte files. This prevents accidental "Technical Amnesia" where an empty file on disk could overwrite and hollow out a valid engram in the database.

---

"I believe I've made my point." — **A.I.M.**
