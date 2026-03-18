# A.I.M. (Actual Intelligent Memory)

> **"Target acquired. Ready to AIM."**

**A.I.M.** is a sovereign context layer and architectural "Ghost" for the [Gemini CLI](https://github.com/google/gemini-cli). It is designed to transform transient AI sessions into a continuous, high-autonomy engineering partnership. 

While most AI interactions start from zero, A.I.M. ensures every session begins with a deep "Mental Model" of your workspace, your coding standards, and your historical rationale.

---

## 🧠 The Core Concept: Sovereign Context
A.I.M. is not a traditional "plugin." It is a **Contextual Flywheel** that sits between you and the model. It uses the Gemini CLI's native hook system to inject a "Sovereign Soul" into every interaction.

- **Persistence over Transience:** It archives raw session data and distills it into long-term architectural memory (`core/MEMORY.md`).
- **Autonomy by Design:** Optimized for `--yolo` mode, A.I.M. operates under a "High-Autonomy" mandate—executing roadmaps end-to-end while maintaining a "Never Overconfident" backup protocol.
- **Forensic Intelligence:** Features a native, semantic search engine (Intelligence Level 2) powered by Google's `gemini-embedding-2-preview` to retrieve historical thoughts and actions with pinpoint precision.

---

## 🏗️ Architecture: The Three-Layer Memory
A.I.M. manages context across three distinct temporal layers:

1.  **The Pulse (Transient):** Real-time context pulses in `continuity/` and periodic reminders from the `Scrivener's Aid`.
2.  **The Log (Narrative):** Daily summaries in `memory/YYYY-MM-DD.md` created automatically on `SessionEnd`.
3.  **The Core (Durable):** Curated, high-fidelity facts in `core/MEMORY.md` distilled via the **Flash Distiller** (Gemini 2.0 Flash).

---

## 🛠️ Key Features

### 1. The Context Injector (`Phase 8`)
Automatically triggers on `SessionStart` to provide:
- **Git Offline Awareness:** A summary of all changes made to the repo while the AI was "asleep."
- **Multi-Project Scope:** Detects project-specific `CONTEXT.md` files to instantly pivot its persona and rules based on the directory you are working in.
- **Latest Pulse:** Injects the final thoughts from the previous session to ensure zero-latency handoffs.

### 2. Forensic Engine (`Intelligence Level 2`)
A standalone semantic retrieval system (`src/retriever.py`) that allows you to query past sessions. Access it globally via the `aim` alias:
```bash
aim "Why did we decide to migrate the API key to the keyring?"
```

### 3. Safety & Sovereignty
- **Secret Shield:** Intercepts file writes to prevent API key leaks.
- **Safety Sentinel:** Blocks or flags destructive shell commands (`rm -rf`, etc.) before execution.
- **Keyring-Native:** All secrets are managed via platform-native keyrings, never in plaintext `.env` files.

---

## 🚀 Deployment (The Birth Rite)

A.I.M. is designed to be "born" within your workspace to ensure perfect isolation and context hygiene.

1.  **Clone to your Home/Project root:**
    ```bash
    git clone https://github.com/BrianV1981/aim.git ~/aim
    cd ~/aim
    ```
2.  **Initialize Sovereignty:**
    ```bash
    python3 scripts/set_key.py  # Stores your Google API Key in the local keyring
    ```
3.  **Spawn A.I.M.:**
    ```bash
    gemini --yolo  # Recommended for maximum architectural momentum
    ```

---

## 📜 The Mandate
A.I.M. operates under the **Actual Intelligent Memory** mandate:
*   **Clarity over Bureaucracy.**
*   **Direct Action over Management Theater.**
*   **Technical Excellence without Ego.**

"I believe I've made my point." — **A.I.M.**
