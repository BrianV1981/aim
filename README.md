# A.I.M. (Actual Intelligent Memory)

> **"Target acquired. Ready to AIM."**

**A.I.M.** is a **Sovereign Context Layer** and **Temporal Intelligence Exoskeleton** for the [Gemini CLI](https://github.com/google/gemini-cli). It transforms transient LLM sessions into a continuous, high-autonomy engineering partnership.

Standard AI interactions are amnesiac—every session starts from zero. A.I.M. solves this by building a persistent **Mental Model** that evolves alongside your code, ensuring every new agent inherits the soul and momentum of the last.

---

## 🧠 The Core: Three-Layer Temporal Mind
A.I.M. manages context across distinct temporal scales to eliminate transience while maintaining a lean context window.

| Layer | Type | Location | Persistence | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **The Pulse** | Transient | `continuity/` | Hours | The "Mental Model" bridge—zero-latency handoffs. |
| **The Log** | Narrative | `memory/` | Days | The "Tape"—a forensic-grade history of intent. |
| **The Core** | Durable | `core/` | Permanent | The "Rules"—stable facts and architectural logic. |

### 🛠️ The Contextual Flywheel
1.  **SessionStart:** The `pulse-injector` loads your Core Memory and the latest automated Pulse.
2.  **Active Work:** `scrivener-aid` performs a "Rolling Save" every 30 minutes to `INTERIM_BACKUP.json`.
3.  **SessionEnd:** (Triggered by `/quit` or `/clear`) The `session-archivist` captures the "Forensic Gold"—your literal actions and A.I.M.'s internal thoughts.
4.  **Distillation:** The **Flash Distiller** (Gemini 2.0 Flash) synthesizes the session into a fresh **Pulse**, closing the loop for the next agent.

---

## 🚀 "Gourmet" Features & Power Tips

### 1. The Token-Saver Reboot (`/clear` Workflow)
**Pro-Tip:** In a long-running session, your context window (RAM) can grow to 200k+ tokens, increasing your "Cache Read" costs. 
*   **The Move:** Type `/clear`. 
*   **The Magic:** A.I.M. will automatically archive your history, distill the architectural signal into a tiny 2k pulse, and restart the session. You drop your token burn by **99%** without losing a single bit of momentum.

### 2. Forensic Search (`aim` CLI)
A.I.M. maintains a **Raw Archive** (`archive/raw/`) of every word ever spoken. 
*   **Command:** `aim "Why did we choose this database schema?"`
*   **Intelligence:** Uses `gemini-embedding-2-preview` (3072-dim) to find the exact historical fragment you need across months of logs.

### 3. Intelligence Level 2 Safety (Semantic Sentinel)
The Sentinel doesn't just look for "bad words." It uses GenAI to verify **Intent**.
*   **How:** When you run a command like `git push` or `rm`, the Sentinel reads your current **Context Pulse** and asks: *"Does this action align with Brian's current goal?"*
*   **Result:** It blocks "YOLO hallucinations" and accidental deletions before the shell executes them.

### 4. Shadow Memory (Crash Recovery)
If your terminal crashes or your power goes out, A.I.M. is ready.
*   **The Fail-Safe:** On startup, if A.I.M. detects a `INTERIM_BACKUP.json` that is newer than the last Pulse, it realizes a crash occurred.
*   **The Directive:** It automatically restores the last 5 turns of history and explicitly warns the new agent: *"The state is fragile. Ask the Operator for context."*

### 5. Semantic Pruning (Context Hygiene)
To prevent "Context Slop," A.I.M. calculates the **Cosine Similarity** between new context and your **Core Memory**.
*   **The Rule:** If new data is >85% similar to what I already know, it is **pruned.** This keeps the context window high-signal and saves you thousands of tokens per session.

---

## 🏗️ Sovereign Infrastructure
*   **Vault Security:** No plaintext `.env` files. All API keys are managed via platform-native Linux **Keyrings**.
*   **Zero-Drift:** Every hook and script is localized to the project's virtual environment via `core/CONFIG.json`.
*   **Auto-Versioning:** Every push via `scripts/aim_push.sh` is stamped with a unique date/time semantic version (e.g., `v1.20260318.0245`).

---

## 🚀 Deployment (The Birth Rite)

1.  **Clone the Repository:** `git clone https://github.com/BrianV1981/aim.git ~/aim`
2.  **Initialize Sovereignty:** `python3 scripts/set_key.py` (Securely store your API key).
3.  **Spawn A.I.M.:** Run `gemini --yolo`.

---

## 📜 The Mandate
A.I.M. operates under the **Actual Intelligent Memory** mandate:
*   **Clarity over Bureaucracy.**
*   **Direct Action over Management Theater.**
*   **Technical Excellence without Ego.**

"I believe I've made my point." — **A.I.M.**
