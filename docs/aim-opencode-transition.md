# A.I.M. → OpenCode Full Transition Roadmap

> **Status:** Phase 1 Complete (Fork Setup)  
> **Branch:** `opencode`  
> **Fork:** `d3c12yp7012/aim-opencode`  
> **Upstream:** `BrianV1981/aim`

---

## Phase 1: Foundation — COMPLETE

- [x] Create fork: `d3c12yp7012/aim-opencode`
- [x] Set up git remotes: `upstream` → BrianV1981/aim, `origin` → d3c12yp7012/aim-opencode
- [x] Create `opencode` branch for all changes (main stays clean upstream mirror)
- [x] Isolate `memory-wiki/` from upstream (cleared, re-scaffolded, gitignored)
- [x] Fix `localhost` → `127.0.0.1` for Ollama WSL2 IPv6 bug (merged upstream via #497)
- [x] Document sync workflow: `main` tracks upstream, `opencode` carries delta

## Phase 2: Session Data Bridge (The Core Plumbing)

Convert from Gemini CLI JSONL session files (`~/.gemini/tmp/`) to OpenCode session exports (`opencode export`).

### #1 — Session Data Source Abstraction
**Files:** `config_utils.py:50,94`, `handoff_pulse_generator.py:49`, `daemon.py:39`, `recover_json_logs.py:17`
- Add `opencode_export_dir` config path
- Update session source resolution from `~/.gemini/tmp/` to `archive/raw/` (post-bridge)
- Keep Gemini fallback for backward compatibility

### #2 — OpenCode Session Bridge Script
**New file:** `aim_core/session_bridge.py`
- Calls `opencode session list` → `opencode export <id>` → writes to `archive/raw/session-*.json`
- Replaces `session_porter.py` Gemini mirroring with OpenCode export pipeline

### #3 — Extract Signal Format Detection
**File:** `aim_core/extract_signal.py` (119 lines)
- Add auto-detection: Gemini JSONL vs OpenCode export JSON format
- Add OpenCode role mapping: `"assistant"` → agent turn (same as `"gemini"`/`"model"`)
- Update `skeleton_to_markdown()` roles: "GEMINI" → "AGENT" for OpenCode turns
- Keep backward compatibility for Gemini format

### #4 — Crash Recovery & Benchmark Recovery
**Files:** `aim_crash.py:32`, `back-populator.py:19`
- Update session file patterns and source paths for OpenCode export naming

## Phase 3: CLI Invocation Layer

Replace every hardcoded `gemini` subprocess with `opencode`.

### #5 — Reincarnation Protocol CLI Spawn
**File:** `aim_reincarnate.py:80`
- Change `gemini --yolo --prompt-interactive` → `opencode run "prompt"`
- Verify `opencode run` supports autonomous mode (permissions in opencode.json)

### #6 — Wiki Agent CLI Spawn
**File:** `wiki_tools.py:86`
- Change `tmux ... gemini --yolo` → `tmux ... opencode run`
- Update wiki prompt for OpenCode agent context

### #7 — Daemon Pulse Injection
**File:** `daemon.py:142`
- Remove `Popen(["gemini", "chat"])` stdin pipe
- Agent reads `core/DAEMON_PULSE.md` via AGENTS.md instructions instead

### #8 — Reasoning Engine Gemini CLI Bridge
**File:** `reasoning_utils.py:64-134`
- Remove `gemini --skip-trust -p "" -o json -y` OAuth path
- Replace with `opencode run --json` or remove (API key path works with DeepSeek)
- Remove Gemini-specific env vars (`GEMINI_CLI_TMP_DIR`, `GEMINI_CLI_DISABLE_CHECKPOINT`)

### #9 — Session Summarizer Fallback
**File:** `hooks/session_summarizer.py:86-102`
- Remove `Popen(["gemini", fallback_prompt])` fallback
- Use `generate_reasoning()` with DeepSeek provider instead

## Phase 4: Hook System → Plugin System

Port Gemini CLI JSON hooks to OpenCode TypeScript plugin events.

### #10 — OpenCode Hook Plugin
**New file:** `.opencode/plugins/aim-hooks.ts`
- Replace `aim_router.py` (Gemini stdin/stdout hook router)
- Subscribe to `session.idle` → trigger session summarizer
- Subscribe to `tool.execute.after` → cognitive mantra counter
- Handle `experimental.session.compacting` → inject AIM continuity context

### #11 — Cognitive Mantra Output Format
**File:** `hooks/cognitive_mantra.py:105-111`
- Replace Gemini-specific `hookSpecificOutput` JSON
- Write mantra to `continuity/MANTRA_PULSE.md` for agent to read

### #12 — Init Hook Registration → Plugin Installation
**File:** `aim_init.py:277-329`
- Replace `register_hooks()` with `install_opencode_plugins()`
- Seed `.opencode/plugins/aim-hooks.ts` + `.opencode/package.json`
- Remove `aim_router.py` deployment

### #13 — CLI Hook Validation
**File:** `aim_cli.py:778-804`
- Replace `ensure_hooks_mapped()` (Gemini settings.json check)
- Check for `.opencode/plugins/aim-hooks.ts` existence instead

## Phase 5: Configuration & Templates

Update project scaffolding for OpenCode-native files.

### #14 — Init Template Files
**File:** `aim_init.py:540-571`
- Replace `.gemini/settings.json` → `opencode.json` template
- Replace `.geminiignore` → `.opencodeignore` (or rely on `.gitignore`)
- Replace `memory-wiki/.gemini/settings.json` → remove (not needed)
- Remove Gemini-specific agent/skill templates

### #15 — AGENTS.md Template Updates
**File:** `aim_init.py` (template strings)
- Replace `.gemini/settings.json` references → `opencode.json`
- Replace "Gemini CLI" → "OpenCode"
- Replace "Node.js V8 engine" → "session compaction failure"
- Replace `gemini login` → `opencode connect`

### #16 — Port Gemini Skills to OpenCode
**Directory:** `.gemini/skills/` → `.opencode/skills/`
- 5 existing Gemini skill manifests → OpenCode SKILL.md format
- Underlying Python scripts (`skills/*/scripts/run.py`) unchanged

### #17 — Port Gemini Agents to OpenCode
**Directory:** `.gemini/agents/` → `opencode.json#agent`
- `python-specialist` and `technical-auditor` → OpenCode agent config
- Update model references from Gemini to DeepSeek

## Phase 6: Cleanup & Polish

### #18 — Variable Renames
**File:** `aim_config.py:101-109`, `cognitive_mantra.py:96-105`
- `gemini_path` → `agents_path`, `gemini_content` → `agents_content`
- TUI references: "Gemini CLI" → "OpenCode"

### #19 — Setup Script
**File:** `setup.sh:84`
- Remove `NODE_OPTIONS` V8 memory patch (Gemini CLI specific)
- Add `opencode.json` seeding step

### #20 — Benchmark Environment Setup
**File:** `setup_environments.sh:77,96,120`
- Rename `GEMINI.md` → `AGENTS.md` for benchmark environments
- Remove `aim_router.py` hook path reference

### #21 — Model Pricing
**File:** `calculate_economics.py`
- Add DeepSeek pricing alongside Gemini pricing

### #22 — Documentation
**Files:** Various
- Update references from "Gemini CLI" to "OpenCode" in docs
- Remove `.gemini/` guide references

---

## Verification Gates

Each phase has an independent test:
- Phase 2: `extract_signal.py` parses `opencode export` JSON, flight recorder generates
- Phase 3: `aim reincarnate` spawns `opencode run` tmux session
- Phase 4: Session summarizer triggers on `session.idle`, mantra fires on `tool.execute.after`
- Phase 5: `aim init` seeds `opencode.json`, `AGENTS.md` references OpenCode
- Phase 6: All `localhost` gone, no Gemini CLI references in core path

## Sync Workflow

```bash
# Pull upstream changes
git checkout main && git pull upstream main && git push origin main

# Merge into opencode branch
git checkout opencode && git merge main

# Push opencode changes to fork
git push origin opencode
```

---

## Phase 7: Upstream RAG Import & Updater (Pending)

See [Issue #23](https://github.com/d3c12yp7012/aim-opencode/issues/23).

- [ ] Import RAG 4.2 search system once stabilized upstream
- [ ] Build `aim_opencode_update.py` — dedicated fork updater
- [ ] Merge conflict strategy for `extract_signal.py` (modified in both repos)

### RAG Files to Watch During Import

| Upstream File | OpenCode Fork Impact |
|---|---|
| `aim_core/plugins/datajack/forensic_utils.py` | Chunking, embedding — no opencode changes; safe merge |
| `aim_core/extract_signal.py` | **CONFLICT ZONE** — both repos modified. Must preserve OpenCode format detection + role mapping |
| `aim_core/handoff_pulse_generator.py` | Session source resolution — minor conflict, easy merge |
| `aim_core/retriever.py` | Search routing — no opencode changes; safe merge |
| `aim_core/aim_cli.py` | `aim search` command — minor conflict, preserve ensure_opencode_plugins() |
| `benchmarks/locomo/` | Benchmark scripts — no opencode changes; safe merge |
