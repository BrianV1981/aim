# DataJack Protocol Pipeline Overhaul: RAG 3.5 Schema Compatibility Gameplan

## 🚀 The Commander's Intent
The A.I.M. OS architecture is transitioning from standard dense vector embeddings to **RAG 3.5 Cognitive Routing** (Parent-Child summarization). This necessitates a profound change to `ForensicDB`'s underlying SQLite `fragments` table: the introduction of a `parent_id` column.

While the SQLite database handles this perfectly via `COALESCE` statements, the **DataJack Protocol** (the `.engram` cartridge export/import system) does not. The DataJack pipeline currently compiles databases into portable zip files filled with `.jsonl` objects that lack relational metadata. If a RAG 3.5 cartridge is jacked-in, the entire relational hierarchy between massive raw text blocks and dense semantic summaries will be lost.

This Gameplan details the exact technical overhaul required to ensure the `.engram` format remains a universal, mathematically perfect standard for the A.I.M. Swarm.

---

## 🎯 Phase 1: The Packer Upgrades (`aim bake` & `pack_cartridge.py`)
The tools responsible for converting a SQLite database into an `.engram` cartridge must explicitly serialize the `parent_id` column.

### 1.1 Modifying the SQL Query
*   **Target File:** `pack_locomo_cartridge.py` and `aim_core/plugins/datajack/forge.py`
*   **Action:** Update the `SELECT` statements to pull the `parent_id` column:
    ```sql
    SELECT id, content, embedding, metadata, parent_id FROM fragments WHERE session_id = ?
    ```

### 1.2 Modifying the JSONL Serialization
*   **Target File:** The `.jsonl` string construction loop.
*   **Action:** Ensure the exported JSON object explicitly includes the `parent_id` key.
    ```python
    rec = {
        "_record_type": "fragment",
        "id": frag_id,
        "text": content,
        "embedding": vec,
        "metadata": meta_dict,
        "parent_id": parent_id  # <--- The Critical Addition
    }
    ```

---

## 🎯 Phase 2: The Unpacker Upgrades (`aim jack-in`)
The tools responsible for unzipping an `.engram` cartridge and inserting the `.jsonl` records back into a local `ForensicDB` must safely deserialize and map the `parent_id` field.

### 2.1 The Relational Integrity Problem (Primary Key Shifting)
When an `.engram` cartridge is imported into an existing `ForensicDB`, the incoming fragments cannot retain their original `id` primary keys, or they will collide with the local database's fragments. They are automatically assigned new auto-incrementing `id`s. 

Because `parent_id` relies on those primary keys, a massive relational collision will occur if we just insert the raw `parent_id` from the JSON.

### 2.2 The In-Memory Identity Map (The Solution)
*   **Target File:** `aim_core/aim_cli.py` (specifically the `cmd_exchange` / `jack-in` logic).
*   **Action:** The unpacker must process the `.jsonl` fragments in two distinct passes (or maintain a live dictionary map) to remap the foreign keys.
*   **The Logic:**
    1.  Initialize a Python dictionary: `id_map = {}`
    2.  Insert all **Parent** fragments (where `parent_id` is null).
    3.  Capture the newly generated local SQLite `id` using `cursor.lastrowid`.
    4.  Map the old cartridge ID to the new local ID: `id_map[old_frag_id] = cursor.lastrowid`.
    5.  Insert all **Child** fragments. When a child has a `parent_id`, do NOT use the raw value. Look it up in the identity map: `new_parent_id = id_map.get(old_parent_id)`.
    6.  Insert the child fragment into the database using `new_parent_id`.

---

## 🎯 Phase 3: Absolute Backwards Compatibility
The A.I.M. OS must not break when a legacy user attempts to `jack-in` a V1 cartridge.

### 3.1 The `COALESCE` Fallback
*   **Target File:** `aim_core/plugins/datajack/forensic_utils.py`
*   **Action:** The RAG 3.5 SQL search queries are already bulletproofed using `COALESCE(p.content, f.content)`. 
*   **The Guarantee:** If an older `.engram` cartridge is imported without `parent_id` data, the Unpacker will simply insert `NULL` for the `parent_id` column. The SQLite database will gracefully fall back to returning the original fragment content, ensuring 100% backwards compatibility for legacy databases.

---

## 🏁 Final Objective
Once these three phases are implemented across the core OS scripts, the `aim-locomo` project can be fully standardized, and we can mathematically guarantee that the RAG 3.5 Parent-Child logic can be safely ported, shared, and backed up across any machine in the world without losing its cognitive routing hierarchy.