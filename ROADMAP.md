# A.I.M. OS: RAG 3.5 & Cognitive Sovereignty Roadmap

## 🌌 The Grand Vision (The North Star)
The goal of the A.I.M. OS is to achieve absolute **Cognitive Sovereignty** and flawless **Long-Term Memory Retrieval** for autonomous AI agents. 

During our rigorous stress-testing against the LoCoMo and LongMemEval benchmarks, we discovered a fatal flaw in modern RAG: **Vector Dilution**. When we attempted to forcefully chunk conversations into "6-Turn Overlapping Windows," the semantic meaning of specific entities (like a visual description of a guinea pig) was completely drowned out by the surrounding conversational noise. 

The A.I.M. OS is evolving into a **RAG 3.5 Architecture (Parent-Child Cognitive Routing)** to solve these issues permanently. We are officially abandoning rigid, overlapping conversational chunking in favor of surgical, summary-based semantic routing.

This roadmap outlines the exact architectural shifts required to unify the `aim`, `aim-locomo`, and `aim-memeval` repositories under this new North Star.

---

## 🏗️ 1. The RAG 3.5 Architecture: Parent-Child Cognitive Routing
### The Problem: Vector Dilution & Rigid Chunking
Standard RAG fails catastrophically when dealing with complex, multi-turn dialogues or massive code dumps:
1. **The Overlap Fallacy:** Forcing 6 conversational turns into a single block dilutes the semantic vector. A search for a specific fact fails because the embedding model (`nomic-embed-text`) is overwhelmed by the surrounding "noise" of the conversation.
2. **Context Window Crashes:** Massive prompts result in `500 Internal Server Errors` from embedding models with strict 8,192 token limits.

### The Solution: Dynamic Parent-Child Linking
We must implement a **2-Stage Parent-Child Pipeline** across the entire A.I.M. ecosystem.
*   **Stage 1 (Surgical Children):** A.I.M. ingests individual conversational turns (or generates highly concentrated "Semantic Summaries" using a local model like `llama3.2:3b`). *Only* these surgical snippets are embedded using `nomic-embed-text`. This guarantees mathematically pristine vectors that never dilute specific facts.
*   **Stage 2 (The Parent Link):** The dense Child vector is linked via a `parent_id` column to the broader conversation (the Parent) in the SQLite database. 
*   **Stage 3 (The `COALESCE` Fallback):** When the surgical Child vector is matched during a semantic search, A.I.M. executes a `LEFT JOIN` using `COALESCE(p.content, f.content)`. This instantly retrieves the broader Parent context and feeds it to the LLM, giving the agent perfect macro-level awareness without sacrificing micro-level retrieval accuracy.

---

## 🗄️ 2. Unifying the Ecosystem (Action Items)
We have successfully prototyped the RAG 3.5 database schema inside the `aim-memeval` sandbox. We must now backport this architecture to the core OS and the LoCoMo benchmark.

### Phase 1: Upgrading the Core OS (`aim`)
*   **Action:** Port the RAG 3.5 `ForensicDB` schema (with the `parent_id` column and `COALESCE` retrieval logic) from `aim-memeval` into `aim_core/plugins/datajack/forensic_utils.py`.
*   **Action:** Overhaul the DataJack Protocol (`aim bake` and `aim jack-in`) to explicitly serialize and remap `parent_id` foreign keys during `.engram` cartridge export/import. (Tracked in Epic #466).

### Phase 2: Correcting LoCoMo (`aim-locomo`)
*   **Action:** "Shitcan" the 6-turn overlapping logic. It causes vector dilution and failed Q33 during the benchmark.
*   **Action:** Re-embed the `locomo-v2-llava.engram` cartridge using the new RAG 3.5 standard. Embed individual, surgical conversational turns (or their LLaVA descriptions) as Children, and link them to the broader session context as Parents.
*   **Action:** Re-run the `gemini_benchmark` using this purified semantic database.

### Phase 3: Validating MemEval (`aim-memeval`)
*   **Action:** Ensure the background cartridge builder is successfully writing the Parent-Child hierarchy.
*   **Action:** Run the LongMemEval benchmark to mathematically prove the superiority of Cognitive Routing over standard flat-vector RAG.

---

## ⚔️ 3. The Proprietary A.I.M. Benchmark
To truly prove the superiority of the A.I.M. OS, we must stop testing it on contaminated academic data and build our own **Adversarial Proprietary Benchmark**.

### The Benchmark Design
We will architect a custom dataset specifically designed to trap "lazy" LLMs and prove that A.I.M.'s RAG 3.5 retrieval harness forces them to obey context. It will feature:
1. **The Tool-Calling vs. RAG Dilemma:** Questions where the answer is intentionally omitted from the text, forcing the agent to realize it has an "epistemic gap" and must trigger an A.I.M. tool call to find the answer.
2. **Context Contradictions:** A session history where a user states a fact in Turn 1, but explicitly changes it in Turn 50. This tests if the agent correctly prioritizes the most recent temporal Parent chunk.
3. **The Multimodal Override:** We will inject visual descriptions (LLaVA OCR) that fundamentally contradict the surrounding text, proving our Dual-Stage RAG 3.5 pipeline correctly routes visual ground truth.

---

## 🛤️ 4. The Dual-Track Benchmark Strategy (Retrieval vs. Sovereignty)
During the LoCoMo benchmark, we discovered that evaluating an autonomous OS requires two fundamentally different testing methodologies. 

When the A.I.M. agent runs natively via the `gemini` CLI, it autonomously executes terminal commands (`grep`, `aim search`) to research answers. This proves its sovereignty, but appending massive terminal outputs into the Continuous Session history causes rapid token fragmentation (e.g., the `_制` hallucination) and API quota lockouts. 

Conversely, bypassing the CLI to test the raw RAG database proves our retrieval math is perfect, but strips the agent of its autonomous "hands." Moving forward, we enforce a **Dual-Track Benchmarking Standard**:

1. **Track 1: The Retrieval Engine Benchmark (Local/API)**
   *   **The Execution:** The Python script bypasses the CLI tool-calling harness. It directly executes `perform_search_internal` and spoon-feeds the raw context to a model (like local `gemma4:e4b` or API-driven `gemini-3-flash`). 
   *   **The Goal:** Purely mathematical evaluation of A.I.M.'s FTS5/Semantic Hybrid Search and the LLM's reading comprehension. Zero context bloat.
2. **Track 2: The Sovereign Agent Benchmark (Reincarnation-Bound)**
   *   **The Execution:** Uses the native `gemini` CLI. Allows the agent to autonomously run terminal commands and search the database itself.
   *   **The Goal:** Test the agent's cognitive autonomy and tool-usage reliability.
   *   **The Critical Fix (Reincarnation):** The Python benchmark script MUST programmatically inject a `/reincarnate` wipe (cycling the `session_id`) at fixed intervals (e.g., every 25 questions). This solves the "Amnesia Problem," preventing terminal bloat from crashing the context window and preserving cognitive clarity.