# Testing

TDD is non-negotiable in aim-opencode. Every change must be empirically proven.

## Test Categories

| Category | Files | What's Tested |
|---|---|---|
| **LanceDB RAG** | `test_lance_backend.py`, `test_lance_merge_integration.py` | Tantivy query generation, EntityIntersection reranker, VectorBackend, fork integrity |
| **Fork Updater** | `test_opencode_update.py` | Conflict zones, safe merge files, dry-run mode, merge ordering, test suite runner |
| **OpenCode Integration** | `test_session_bridge.py`, `test_extract_open_code.py`, `test_aim_hooks_plugin.py` | Session export pipeline, format auto-detection, plugin validation |
| **Phase Tests** | `test_phase4_issues_11_13.py`, `test_phase5_init_templates.py`, `test_phase6_cleanup.py` | Hook→plugin migration, init template seeding, cleanup renames |
| **Subsystem Tests** | `test_reasoning_engine.py`, `test_reincarnation_spawn.py`, `test_wiki_agent_spawn.py`, `test_session_summarizer_fallback.py`, `test_daemon_pulse_injection.py`, `test_session_source_resolution.py` | Each replaced Gemini subshell verified |
| **Core Tests** | `test_retriever.py`, `test_forensic_utils.py`, `test_datajack.py`, `test_aim_cli.py`, `test_aim_config.py`, `test_aim_init.py` | Cross-platform core functionality |
| **Memory Tests** | `test_handoff_pulse_generator.py`, `test_cognitive_mantra.py`, `test_sovereign_sync.py`, `test_federated_db.py` | Continuity protocol, session sync |
| **Tools** | `test_mcp_server.py`, `test_mcp_extended.py`, `test_audit_tools.py`, `test_recall_tools.py` | MCP server, audit and recall tools |

## Running Tests

```bash
# Full suite (stop on first failure)
venv/bin/python -m pytest tests/ -x -v

# Quick smoke test (quiet mode)
venv/bin/python -m pytest tests/ -x -q

# Specific category
venv/bin/python -m pytest tests/test_lance_merge_integration.py -v

# Specific test
venv/bin/python -m pytest tests/test_opencode_update.py::test_dry_run_does_not_modify_branches -v

# With coverage
venv/bin/python -m pytest tests/ --cov=aim_core --cov-report=term-missing
```

## Test Requirements

Some tests have specific dependencies:

| Test | Requires |
|---|---|
| `test_lance_*` | `lancedb`, `pyarrow` installed |
| `test_retriever.py` | LanceDB migrated (`VectorBackend().migrate_from_sqlite()`) |
| `test_opencode_update.py` (some) | `upstream` remote configured |
| `test_session_bridge.py` | `opencode` CLI installed |
| `test_reasoning_engine.py` | DeepSeek API key in keyring |

## Writing New Tests

1. Follow existing patterns — look at neighboring test files for conventions
2. Use `pytest` fixtures (`tmp_path` for temp dirs)
3. Mock external dependencies when possible
4. Fork integrity tests: verify no Gemini CLI regressions in modified files
5. Each test should assert one specific behavior

## Fork Integrity Pattern

When merging upstream changes, always add tests that verify:

```python
def test_no_gemini_cli_in_<new_file>():
    """Ensure <new_file> doesn't reintroduce Gemini CLI subprocess calls."""
    with open(path, "r") as f:
        content = f.read()
    assert "Popen([\"gemini\"" not in content
    assert "gemini --yolo" not in content

def test_deepseek_defaults_in_<file>():
    """Ensure <file> keeps DeepSeek defaults."""
    with open(path, "r") as f:
        content = f.read()
    assert "deepseek-chat" in content
    assert "gemini-2.5-flash" not in content
```
