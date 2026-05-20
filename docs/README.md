# A.I.M. Documentation Index (`docs/`)

This directory serves as a comprehensive archive of architectural plans, benchmark reports, forensic logs, and conceptual blueprints for the A.I.M. operating system. 

Below is a categorized summary of every file currently present in this folder:

## 🏛️ Core Architecture & Strategic Gameplans
*   **`AIM_SEARCH_V2_SECRET_SAUCE.md`**: The definitive mathematical blueprint for RAG 5.21 (Tantivy, LanceDB, Sandwich Context Expansion).
*   **`LLM_LANCEDB.md`**: The original "Active Epic" proposal outlining the migration from SQLite to Full LanceDB Native Hybrid Search.
*   **`LLM_WIKI.md`**: A foundational "idea file" inspired by Andrej Karpathy, outlining the core philosophy of a persistent, compounding LLM-maintained personal knowledge base.
*   **`MEMORY_WIKI_GAMEPLAN.md`**: The original gameplan tracking the transition away from the deprecated `MEMORY.md` file to the new Persistent LLM Wiki Architecture.
*   **`RAG_5.2_UPGRADE_PLAN.md`**: A checklist tracking the execution of the ROM vs RAM Decoupling epic.
*   **`RAG_6_0_HYBRID_ROUTER_DESIGN.md`**: An Architecture Decision Record (ADR) planning the *next* evolution: adding a local LLM to route queries concurrently between vector search and deterministic Python grep scripts.

## 🐛 Flaws & Architecture Decision Records (ADRs)
*   **`ADR_TWO_STAGE_RERANKING.md`**: Explains the shift to a Two-Stage Filter & Rank retrieval pipeline (Tantivy Strict Inclusion + FlashRank Cross-Encoder) to eliminate false positives when searching for proper nouns.
*   **`architecture_flaw_update_mechanism.md`**: Documents a critical flaw where `aim update` polluted target repositories with A.I.M.'s engine history. Proposes splitting the command.
*   **`CONVERGENCE_AUDIT_2026-04-09.md`**: An exhaustive cross-team audit comparing the `aim` (Gemini) and `aim-claude` repositories, recommending standardizing on a pure-function architecture.
*   **`memory-wiki-agent-pipeline.md`**: Details the end-to-end execution pipeline of the A.I.M. Memory-Wiki architecture during reincarnation.

## 📊 Benchmark Forensics & Reports
*   **`benchmark_diagnostics/BENCHMARK_DIAGNOSTICS_REPORT.md`**: A forensic analysis of a 10.7-hour Gemini CLI hang (429 Rate Limit error) compared against a flawless DeepSeek baseline.
*   **`benchmark_logs_only.zip`**: A compressed archive of the raw JSON/JSONL logs from the Gemini and DeepSeek benchmarks.
*   **`aerospace.md`**: A status report on an orbital mechanics benchmark. It details a "cascade of failures" where the agent bypassed GitOps rules and hallucinated constants instead of retrieving them from its cartridge.
*   **`BENCHMARK_ECOSYSTEM.md`**: A comprehensive map of the entire LoCoMo V2 benchmark pipeline across 6 different repositories.
*   **`QUOTA_DISCREPANCY_REPORT.md`**: Highlights a severe discrepancy in daily token quotas between Gemini Flash (~178M) and Gemini Pro (~556M).
*   **`RAG_5.1_UPGRADE_REPORT.md`**: A detailed report validating the 89.4% raw accuracy jump achieved by speaker-boundary chunking on the `aim-opencode` fork.
*   **`SCRIPT_MAP.md`**: Maps the benchmark runner and evaluator scripts (e.g., `ghost_judge.py`) located specifically within the air-gapped `benchmark_results/` evaluation hub.

## 🗃️ Dataset Rebuilds (LoCoMo)
*   **`locomo_v2_rebuild_forensics.md`**: A forensic record of the `locomo-v2` dataset rebuild addressing a "Link Rot Crisis" and cross-contamination bugs.
*   **`MASTER_TAGGED_REVIEW_LOG.md`**: A massive 1,175-line log containing all tagged questions (corrections and replacements) from the finalized LoCoMo V2 dataset.
*   **`QA_PAIRS.md`**: A raw list of QA pairs evaluating agent memory retention regarding characters from the dataset.
*   **`V2_EVIDENCE_MAPPING_REVIEW.md`**: A manual review log tracking the semantic synchronization of evidence markers (`D:X:Y`) against updated V2 Ground Truth answers.

## 🛠️ Infrastructure & Setup
*   **`AIM_HEARTBEAT.md`**: Documentation for `aim_heartbeat.py`, a system-level cronjob sentinel that performs routine health checks.
*   **`AIM_PLAN_PINGER.md`**: A guide for `aim_plan_pinger.py`, an agent-initiated detached watchdog that injects `tmux` nudges to keep long-running agents aligned with their plans.
*   **`aim.wiki_overhaul.md`**: The strategy document proposing we split the bloated wiki into a clean user manual and a separate `aim-knowledge` repository.
*   **`aim.wiki_public_obsidian_vault.md`**: Explains the concept of turning the new `aim-knowledge` repository into a public Obsidian Vault for users to browse native Markdown graphs.