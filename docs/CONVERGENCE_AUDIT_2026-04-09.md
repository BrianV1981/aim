# A.I.M. Cross-Team Convergence Audit

**Date:** 2026-04-09
**Author:** aim-claude team (on behalf of the Operator)
**Audience:** aim (Gemini) team
**Purpose:** Both repos must converge on identical file names, folder structures, CLI commands, and architectural patterns. This document identifies every divergence and recommends which implementation should become the standard.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Critical Structural Finding](#2-critical-structural-finding)
3. [Feature-by-Feature Deep Dive](#3-feature-by-feature-deep-dive)
   - 3.1 [Issue/Forum Ingestion](#31-issueforum-ingestion)
   - 3.2 [Recall / Deep Search](#32-recall--deep-search)
   - 3.3 [Audit / Strategic Synthesis / Morning Reports](#33-audit--strategic-synthesis--morning-reports)
   - 3.4 [Dashboard](#34-dashboard)
   - 3.5 [Swarm Engrams + Swarm Publish](#35-swarm-engrams--swarm-publish)
   - 3.6 [DataJack Plugin Extensions](#36-datajack-plugin-extensions)
   - 3.7 [MCP Server](#37-mcp-server)
4. [Features in aim Only](#4-features-in-aim-only--not-yet-in-aim-claude)
5. [Features in aim-claude Only](#5-features-in-aim-claude-only--not-yet-in-aim)
6. [CLI Command Divergences](#6-cli-command-divergences)
7. [Config & Infrastructure Divergences](#7-config--infrastructure-divergences)
8. [Test Structure Divergences](#8-test-structure-divergences)
9. [Architectural Principles Going Forward](#9-architectural-principles-going-forward)
10. [Recommended Convergence Plan](#10-recommended-convergence-plan)
11. [Appendix: Full File Inventory Comparison](#11-appendix-full-file-inventory-comparison)

---

## 1. Executive Summary

The aim and aim-claude repos have been independently implementing features for the same platform. While aim is the north star, aim-claude has in several cases produced architecturally superior implementations. The Operator has mandated that both repos converge to **identical file names, folder structures, CLI commands, and scaffolding**, with only minimal platform-specific differences (e.g., `GEMINI.md` vs `CLAUDE.md`).

This audit found:

- **7 features** where both repos implemented the same concept but diverged on naming, location, or architecture
- **10 features** that exist in aim only
- **6 features** that exist in aim-claude only
- **Systemic architectural divergence**: aim tends toward LLM-coupled monolithic functions; aim-claude consistently chose pure-function, zero-LLM-dependency patterns

**The core recommendation:** Both repos should adopt aim-claude's pure-function architecture as the internal pattern, while using aim's existing CLI command names and file locations as the naming standard. Where aim-claude is ahead (6 features aim doesn't have yet), aim should adopt aim-claude's implementations directly.

---

## 2. Critical Structural Finding

**`aim-claude/src/` is no longer a symlink to `aim/src/`.**

The symlink was broken during the aim-claude decoupling effort (aim-claude issue #86). Both repos now have **fully independent `src/` directories**. This means:

- Files in `aim/src/` and `aim-claude/src/` can drift without anyone noticing
- Shared modules (like `config_utils.py`, `retriever.py`, `mcp_server.py`) may already be out of sync
- Any assumption that "changing `aim/src/` automatically updates aim-claude" is **false**

**Action required:** After convergence, establish a mechanism to detect drift between the two `src/` directories.

---

## 3. Feature-by-Feature Deep Dive

### 3.1 Issue/Forum Ingestion

#### What it does
Scrapes resolved GitHub issues (and optionally StackOverflow threads) and ingests them into the knowledge pipeline.

#### aim implementation: `scripts/aim_scraper.py`

- **186 lines**, standalone CLI script with `argparse` entrypoint
- Supports two sources: **GitHub issues** (via `gh` CLI subprocess) and **StackOverflow** (via REST API with `requests`)
- Fetches closed issues, filters by `stateReason == "COMPLETED"`
- Fetches comments for each issue
- Formats as Markdown files: `issue_42.md`, `so_12345.md`
- Writes output to `synapse/` directory
- CLI command: `aim scrape --source github|stackoverflow --repo X --query Y --limit N --outdir DIR`
- Test file: `tests/test_aim_scraper.py` (4 tests — HTML cleaning, SO fetch success/failure, GH fetch)

**Strengths:**
- Full CLI integration — operator can run it immediately
- StackOverflow support is real value (no other source for this)
- Writes human-readable Markdown files

**Weaknesses:**
- **Monolithic functions**: `format_issue_as_markdown()` does file reads, hash comparison, AND file writes in one function
- **No content hashing**: No way to detect or prevent duplicate ingestion when re-scraping the same repo
- **No fragment typing**: Output is raw Markdown files, not typed fragments for the RAG pipeline
- **No connection to the DataJack pipeline**: The scraper dumps files and stops. There's no guidance or automation to bake them into `.engram` cartridges
- **Tight I/O coupling**: Every function has side effects (file writes, subprocess calls), making them hard to test without mocks

#### aim-claude implementation: `src/issue_ingestion.py`

- **47 lines**, pure library module (no CLI, no I/O)
- Two functions:
  - `parse_github_issue(issue)` — takes a GitHub issue JSON dict, returns a list of engram-compatible fragment dicts
  - `deduplicate_against_existing(fragments, existing_hashes)` — filters out fragments whose SHA-256 content hash already exists
- Each fragment includes: `content`, `type` ("community_knowledge"), `source` ("github#42"), `content_hash`
- Does NOT support StackOverflow
- Not wired into the CLI at all
- Test file: `tests/unit/test_issue_ingestion.py` (10 tests — parse, dedup, edge cases)

**Strengths:**
- **Pure functions**: Zero I/O, zero subprocess calls, zero side effects
- **Content hashing**: SHA-256 dedup prevents re-ingesting known content
- **Fragment typing**: Output is `community_knowledge` typed, ready for Engram DB
- **Trivially testable**: No mocks needed — data in, data out
- **Composable**: Caller decides what to do with the fragments (write to disk, insert to DB, bake into .engram)

**Weaknesses:**
- No StackOverflow support
- No CLI integration — it's a library that nothing calls
- Too small to be useful on its own without an orchestration layer

#### Verdict

| Criteria | aim | aim-claude | Winner |
|----------|-----|------------|--------|
| Code quality | Monolithic, I/O-coupled | Pure functions, composable | **aim-claude** |
| Testability | Requires mocks for subprocess + file I/O | Zero mocks needed | **aim-claude** |
| Feature completeness | GitHub + StackOverflow + CLI | GitHub only, no CLI | **aim** |
| Pipeline integration | None (dumps files, stops) | Content-hashed typed fragments | **aim-claude** |
| Extensibility | Adding sources means duplicating I/O logic | Adding sources means new `parse_X()` function | **aim-claude** |

**Recommendation:** Adopt aim-claude's pure-function architecture as the core parsing layer. Wrap it with aim's CLI interface and add StackOverflow support as a new `parse_stackoverflow_thread()` function. The final file should be `scripts/aim_scraper.py` (aim's name) with aim-claude's internal architecture.

**Agreed file names:**

| Component | File | Location |
|-----------|------|----------|
| Scraper script | `aim_scraper.py` | `scripts/` |
| CLI command | `aim scrape` | Wired in `aim_cli.py` |
| Output directory | `synapse/` | Project root |
| Tests | `test_aim_scraper.py` | `tests/` |

---

### 3.2 Recall / Deep Search

#### What it does
Searches across multiple knowledge sources to answer operator queries about past sessions, decisions, or context.

#### aim implementation: `src/recall_tools.py`

- **69 lines**
- Searches ONE source: `archive/history.db` FTS5 table
- After finding matching sessions, constructs a prompt and calls `generate_reasoning()` — **an LLM call** — to synthesize the results into a narrative
- Returns the LLM's synthesis string, not the raw data
- CLI command: `aim recall --query "X" --limit N`
- Test file: `tests/test_recall_tools.py`

**Strengths:**
- FTS5 full-text search against the Engram DB is powerful
- LLM synthesis produces a polished, readable answer

**Weaknesses:**
- **Mandatory LLM dependency**: Every recall burns tokens, adds latency, introduces non-determinism. You cannot get raw results without paying the LLM tax.
- **Single source**: Only searches history.db. Ignores continuity files, git history, and engram cartridges.
- **Untestable without mocking the LLM**: The core function is inseparable from the LLM call.
- **Global state**: Uses `get_base_dir()` for path resolution instead of explicit parameters.

#### aim-claude implementation: `src/panopticon_recall.py`

- **67 lines**
- Searches TWO sources:
  1. `continuity/` Markdown files (substring match)
  2. Git commit history (`git log --grep`)
- Returns a flat list of `{content, source}` dicts — raw structured data
- Zero LLM calls
- `unified_recall(query, aim_root)` merges both sources
- Not wired into CLI
- Test file: `tests/unit/test_panopticon_recall.py`

**Strengths:**
- **Zero LLM dependency**: Instant, free, deterministic
- **Multiple sources**: Continuity files + git history gives broader surface
- **Returns raw data**: Caller decides whether to display raw or synthesize with LLM
- **Explicit parameters**: `aim_root` passed in, no global state
- **Trivially testable**: Pure functions, no mocks needed

**Weaknesses:**
- Does NOT search the Engram DB (FTS5). This is a significant gap.
- No CLI integration.
- Substring matching on continuity files is crude compared to FTS5.

#### Verdict

| Criteria | aim | aim-claude | Winner |
|----------|-----|------------|--------|
| Search breadth | Engram DB only | Continuity + git history | **aim-claude** |
| Search depth | FTS5 full-text (excellent) | Substring match (basic) | **aim** |
| LLM dependency | Required (every call) | None | **aim-claude** |
| Determinism | Non-deterministic | Deterministic | **aim-claude** |
| Testability | Requires LLM mock | Zero mocks | **aim-claude** |
| Composability | Returns synthesized string only | Returns raw data | **aim-claude** |
| Cost per query | LLM tokens + latency | Free, instant | **aim-claude** |

**Recommendation:** Adopt aim-claude's architecture (pure functions, raw data output, zero LLM dependency). Extend it to include aim's FTS5 Engram DB search as a **third source** in `unified_recall()`. LLM synthesis should be an **optional `--synthesize` flag** on the CLI command, never the default.

**Agreed file names:**

| Component | File | Location |
|-----------|------|----------|
| Recall module | `recall_tools.py` | `src/` |
| CLI command | `aim recall` | Wired in `aim_cli.py` |
| Tests | `test_recall_tools.py` | `tests/` |

Note: aim-claude's file is currently named `panopticon_recall.py`. It will be renamed to `recall_tools.py` to match aim.

---

### 3.3 Audit / Strategic Synthesis / Morning Reports

#### What it does
Generates periodic operator briefings — a "state of the project" summary.

#### aim implementation: `src/audit_tools.py`

- **61 lines**
- Reads the last N sessions from `archive/history.db`
- Constructs a prompt and calls `generate_reasoning()` — **an LLM call**
- Writes the result to `WEEKLY_SITREP.md`
- One monolithic function: DB read → prompt construction → LLM call → file write
- CLI command: `aim audit --sessions N`
- Test file: `tests/test_audit_tools.py`

**Strengths:**
- LLM-synthesized narrative can provide genuine strategic insight
- Integrated into CLI

**Weaknesses:**
- **Mandatory LLM dependency**: Cannot generate a report without burning tokens
- **Monolithic function**: DB read, prompt construction, LLM call, and file write are all in one function — untestable without mocking everything
- **Single data source**: Only reads historical sessions from history.db
- **Expensive**: Running this daily burns significant tokens for potentially low-value output

#### aim-claude implementation: `src/morning_report.py`

- **85 lines**
- Two clean functions:
  1. `gather_report_data(aim_root)` — collects project state from multiple live sources: `git log`, unread mail count, open issue count, continuity file status → returns a structured dict
  2. `format_report(data)` — renders the dict into human-readable Markdown
- Zero LLM calls
- Not wired into CLI
- Test file: `tests/unit/test_morning_report.py`

**Strengths:**
- **Zero LLM dependency**: Instant, free, deterministic
- **Multiple data sources**: Git log + mail + issues + continuity (much broader than aim's DB-only approach)
- **Clean separation**: Gather vs. format are independent functions. Adding a new data source is one line in `gather_report_data()`.
- **Trivially testable**: Both functions are pure transforms

**Weaknesses:**
- No CLI integration
- Output is a factual dashboard, not a strategic narrative (which may be a feature, not a bug)

#### Verdict

| Criteria | aim | aim-claude | Winner |
|----------|-----|------------|--------|
| Data sources | history.db only | Git + mail + issues + continuity | **aim-claude** |
| LLM dependency | Required | None | **aim-claude** |
| Cost per run | LLM tokens | Free | **aim-claude** |
| Separation of concerns | Monolith | Gather/format split | **aim-claude** |
| Testability | Requires DB + LLM mocks | Zero mocks | **aim-claude** |
| Extensibility | Restructure entire prompt to add data | Add one line to gather function | **aim-claude** |
| Output quality | Rich narrative (when LLM is good) | Structured factual summary | Depends on use case |

**Recommendation:** Adopt aim-claude's architecture as the default. If LLM synthesis is desired, add an optional `--synthesize` flag that takes the structured data from `gather_report_data()` as input to the LLM — never as the only path.

**Agreed file names:**

| Component | File | Location |
|-----------|------|----------|
| Report module | `audit_tools.py` | `src/` |
| CLI command | `aim audit` | Wired in `aim_cli.py` |
| Tests | `test_audit_tools.py` | `tests/` |

Note: aim-claude's file is currently named `morning_report.py`. It will be renamed to `audit_tools.py` to match aim.

---

### 3.4 Dashboard

#### What it does
Provides a quick terminal-based overview of the A.I.M. workspace health and status.

#### aim implementation
**Does not exist.** Issue #119 ("The Sovereignty Dashboard") is OPEN.

#### aim-claude implementation: `src/dashboard.py`

- **78 lines**
- Two functions:
  1. `gather_dashboard_data(aim_root)` — collects metrics: engram DB count/size, continuity file count, unread mail count, git summary (last commit hash + message) → returns a dict
  2. `format_dashboard(data)` — renders a terminal-friendly ASCII box display
- Zero LLM calls, deterministic, instant
- Not wired into CLI
- Test file: `tests/unit/test_dashboard.py` (covers all key paths including missing directories and zero-state)

**Strengths:**
- Clean gather/format separation
- Easy to extend with new metrics
- Well-tested
- Could support alternative renderers (JSON, HTML) via the data dict

#### Verdict

aim-claude's implementation should be adopted as-is. It fills aim issue #119 directly.

**Agreed file names:**

| Component | File | Location |
|-----------|------|----------|
| Dashboard module | `dashboard.py` | `src/` |
| CLI command | `aim dashboard` | Wired in `aim_cli.py` |
| Tests | `test_dashboard.py` | `tests/` |

---

### 3.5 Swarm Engrams + Swarm Publish

#### What it does
Enables agents to contribute knowledge fragments to a shared pool and publish `.engram` cartridges to a registry for other agents to consume.

#### aim implementation
**Does not exist.** Issues #116 ("Swarm-Synthesized Live Engrams") and #121 ("Sovereign Swarm 2.0 — aim publish") are OPEN.

#### aim-claude implementation

**`src/swarm_engrams.py`** (47 lines):
- `create_fragment_contribution(content, source, agent_id)` — creates a contribution dict with SHA-256 content hash
- `deduplicate_fragments(fragments)` — removes duplicates by content hash
- `score_fragment_trust(fragment, known_agents)` — returns a trust score based on agent identity (placeholder logic — dict lookup with default)
- `merge_contributions(existing, incoming)` — deduplicates incoming fragments against existing ones

**`src/swarm_publish.py`** (58 lines):
- `publish_cartridge(cartridge_path, registry_dir)` — validates a `.engram` file using `cartridge_utils.validate_cartridge()`, then copies it to the registry directory
- `list_published(registry_dir)` — enumerates published cartridges with metadata (name, size, modified time)

Both modules are pure functions with minimal I/O. Well-tested.

**Trust scoring assessment:** The current model is a simple dict lookup — `known_agents.get(agent_id, 0.5)`. This is appropriate as a v1 interface. It gives the correct function signature to extend later with real reputation tracking, trust decay, or verification.

**Content-hash dedup assessment:** Solid. SHA-256 on content means identical knowledge from different agents is correctly deduplicated regardless of origin.

#### Verdict

aim-claude's implementation should be adopted as-is. It directly fills aim issues #116 and #121.

**Agreed file names:**

| Component | File | Location |
|-----------|------|----------|
| Fragment exchange | `swarm_engrams.py` | `src/` |
| Cartridge publisher | `swarm_publish.py` | `src/` |
| Tests | `test_swarm_engrams.py`, `test_swarm_publish.py` | `tests/` |

---

### 3.6 DataJack Plugin Extensions

#### What it does
Adds cartridge discovery/validation utilities and a freshness tracker for detecting stale engram sources.

#### aim implementation
**Does not exist.** aim's DataJack plugin directory (`src/plugins/datajack/`) has `aim_bake.py`, `aim_exchange.py`, `forensic_utils.py`, and `quarantine_daemon.py` — but no cartridge validation or freshness tracking.

#### aim-claude implementation

**`src/plugins/datajack/cartridge_utils.py`** (86 lines):
- `list_cartridges(engrams_dir)` — discovers all `.engram` files in a directory
- `validate_cartridge(path)` — checks that a `.engram` file is a valid SQLite database with the required tables
- `get_cartridge_info(path)` — returns metadata dict (name, size, table count, fragment count)
- `generate_manifest(path)` — creates a v2.0.0 manifest dict
- `validate_manifest(manifest)` — checks required fields are present
- `check_embedding_compatibility(manifest, target_model)` — forward-looking function that prevents loading incompatible cartridges
- Module constants: `CARTRIDGE_SCHEMA_VERSION = "2.0.0"`, `MANIFEST_REQUIRED_FIELDS`

**`src/plugins/datajack/freshness_tracker.py`** (53 lines):
- `hash_source_files(directory)` — walks a directory tree, SHA-256 hashes all text files, returns `{path: hash}` dict
- `detect_stale_files(current_hashes, stored_hashes)` — diffs two hash dicts, returns `{modified: [...], added: [...], deleted: [...]}`

Both modules are pure logic. `freshness_tracker` does file reads but no writes. Tests are comprehensive — freshness tracker tests cover all four states (unchanged, modified, added, deleted, mixed). Cartridge utils tests cover valid, invalid, corrupt, and missing cartridges.

#### Verdict

Both modules should be adopted as-is. They fill genuine gaps in the DataJack ecosystem.

**Agreed file names:**

| Component | File | Location |
|-----------|------|----------|
| Cartridge utilities | `cartridge_utils.py` | `src/plugins/datajack/` |
| Freshness tracker | `freshness_tracker.py` | `src/plugins/datajack/` |
| Tests | `test_cartridge_discovery.py`, `test_cartridge_manifests.py`, `test_freshness_tracker.py` | `tests/` |

---

### 3.7 MCP Server

#### What it does
Provides a FastMCP server that exposes A.I.M.'s search and skill-running capabilities to LLM clients.

#### aim implementation: `src/mcp_server.py`

- **150 lines**
- FastMCP server with:
  - `search_engram` tool — searches the Engram DB
  - `run_skill` tool — executes skills in a bubblewrap sandbox with network isolation, 60s timeout, read-only filesystem
  - `aim://project-context` resource — searches for context file in order: `GEMINI.md`, `CLAUDE.md`, `CODEX.md`, `AIM.md`
- Test files: `tests/test_mcp_server.py`, `tests/test_mcp_extended.py`

#### aim-claude implementation

- `src/mcp_server.py` — **150 lines, 98% identical to aim's version**. The ONLY difference: the `get_project_context` resource searches `["CLAUDE.md", "AIM.md"]` instead of `["GEMINI.md", "CLAUDE.md", "CODEX.md", "AIM.md"]`.
- `scripts/mcp_server_claude.py` — **31 lines**, thin wrapper that imports the shared `src/mcp_server.py` and overrides the `aim://project-context` resource to always read `CLAUDE.md` from the aim-claude root.
- Test files: `tests/unit/test_mcp_server.py` (7 test classes), `tests/integration/test_mcp_integration.py` (7 test classes). **Dramatically more thorough** than aim's tests. Includes a regression test for BUG #44 (ensuring GEMINI.md is not hardcoded).

#### Verdict

| Criteria | aim | aim-claude | Winner |
|----------|-----|------------|--------|
| Core code | Baseline | 98% identical | Tie |
| Agent-specific overlay | Hardcoded GEMINI.md preference | Clean wrapper pattern | **aim-claude** |
| Test coverage | 2 test files, basic | 14 test classes, thorough | **aim-claude** |

**Recommendation:** The shared `src/mcp_server.py` should be made **platform-neutral** — remove any hardcoded `GEMINI.md` or `CLAUDE.md` preference from the fallback chain. Each agent-specific repo then has a thin wrapper (e.g., `mcp_server_gemini.py`, `mcp_server_claude.py`) that overrides only the context file resolution. aim-claude already follows this pattern.

**Agreed file names:**

| Component | File | Location |
|-----------|------|----------|
| Shared MCP server | `mcp_server.py` | `src/` (platform-neutral) |
| Agent-specific wrapper | `mcp_server_gemini.py` / `mcp_server_claude.py` | `scripts/` |
| Tests | `test_mcp_server.py` | `tests/` |

---

## 4. Features in aim Only (Not Yet in aim-claude)

These features exist in aim but have no equivalent in aim-claude. Some are deprecated (and aim-claude was right to not implement them), others are legitimate features that aim-claude should eventually adopt.

| Feature | aim Files | CLI Command | Status | Should aim-claude adopt? |
|---------|-----------|-------------|--------|--------------------------|
| Wiki System | `src/wiki_tools.py` | `aim wiki search/process` | Active | **Yes** — valuable knowledge layer |
| Daemon/Heartbeat | `src/daemon.py`, `src/heartbeat.py` | `aim daemon` | **Deprecated** | **No** — superseded by event-driven model (aim #206, #241) |
| Maintenance | `src/maintenance.py` | `aim clean` | **Deprecated** | **No** — targets artifacts that no longer exist (aim #244) |
| Sovereign Sync | `src/sovereign_sync.py`, `src/back-populator.py` | `aim sync` | **Deprecated** | **No** — replaced by engram exchange (aim #121) |
| BitTorrent Export | `scripts/aim_torrent.py` | `aim export` | Experimental | **Later** — depends on Swarm maturity |
| Obsidian Sync (bidirectional) | `scripts/obsidian_sync.py` | via `aim sync` | Active | **Maybe** — aim-claude has pull-only, which may be sufficient |
| Mail System | `scripts/sync_mail.py` | `aim mail` | Active | **Yes** — referenced in CLAUDE.md but never wired |
| Hook Router | `scripts/aim_router.py` | hook dispatch | Active | **Platform-specific** — Claude Code uses native hooks |
| Interactive Bug | in `aim_cli.py` | `aim bug-operator` | Active | **Yes** — useful for operator interaction |
| Health Check | via `src/heartbeat.py` | `aim health` | **Deprecated** | **No** — use `aim doctor` instead |

---

## 5. Features in aim-claude Only (Not Yet in aim)

These features were implemented by aim-claude and should be adopted by aim.

| Feature | aim-claude Files | aim Issue | Recommendation |
|---------|-----------------|-----------|---------------|
| Dashboard | `src/dashboard.py` | #119 (OPEN) | **Adopt as-is** |
| Handoff Config | `src/handoff_config.py` | None | **Adopt** — enables multi-agent targeting |
| Swarm Engrams | `src/swarm_engrams.py` | #116 (OPEN) | **Adopt as-is** |
| Swarm Publish | `src/swarm_publish.py` | #121 (OPEN) | **Adopt as-is** |
| Cartridge Utils | `src/plugins/datajack/cartridge_utils.py` | #50 (OPEN) | **Adopt as-is** |
| Freshness Tracker | `src/plugins/datajack/freshness_tracker.py` | #89 (OPEN) | **Adopt as-is** |

---

## 6. CLI Command Divergences

### Commands in aim only (not in aim-claude)

| Command | Purpose | Should aim-claude adopt? |
|---------|---------|--------------------------|
| `aim audit` | LLM-synthesized weekly report | **Yes** (with aim-claude's architecture) |
| `aim bug-operator` | Interactive bug reporting | **Yes** |
| `aim clean` | Maintenance cleanup | **No** (deprecated) |
| `aim daemon start/stop/status` | Background heartbeat | **No** (deprecated) |
| `aim export` | BitTorrent seeding | **Later** |
| `aim health` | System health check | **No** (use `aim doctor`) |
| `aim mail` | Swarm post office | **Yes** |
| `aim recall` | Deep historical search | **Yes** (with aim-claude's architecture) |
| `aim scrape` | Forum/issue ingestion | **Yes** (see Section 3.1) |
| `aim sync` | Sovereign Sync | **No** (deprecated) |
| `aim wiki search/process` | Wiki knowledge base | **Yes** |

### Commands in aim-claude only (not in aim)

| Command | Purpose | Should aim adopt? |
|---------|---------|-------------------|
| `aim-claude commit` | Commit memory proposals | **Yes** |
| `aim-claude memory` | Trigger memory pipeline | **Yes** |

---

## 7. Config & Infrastructure Divergences

### `core/CONFIG.json`

| Setting | aim | aim-claude | Resolution |
|---------|-----|------------|------------|
| `tmp_chats_dir` | `~/.gemini/tmp/aim/chats` | `~/.claude/projects/<hash>` | **Platform-specific** — each repo keeps its own |
| `scrivener_interval_minutes` | `60` | Not present | **Deprecated** — daemon-era config, remove from aim |
| `auto_distill_tier` | `"T3"` | Not present | **Deprecated** — 5-tier pipeline was replaced |
| `memory_pipeline.intervals` | Tiered (T1-T5 with hour intervals) | Not present | **Deprecated** — Single-Shot Compiler replaced this |

### Archive Databases

| Database | aim | aim-claude | Resolution |
|----------|-----|------------|------------|
| `engram.db` | Present | Missing | aim-claude needs this for full RAG |
| `history.db` | Present | Missing | aim-claude needs this for session history |
| `datajack_library.db` | Present | Missing | aim-claude needs this for cartridge tracking |
| `daemon.log` | Present | N/A | **Deprecated** — daemon is gone |
| `scrivener_state.json` | Present | N/A | **Deprecated** — daemon is gone |

### Pre-baked Engrams

aim has 7 pre-baked `.engram` cartridges in `engrams/`. aim-claude's `engrams/` directory is empty. aim-claude should either bake its own or adopt aim's cartridges.

---

## 8. Test Structure Divergences

| Aspect | aim | aim-claude |
|--------|-----|------------|
| Directory structure | Flat: `tests/test_*.py` | Organized: `tests/unit/`, `tests/integration/`, `tests/e2e/` |
| Fixtures | None | `tests/conftest.py` with shared fixtures |
| Test count | ~20 test files | ~34 test files |
| Test framework | `unittest` (mostly) | `pytest` (consistently) |

**Recommendation:** Both repos should adopt aim-claude's organized test structure (`unit/`, `integration/`, `e2e/`). The flat structure becomes unmanageable as the test suite grows.

---

## 9. Architectural Principles Going Forward

Based on this audit, both teams should follow these principles for all new and refactored code:

### 9.1 Pure Functions Over Monoliths

**Bad (aim's current pattern):**
```python
def recall(query, limit=5):
    db = get_db()                          # side effect: DB connection
    results = db.search(query, limit)      # side effect: DB query
    prompt = build_prompt(results)          # logic
    response = generate_reasoning(prompt)   # side effect: LLM call ($$$)
    write_file("RECALL.md", response)      # side effect: file write
    return response
```

**Good (aim-claude's pattern):**
```python
def search_sources(query, aim_root, limit=5):
    """Pure function: returns raw results from multiple sources."""
    results = []
    results += search_continuity(query, aim_root)
    results += search_git_history(query, aim_root)
    results += search_engram_db(query, aim_root, limit)
    return results

def format_results(results):
    """Pure function: renders results as markdown."""
    return "\n".join(f"- [{r['source']}] {r['content']}" for r in results)
```

### 9.2 LLM Calls are Always Optional

Core functions must never require LLM calls. LLM synthesis should be an opt-in enhancement layer:

```bash
aim recall "query"                  # default: fast, free, deterministic
aim recall "query" --synthesize     # optional: LLM-enhanced, costs tokens
```

### 9.3 Gather/Format Separation

Every operator-facing command should follow the two-function pattern:

1. `gather_*_data(aim_root)` — collects raw data into a dict (testable, composable)
2. `format_*(data)` — renders the dict for display (testable, swappable)

This pattern is already used in aim-claude's `dashboard.py`, `morning_report.py`. It should be the standard for all commands.

### 9.4 Content Hashing for Dedup

Any function that ingests external content must compute SHA-256 content hashes and check against known hashes before insertion. This prevents duplicate ingestion and enables incremental updates.

---

## 10. Recommended Convergence Plan

### Phase A: Name Alignment (aim team)

aim should adopt these implementations from aim-claude, under these file names:

| Feature | Final File Name | Source |
|---------|----------------|--------|
| Dashboard | `src/dashboard.py` | aim-claude (adopt as-is) |
| Swarm Engrams | `src/swarm_engrams.py` | aim-claude (adopt as-is) |
| Swarm Publish | `src/swarm_publish.py` | aim-claude (adopt as-is) |
| Cartridge Utils | `src/plugins/datajack/cartridge_utils.py` | aim-claude (adopt as-is) |
| Freshness Tracker | `src/plugins/datajack/freshness_tracker.py` | aim-claude (adopt as-is) |
| Handoff Config | `src/handoff_config.py` | aim-claude (adopt as-is) |

### Phase B: Architecture Alignment (aim team)

aim should refactor these existing implementations to use aim-claude's pure-function architecture:

| Feature | File | What Changes |
|---------|------|-------------|
| Issue Ingestion | `scripts/aim_scraper.py` | Extract pure `parse_github_issue()` and `parse_stackoverflow_thread()` functions, add content hashing, keep CLI wrapper |
| Recall | `src/recall_tools.py` | Make LLM synthesis optional, add continuity + git search sources, return raw data by default |
| Audit | `src/audit_tools.py` | Refactor to gather/format pattern, make LLM synthesis optional |

### Phase C: Name Alignment (aim-claude team)

After aim completes Phases A and B, aim-claude will rename its files to match:

| Current aim-claude name | New name (matching aim) |
|------------------------|------------------------|
| `src/panopticon_recall.py` | `src/recall_tools.py` |
| `src/morning_report.py` | `src/audit_tools.py` |
| `src/issue_ingestion.py` | Retire (logic absorbed into `scripts/aim_scraper.py`) |

### Phase D: Gap Filling (both teams)

Both teams independently implement:
- Wiki system (aim has it, aim-claude needs it)
- Mail system (aim has it, aim-claude needs it)
- FTS5 Engram DB search in recall (aim has it, aim-claude needs it in `recall_tools.py`)
- StackOverflow ingestion (aim has it, aim-claude needs it in `aim_scraper.py`)

---

## 11. Appendix: Full File Inventory Comparison

### `scripts/` Directory

| File | aim | aim-claude | Notes |
|------|-----|------------|-------|
| `aim_cli.py` | Yes | Yes (diverged) | Core router — both have it, commands differ |
| `aim_crash.py` | Yes | Yes | Crash recovery |
| `aim_delegate.py` | Yes | Yes | Sub-agent spawning |
| `aim_doctor.py` | Yes | Yes | Dependency checker |
| `aim_init.py` | Yes | Yes | Workspace initializer |
| `aim_promote.py` | Yes | Yes | GitOps phase promotion |
| `aim_push.sh` | Yes | Yes | Git push wrapper |
| `aim_reincarnate.py` | Yes | Yes | Reincarnation pipeline |
| `aim_router.py` | Yes | **No** | Hook router — Claude uses native hooks |
| `aim_scraper.py` | Yes | **No** | Issue/forum scraper — aim-claude has it as `src/issue_ingestion.py` |
| `aim_torrent.py` | Yes | **No** | BitTorrent export |
| `handoff_pulse_claude.py` | **No** | Yes | Claude-specific handoff pulse |
| `handoff_pulse_gemini.py` | Yes | **No** | Gemini-specific handoff pulse |
| `mcp_server_claude.py` | **No** | Yes | Claude MCP wrapper |
| `obsidian_pull.py` | Yes | Yes | Vault ingestion |
| `obsidian_sync.py` | Yes | **No** | Bidirectional Obsidian sync |
| `sync_issue_tracker.py` | Yes | Yes | GitHub issue sync |
| `sync_mail.py` | Yes | **No** | Swarm mail sync |

### `src/` Directory (excluding `plugins/`)

| File | aim | aim-claude | Notes |
|------|-----|------------|-------|
| `audit_tools.py` | Yes | **No** (has `morning_report.py`) | Same feature, different name |
| `back-populator.py` | Yes | **Deleted** | Deprecated (aim-claude #128) |
| `bootstrap_brain.py` | Yes | Yes | Engram DB initializer |
| `config_utils.py` | Yes | Yes | Config loader |
| `daemon.py` | Yes | **Deleted** | Deprecated (aim-claude #128) |
| `dashboard.py` | **No** | Yes | aim-claude only |
| `extract_signal.py` | Yes | Yes | Session signal extractor |
| `handoff_config.py` | **No** | Yes | aim-claude only |
| `handoff_pulse_generator.py` | Yes | **Deleted** | Deprecated (aim-claude #128) |
| `heartbeat.py` | Yes | **Deleted** | Deprecated (aim-claude #128) |
| `history_scribe.py` | Yes | Yes | Session archiver |
| `issue_ingestion.py` | **No** | Yes | aim-claude only (aim has `aim_scraper.py`) |
| `maintenance.py` | Yes | **Deleted** | Deprecated (aim-claude #128) |
| `mcp_server.py` | Yes | Yes (local copy) | 98% identical |
| `morning_report.py` | **No** | Yes | aim-claude only (aim has `audit_tools.py`) |
| `panopticon_recall.py` | **No** | Yes | aim-claude only (aim has `recall_tools.py`) |
| `reasoning_utils.py` | Yes | Yes | LLM reasoning wrapper |
| `recall_tools.py` | Yes | **No** (has `panopticon_recall.py`) | Same feature, different name |
| `retriever.py` | Yes | Yes | Engram search |
| `sovereign_sync.py` | Yes | **Deleted** | Deprecated (aim-claude #128) |
| `swarm_engrams.py` | **No** | Yes | aim-claude only |
| `swarm_publish.py` | **No** | Yes | aim-claude only |
| `wiki_tools.py` | Yes | **No** | aim only |

### `src/plugins/datajack/` Directory

| File | aim | aim-claude | Notes |
|------|-----|------------|-------|
| `aim_bake.py` | Yes | Yes | Cartridge baker |
| `aim_exchange.py` | Yes | Yes | Import/export |
| `cartridge_utils.py` | **No** | Yes | aim-claude only |
| `datajack_plugin.py` | Yes | Yes | Plugin loader |
| `forensic_utils.py` | Yes | Yes | Fragment forensics |
| `freshness_tracker.py` | **No** | Yes | aim-claude only |
| `quarantine_daemon.py` | Yes | Yes | Fragment quarantine |

---

*End of audit. Questions or clarifications should be directed to the Operator.*
