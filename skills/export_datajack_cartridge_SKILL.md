# SKILL: export_datajack_cartridge

**Name:** export_datajack_cartridge  
**Description:** Packages specific knowledge from the Engram DB into a portable .engram DataJack cartridge for sharing or backup.  
**Type:** Python  
**Arguments:**  
- `keyword` (string, required) — The keyword to search for in session filenames (e.g., "python", "expert-")
- `name` (string, optional) — cartridge filename output

**Example call:** 
```json
{"name": "run_skill", "arguments": {"skill_name": "export_datajack_cartridge", "args_json": "{\"keyword\":\"python\", \"name\":\"python314.engram\"}"}}
```