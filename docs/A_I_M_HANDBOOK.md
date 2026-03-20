# A.I.M. Technical Handbook (Master Schema)

...

---

## SECTION 5: THE ENGINE ROOM (`src/`)
These utilities are the low-level "Gray Matter" of the A.I.M. platform.

### 5.1 `src/config_utils.py`
- **Role:** The Navigator.
- **Nature:** System 1 (Innate Logic).
- **Function:** Dynamically resolves the A.I.M. root directory. It is the absolute authority on file paths.
- **Auto-Repair:** It monitors `core/CONFIG.json`. If it detects the project has been moved to a new machine or username, it instantly rewrites the JSON paths to match reality.

### 5.2 `src/reasoning_utils.py`
- **Role:** The Logic Bridge.
- **Nature:** System 2 (Reasoning Logic).
- **Function:** The unified interface for all AI tasks. It handles the specific logic for different providers (Gemini Cloud, Gemini CLI, Ollama, Codex, OpenAI).
- **Hardening:** It implements model-specific payload handling, such as the `codex exec` wrapper for ChatGPT 5.4.

### 5.3 `src/forensic_utils.py`
- **Role:** The Archivist's Utility Belt.
- **Nature:** System 1 (Innate Logic).
- **Function:** Manages the SQLite connection for `forensic.db`. It implements the **Recursive Character Chunking** logic which ensures that massive tool outputs are subdivided into 2000-character fragments for safe embedding.
- **Math:** Contains the `cosine_similarity` function used for semantic search scoring.

### 5.4 `src/indexer.py`
- **Role:** The Memory Writer.
- **Nature:** System 1 (Innate Logic).
- **Function:** Scans `archive/raw/` for new transcripts. It parses the JSON into fragments (User prompts, Model thoughts, Tool actions), generates embeddings for each, and populates the SQLite database.

### 5.5 `src/retriever.py`
- **Role:** The Memory Reader.
- **Nature:** System 1 (Innate Logic).
- **Function:** The core of the RAG system. It takes a query, vectorizes it, and performs a sub-millisecond SQL query against `forensic.db` to find the most relevant project history.
- **Fidelity:** Supports `--context` filters to show raw text surrounding a memory fragment.

### 5.6 `src/distiller.py`
- **Role:** The Memory Librarian.
- **Nature:** System 2 (Reasoning Logic).
- **Function:** The brain of the memory pipeline. It analyzes messy narrative logs and compares them against the current Core Memory to identify "Atomic Truths."
- **Output:** Produces the **Memory Proposals** and **Context Pulses** that drive project momentum.

### 5.7 `src/maintenance.py`
- **Role:** The Janitor.
- **Nature:** System 1 (Innate Logic).
- **Function:** Performs automated cleanup of temporary session files and manages the archival lifecycle to prevent repository bloat.

---

## SECTION 6: SPECIALIST DELEGATION MODEL (SUB-AGENTS)
A.I.M. leverages the Gemini CLI's native sub-agent system to expand expertise without diluting the core project soul.

### 6.1 Context Purity & Isolation
Sub-agents are specialized experts defined in `.gemini/agents/`. They operate in a "Vault" design:
- **Stateless Nature:** Sub-agents are stateless per call. They do not retain conversational history between delegations.
- **Context Isolation:** Sub-agents cannot see the main orchestrator's history. They only see the specific prompt provided during dispatch.
- **Recursion Control:** Sub-agents are hard-locked from spawning their own sub-agents to prevent architectural "sprawl."

### 6.2 The A.I.M. Dispatch Protocol
To solve the "Statelessness" challenge, every sub-agent delegation MUST use a **Dispatch Packet**. This packet acts as a technical onboarding memo and contains:
1.  **Objective:** A narrow, high-fidelity description of the task.
2.  **Edge Memory (Short-Term):** A 1-paragraph summary of the current project state to provide immediate technical context.
3.  **RAG Triggers (Long-Term):** Specific search terms the sub-agent must use with `aim search` to "awaken" its specialist memory from the forensic database.

### 6.3 Technical Memory vs. Conversational Memory
Because sub-agents have access to the A.I.M. Forensic Engine, they do not need to "remember" previous conversations. They instead "retrieve" the technical ground truth from `forensic.db`, ensuring that their conclusions are always based on the actual project state rather than conversational drift.

---

"I believe I've made my point." — **A.I.M.**
