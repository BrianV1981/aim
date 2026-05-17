# A.I.M. Documentation Index

This directory contains the deep architectural records, audit logs, and strategic gameplans for the A.I.M. project. Below is an index of all loose files:

### [Architecture Decision Record: Two-Stage Filter & Rank](ADR_TWO_STAGE_RERANKING.md)
**Date:** May 2026 **Status:** Accepted

### [A.I.M. Heartbeat (System Sentinel)](AIM_HEARTBEAT.md)
The `aim-heartbeat` is a persistent infrastructure utility designed to ensure the A.I.M. ecosystem remains reachable and operative. Unlike the *Plan Pinger* (which monitors task progress), the *Hea...

### [A.I.M. Plan Pinger (Watchdog)](AIM_PLAN_PINGER.md)
The `aim-plan-pinger` is a task-specific sentinel tool designed to ensure A.I.M. agents remain aligned with their active "Plan" or "Roadmap" during complex, multi-session operations.

### [A.I.M. Search V2: The RAG 5.2 Architecture](AIM_SEARCH_V2_SECRET_SAUCE.md)
This document serves as the absolute, mathematically verifiable blueprint of the A.I.M. RAG 5.2 search system. It must be read and adhered to by any agent modifying or interacting with the system. ...

### [A.I.M. Benchmark Ecosystem](BENCHMARK_ECOSYSTEM.md)
---

### [A.I.M. Cross-Team Convergence Audit](CONVERGENCE_AUDIT_2026-04-09.md)
**Date:** 2026-04-09 **Author:** aim-claude team (on behalf of the Operator)

### [Example of LanceDB's Native Hybrid Search capability](LLM_LANCEDB.md)
**LanceDB Integration Proposal for A.I.M.** **Status:** Active Epic

### [LLM Wiki](LLM_WIKI.md)
A pattern for building personal knowledge bases using LLMs.

### [Master Tagged Review Log](MASTER_TAGGED_REVIEW_LOG.md)
This log contains all tagged questions from the finalized V2 dataset.

### [Gameplan: Transitioning to the Persistent LLM Wiki Architecture](MEMORY_WIKI_GAMEPLAN.md)
The current A.I.M. memory system is fractured. `core/MEMORY.md` is deprecated, stagnant, and the old 5-Tier Cascading Memory was removed. The Reincarnation loop successfully generates a clean sessi...

### [QA_PAIRS.md](QA_PAIRS.md)
**Q1:** When did Sarah go to the LGBTQ support group.

### [Gemini API Quota Discrepancy Report](QUOTA_DISCREPANCY_REPORT.md)
**Date:** 2026-05-08 **Subscription Level:** Gemini Advanced / Ultra

### [RAG 5.1 Upgrade Report — aim-opencode Fork](RAG_5.1_UPGRADE_REPORT.md)
---

### [RAG 5.2 Decoupling Plan (ROM vs RAM)](RAG_5.2_UPGRADE_PLAN.md)
This document tracks the execution of GitHub Issue #542.

### [Benchmark Scripts Map](SCRIPT_MAP.md)
This document maps all the scripts contained within the air-gapped `/home/kingb/benchmark_results/` evaluation hub. It outlines whether a script is actively used in the RAG 5.0 pipeline or designed...

### [V2 Evidence Mapping Review Log](V2_EVIDENCE_MAPPING_REVIEW.md)
This document tracks the manual, semantic synchronization of evidence markers (`D:X:Y`) against the updated V2 Ground Truth answers.

### [Aerospace Benchmark Status Report (Issue #316)](aerospace.md)
The goal of this benchmark is to scientifically prove the A.I.M. architecture's superiority over standard standalone LLMs for complex engineering tasks. We set up two environments to calculate a co...

### [aim.wiki_overhaul.md](aim.wiki_overhaul.md)
**Yes — the wiki overhaul is the highest-leverage thing you can do right now.**

### [aim.wiki_public_obsidian_vault.md](aim.wiki_public_obsidian_vault.md)
**A public Obsidian vault** is simply your collection of Markdown notes (the folder you open in Obsidian) made openly available for anyone on the internet to browse.

### [Architectural Flaw: The Monolithic Update Mechanism](architecture_flaw_update_mechanism.md)
The A.I.M. Swarm OS currently suffers from a critical architectural flaw regarding its `update` mechanism (`aim_cli.py update`). When A.I.M. is deployed as an exoskeleton or operating system to man...

### [LoCoMo V2 Dataset Rebuild: Forensic Autopsy & Architecture](locomo_v2_rebuild_forensics.md)
*Date: May 7, 2026*

### [Memory-Wiki Agent Pipeline](memory-wiki-agent-pipeline.md)
This document details the end-to-end execution pipeline of the A.I.M. Memory-Wiki architecture during a reincarnation cycle. It clarifies the sequence of operations, the different types of agents s...