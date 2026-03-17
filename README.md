# A.I.M. - Actual Intelligent Memory

> **"Target acquired. Ready to AIM."**

**A.I.M. (Actual Intelligent Memory)** is a sophisticated, proactive digital right-hand and workspace orchestration platform. It is the successor to previous-generation contextual assistants, designed for forensic-grade memory, total environment awareness, and autonomous execution.

---

## 🏗️ Architecture & Core Components

A.I.M. is built on a "semantic-first" architecture, rejecting legacy bridges in favor of native, high-fidelity context management.

### [Core Identity](./core/)
The "Soul" of A.I.M. resides in the `core/` directory:
- **[IDENTITY.md](./core/IDENTITY.md):** The primary persona and behavioral mandate.
- **[USER.md](./core/USER.md):** Brian's profile, tech stack, and working style.
- **[AGENTS.md](./core/AGENTS.md):** Rules for sub-agent orchestration and concurrency.
- **[MEMORY.md](./core/MEMORY.md):** Curated, long-term memory and durable facts.

### [Hooks & Automation](./hooks/)
Active integration layers for real-time workspace response:
- **[HOOKS_INDEX.md](./hooks/HOOKS_INDEX.md):** Registry of active and proposed hooks.
- **[session_summarizer.py](./hooks/session_summarizer.py):** Automated forensic session logging on exit.

### [Documentation Hub](./docs/)
The operational state and roadmap of the platform:
- **[CURRENT_STATE.md](./docs/CURRENT_STATE.md):** The latest accomplishments and system health.
- **[ROADMAP.md](./docs/ROADMAP.md):** The Phase-by-Phase plan for A.I.M. evolution.
- **[DECISIONS.md](./docs/DECISIONS.md):** Architectural ADRs and historical rationale.
- **[NEXT_ACTIONS.md](./docs/NEXT_ACTIONS.md):** Immediate technical tasks and the "Edge."

---

## 📂 Repository Structure

```text
aim/
├── core/               # Identity, Persona, and Long-term Memory
├── hooks/              # Workspace automation and event triggers
├── docs/               # Operational state, roadmap, and decisions
├── src/                # [Planned] Native Archivist Engine and Indexer logic
├── tests/              # Verification suites for all A.I.M. components
├── memory/             # Daily logs and transient session context (ignored by Git)
├── continuity/         # High-fidelity handoff logs and context pulses
└── projects/           # Sandboxed project context and workspace links
```

---

## 🚀 Getting Started (The A.I.M. Way)

1. **Bootstrap:** Read `GEMINI.md` in the root and load the `core/` files.
2. **Context Pulse:** Check `docs/CURRENT_STATE.md` and the most recent file in `continuity/`.
3. **Execute:** Follow the `docs/NEXT_ACTIONS.md` to pick up where the previous session left off.

---

## 📜 Mandates & Safety
- **No Session Slop:** All decisions must be committed to `MEMORY.md` or `DECISIONS.md`.
- **Validation First:** No code change is complete without a corresponding test or verification step.
- **Security:** Session retention is disabled; forensic logging is automated via hooks.

---
"I believe I've made my point." — **A.I.M.**
