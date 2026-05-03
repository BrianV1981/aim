# Updating the Fork

How to safely pull upstream changes from `BrianV1981/aim` into `d3c12yp7012/aim-opencode`.

## Quick Start

```bash
# Preview what would happen (no changes made)
aim update fork --dry-run

# Execute the full sync
aim update fork
```

This runs the pipeline:
1. Fetch `upstream/main`
2. Check for new commits vs local `main`
3. Merge `upstream/main` → `main` (Phase 1)
4. Merge `main` → `opencode` (Phase 2)
5. Run full test suite (Phase 3)
6. Report results (conflicts, test failures)

## Manual Sync (if automation fails)

```bash
# 1. Sync main with upstream
git checkout main
git pull upstream main
git push origin main

# 2. Merge into opencode
git checkout opencode
git merge main

# 3. Resolve conflicts (see below)
# 4. Run tests
venv/bin/python -m pytest tests/ -x -q

# 5. Push
git push origin opencode
```

## Conflict Zones

These 5 files are modified in both the upstream repo and our fork. When upstream touches them, manual resolution is required:

### 1. `aim_core/extract_signal.py`
**OpenCode has:** Format auto-detection (Gemini JSONL vs OpenCode JSON), `"assistant"` → `"AGENT"` role mapping  
**Upstream may have:** RAG chunking improvements, signal extraction changes  
**Resolution:** Keep both — preserve OpenCode format detection AND upstream's extraction logic. They're in different functions.

### 2. `aim_core/reasoning_utils.py`
**OpenCode has:** `deepseek-chat` as emergency fallback model  
**Upstream may have:** `gemini-2.5-flash` fallback, provider routing changes  
**Resolution:** ALWAYS keep the DeepSeek default. Upstream provider routing changes are usually additive and compatible.

### 3. `aim_core/aim_cli.py`
**OpenCode has:** `ensure_opencode_plugins()`, `cmd_update(target="fork")`  
**Upstream may have:** New CLI subcommands, search improvements  
**Resolution:** Keep both. New upstream commands and our fork additions are in different sections of the file.

### 4. `aim_core/handoff_pulse_generator.py`
**OpenCode has:** `resolve_session_sources()` priority queue, OpenCode export path  
**Upstream may have:** Flight recorder pipeline changes  
**Resolution:** Usually a simple merge. Our changes are in the session source selection; upstream changes are in the markdown rendering.

### 5. `aim_core/wiki_tools.py`
**OpenCode has:** `opencode` tmux spawn, static `wiki_agent` session name  
**Upstream may have:** Dynamic session naming, prompt changes  
**Resolution:** Keep `opencode` spawn and our prompt format. Upstream naming changes are cosmetic.

## What Happens During a Conflict

The updater stops at Phase 2 and prints:

```
[!] MERGE CONFLICT on opencode branch
    2 conflicted file(s):
      - aim_core/extract_signal.py [CONFLICT ZONE]
      - aim_core/reasoning_utils.py [CONFLICT ZONE]

    To resolve:
      1. Edit each conflicted file (preserve OpenCode/DeepSeek variants)
      2. git add <resolved_files>
      3. git commit
      4. Re-run 'aim update fork' to verify tests pass
```

## Safe Merge Files

These files are pure upstream — no fork modifications. They'll never conflict:

- `aim_core/lance_backend.py`
- `aim_core/retriever.py`
- `aim_core/plugins/datajack/forensic_utils.py`
- `hooks/coreference_rewriter.py`
- `requirements.txt`
- `AGENTS.md`

## After a Successful Update

```bash
# Verify everything works
aim update fork --dry-run    # Should say "No new upstream changes"
pytest tests/ -x -q          # All tests should pass
aim map                      # Knowledge map should be intact
```

## Disaster Recovery

If the merge goes badly wrong:

```bash
# Abort the merge and return to previous state
git merge --abort

# Or reset to last known good state
git reset --hard origin/opencode
```
