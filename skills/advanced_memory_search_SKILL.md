# SKILL: advanced_memory_search

**Name:** advanced_memory_search  
**Description:** Runs a deep hybrid (semantic + FTS5) search across the entire Engram DB — perfect for "what did we decide about X last week?"  
**Type:** Python  
**Arguments:**  
- `query` (string, required) — natural language or keyword search

**Example call:**
```json
{"name": "run_skill", "arguments": {"skill_name": "advanced_memory_search", "args_json": "{\"query\": \"user prefers dark mode\"}"}}
```