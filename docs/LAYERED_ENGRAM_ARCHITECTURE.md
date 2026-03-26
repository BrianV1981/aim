# Layered Engram Architecture: Torrents vs. Live Polling

## The Architectural Conflict
A.I.M. is driving toward two advanced knowledge-distribution features that are seemingly at odds:

1. **The Decentralized Torrent Registry (Phase 38):** `.engram` cartridges should be immutable, mathematically hashed SQLite binaries shared via a peer-to-peer torrent network. This requires the file to be static.
2. **Self-Upgrading Engrams (Live Polling):** Background daemons should scrape GitHub and forums nightly to inject new bug fixes into the local knowledge base. This requires the file to be highly mutable.

If local background daemons mutate the torrented `.engram` files, they break the cryptographic hash, destroying the torrent swarm and fragmenting the community's knowledge base.

## The Solution: The Base vs. The Delta
To resolve this, A.I.M. must adopt a **Layered RAG Architecture**—operating much like Docker image layers or Linux package managers (LTS core + daily security patches).

### 1. The Immutable Base (The Master Cartridge)
*   Generated via `aim bake`.
*   Contains the vast bulk of foundational documentation (e.g., `django-v5-core.engram`).
*   **Read-Only:** Once generated, this local SQLite table/file cannot be modified by the daemon.
*   **Decentralized:** Because it is static, its hash is permanent, making it perfect for seeding to the decentralized torrent registry.

### 2. The Live Patch Ledger (The Mutable Delta)
*   Managed by the `aim watch` Autonomous Daemon.
*   When the daemon scrapes new solutions from GitHub, it does **not** insert them into the core cartridge.
*   Instead, it inserts the vectorized data into a highly mutable, local-only SQLite table called `live_deltas` (or writes them to a designated `synapse/live_feed/` text directory).

### 3. The Query Resolver (Execution Time)
When the active AI agent executes `aim search "timeout bug"`, the `retriever.py` script queries **both** layers simultaneously:
1. It searches the `live_deltas` table.
2. It searches the read-only Base Cartridges.
If a conflict or duplicate topic exists, the **Live Delta takes precedence**, effectively "patching" the outdated knowledge in the Base Cartridge at runtime.

## The Community Minting Process
This layered approach naturally creates an open-source lifecycle for knowledge:

1. **The Daily Grind:** 1,000 operators run `aim watch` locally. Over 6 months, their `live_deltas` databases fill up with hundreds of new bug fixes.
2. **The Minting:** A community maintainer decides it is time for an official release. They run:
   `aim bake --merge-deltas django-v5.1.engram`
3. **The Fusion:** The CLI takes the old immutable base, merges all the proven solutions from the `live_deltas` table, and mints a brand-new, officially hashed `.engram` file.
4. **The Reset:** The new cartridge is uploaded to the torrent swarm. Users run `aim jack-in django-v5.1.engram`, which automatically wipes their local `live_deltas` table clean to begin the cycle anew.

## Implementation Requirements
*   Update `src/forensic_utils.py` and the database schema to isolate core data from live delta data.
*   Modify `src/retriever.py` to prioritize `live_deltas` results over core results in the final FTS5/Vector ranking algorithm.