# Key Feature: Cognitive Routing & The Zero-Dollar Brain

**The Problem:** Running a background memory refinement pipeline (summarizing 100,000 tokens of raw terminal logs every hour) using a flagship model like Gemini 3.1 Pro or GPT-5.4-pro will rapidly drain your API credits. 

**The Solution:** Cognitive Routing. A.I.M. splits the "Brain" into discrete, interchangeable LLM endpoints, allowing you to use hyper-expensive models for logic, and 100% free local models for memory management.

---

## The Universal Hub (The Cockpit)
A.I.M. is completely model-agnostic. The `aim tui` command opens the Sovereign Cockpit, allowing you to route different tiers of the architecture to completely different API providers (Google, OpenAI, Anthropic, OpenRouter, or Local Ollama).

### 1. The Frontal Lobe (Maximum Reasoning)
*   **Assignment:** The Default Agent.
*   **Model:** Gemini 3.1 Pro or Claude 3.5 Sonnet.
*   **Use Case:** Writing complex Rust backends, debugging React states, and making deep architectural decisions. You pay the premium API price because you need maximum logic.

### 2. The Muscle (The Zero-Dollar Brain)
*   **Assignment:** The Tier 1 Harvester / The Indexer.
*   **Model:** Local Ollama (Llama-3 8B) or Gemini Flash.
*   **Use Case:** Reading 10,000 lines of JSON to extract the "Signal Skeleton."
*   **The Secret:** Smaller models typically fail at complex RAG pipelines due to hallucination or sequential tool spam. A.I.M. solves this via the **Explicit Guardrails** toggle during `aim init`. 

## The "Token Tax" (Explicit Guardrails)
When you assign a local, lightweight model to handle your background tasks, A.I.M. automatically injects a rigid, ALL-CAPS behavioral matrix into the prompt:

```markdown
## ⚠️ EXPLICIT GUARDRAILS (Lightweight Mode Active)
1. **NO TITLE HALLUCINATION:** You MUST NOT guess file contents from titles.
2. **PARALLEL TOOLS:** You MUST request all files in a single tool turn.
3. **DESTRUCTIVE MEMORY:** You MUST delete stale facts.
```

By imposing this strict "Token Tax" on the prompt, A.I.M. physically forces low-IQ local models to behave like disciplined data-entry clerks. 

## The Result
You experience the brilliant coding capabilities of a flagship model in your terminal, while your massive background memory cascade runs entirely offline on your GPU for $0.00.