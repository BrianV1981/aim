# Architectural Design: The DataJack Protocol
**Status:** Live — v1.7.0
**Goal:** Implement a zero-compute, instant-knowledge transfer system for A.I.M., allowing operators to share massive, pre-embedded datasets (Brain Plugins) without incurring API or CPU token taxes.

---

## 1. The Core Philosophy ("I Know Kung Fu")
While standard CLIs have "Skills" (which are executable actions/tools), A.I.M. features **The DataJack Protocol** (which is instant memory). 

This is a direct nod to the concept of the *Construct* training programs. Instead of asking the AI to read 10,000 pages of Python documentation and waiting hours for it to generate vector embeddings, an operator can simply download a pre-compiled `.engram` cartridge. 

Once "jacked in," the AI instantly possesses flawless semantic recall of that subject matter.

```text
> aim jack-in python314.engram
[1/2] Unpacking cartridge...
[2/2] Downloading Math (Nomic Embeddings) into Subconscious...
[SUCCESS] I know Kung Fu. (503 knowledge sessions injected in 3.1s)
```

## 2. The Mechanics of an `.engram` Cartridge
An `.engram` file is simply a compressed (zipped) directory containing:
1. **`metadata.json`:** Defines the contents (e.g., "Python 3.14 Standard Library", "Solana Smart Contract Security").
2. **`chunks/*.jsonl`:** The Sovereign Sync files containing the raw text *and* the pre-calculated high-dimensional float arrays (Nomic Embeddings).

## 3. The Workflow

### Extracting a Cartridge (The Operator)
If you spend an hour indexing the official React documentation into your local database, you can extract it to share with the community:
```bash
aim exchange export "React 19 Docs" --out react19.engram
```
*Behind the scenes:* A.I.M. queries the database, isolates all fragments where the `source` matches the React docs, exports them to JSONL, and zips them into the cartridge.

### Jacking In (The Receiver)
When another developer downloads your `react19.engram` file, they drop it into their workspace and run:
```bash
aim exchange import react19.engram
```
*(Or, if we want to be truly cinematic, we alias the command to `aim jack-in react19.engram`)*.

*Behind the scenes:* 
1. A.I.M. unzips the cartridge.
2. It detects the pre-calculated Nomic math.
3. It executes raw SQLite `INSERT` statements directly into the receiver's `engram.db`.
4. The transfer takes ~3 seconds. Zero embedding API calls are made. 

## 4. The Value Proposition
This completely changes how AI knowledge is distributed. Instead of sharing massive raw text files and forcing every developer on Earth to waste GPU cycles embedding them, one person embeds the knowledge once, compiles the `.engram` cartridge, and shares the mathematical "memories" infinitely.

## 5. The Engram Marketplace (High-ROI Cartridge Concepts)
To maximize the utility of the DataJack protocol, we must focus on injecting **Protocols, Schemas, and Edge Cases** rather than general trivia. 

### A. The "API Fingerprint" Cartridges
*   **Concept:** Raw OpenAPI JSON schemas and official API documentation (e.g., Stripe, Discord, AWS).
*   **Value:** Prevents the AI from hallucinating deprecated endpoints from its baseline training data. The agent jacks into the exact API schema to write 100% flawless, modern integration code instantly.

### B. The "Anti-Hallucination" (Breaking Changes) Packs
*   **Concept:** Cartridges containing exclusively migration guides and breaking changes (e.g., React 19, Python 3.14).
*   **Value:** AI models suffer from outdated training weights. A cartridge of purely "what NOT to do" forces the AI to abandon deprecated syntax and adopt bleeding-edge standards.

### C. The "Security Audit" Packs
*   **Concept:** Historical vulnerability reports and audit checklists (e.g., Solana Anchor exploits, OWASP Top 10).
*   **Value:** Before the agent writes or commits code, it queries the audit pack to ensure it isn't accidentally writing a known exploit.

### D. The "Diagnostic Decision Tree" Packs
*   **Concept:** Rigid, step-by-step diagnostic trees (e.g., Kubernetes Outage Playbooks, Medical Triage logic).
*   **Value:** Forces the agent to stop "guessing" answers and instead systematically run terminal tools or ask the user clarifying questions based on a proven flowchart.