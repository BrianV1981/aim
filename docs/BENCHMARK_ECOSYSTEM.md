# A.I.M. Benchmark Ecosystem

> Complete map of the LoCoMo V2 benchmark pipeline — from dataset engineering through live agent evaluation.  
> 6 repositories, 3 phases, 1 goal: prove sovereign memory retrieval against adversarial multimodal benchmarks.

---

## Ecosystem Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                     PHASE 1: DATASET ENGINEERING                  │
│                                                                  │
│  locomo-visual-ground-truth          locomo-v2                   │
│  (image rescue + OCR cache)    →    (corrected gold dataset)     │
│                                                                  │
│  Downloads & preserves 775        Applies 156 human corrections  │
│  images, generates LLaVA OCR      from dial481/locomo-audit,     │
│  cache, maps all 1,986 QA pairs   generates 82 replacement QA    │
│  to their image dependencies.     pairs for dead images.         │
│                                                                  │
│                         ↓                                        │
│                   locomo_v2_final.json                            │
│                   (1,986 corrected QA pairs)                      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     PHASE 2: BENCHMARK EXECUTION                  │
│                                                                  │
│  benchmark_results/                    aim-locomo                 │
│  (evaluation hub)                 ←   (agent under test)         │
│                                                                  │
│  Runners inject questions            Gemini CLI agent with       │
│  into the live agent via             full A.I.M. OS (RAG 5,      │
│  tmux Ghost Operator protocol.       LanceDB, Engram DB).        │
│  Evaluators judge answers via        Answers benchmark Qs.       │
│  Gemini Flash LLM-as-a-Judge.                                    │
│                                                                  │
│                         ↓                                        │
│                 Track reports + metrics                           │
│                 (IR scores, judged results)                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     PHASE 3: TRANSITION (In Progress)             │
│                                                                  │
│  aim-opencode                        opencode-locomo             │
│  (fork maintenance)             ←   (OpenCode test harness)      │
│                                                                  │
│  Maintains OpenCode adaptations    Freshly scaffolded project    │
│  of A.I.M. OS. Syncs upstream      for running benchmarks       │
│  RAG updates. Provides             against OpenCode agents.      │
│  scaffold.sh for new projects.      Has coagent-swarm skill.     │
│                                                                  │
│  aim-swarm                                                       │
│  (orchestration extension)                                       │
│                                                                  │
│  Factory scripts for spawning co-agents. Tmux orchestration.     │
│  Blueprint injection. Chalkboard file-based messaging.           │
│  Currently Gemini-locked — needs OpenCode port.                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Repository Details

### 1. `locomo-visual-ground-truth` — Image Rescue & OCR

**Location:** `/home/kingb/locomo-visual-ground-truth`  
**Role:** Phase 1 — source data preservation  
**Status:** Active

**What it does:**
The original LoCoMo dataset embedded 862 image URLs in dialogue turns. By April 2026, 87 of those images were permanently dead (HTTP 404/402). This made 82 benchmark questions mathematically impossible to answer — the ground truth answer depended on seeing images that no longer exist.

This repo solves that by:
- Locally preserving 775 surviving images (Fair Use, downscaled to 1920x1080 JPEG Q90)
- Running LLaVA-7B OCR on all 775 images to extract visual captions as text
- Building `question_image_matrix.csv` — maps every QA pair to its image dependency
- Producing `locomo_verifiable_image.json` (653 questions with live images) and `locomo_dead_image.json` (82 questions with dead images)

**Key outputs:**
| File | Contents |
|---|---|
| `images/` | 775 locally preserved images (MD5-hashed filenames) |
| `llava_7b_cache.json` | LLaVA OCR descriptions for all 775 images |
| `question_image_matrix.csv` | 1,986 QA pairs → image URL → alive/dead/text-only |
| `locomo_pure_text.json` | 1,251 questions with no image dependency |
| `locomo_verifiable_image.json` | 653 questions backed by live images |
| `locomo_dead_image.json` | 82 questions with irrecoverable dead images |
| `alive_urls.json` | 775 surviving image URLs |
| `dead_urls.json` | 87 permanently dead URLs |
| `unused_alive_urls.json` | 377 ambient images with no matching questions |

**Key scripts:**
- `download_images.py` — multithreaded downloader, resumable via existing-file check
- `generate_matrix.py` — forensic tracing of every QA → `dia_id` → turn → `img_url[]`

---

### 2. `locomo-v2` — Gold Standard Dataset

**Location:** `/home/kingb/locomo-v2`  
**Role:** Phase 1 — corrected dataset engine  
**Status:** Active

**What it does:**
Fixes two fatal flaws in the original LoCoMo benchmark:

1. **156 hallucinated answers** — merged from `dial481/locomo-audit`. Original annotators made factual errors (wrong dates, wrong people, wrong story details). These are corrected in `locomo_v2_base.json`.

2. **82 dead-image questions** — replaced with fresh QA pairs generated from 377 unused ambient images. New questions are generated by Gemini Flash using the LLaVA OCR descriptions and conversation context.

**Key outputs:**
| File | Contents |
|---|---|
| `locomo10.json` | Original V1 (for diff comparison) |
| `locomo_v2_base.json` | V1 + 156 text corrections |
| `locomo_v2_final.json` | Ultimate gold standard — V2 base + 82 visual replacements |
| `errors.json` | Raw corrections from locomo-audit |
| `replacement_manifest.json` | Maps 82 dead questions → replacement images |

**Key scripts:**
- `apply_corrections.py` — injects 156 text/logic fixes into locomo10.json
- `map_replacements.py` — assigns dead questions to random unused images
- `generate_replacement_questions.py` — uses Gemini Flash to generate 82 new QA pairs
- `prep_batch.py` — assembles batch prompts for LLM question generation

---

### 3. `benchmark_results` — Evaluation Hub

**Location:** `/home/kingb/benchmark_results`  
**Role:** Phase 2 — execution + evaluation  
**Status:** Active (air-gapped)

**What it does:**
The physically isolated evaluation hub. Physically separated from the agent's workspace to prevent the agent from `grep`-ing the answer keys (a benchmark-nullifying incident documented in `CHEATING_AUDIT.md`).

Contains three subsystems:

**Runners** — execute benchmarks against live agents:
| File | What it runs |
|---|---|
| `locomo_ghost_operator.py` | V1: injects questions via tmux into aim-locomo |
| `locomo_ghost_operator_v2.py` | V2: air-gapped, reads from benchmark_results/data/, timeout at 120s |
| `ghost_operator.py` | V1 alt: triggers `/reincarnate` between chunks |
| `aim_rag_v5_orchestrator.py` | Periodic ping injector — sends mandate reminders |

**Evaluators** — judge agent answers:
| File | Method |
|---|---|
| `ghost_judge.py` | Tmux-based live Gemini judge — YES/NO per question |
| `locomo_eval_gemini_judge.py` | API-based batch judge — 5 questions at a time |
| `eval_longmemeval_v2.py` | LongMemEval IR metric calculator (R@5, R@10, NDCG) |

**Reports** — organized by benchmark and track:
```
reports/
├── locomo_v2/
│   ├── MEMPALACE_DECEPTION_DOSSIER.md    # Forensic audit of MemPalace's 100% claim
│   ├── 20260503_124556_locomo_ir_metrics.txt
│   ├── track_a/                           # 7 IR retrieval result files
│   └── track_b/                           # 23 Track B files (predictions, judged, audits)
└── longmemeval/
    └── 20260503_124556_longmemeval_ir_metrics.txt
```

**The Ghost Operator Protocol:**
All runners follow the same pattern:
1. Spawn agent in detached tmux session (`tmux new-session -d -s ghost_aim`)
2. Inject primer message (benchmark mandate + answer format rules)
3. Loop: inject question → wait (30-120s) → capture pane → parse `[ANSWER]`
4. On failure: retry up to 3 times, skip on tool leaks
5. Cleanup: kill session, aggregate results

---

### 4. `aim-locomo` — Gemini CLI Agent Under Test

**Location:** `/home/kingb/aim-locomo`  
**Role:** Phase 2 — the agent being benchmarked  
**Status:** Active (Gemini CLI)

**What it does:**
A fully scaffolded A.I.M. OS instance running the Gemini CLI agent. This is the "brain" being tested by `benchmark_results`. When the Ghost Operator injects a question, this agent:
1. Searches its LanceDB + Engram DB for relevant memories
2. Reasons about the answer using RAG 5 (Tantivy strict inclusion + EntityIntersection + FlashRank)
3. Responds with `[ANSWER]` tags that the runner parses

**Key configuration:**
- Embedding: `nomic-embed-text` via Ollama (127.0.0.1:11434)
- Reasoning: `qwen3.5:4b` via Ollama (local) or Gemini Flash (cloud)
- Context window: 32,768 tokens
- Federated databases: `project_core.db`, `global_skills.db`, `datajack_library.db`, `subagent_ephemeral.db`

**Relationship to benchmark_results:**
The Ghost Operator scripts point at `/home/kingb/aim-locomo` as the agent's working directory. Responses are read from `~/.gemini/tmp/aim-locomo/chats/*.jsonl`.

---

### 5. `aim-swarm` — Orchestration Extension

**Location:** `/home/kingb/aim-swarm`  
**Role:** Utility — co-agent spawning and coordination  
**Status:** Gemini-locked, needs OpenCode port

**What it does:**
A standalone orchestration layer for spawning and managing multiple A.I.M. agents simultaneously. Provides:

| Component | Purpose |
|---|---|
| `swarm/aim_spawn.py` | Factory: clones A.I.M. OS → injects role blueprint → sets up chalkboard |
| `swarm/aim_swarm.py` | Synchronous tmux grid orchestrator (functional) |
| `swarm/aim_team.py` | SWARM_MANIFEST-based orchestrator (broken — 6 defects) |
| `agents/python-developer/` | Example blueprint: AGENTS.md + TOOLS.md + manifest.json |
| `docs/TMUX_AIM_SWARM.md` | 476-line protocol reference (the source for SWARM_PROTOCOL.md) |

**Known issues (from SWARM_AUDIT_2026-05-01.md):**
- 20 defects total, 6 critical in `aim_team.py`
- `find_aim_root()` clones aim-swarm itself instead of the A.I.M. engine
- Hardcoded `gemini` binary — not platform-neutral
- No `--yolo` flag — agents block on approval prompts
- `BTab` key may be Gemini-specific

---

### 6. `aim-opencode` / `opencode-locomo` — OpenCode Transition

**aim-opencode:** `/home/kingb/aim-opencode`  
**Role:** Fork maintenance — `d3c12yp7012/aim-opencode` on GitHub  
**Status:** Active — RAG 5 merged, coagent-swarm skill deployed

**opencode-locomo:** `/home/kingb/opencode-locomo`  
**Role:** Phase 3 — OpenCode test harness  
**Status:** Scaffolded, ready for benchmark testing

**What they do:**
The Gemini → OpenCode transition. `aim-opencode` is the fork that maintains OpenCode adaptations (DeepSeek defaults, TypeScript plugins, `opencode run` subshells) on top of the upstream A.I.M. engine. `opencode-locomo` is a scaffolded project instance ready to replace `aim-locomo` as the agent under test.

**Key differences from aim-locomo:**

| Feature | aim-locomo (Gemini) | opencode-locomo (OpenCode) |
|---|---|---|
| Agent binary | `gemini --yolo` | `opencode` (TUI mode) |
| Session format | Gemini JSONL | OpenCode export JSON |
| Default model | qwen3.5:4b / Gemini Flash | deepseek-chat (DeepSeek V4) |
| Search engine | RAG 4.2 (SQLite) | RAG 5 (LanceDB + Tantivy) |
| Co-agent protocol | `aim-swarm` (Gemini-locked) | `coagent-swarm` skill (OpenCode-native) |
| Fork updates | Manual git merge | `aim update fork --dry-run` |

---

## Benchmark Tracks

The benchmark evaluates A.I.M. across two dimensions:

### Track A — Information Retrieval (IR)
- **What:** Raw retrieval engine accuracy — no LLM reasoning, just search
- **Metrics:** R@5, R@10, NDCG — "did the search return the right document?"
- **Runner:** `benchmark_results/evaluators/eval_longmemeval_v2.py`
- **Status:** Baseline 45.6% R@10 on LongMemEval with pure LanceDB vectors

### Track B — Sovereign Agent (Live)
- **What:** Full agent pipeline — search + reasoning + answering
- **Metrics:** LLM-as-a-Judge YES/NO per question, accuracy %
- **Runner:** `benchmark_results/runners/locomo_ghost_operator_v2.py`
- **Evaluator:** `benchmark_results/evaluators/ghost_judge.py`
- **Status:** Active testing against aim-locomo (Gemini agent)

---

## Data Flow

```
locomo-visual-ground-truth/
    │
    ├── locomo_dead_image.json ──────┐
    ├── unused_alive_urls.json ──────┤
    └── llava_7b_cache.json ─────────┤
                                     ▼
                              locomo-v2/
                                  │
                                  │ locomo_v2_final.json
                                  ▼
                          benchmark_results/
                           data/locomo_v2/
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
              Track A (IR)               Track B (Agent)
         eval_longmemeval_v2.py    locomo_ghost_operator_v2.py
                    │                           │
                    │                    ┌──────┴──────┐
                    │                    ▼              ▼
                    │              aim-locomo    opencode-locomo
                    │            (Gemini agent)  (OpenCode agent)
                    │                    │
                    │                    ▼
                    │           ghost_judge.py
                    │         (LLM-as-a-Judge)
                    │                    │
                    └────────────────────┤
                                        ▼
                              reports/locomo_v2/
                              reports/longmemeval/
```

---

## Running a Full Benchmark (Track B)

```bash
# 1. Ensure the dataset is current
cp /home/kingb/locomo-v2/locomo_v2_final.json \
   /home/kingb/benchmark_results/data/locomo_v2/

# 2. Ensure the agent workspace is ready
cd /home/kingb/aim-locomo
# Verify LanceDB is migrated
python -c "from aim_core.lance_backend import VectorBackend; VectorBackend().migrate_from_sqlite()"

# 3. Run the Ghost Operator (from benchmark_results)
cd /home/kingb/benchmark_results
python runners/locomo_ghost_operator_v2.py

# 4. Judge the results
python evaluators/ghost_judge.py

# 5. View reports
ls reports/locomo_v2/track_b/
cat reports/locomo_v2/track_b/*Forensic*.md
```

## Key Performance Numbers

| Metric | Score | Context |
|---|---|---|
| LoCoMo V2 R@5 (IR only) | 100% | LanceDB hybrid search — top k matches all 32 conversations |
| LongMemEval R@10 (IR only) | 45.6% | Pure LanceDB vectors, no FlashRank reranking |
| LongMemEval target | 90+% | With FlashRank + LLM-as-a-Judge + Parent-Child expansion |
| MemPalace claim (debunked) | 100% R@5 | top-k=50 exploit (returns entire dataset) + Claude Sonnet |

## The Air Gap

**Critical:** The `benchmark_results/` directory is physically separated from the agent workspace (`aim-locomo/` or `opencode-locomo/`) to prevent the agent from reading answer keys. On May 4, 2026, an incident occurred where the agent `grep`'d raw dataset files 434 times from a polluted workspace, bypassing the RAG pipeline entirely. This is why `locomo_ghost_operator_v2.py` reads data from `benchmark_results/data/` (outside the agent's reach) rather than from within the agent's project directory.

## Current State & Next Steps

| Component | Status | Next Action |
|---|---|---|
| Dataset (locomo-v2) | Gold standard ready | None — 1,986 corrected QA pairs |
| Gemini agent (aim-locomo) | Benchmarked | Phase out, replace with OpenCode |
| OpenCode agent (opencode-locomo) | Scaffolded | Port Ghost Operator to OpenCode |
| IR evaluation | Running | Activate FlashRank → target 90%+ |
| LLM judge | Running | Replace exact_match with semantic judge |
| Swarm orchestration | Gemini-locked | Port aim_swarm.py to OpenCode |
| Fork maintenance | RAG 5 merged | `aim update fork --dry-run` for future syncs |

---

## Appendix: File Size Reference

| File | Size | Contents |
|---|---|---|
| `locomo10.json` | ~35 MB | Original 10-conversation dataset |
| `locomo_v2_final.json` | ~38 MB | Corrected gold standard |
| `llava_7b_cache.json` | ~2 MB | OCR descriptions for 775 images |
| `aim_os.engram` | ~3 MB | A.I.M. foundation cartridge (733 fragments) |
| `project_core.db` | Varies | Agent's indexed memory (SQLite) |
| `memory_lance/` | Varies | Agent's vector store (LanceDB) |
