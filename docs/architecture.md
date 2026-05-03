# Architecture

## Fork Structure

```
BrianV1981/aim (upstream)
        │
        ▼
d3c12yp7012/aim-opencode (origin)
   ├── main          ← Clean upstream mirror, never modified directly
   └── opencode      ← Active development branch, carries all fork deltas
```

**Rule:** Never commit to `main`. All work happens on `opencode` or feature branches merged into `opencode`.

## Branch Strategy

| Branch | Purpose | Tracks |
|---|---|---|
| `main` | Upstream mirror | `upstream/main` via `git pull upstream main` |
| `opencode` | Active development | Fork-specific code, all features and fixes |
| `fix/issue-<id>` | Isolated worktrees | Created by `aim fix <id>`, merged into `opencode` |

## Git Remotes

```bash
origin    → https://github.com/d3c12yp7012/aim-opencode.git
upstream  → https://github.com/BrianV1981/aim.git
```

## File Categories

### Fork-Specific (Added — upstream doesn't have these)

| Directory/File | Purpose |
|---|---|
| `.opencode/` | Agents (python-specialist, technical-auditor), skills (5 ported), plugins (aim-hooks.ts) |
| `aim_core/session_bridge.py` | OpenCode session export pipeline (`opencode export`) |
| `aim_core/aim_opencode_update.py` | Fork updater (`aim update fork`) |
| `docs/aim-opencode-transition.md` | Full migration roadmap |
| `tests/test_session_bridge.py`, `test_extract_open_code.py`, `test_aim_hooks_plugin.py`, `test_opencode_update.py`, `test_lance_merge_integration.py` | Fork-specific TDD tests |

### Conflict Zones (modified in both repos)

These require manual resolution during upstream merges. See [Updating the Fork](updating.md).

| File | OpenCode Change | Upstream Risk |
|---|---|---|
| `extract_signal.py` | OpenCode JSON format auto-detection + `"assistant"` → `"AGENT"` role mapping | High — upstream may add RAG chunking |
| `reasoning_utils.py` | Emergency fallback: `deepseek-chat` instead of `gemini-2.5-flash` | Medium — provider routing changes |
| `aim_cli.py` | `ensure_opencode_plugins()`, `cmd_update(target="fork")` | Medium — new CLI subcommands |
| `handoff_pulse_generator.py` | `resolve_session_sources()` priority: OpenCode → Gemini | Low — flight recorder changes |
| `wiki_tools.py` | `opencode` TUI spawn instead of `gemini --yolo` | Low — session naming |

### Cross-Platform (pure upstream — safe merge)

| File | Description |
|---|---|
| `lance_backend.py` | LanceDB vector backend with Tantivy FTS + EntityIntersection |
| `retriever.py` | Hybrid search: LanceDB → FlashRank → Knowledge weighting → Temporal decay |
| `forensic_utils.py` | RAG 4.0 summarizer, embedding pipeline |
| `coreference_rewriter.py` | RAG 4.2 pronoun → entity query rewriting |

## Memory Wiki vs Project Wiki

| | `memory-wiki/` | `docs/` (Project Wiki) |
|---|---|---|
| **Who edits** | Subconscious Daemon (wiki agent) | Humans + agents |
| **Content** | Session discoveries, concept pages, activity log | Architecture docs, setup guides, API reference |
| **Format** | Processed from `_ingest/` | Hand-written Markdown |
| **Git** | Gitignored (local only) | Tracked in repo |

## Directory Map

```
aim-opencode/
├── aim_core/          # Core engine (shared with upstream, fork-modified)
├── .opencode/         # OpenCode runtime config (fork-only)
│   ├── agents/        # Agent definitions (DeepSeek models)
│   ├── plugins/       # TypeScript hooks (aim-hooks.ts)
│   └── skills/        # Ported Gemini skills
├── docs/              # Project Wiki (this directory)
├── memory-wiki/       # Daemon-processed long-term memory
├── tests/             # TDD test suite
├── benchmarks/        # Benchmark data and runners
├── hooks/             # Pre/post-execution hooks
├── archive/           # Federated databases (SQLite + LanceDB)
├── continuity/        # Session handoff artifacts
└── workspace/         # Git worktrees (gitignored)
```
