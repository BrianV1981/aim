# OpenCode Integration

How aim-opencode ported from the Gemini CLI ecosystem to OpenCode. All Gemini subshell spawns have been replaced. Zero `gemini` Popen calls remain in core.

## Phase Summary

| Phase | Issues | What Changed |
|---|---|---|
| **Phase 2** | #1–#4 | Session data source abstraction — OpenCode export JSON pipeline |
| **Phase 3** | #5–#9 | CLI invocation — all `gemini` subprocess → `opencode run` |
| **Phase 4** | #10–#13 | Hook system → TypeScript plugin system |
| **Phase 5** | #14–#17 | Configuration templates — `opencode.json`, skills, agents |
| **Phase 6** | #18–#22 | Cleanup — variable renames, NODE_OPTIONS removed |

## Session Data (Phase 2)

**Problem:** The original A.I.M. read Gemini CLI JSONL session files from `~/.gemini/tmp/`. OpenCode uses `opencode export` which produces a different JSON format.

**Solution:** `session_bridge.py` wraps `opencode session list` → `opencode export <id>` with atomic writes to `archive/raw/session-*.json`. `config_utils.py:resolve_session_sources()` returns prioritized backends: OpenCode first, Gemini fallback.

`extract_signal.py` auto-detects format:
- Gemini JSONL: line-delimited JSON records
- OpenCode export JSON: `{info, messages}` structure with `parts[]` arrays
- Role mapping: `"assistant"` → `"AGENT"` (consistent internal representation)

## CLI Invocation (Phase 3)

Every hardcoded `gemini` subprocess replaced:

| File | Before | After |
|---|---|---|
| `aim_reincarnate.py` | `gemini --yolo` | `opencode run` |
| `wiki_tools.py` | `tmux ... gemini --yolo` | `tmux ... opencode` |
| `daemon.py` | `Popen(["gemini", "chat"])` | Agent reads `DAEMON_PULSE.md` via AGENTS.md |
| `reasoning_utils.py` | 70-line Gemini OAuth bridge | Direct REST API calls (DeepSeek) |
| `session_summarizer.py` | `Popen(["gemini", ...])` fallback | `generate_reasoning()` with DeepSeek |

Removed all `GEMINI_CLI_TMP_DIR`, `GEMINI_CLI_DISABLE_CHECKPOINT` env vars.

## Plugin System (Phase 4)

Replaced Gemini JSON hooks with OpenCode TypeScript plugins.

**Before:** `aim_router.py` (stdin/stdout JSON hook router)  
**After:** `.opencode/plugins/aim-hooks.ts` (TypeScript SDK plugins)

Three hooks:

| Hook | Trigger | Action |
|---|---|---|
| `session.idle` | Session becomes idle | Trigger `session_summarizer.py` |
| `tool.execute.after` | After each tool call | Increment cognitive mantra counter |
| `experimental.session.compacting` | Context window fills up | Inject AIM continuity context |

## Skills & Agents (Phase 5)

Five Gemini skills ported to `.opencode/skills/`:

| Skill | Purpose |
|---|---|
| `advanced-memory-search` | Hybrid semantic + FTS5 search of Engram DB |
| `aim-calc` | Stateful scientific calculator |
| `aim-google` | Google Workspace integration (Gmail, Calendar, Drive) |
| `export-datajack-cartridge` | Export .engram DataJack cartridges |
| `list-recent-sessions` | List N most recent sessions from Engram DB |

Two agents ported to `.opencode/agents/`:

| Agent | Model | Purpose |
|---|---|---|
| `python-specialist` | `deepseek/deepseek-v4-pro` | High-fidelity implementation with TDD |
| `technical-auditor` | `deepseek/deepseek-v4-pro` | Architectural precision expert |

## Configuration (Phase 5)

| Gemini (old) | OpenCode (new) |
|---|---|
| `.gemini/settings.json` | `opencode.json` |
| `.geminiignore` | `.opencodeignore` |
| `.gemini/skills/` | `.opencode/skills/` |
| `.gemini/agents/` | `.opencode/agents/` |
| Gemini Flash/Pro models | DeepSeek V4 Pro/Chat |

## Cleanup (Phase 6)

- Renamed: `gemini_path` → `agents_path`, `update_gemini_behavior_file` → `update_agents_file`
- Removed: `NODE_OPTIONS` V8 memory patch from `setup.sh`
- Added: `opencode.json` seeding step to `aim_init.py`
- Added: DeepSeek pricing tier to `calculate_economics.py`

## Verification

```bash
# Verify zero Gemini CLI references in core
grep -r "gemini --yolo\|Popen.*gemini\|gemini\", \"chat" aim_core/

# Run integration tests
pytest tests/test_session_bridge.py tests/test_extract_open_code.py \
       tests/test_reincarnation_spawn.py tests/test_reasoning_engine.py \
       tests/test_wiki_agent_spawn.py tests/test_aim_hooks_plugin.py
```
