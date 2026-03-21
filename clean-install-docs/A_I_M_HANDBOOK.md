# A.I.M. Technical Handbook (Master Schema)

...

---

## SECTION 7: SAFETY & SOVEREIGNTY
A.I.M. utilizes a multi-layered defense system to protect the Operator's system and secrets.

### 7.1 The Safety Sentinel (`hooks/safety_sentinel.py`)
- **Protocol:** Intercepts `rm`, `replace`, and `write_file` commands.
- **YOLO Protection:** Uses `EXIT 2` and the `deny` decision to block dangerous actions even in high-autonomy mode.
- **Logic:** Performs a Level 1 path check followed by a Level 2 AI intent audit against the current Context Pulse.

### 7.2 The Secret Shield (`hooks/secret_shield.py`)
- **Function:** Real-time regex scanning of tool inputs for high-entropy strings, API keys, and private keys.
- **Action:** Instantly aborts any tool call that would result in a credential leak to the narrative logs.

### 7.3 The Obsidian Bridge (`scripts/obsidian_sync.py`)
- **Role:** Sovereign Backup Layer.
- **Function:** Mirrors all Narrative (Logs), Durable (Core), and Forensic (Raw JSON) artifacts to an external vault.
- **Benefit:** Ensures 100% data recovery even if the local repository is deleted.

### 7.4 Universal Portability Mandate
- **Rule:** Absolute hardcoded paths are forbidden.
- **Mechanism:** Root discovery is resolved at runtime via `config_utils.py`.
- **Auto-Healing:** The system detects machine shifts and re-maps all internal pointers automatically.

---

"I believe I've made my point." — **A.I.M.**
