# The Eureka Protocol & Cartridge Farming

This document defines A.I.M.'s Self-Optimization cycle. Instead of relying solely on offline pipelines to generate synthetic training data, A.I.M. uses the active operator session as a live data-farming engine.

## 1. The Philosophy: Zero-Noise Knowledge
Traditional RAG systems suffer from "garbage in, garbage out." If raw, thrashing chat logs are dumped directly into a vector database, the AI will retrieve hallucinations and failed attempts when searching for answers later. 
The Eureka Protocol guarantees that **only the highest-signal, empirically verified solutions are archived.**

## 2. Hindsight Pruning (The Eureka Moment)
When an agent encounters a complex problem, it may spend multiple turns trial-and-erroring solutions (The Thrash). Once a verifiable success state is achieved (The Resolution), the protocol is triggered.
1.  **The Trigger:** The agent or operator explicitly marks the solution.
2.  **The Prune:** The active context is rewound. The intermediate failures are squashed and deleted.
3.  **The Synthesis:** A synthetic, one-shot summary of the solution is injected in their place. This "Problem -> Solution" pair contains zero noise and zero hallucination vectors.

## 3. Cartridge Farming (Sweat Equity into ROM)
Simultaneously, the system takes the original problem (User Prompt/Error Trace) and the final synthetic summary (The Action/Fix) and permanently archives it.
*   The system writes this distilled pair to a standalone `.parquet` file in the `archive/cartridges/` directory or natively into the `memory_lance` RAM pool.
*   This converts the agent's real-time "sweat equity" into a pre-packaged, exportable expertise cartridge.

## 4. The Curse of Knowledge Shield
By generating these high-density `.parquet` cartridges from real-world thrashing sessions, the knowledge becomes portable. The operator can take this Eureka cartridge and inject it into a completely different A.I.M. workspace. The new agent instantly possesses the exact "knowledge" of the migration or bug fix without ever having to experience the thrashing. Every mistake the AI makes mathematically improves the baseline intelligence of the entire swarm.