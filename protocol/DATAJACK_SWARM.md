# The DataJack Protocol & Sovereign Swarm

This document outlines the mechanics of A.I.M.'s peer-to-peer knowledge sharing network. The DataJack protocol allows operators to share massive, pre-embedded datasets (Brain Plugins) as Native Apache Arrow Parquet cartridges, bypassing expensive LLM embedding API calls.

## 1. The ROM vs. RAM Architecture
A.I.M. strictly separates ephemeral context from permanent knowledge:
*   **RAM (`memory_lance`):** The live, mutable LanceDB pool where active session flight recorders and daily wiki updates are ingested.
*   **ROM (`archive/cartridges/*.parquet`):** Immutable, highly-compressed Parquet cartridges containing specialized knowledge (e.g., the entire Django framework documentation). These are mounted via Zero-Copy reads and queried instantaneously without database duplication.

## 2. Compiling Knowledge (`aim bake`)
The "Factory Floor" protocol compiles raw documentation into a `.parquet` ROM cartridge natively using PyArrow. It requires zero temporary SQLite databases.

**Workflow:**
1.  Drop raw documentation files (`.md`, `.py`, `.txt`) into an isolated folder (e.g., `synapse/react-docs`).
2.  Execute the compiler: `aim bake synapse/react-docs react19.parquet`
3.  **The Engine:** A.I.M. parses the files, chunks them using the Length-Constrained Accumulator, embeds them locally (via Ollama/Nomic), structures the data into a native PyArrow table, and writes the highly-compressed `.parquet` file directly to disk.

## 3. The Sovereign Swarm (P2P Distribution)
A.I.M. uses a BitTorrent-style Distributed Hash Table (DHT) to share these immutable Parquet cartridges. 

**Seeding (The Exporter):**
*   Command: `aim export react19.parquet`
*   Action: Generates a cryptographic SHA-256 hash and begins seeding the cartridge to the decentralized P2P Swarm.

**Jacking In (The Receiver):**
*   Command: `aim jack-in "magnet:?xt=urn:btih:..."` (or a local file path).
*   **The Quarantine:** The payload downloads into the airgapped `archive/quarantine/` folder. The background Quarantine Daemon verifies the SHA-256 hash and heuristically scans the metadata for adversarial prompt injections.
*   **The Mount:** If clean, LanceDB mounts the `.parquet` file directly into the `archive/cartridges/` directory using Zero-Copy reads. No vectors are `INSERT`ed into the live database, eliminating token taxation.

## 4. Layered RAG Conflicts (Live Deltas)
Because ROM cartridges are immutable to preserve their cryptographic hashes, they cannot be updated directly when a community discovers a new bug fix.
*   **The Solution:** The Subconscious Daemon scrapes GitHub/forums daily and injects new solutions into the mutable `memory_lance` RAM pool (the Live Delta). 
*   **The Retrieval:** When the Conscious Agent executes `aim search`, the `retriever.py` engine queries both the ROM and the RAM simultaneously. If there is a conflict, the mathematical ranking algorithm heavily prioritizes the live delta over the immutable base.
*   **The Minting Cycle:** Eventually, community maintainers use `aim bake --merge-deltas` to fuse the old Base Cartridge with the thousands of RAM patches, minting a brand new `.parquet` ROM and re-seeding it to the Swarm.
