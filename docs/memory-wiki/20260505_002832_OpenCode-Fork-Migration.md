# OpenCode Fork Migration

## Summary
Migration of A.I.M. from Gemini CLI to OpenCode CLI as the execution substrate. All Gemini CLI subprocess spawns have been replaced with `opencode run --dangerously-skip-permissions`. Zero gemini subprocess spawns remain in core.

## Phase Breakdown

### Phase 2 — Session Data Source Abstraction (#1-#3)
`resolve_session_sources()` in `config_utils.py` returns prioritized tuples: OpenCode `archive/raw/*.json` first, Gemini `~/.gemini/tmp/*.jsonl` fallback. `session_bridge.py` implements `opencode session list` → `opencode export <id>` pipeline with atomic writes. `extract_signal.py` auto-detects Gemini JSONL vs OpenCode export JSON with `"assistant"` → `"AGENT"` role mapping.

See: [Session Data Source](Session-Data-Source.md)

### Phase 3 — CLI Invocation Layer (#5-#9)
Replaced ALL `gemini` subprocess/Popen spawns with `opencode run --dangerously-skip-permissions` across 5 files:
- `aim_reincarnate.py`
- `wiki_tools.py`
- `daemon.py`
- `reasoning_utils.py`
- `session_summarizer.py`

Removed the 70-line Gemini CLI OAuth bridge and `GEMINI_CLI_*` env vars from `reasoning_utils.py`.

### Phase 4 — Hook System → Plugin System (#10-#13)
Created `.opencode/plugins/aim-hooks.ts` TypeScript plugin using `@opencode-ai/plugin` SDK. Three hooks: `session.idle`, `tool.execute.after`, `experimental.session.compacting`. Added `install_opencode_plugins()` and updated `ensure_hooks_mapped()`.

See: [Plugin System](Plugin-System.md)

### Phase 5 — Configuration & Templates (#14-#17)
Replaced `.gemini/settings.json` → `opencode.json`, `.geminiignore` → `.opencodeignore` in all init templates. Ported 5 Gemini skills to `.opencode/skills/` and 2 agents to `.opencode/agents/` with `model: deepseek/deepseek-v4-pro`. Updated T_SOUL template.

### Phase 6 — Cleanup & Polish (#18-#22)
Renamed `gemini_path` → `agents_path`, `update_gemini_behavior_file` → `update_agents_file`. Removed `NODE_OPTIONS` V8 memory patch from `setup.sh`. Added `opencode.json` seeding. Added DeepSeek pricing tier to `calculate_economics.py`.

## Test Results
143 tests pass. 2 pre-existing failures: missing cartridge file, legacy thought formatting.
New tests cover: `resolve_session_sources` (9), session bridge (9), format detection (11), reincarnation spawn (5), daemon pulse (3), reasoning engine (5), session summarizer (3), plugin validation (12), init templates (11), cleanup (9).

## GitOps
See: [GitOps Pattern](GitOps-Pattern.md)
