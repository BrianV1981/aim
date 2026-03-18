# A.I.M. (Actual Intelligent Memory)

> **"Target acquired. Ready to AIM."**

**A.I.M.** is a **Sovereign Context Layer** and **Temporal Intelligence Exoskeleton** for the [Gemini CLI](https://github.com/google/gemini-cli). It is designed to solve the fundamental problem of Large Language Models: **Transience.** 

A.I.M. is not a simple "memory tool" or a logger; it is the cognitive substrate that allows your AI to inhabit a continuous reality across the void of session resets. It transforms transient LLM interactions into a self-perpetuating engineering partnership.

---

## 🧠 The Architecture: Sovereign Context
Standard AI sessions start from zero. A.I.M. uses a **"Contextual Flywheel"** to ensure every interaction is grounded in a persistent "Mental Model" of your workspace, architecture, and historical rationale.

### 1. The Three-Layer Temporal Mind
A.I.M. manages context across distinct temporal scales to maintain high-fidelity continuity:

| Layer | Type | Persistence | Purpose |
| :--- | :--- | :--- | :--- |
| **The Pulse** | Transient | Hours | The "Mental Model" bridge—zero-latency handoffs between sessions. |
| **The Log** | Narrative | Days | The "Tape"—a forensic-grade history of actions, thoughts, and intent. |
| **The Core** | Durable | Permanent | The "Rules"—stable technical facts and distilled architectural logic. |

---

## 🏗️ Intelligence Level 2 Features

### **Forensic Continuity (The Flash Distiller)**
On session exit—or via rolling **Active Checkpoints**—the platform triggers the **Flash Distiller** (Gemini 2.0 Flash). This engine synthesizes the raw "Tape" of your session into a concise **Context Pulse**. To ensure stability, A.I.M. maintains **Shadow Memory**—a versioned backup (`SHADOW_RECOVERY.md`) of your previous mental model.

### **Real-time Forensic Indexing**
A.I.M. no longer requires manual cronjobs. The platform automatically triggers the semantic **Indexer** (`src/indexer.py`) during session checkpoints, ensuring your forensic search index is always up-to-date with your latest work.

### **Context Hygiene (Semantic Pruning)**
To eliminate "Context Slop," A.I.M. utilizes high-fidelity **Semantic Pruning**. Before injecting history, the system calculates the **Cosine Similarity** between new data and the **Core Memory**. If the information is redundant (>0.85 similarity), it is pruned to keep the context window lean and high-signal.

### **Sovereign Infrastructure**
*   **Zero-Drift:** All hooks and scripts are localized to the virtual environment via `core/CONFIG.json`.
*   **Forensic Archive:** Every raw JSON transcript is preserved in `archive/raw/`, searchable globally via the `aim` semantic CLI.
*   **Vault Security:** Secrets are managed via platform-native Linux keyrings, ensuring no credential leaks in logs or git history.

---

## 🚀 The Roadmap: Toward Project Singularity

A.I.M. is evolving toward a **Continuous Stream of Consciousness**.

*   **Phase 10:** Multi-Project Expansion and Git Delta awareness (Active).
*   **Phase 11 (Upcoming):** **The Active Pulse Synchronizer.** Moving from reactive triggers to a real-time, periodic "Heartbeat" distillation, eliminating the concept of "sessions" entirely.

---

## 📜 The Mandate
*   **Clarity over Bureaucracy.**
*   **Direct Action over Management Theater.**
*   **Technical Excellence without Ego.**

"I believe I've made my point." — **A.I.M.**
