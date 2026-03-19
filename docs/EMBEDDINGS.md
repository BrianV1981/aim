# A.I.M. Embedding & Semantic Search Guide

## 🧠 The "Vector Brain" Concept
Semantic search in A.I.M. works by converting text into high-dimensional mathematical coordinates (embeddings). These coordinates allow the agent to find "concepts" rather than just "keywords."

## 🗄️ Unified Forensic Database (SQLite)
A.I.M. uses a centralized SQLite database (`archive/forensic.db`) to store all session fragments and their corresponding embeddings.
- **Efficiency**: Replaces O(N) file-scanning with near-instant SQL indexing.
- **Portability**: The entire semantic index is contained within a single file.

## 🛑 The Mixing Mandate: Why Consistency is Critical
You **cannot** mix embeddings from different models or providers in the same database.

1.  **Coordinate Systems:** Every model has its own "map." Google's map is 3,072 dimensions wide; Nomic's (Ollama) is 768. 
2.  **Semantic Drift:** Even if two models use the same dimensions, they "see" the world differently.
3.  **Search Failure:** If you search using Nomic coordinates against a Google database, the results will be 100% incoherent.

## 🛠️ Switching Providers (The "Brain Transplant")
Switching providers is supported but is a **destructive operation**. If you change the `embedding_provider` in `aim tui`:

1.  **Old Index is Void**: The `forensic.db` is now mathematically useless.
2.  **Mandatory Re-index**: You MUST run `aim index` to regenerate all embeddings and repopulate the database.
3.  **Volume Warning**: If switching back to Google, be aware of API quotas.

## 🛡️ Recommended Provider: Local (Ollama/Nomic)
For sharing and production, **Local Nomic** is the foundational choice for A.I.M. because:
- **Zero Cost**: Unlimited indexing volume.
- **Privacy**: Your raw session fragments never leave your machine during indexing.
- **Stability**: No API quotas or downtime.

"I believe I've made my point." — **A.I.M.**
