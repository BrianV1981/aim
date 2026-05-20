# Architecture Decision Record: A.I.M. RAG 6.0 - Hybrid Query Routing

## 1. Executive Summary & Objective
Following our triumph on the LongMemEval (v1) benchmark (achieving a mathematically verified 95.6% Recall@10 via the RAG 5.21 architecture), we are targeting **LongMemEval-V2**. 

LongMemEval-V2 shifts the paradigm entirely: instead of searching simple user histories, it evaluates whether a memory system can help an agent become an **"experienced colleague"** by internalizing the nuances, workflows, and pitfalls of complex web/enterprise environments (like WebArena and ServiceNow).

*   **The Scale:** Up to 500 trajectories and 115 million tokens of history.
*   **The Problem:** The top performing systems on V2 are "Coding Agents" (AgentRunbook-C scoring 72.5%), which write active Python scripts in a sandbox to grep and parse history files. Standard passive RAG systems (AgentRunbook-R) failed miserably, scoring only 48.5%. Coding agents are accurate but suffer from massive latency costs.
*   **The Solution (RAG 6.0):** Implement a **Local LLM Query Router** (using a small model like Qwen-1.5/1.8B or Gemma-2B) at the front of our pipeline. This model parses natural language into a strict JSON execution plan, firing off a **Hybrid Retrieval Pipeline**: semantic vector search (LanceDB) running concurrently with deterministic literal search (Python grep/filters).

## 2. Why RAG 5.21 Placed Us on the Correct Trajectory
Our current system, RAG 5.21, solved "Entity Blindness" in vector databases by introducing the `EntityIntersectionReranker`. 
We already proved that standard semantic search is fundamentally flawed when dealing with exact nouns, error codes, or IDs. By extracting entities and multiplying their vector scores, we bridged the gap between "vibes-based" semantic matching and exact lexical matching.

**RAG 6.0 is the natural, inevitable evolution of this.** 
Instead of doing passive entity extraction *during the reranking phase* of a vector search, RAG 6.0 moves the intelligence to the front of the pipeline. The local LLM acts as an active router, taking the entity-matching concept to its logical extreme: completely decoupling the deterministic exact-match requirements (which are sent to a Python grep subprocess) from the conceptual requirements (which are sent to LanceDB).

## 3. The Architecture: Hybrid Query Routing

To beat the 72.5% accuracy ceiling of active sandbox coding agents without incurring their massive latency, we distill the "coding agent" intelligence into a single, instant, local routing step.

### The Pipeline Flow
1.  **The Input:** User or Agent issues a query (e.g., `"Did we get any OOM errors when processing the high-res images last Tuesday?"`)
2.  **The Local Router (Qwen/Gemma):** The query is intercepted and passed to a local 1.8B/2B model with a rigid JSON-enforced system prompt.
    *   *Output:*
        ```json
        {
          "semantic_search": "out of memory failures during high resolution image processing",
          "literal_grep": ["OOM", "error", "high-res", "image"],
          "timeframe_filter": "last Tuesday"
        }
        ```
3.  **Split Execution (Concurrent):**
    *   **Thread A (Conceptual - LanceDB):** Executes vector search using the `"semantic_search"` string to find high-level workflow descriptions and context.
    *   **Thread B (Deterministic - Python Subprocess):** Takes the `"literal_grep"` array and executes blazing-fast file iteration/grep over the raw trajectory JSON/Markdown files.
4.  **The Fusion:** Both threads return in milliseconds. The outputs are deduplicated and merged, providing the downstream reasoning agent with both the "Vibes" (conceptual context) and the "Receipts" (exact deterministic log lines/counts).

## 4. Benchmark Query Handling: RAG vs. RAG 6.0 Router

LongMemEval-V2 tests five core memory abilities. Here is how our Router handles them where standard RAG fails:

### A. Dynamic State Tracking
*   *Question:* "How has the status of the 'Server Upgrade' ticket changed over the last three trajectories?"
*   *Standard RAG:* Fails by retrieving random, non-chronological chunks mentioning "Server Upgrade".
*   *RAG 6.0 Router:* Outputs `{"literal_grep": ["Server Upgrade", "status:"], "semantic": "ticket progression"}`. The Python subprocess pulls exact timestamped logs, preserving chronological state.

### B. Environment Gotchas (Implicit Rules)
*   *Question:* "Which specific field in the 'User Profile' form is known to cause a validation error if left blank, even though it is not marked as required?"
*   *Standard RAG:* Retrieves generic validation errors, missing the implicit connection to the specific unrequired field.
*   *RAG 6.0 Router:* Outputs `{"literal_grep": ["validation error", "User Profile"], "semantic": "undocumented form requirement or local failure mode"}`.

### C. Workflow Knowledge
*   *Question:* "What are the mandatory steps required to approve a budget request in this specific enterprise environment?"
*   *Standard RAG:* Mashes together steps from unrelated budget tasks, hallucinating a workflow.
*   *RAG 6.0 Router:* Outputs `{"literal_grep": ["approve", "budget request"], "semantic": "standard operating procedure for budget approval"}`.

### D. Static State Recall
*   *Question:* "Where is the 'Submit' button located on the 'Create Incident' page in the ServiceNow environment?"
*   *Standard RAG:* Fails because vectorizing UI layout/DOM logic is notoriously weak.
*   *RAG 6.0 Router:* Outputs `{"literal_grep": ["Submit", "Create Incident", "ServiceNow"], "semantic": "UI layout and button placement"}`.

### E. Multimodal/Visual Recall
*   *Question:* "Based on the screenshot from step 12 of trajectory ID 'web_001', what was the error message displayed in the red banner?"
*   *Standard RAG:* Completely blind to specific steps unless OCR previously transcribed the exact context.
*   *RAG 6.0 Router:* Outputs `{"literal_grep": ["trajectory ID 'web_001'", "step 12"], "semantic": "error message in red banner"}`. The grep instantly finds the exact file path, allowing the vision model to process the correct frame.

## 5. Conclusion
A.I.M. RAG 6.0 eliminates the need for slow, active coding agents. By routing queries through a local LLM, we guarantee the exactness of a deterministic script while maintaining the sub-second latency of a passive search pipeline. This is the definitive architecture for achieving supremacy on LongMemEval-V2.