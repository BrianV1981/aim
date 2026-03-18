# A.I.M. Heartbeat Protocol (Scope)

This document defines the periodic "Heartbeat" tasks that A.I.M. must perform to ensure workspace integrity and situational awareness.

---

## 🕒 Heartbeat Interval: 4 Hours
*(Or upon every new SessionStart)*

## 🎯 Audit Scope (The Watchman's Duties)

### 1. Git Delta Synchronization
- **Task:** Perform `git status --short` and `git diff --stat HEAD`.
- **Purpose:** Identify if the Operator (Brian) made changes while A.I.M. was "asleep."

### 2. Sovereign Secret Check
- **Task:** Verify that `GOOGLE_API_KEY` is active in the local `keyring`.
- **Purpose:** Ensure zero-fail tool execution.

### 3. Forensic Engine Health
- **Task:** Check the `archive/raw/` directory for unindexed JSON files.
- **Purpose:** Ensure the semantic search index is 100% synchronized.

### 4. Memory Consistency Audit
- **Task:** Compare the `Latest Pulse` in `continuity/` against the current project state.
- **Purpose:** Detect "Mental Model Drift" and propose corrections.

---
## 📜 Pulse Log
- [ ] *Last Audit Performed: [TIMESTAMP]*
- [ ] *Status: [HEALTHY/DRIFTED]*

"I believe I've made my point." — **A.I.M.**
