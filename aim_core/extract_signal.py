#!/usr/bin/env python3
import json
import sys
import os

def extract_signal(json_path):
    """
    Surgically extracts the architectural signal from a session JSONL.
    Removes raw tool outputs while keeping Intent, Thoughts, and Actions.
    Also extracts token counts and tool execution metrics for the Eureka Protocol.
    """
    try:
        signal = []
        with open(json_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                if "$set" in msg or "kind" in msg or "sessionId" in msg:
                    continue
                    
                m_role = msg.get("type") or msg.get("role")
                if not m_role: continue
                ts = msg.get("timestamp", "Unknown")
                
                fragment = { "role": m_role, "timestamp": ts }
                content = msg.get("content")
                tokens = msg.get("tokens", {})
                if tokens:
                    fragment["tokens"] = tokens
                
                def process_content(c):
                    import re
                    if isinstance(c, list):
                        text = " ".join([str(item.get("text", "")) for item in c if isinstance(item, dict) and "text" in item])
                    elif isinstance(c, dict):
                        text = str(c.get("text", ""))
                    else:
                        text = str(c) if c is not None else ""
                    return re.sub(r"\n{3,}", "\n\n", text)

                if m_role == "user" or m_role == "system":
                    fragment["text"] = process_content(content)
                elif m_role in ["gemini", "model"]:
                    fragment["text"] = process_content(content)
                    fragment["thoughts"] = msg.get("thoughts", [])
                    
                    tool_calls = msg.get("toolCalls", []) or msg.get("tool_calls", [])
                    fragment["actions"] = []
                    for call in tool_calls:
                        if not isinstance(call, dict):
                            continue
                        name = call.get("name") or call.get("function", {}).get("name")
                        args = call.get("args") or call.get("function", {}).get("arguments")
                        fragment["actions"].append({ "tool": name, "intent": str(args)[:200] })
                else:
                    continue
                
                signal.append(fragment)
                
        return signal
    except Exception as e:
        return f"Extraction Error: {e}"

def skeleton_to_markdown(skeleton, session_id):
    """
    Converts a JSON signal skeleton into a beautifully formatted Obsidian-native Markdown string.
    Zero API cost.
    """
    md = f"---\nSession: {session_id}\nType: Raw Backup\n---\n\n# A.I.M. Signal Skeleton\n\n"
    for turn in skeleton:
        if not isinstance(turn, dict): continue
        role = turn.get("role", "unknown").upper()
        text = turn.get("text", "").strip()
        ts = turn.get("timestamp", "")
        
        if role == "USER":
            md += f"## 👤 USER ({ts})\n"
            if text:
                md += f"{text}\n\n"
        elif role == "GEMINI" or role == "MODEL":
            md += f"## 🤖 A.I.M. ({ts})\n"
            thoughts = turn.get("thoughts", [])
            if thoughts:
                md += "> **Internal Monologue:**\n"
                for thought in thoughts:
                    if isinstance(thought, dict):
                        desc = thought.get("description", "") or thought.get("text", "")
                        md += f"> * {desc}\n"
                    else:
                        md += f"> * {thought}\n"
                md += "\n"
            
            if text:
                md += f"{text}\n\n"
            
            actions = turn.get("actions", [])
            if actions:
                md += "**Tools Executed:**\n"
                for action in actions:
                    tool = action.get("tool", "unknown")
                    intent = action.get("intent", "")
                    md += f"- `{tool}`: {intent}\n"
                md += "\n"
                
        md += "---\n\n"
    return md

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_signal.py <path_to_jsonl>")
        sys.exit(1)
    
    result = extract_signal(sys.argv[1])
    print(json.dumps(result, indent=2))
