# A.I.M. OpenCode — Project Wiki

> **Fork:** [d3c12yp7012/aim-opencode](https://github.com/d3c12yp7012/aim-opencode)  
> **Upstream:** [BrianV1981/aim](https://github.com/BrianV1981/aim)  
> **Branch:** `opencode` (main tracks upstream, opencode carries fork deltas)

## What is aim-opencode?

A.I.M. OpenCode is a fork of the A.I.M. (Actual Intelligent Memory) sovereign agent OS, ported from the Gemini CLI substrate to the OpenCode CLI ecosystem. It preserves all upstream architecture (RAG 4.0 LanceDB search, sovereign sync, GitOps discipline) while adapting to the OpenCode runtime: TypeScript plugin hooks, DeepSeek models, and `opencode run` subshell invocation.

## Quick Links

| Page | Topic |
|---|---|
| [Architecture](architecture.md) | Fork structure, branch strategy, conflict zones |
| [Setup & Installation](setup.md) | First-time setup, dependencies, configuration |
| [OpenCode Integration](opencode-integration.md) | Gemini → OpenCode migration: skills, plugins, agents |
| [Updating the Fork](updating.md) | `aim update fork` — syncing with upstream safely |
| [GitOps Discipline](gitops.md) | Branch strategy, surgical staging, worktree hygiene |
| [Testing](testing.md) | TDD approach, test categories, running the suite |
| [RAG & Search](rag-search.md) | LanceDB hybrid search, Tantivy FTS, EntityIntersection |
| [Transition Roadmap](aim-opencode-transition.md) | Full migration plan (Phases 1–7) |

## Key Differences from Upstream

| Area | Upstream (aim) | OpenCode Fork |
|---|---|---|
| **CLI Shell** | `gemini --yolo` | `opencode run` |
| **Default Model** | gemini-2.5-flash | deepseek-chat (DeepSeek V4) |
| **Hook System** | Gemini JSON hooks | TypeScript `.opencode/plugins/` |
| **Skills** | `.gemini/skills/` | `.opencode/skills/` |
| **Session Format** | Gemini JSONL | OpenCode export JSON |
| **Config File** | `.gemini/settings.json` | `opencode.json` |
| **Init Command** | `aim init` (Gemini hooks) | `aim init` (OpenCode plugins) |
| **Update** | `aim update engine` | `aim update fork` (dual-branch) |
| **Wiki Processing** | Memory-wiki daemon (`gemini`) | OpenCode TUI co-agent (`opencode`) |

## Conflict Zones

These files are modified in both repos and require manual resolution during upstream merges:

| File | OpenCode Delta | Upstream Delta |
|---|---|---|
| `aim_core/extract_signal.py` | OpenCode JSON format detection | RAG chunking improvements |
| `aim_core/reasoning_utils.py` | DeepSeek defaults | Provider routing changes |
| `aim_core/aim_cli.py` | OpenCode plugins, fork update | CLI command additions |
| `aim_core/handoff_pulse_generator.py` | Session source priority | Flight recorder pipeline |
| `aim_core/wiki_tools.py` | `opencode` tmux spawn | Session naming changes |

## Current State

- **LanceDB RAG 4.2:** Fully merged from upstream (#522) — hybrid vector+FTS search with Tantivy, EntityIntersection reranker, FlashRank cross-encoder
- **Coreference Rewriter:** RAG 4.2 query rewriting for conversational follow-ups (#508)
- **Fork Updater:** `aim update fork [--dry-run]` automates upstream sync pipeline (#532)
- **Tests:** 143+ tests passing, TDD-enforced fork integrity
