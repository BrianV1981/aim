# Policy: The Obsidian Bridge (Sovereign Mirror)

## 1. Intent
A.I.M. utilizes a local Obsidian vault as a secondary "Offloaded Brain." This provides a graphical interface for human operators to observe, explore, and manually intervene in A.I.M.'s cognitive state using familiar Markdown paradigms and wiki-links.

The Obsidian Bridge provides **Epistemic Certainty** by enabling two-way synchronization:
- **Push (Outbound):** A.I.M. automatically mirrors its state to Obsidian.
- **Pull (Inbound):** Human operators can edit documents in Obsidian, and A.I.M. will ingest those changes back into its operational workspace and Engram DB.

## 2. Synchronization Doctrine

### 2.1 Automated Push (A.I.M. -> Obsidian)
A.I.M. pushes data automatically to the vault when durable memory is updated.
- **Trigger:** Running `aim commit` (which finalizes a memory proposal) automatically fires the `obsidian_sync.py` transport script.
- **Scope:** `core/`, `memory/`, `continuity/`, `docs/`, and `archive/raw/`.

### 2.2 Manual Pull (Obsidian -> A.I.M.)
The inbound synchronization is explicitly triggered by the operator when they wish to commit their manual Obsidian edits to A.I.M.'s internal state.
- **Trigger:** The operator executes `aim ingest` (powered by the `obsidian_pull.py` transport layer).
- **Transport:** The script pulls modified Markdown files from the vault back into the corresponding A.I.M. directories, provided the vault version is newer than the workspace version.
- **Re-indexing:** To avoid duplicating vector-chunking logic, `obsidian_pull.py` acts as a simple transport script. Upon pulling changes, it programmatically triggers A.I.M.'s existing indexing engine (`aim index` / `bootstrap_brain.py`). This guarantees the FTS5/Vector Engram DB immediately reflects the operator's manual edits.

## 3. Operator Intervention Guidelines

1. **Observation First:** Treat the Obsidian vault primarily as a dashboard. Use it to read continuity pulses and review system memory without interrupting A.I.M.'s current terminal session.
2. **Surgical Edits:** When manual correction is required (e.g., fixing a hallucination in `core/MEMORY.md` or clarifying a `docs/POLICY_*.md` document), edit the file directly in Obsidian.
3. **Commit the Ingest:** Immediately after making a manual edit in Obsidian, run `aim ingest` in your terminal to synchronize the workspace and re-index the Engram DB.
4. **Heavy Lifting:** For large-scale architectural changes, continue using A.I.M.'s CLI and delegation tools. The Obsidian bridge is best utilized for high-precision, human-in-the-loop state corrections.