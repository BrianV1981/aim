# SKILL: list_recent_sessions

**Name:** list_recent_sessions  
**Description:** Returns the N most recent sessions from the Engram DB (perfect for agents that want to know "what have we worked on lately").  
**Type:** Python  
**Arguments:**
- `limit` (integer, default 5) — how many recent sessions to return

**Example call (from any MCP-aware CLI):**
```json
{
  "name": "list_recent_sessions",
  "arguments": { "limit": 10 }
}
```

**Returns:** JSON with session_id, timestamp, and fragment count.