# 🛰️ Gameplan: Sovereign Swarm (BitTorrent) Integration

> **Core Thesis:** Transition A.I.M. knowledge distribution from a centralized HTTP model to a decentralized, P2P "Sovereign Swarm" using BitTorrent (aria2c) as the primary transport layer.

---

## 🏗️ Phase 1: Configuration & TUI (The Toggle)
The Swarm must be an "Opt-In" feature to respect local bandwidth and security constraints.

1.  **`core/CONFIG.json` Expansion:**
    *   Add `swarm_enabled: boolean` (Default: `false`).
    *   Add `swarm_settings`:
        *   `max_download_speed`: string (e.g., "5M").
        *   `seeding_ratio`: float (Default: 1.0).
        *   `rpc_port`: int (Default: 6800).
2.  **TUI Integration (`scripts/aim_config.py`):**
    *   Add a "Transport" section to the configuration menu.
    *   Implement a checkbox for "Enable Sovereign Swarm (P2P)".
    *   Verification: The TUI must update the local JSON without corrupting existing paths.

---

## 📡 Phase 2: The Transport Bridge (Wiring)
Formalize the handshake between the DataJack and the Torrent Handler.

1.  **Refactor `scripts/aim_cli.py` (Command Logic):**
    *   Standardize `aim jack-in <URI>`.
    *   Implement URI detection logic:
        *   If starts with `magnet:?` -> Route to `aim_torrent.py`.
        *   If starts with `http` -> Route to `requests` fallback.
2.  **Harden `src/plugins/datajack/aim_exchange.py`:**
    *   Implement the `ExchangeImporter` interface to accept local file paths provided by the torrent handler after successful DHT resolution.
3.  **Atomic Handoff:**
    *   The torrent handler must return a `SUCCESS_PATH:<path>` string to stdout.
    *   The CLI must capture this path and immediately trigger `aim exchange import --file <path>`.

---

## 🗳️ Phase 3: Seeding & Engram Packaging (The Daemon)
A.I.M. must be able to "give back" to the swarm to ensure knowledge persistence.

1.  **The Seeding Daemon (`aim daemon --seed`):**
    *   Implement a background process that monitors the `archive/engrams/` folder.
    *   For every verified `.engram` file, generate a `.torrent` file using `aria2c`.
    *   Keep the `aria2c` RPC daemon alive to serve as a local seed node.
2.  **Engram Export Logic:**
    *   Implement `aim export <engram_id>`.
    *   This script must:
        1. Query `engram.db` for the target knowledge block.
        2. Package it into a compressed `.engram` (tar.gz) file.
        3. Notify the Seeding Daemon to begin announcing the new payload.

---

## 🧪 Phase 4: TDD & Verification (The Integrity Check)
P2P data is inherently "untrusted" until verified.

1.  **Checksum Validation:**
    *   Every engram package must include a `manifest.json` with a SHA-256 hash.
    *   The `aim_exchange.py` importer must verify the hash before injecting data into the local SQLite brain.
2.  **Local Peer Testing:**
    *   Develop a test script that spawns two local `aria2c` instances on different ports to simulate a "Swarm of Two."
    *   Verify that `aim jack-in` can successfully transfer an engram from Node A to Node B without an internet connection (Local Peer Discovery).

---

## 📅 Roadmap to Release
*   **Milestone 1:** Config/TUI Toggle (Visible in `aim config`).
*   **Milestone 2:** Magnet link resolution (Proven via `aim jack-in`).
*   **Milestone 3:** Automatic import after download.
*   **Milestone 4:** Background seeding enabled.

---
**Mandate Check:** This plan aligns with the **Forensic-First Protocol**. No code has been written. This is a purely architectural directive.
