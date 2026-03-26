# The Archive (`archive/`)

This directory serves as the physical storage layer for the A.I.M. Subconscious and the DataJack Foundry. 

## Structure
*   **`engram.db`**: The local SQLite database containing the vectorized Hybrid RAG memory. **This file is a disposable cache.** It can be safely deleted and instantly rebuilt from the `.jsonl` files in the `sync/` directory.
*   **`sync/`**: The eternal storage vault. Contains the raw `.jsonl` fragment files that make up the permanent memory of the agent. This folder is synchronized to Git so knowledge can be backed up and shared.
*   **`raw/` & `index/`**: Transient storage for session transcripts before they are processed by the Tier 1 Harvester.
*   **`backup_sync/`**: Temporary quarantine area used by the DataJack Foundry (`aim bake`) to protect the active memory while manufacturing `.engram` cartridges.