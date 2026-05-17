# Benchmark Scripts Map

This document maps all the scripts contained within the air-gapped `/home/kingb/benchmark_results/` evaluation hub. It outlines whether a script is actively used in the RAG 5.0 pipeline or designed for a specific agent (Gemini CLI vs OpenCode).

---

## 🏃 RUNNERS (`benchmark_results/runners/`)
*These scripts are responsible for injecting the benchmark questions into the live agents via tmux.*

*   **`opencode_ghost_operator.py`** 
    *   **Target:** OpenCode Agent (`opencode-locomo` project)
    *   **Status:** **ACTIVE**
    *   **Purpose:** The definitive Track B runner for OpenCode. It explicitly spawns the OpenCode TUI, passes the `-m deepseek/deepseek-v4-flash` flag, and includes the `tmux clear-history` fix to prevent cross-bleed between questions.
*   **`locomo_ghost_operator_v2.py`**
    *   **Target:** Gemini CLI Agent (`aim-locomo` project)
    *   **Status:** **ACTIVE**
    *   **Purpose:** The definitive Track B runner for Gemini. It reads the dataset exclusively from the air-gapped data folder, injects the benchmark primer, and strictly enforces the RAG 5.0 Semantic Sandwich retrieval.
*   **`aim_rag_v5_orchestrator.py`**
    *   **Target:** Swarm Orchestration
    *   **Status:** **ACTIVE**
    *   **Purpose:** The Python utility script that runs in the background and injects a 30-minute mandate reminder ping into our active tmux session to enforce GitOps and TDD focus.
*   **`build_cartridge_memeval.py`**
    *   **Target:** Data Ingestion
    *   **Status:** **ACTIVE (Utility)**
    *   **Purpose:** Builds the RAG database specifically for the massive `LongMemEval` dataset. 

---

## ⚖️ EVALUATORS (`benchmark_results/evaluators/`)
*These scripts analyze the predictions outputted by the runners to generate the final scores.*

*   **`ghost_judge.py`**
    *   **Target:** Gemini CLI (as a Judge)
    *   **Status:** **ACTIVE**
    *   **Purpose:** The definitive LLM-as-a-Judge for Track B. It spawns a Gemini session strictly bound by `AGENTS.md` (which now includes the "SEMANTIC FLEXIBILITY" and "STRICT TEMPORAL MATCHING" rules) to grade the agent's predictions against the V2 Ground Truth.
*   **`eval_longmemeval_v2.py`**
    *   **Target:** Track A (IR Scoring)
    *   **Status:** **ACTIVE (Utility)**
    *   **Purpose:** Purely mathematical evaluator for Track A. It calculates the Information Retrieval (IR) metrics (R@5, R@10, NDCG) based on the database vectors without LLM reasoning.
*   **`generate_failures_audit.py`**
    *   **Target:** Reporting
    *   **Status:** **ACTIVE**
    *   **Purpose:** A utility script that parses the final JSON output of `ghost_judge.py` to extract all missed questions and their raw RAG context into a readable Markdown report (`Failures_Context_Audit.md`).