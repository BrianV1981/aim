import json

path = "/home/kingb/.gemini/tmp/django-matrix-pro/chats/session-2026-03-26T09-34-a4f28921.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

messages = data.get("messages", []) if isinstance(data, dict) else data

push_id = None
for msg in messages:
    if msg.get("type") in ["gemini", "model"] and "toolCalls" in msg:
        for tc in msg["toolCalls"]:
            args = tc.get("functionCall", {}).get("args", {}) or tc.get("args", {})
            cmd = args.get("command", "")
            if "aim_cli.py push" in cmd:
                print(f"COMMAND: {cmd}")
                print(f"CWD: {args.get('dir_path', 'Not specified (defaults to aim root)')}")
                push_id = tc.get("id") or tc.get("functionCall", {}).get("id")

    if msg.get("type") == "tool_response" and push_id:
        for tr in msg.get("toolResponses", []) or msg.get("tool_responses", []):
            try:
                out = tr.get("response", {}).get("output", "")
            except AttributeError:
                # Structure might be nested differently
                if "functionResponse" in tr:
                    out = tr["functionResponse"].get("response", {}).get("output", "")
                else:
                    out = str(tr)
            print(f"\nOUTPUT:\n{out[:2000]}")
            push_id = None
