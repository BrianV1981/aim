# OpenCode Track B Benchmark — Agent Onboarding Guide

> **For:** The next agent assigned to run the LoCoMo V2 Track B benchmark
> **Model:** DeepSeek V4 Flash
> **Platform:** OpenCode CLI (aim-opencode fork)
> **RAG Version:** 5.1 (speaker-boundary chunking, Sandwich expansion, LanceDB hybrid search)

---

## 1. What You're Testing

You are running a **live-agent memory benchmark** against the LoCoMo V2 dataset. The benchmark tests whether the A.I.M. RAG 5.1 search engine + DeepSeek reasoning can correctly answer 199 questions about a multi-month conversation between two characters (Caroline & Melanie).

**Track B means:** The agent must search its LanceDB memory, find the relevant conversation context, reason about the answer, and respond with `[ANSWER]`. This is NOT a retrieval-only test — it's the full pipeline.

---

## 2. Required Reading (15 minutes)

Read these in order to understand the ecosystem:

| # | Document | Location | Why |
|---|---|---|---|
| 1 | **BENCHMARK_ECOSYSTEM.md** | `docs/BENCHMARK_ECOSYSTEM.md` | Full map of all 6 repos: locomo-visual-ground-truth, locomo-v2, benchmark_results, aim-locomo, aim-swarm, aim-opencode |
| 2 | **RAG_5.1_UPGRADE_REPORT.md** | `docs/RAG_5.1_UPGRADE_REPORT.md` | What RAG 5.1 changed: chunking, extraction fix, judge calibration |
| 3 | **SWARM_PROTOCOL.md** | `docs/SWARM_PROTOCOL.md` | Tmux buffer injection protocol — how the Ghost Operator communicates with the test agent |
| 4 | **GitHub Wiki RAG-and-Search** | [Wiki](https://github.com/d3c12yp7012/aim-opencode/wiki/RAG-and-Search) | RAG 5.1 pipeline architecture |
| 5 | **locomo-v2/README.md** | `/home/kingb/locomo-v2/README.md` | How the gold standard dataset was built (156 corrections + 82 visual replacements) |
| 6 | **locomo-visual-ground-truth/README.md** | `/home/kingb/locomo-visual-ground-truth/README.md` | Image preservation + OCR cache (775 surviving images of 862) |

---

## 3. The 6-Repo Ecosystem

```
locomo-visual-ground-truth/     ← Preserved images (775) + LLaVA OCR cache
        │
        ▼
locomo-v2/                      ← Corrected gold dataset (156 text fixes + 82 dead-image replacements)
        │
        │ locomo_v2_final.json
        ▼
benchmark_results/data/locomo_v2/  ← Air-gapped question source
        │
        │ Ghost Operator reads questions
        ▼
benchmark_results/opencode/runners/opencode_ghost_operator_v2.py
        │
        │ Spawns agent in tmux, injects questions, monitors SQLite
        ▼
opencode-locomo/                ← Agent under test (RAG 5.1 LanceDB + DeepSeek Flash)
        │
        │ Predictions saved
        ▼
benchmark_results/opencode/reports/locomo_v2/track_b/
        │
        │ Judge evaluates
        ▼
benchmark_results/opencode/evaluators/opencode_ghost_judge.py
        │
        ▼
Final accuracy report
```

---

## 4. How the Ghost Operator Works

The Ghost Operator (`opencode_ghost_operator_v2.py`) is the bridge between the air-gapped question data and the live agent:

1. **Spawn:** Creates a detached tmux session running OpenCode in the `opencode-locomo` project
2. **Find session:** Queries `~/.local/share/opencode/opencode.db` for the session ID
3. **Primer:** Injects benchmark mandate + answer format instructions
4. **Loop (199×):** Buffer-pastes a question → waits for agent response → extracts `[ANSWER]` from SQLite `part` table
5. **Retry:** Up to 3 retries on tool leaks/errors, 120s timeout per question
6. **Output:** Saves predictions incrementally to `opencode_trackB_{timestamp}.json`

The key innovation over the Gemini version: **SQLite polling replaces JSONL file monitoring.** The OpenCode `part` table contains structured text responses that can be parsed for `[ANSWER]` tags — no TUI noise, no cross-bleed.

---

## 5. Prerequisites Checklist

Before running, verify:

```bash
# 1. opencode-locomo project is scaffolded with LanceDB
ls /home/kingb/opencode-locomo/memory_lance/fragments.lance

# 2. DeepSeek API key is in keyring
python -c "import keyring; print(keyring.get_password('aim-system', 'reasoning-api-key')[:10])"

# 3. OpenCode binary exists
which opencode

# 4. Air-gapped data is in place (not in agent workspace!)
ls /home/kingb/benchmark_results/data/locomo_v2/locomo_v2_final.json

# 5. No raw flight recorders in agent workspace (anti-cheat)
ls /home/kingb/opencode-locomo/benchmarks/locomo/data/flight_recorders/ 2>&1 | grep -q "No such" && echo "CLEAN"
```

---

## 6. Running the Benchmark

### Quick Validation (5 Questions)

```bash
cd /home/kingb/benchmark_results
python opencode/runners/opencode_ghost_operator_v2.py 5
```

Watch the agent in real-time:
```bash
tmux attach-session -t ghost_oc
# Ctrl+B, D to detach
```

### Full Track B (199 Questions, ~3 hours)

```bash
# Kill any stale session first
tmux kill-session -t ghost_oc 2>/dev/null

# Run (unbuffered for live log)
/usr/bin/python3 -u /home/kingb/benchmark_results/opencode/runners/opencode_ghost_operator_v2.py > /tmp/oc_trackB.log 2>&1 &

# Monitor progress
tail -f /tmp/oc_trackB.log
grep -c "Answer:" /tmp/oc_trackB.log  # count completed
```

### Judge Results

```bash
python opencode/evaluators/opencode_ghost_judge.py
```

### View Forensic Breakdown

```bash
cat opencode/reports/locomo_v2/INCORRECT_ANSWER_BREAKDOWN.md
```

---

## 7. Rebuilding the LanceDB (if needed)

If the LanceDB needs to be rebuilt with fresh chunking:

```bash
python opencode/build_locomo_lance.py
```

This reads `locomo_v2_final.json`, chunks at speaker boundaries (500-1,500 chars), embeds via nomic-embed-text, and writes to `opencode-locomo/memory_lance/`. Expected output: 565 fragments across 10 conversations.

---

## 8. Known Issues & Pitfalls

| Issue | Symptom | Fix |
|---|---|---|
| Ollama 500 errors | Embedding failures in log | Restart Ollama: `ollama serve` |
| Agent reads raw files | Prediction contains file paths | Delete flight_recorders dir (anti-cheat mandate) |
| Extraction bug | "Let me search..." as prediction | Already fixed in RAG 5.1 — `find_answer_in_parts` skips intermediate prompts |
| Cross-bleed | Answer from previous Q in current capture | `clear-history` runs between questions |
| Primer timeout | "TIMEOUT_ERROR" for primer response | Normal — agent may not respond to primer. Questions still work. |
| LanceDB FTS error | "Cannot perform full text search unless an INVERTED index" | Rebuild LanceDB with `build_locomo_lance.py` |

---

## 9. Expected Results

Based on RAG 5.0 baseline (178/199 = 89.4% with coarse 4,000-char chunks), RAG 5.1 with 565 fine-grained chunks should improve significantly:

| Metric | RAG 5.0 | RAG 5.1 (projected) |
|---|---|---|
| Accuracy | 89.4% | 95-99% |
| Tool errors | 0 | 0 |
| Timeouts | 0 | 0 |

---

## 10. Artifact Map

| Artifact | Path |
|---|---|
| Ghost Operator | `benchmark_results/opencode/runners/opencode_ghost_operator_v2.py` |
| SQLite Judge | `benchmark_results/opencode/evaluators/opencode_ghost_judge.py` |
| LanceDB Builder | `benchmark_results/opencode/build_locomo_lance.py` |
| Predictions (raw) | `benchmark_results/opencode/reports/locomo_v2/track_b/predictions.json` |
| Judged results | `benchmark_results/opencode/reports/locomo_v2/track_b/judged.json` |
| Forensic breakdown | `benchmark_results/opencode/reports/locomo_v2/INCORRECT_ANSWER_BREAKDOWN.md` |
| Dataset (air-gapped) | `benchmark_results/data/locomo_v2/locomo_v2_final.json` |
| Agent workspace | `/home/kingb/opencode-locomo` |
