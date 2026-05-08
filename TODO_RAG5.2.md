# RAG 5.2 Decoupling Plan (ROM vs RAM)

This document tracks the execution of GitHub Issue #542.

## Phase 1: LanceDB Native Ingestion (The RAM Upgrade)
- [x] Update `aim_core/lance_backend.py` to expose a public `add_fragments()` method.
- [x] Refactor `hooks/session_summarizer.py` to bypass `ForensicDB` and write directly to LanceDB.
- [x] Remove the `migrate_from_sqlite()` bottleneck function from `lance_backend.py`.

## Phase 2: Parquet Cartridge Generation (`aim bake`)
- [x] Refactor `aim_core/plugins/datajack/aim_bake.py` to compile markdown directly into a `knowledge.parquet` file using `pyarrow`.
- [x] Ensure Parquet schema identically matches the LanceDB schema (`session_id`, `content`, `vector`, `metadata`, `parent_id`).

## Phase 3: Zero-Copy ROM Mounting (`aim jack-in`)
- [x] Refactor `aim_core/plugins/datajack/aim_exchange.py` to move downloaded `.parquet` files into an `archive/cartridges/` directory instead of unzipping and firing SQLite INSERTs.
- [x] Update `lance_backend.py` and `retriever.py` to perform Federated Querying (searching both `memory_lance` RAM and `cartridges/*.parquet` ROM simultaneously).

## Phase 4: Decoupling the "Sandwich Context"
- [x] Refactor `expand_sandwich_context()` in `aim_core/retriever.py` to stop using raw SQLite `SELECT` queries for fetching adjacent fragments.
- [x] Implement secondary LanceDB/Parquet metadata queries to fetch adjacent IDs natively via Arrow.

## Phase 5: The Clean Sweep (Deprecation)
- [ ] Strip `ForensicDB` out of `forensic_utils.py` entirely (or isolate it as a legacy v1.6 migration script).
- [ ] Update all unit tests (`test_federated_db.py`, `test_lance_backend.py`) to mock PyArrow and Parquet instead of SQLite.
- [ ] Update the `aim purge` command in `aim_cli.py` to wipe LanceDB and the `cartridges/` directory.