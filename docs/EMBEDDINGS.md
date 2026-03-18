# A.I.M. Embedding & Semantic Search Guide

## 🧠 The "Vector Brain" Concept
Semantic search in A.I.M. works by converting text into high-dimensional mathematical coordinates (embeddings). These coordinates allow the agent to find "concepts" rather than just "keywords."

## 🛑 The Mixing Mandate: Why Consistency is Critical
You **cannot** mix embeddings from different models or providers in the same database.

1.  **Coordinate Systems:** Every model has its own "map." Google's map is 3,072 dimensions wide; Nomic's (Ollama) is 768. 
2.  **Semantic Drift:** Even if two models use the same dimensions, they "see" the world differently. A concept like "Python" might be at coordinate A in Google but coordinate Z in OpenAI.
3.  **Search Failure:** If you search using Nomic coordinates against a Google database, the results will be 100% incoherent (effectively random noise).

## 🛠️ Switching Providers (The "Brain Transplant")
Switching providers is supported but is a **destructive operation**. If you change the `embedding_provider` in `aim tui`:

1.  **Old Index is Void:** All files in `archive/index/` are now mathematically useless.
2.  **Mandatory Re-index:** You MUST run `aim index` to regenerate all embeddings using the new model.
3.  **Volume Warning:** If switching back to Google, be aware of the 1,000/day free tier quota. Re-indexing a large archive may hit this wall instantly.

## 🛡️ Recommended Provider: Local (Ollama/Nomic)
For sharing and production, **Local Nomic** is the foundational choice for A.I.M. because:
- **Zero Cost:** Unlimited indexing volume.
- **Privacy:** Your raw session fragments never leave your machine during indexing.
- **Stability:** No API quotas or downtime.

## ☁️ The Sovereign Gateway (Ollama Cloud)
A.I.M. supports "Hybrid Sovereignty." By using a local gateway like Ollama, you can run massive cloud models (like **Qwen 3.5**) while keeping your configuration pointed at `localhost`. This allows A.I.M. to stay flexible without needing to manage complex cloud credentials for every individual tool.

"I believe I've made my point." — **A.I.M.**
