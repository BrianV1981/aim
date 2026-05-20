# A.I.M. Operating System Protocols (`aim_os/`)

This directory contains the highly distilled, operational markdown files that define the A.I.M. architecture and behavioral guardrails. These files are extracted and summarized from the deep philosophical lore of the `aim-wiki` repository.

## 🛑 MANDATORY RE-BAKING RULE
The files in this directory are **not** read natively by the Conscious Agent during standard operation. Instead, they serve as the raw materials for the A.I.M. OS Knowledge Cartridge.

**If you modify, add, or delete ANY file in this directory, you MUST execute the following command to re-compile the Parquet cartridge:**

```bash
aim bake aim_os aim_os.parquet
```

Once baked, you MUST move the resulting `aim_os.parquet` file into `assets/default_engrams/aim_os.parquet` and deploy the changes via GitOps. If you fail to do this, newly initialized agents will be provisioned with an outdated OS handbook and will hallucinate legacy architecture.

---

## Index of Protocol Files

*   **`AIM_CLI_TOOLS.md`**: Maps the core command-line tools (`aim bug`, `aim push`, `aim search`, `aim reincarnate`) that agents must use instead of raw bash commands.
*   **`COGNITIVE_ARCHITECTURE.md`**: Maps the flow of data through the system, identifying the Failsafe Layer, Continuity Pulse, LanceDB RAM/ROM, and Sovereign Sync mechanisms.
*   **`DATAJACK_SWARM.md`**: Outlines the P2P knowledge sharing network, detailing how Parquet cartridges are exported and mounted as Zero-Copy ROM.
*   **`EUREKA_FARMING.md`**: Defines the self-optimization cycle, instructing agents on hindsight pruning and forging "sweat equity" into exportable skill cartridges.
*   **`GITOPS_DEPLOYMENT.md`**: The strict version control rules. Forbids raw git commands and mandates the `aim bug` -> `aim fix` -> `aim push` atomic deployment pipeline.
*   **`HYBRID_SEARCH.md`**: Details the mechanics of the RAG 5.21 engine (Tantivy FTS + Nomic Embeddings + Reciprocal Rank Fusion) and "Sandwich" context expansion.
*   **`LANCEDB_INGESTION_PROTOCOL.md`**: Explains the 5-stage ingestion pipeline, including multimodal flattening, format shifting, the Length-Constrained Accumulator, and the critical `table.optimize()` compaction protocol for preventing version bloat.
*   **`PERSISTENT_WIKI.md`**: Establishes the Dual-Search architecture and the rule that Conscious Agents must drop notes into `wiki/_ingest/` for the Subconscious Daemon rather than editing markdown manually.
*   **`REINCARNATE_PROTOCOL.md`**: Formalizes the 5-Phase teleportation sequence that defeats the "Amnesia Problem," detailing the Direct Python Handoff and the background summarization daemon.
*   **`SCRIPT_MAP.md`**: A literal, file-by-file directory map of every Python engine, CLI router, and maintenance script operating in the `aim_core/` folder.
*   **`TESTING_AND_VALIDATION.md`**: Enforces the "TDD Reflex" and forbids "Vibe Coding." Mandates that all architectural changes must be empirically proven by automated tests before deployment.
