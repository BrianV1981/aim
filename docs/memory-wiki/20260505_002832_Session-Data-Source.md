# Session Data Source

## Overview
Abstraction layer for session data ingestion. Supports multiple backends with a priority-based fallback chain.

## resolve_session_sources()
Location: `config_utils.py`

Returns prioritized tuples of session data sources:
1. **OpenCode** `archive/raw/*.json` — primary source
2. **Gemini** `~/.gemini/tmp/*.jsonl` — fallback

## session_bridge.py
Location: `aim_core/session_bridge.py`

Implements the execution pipeline:
1. `opencode session list` — enumerates available sessions
2. `opencode export <id>` — exports session data as JSON
3. Atomic file writes to prevent corruption during concurrent access

## Format Auto-Detection
Location: `extract_signal.py`

`detect_format()` distinguishes between:
- **Gemini JSONL** — line-delimited JSON records
- **OpenCode export JSON** — single structured JSON document

Includes role mapping: `"assistant"` → `"AGENT"` for consistent internal representation across backends.

## Related
- [OpenCode Fork Migration](OpenCode-Fork-Migration.md)
