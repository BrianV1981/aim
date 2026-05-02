#!/usr/bin/env python3
import json
import sys
import os
import re

# ── Format Detection ───────────────────────────────────────────────

def detect_format(json_path):
    """
    Determine whether a session file is Gemini JSONL or OpenCode export JSON.

    Returns 'opencode' if the file contains a top-level JSON object with
    'info' and 'messages' keys. Returns 'gemini' otherwise (line-delimited JSONL).
    """
    ext = os.path.splitext(json_path)[1].lower()

    # Quick heuristic: .jsonl extension is always Gemini
    if ext == ".jsonl":
        return "gemini"

    # Try parsing as a single JSON object (OpenCode format)
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "info" in data and "messages" in data:
            return "opencode"
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass

    return "gemini"


# ── Content Processing (shared) ────────────────────────────────────

def _process_content(c):
    """Normalise content into a clean text string."""
    if isinstance(c, list):
        text = " ".join([
            str(item.get("text", ""))
            for item in c
            if isinstance(item, dict) and "text" in item
        ])
    elif isinstance(c, dict):
        text = str(c.get("text", ""))
    else:
        text = str(c) if c is not None else ""
    return re.sub(r"\n{3,}", "\n\n", text)


# ── Extractors ─────────────────────────────────────────────────────

def _extract_gemini(json_path):
    """Extract signal from a Gemini CLI JSONL file (line-delimited)."""
    signal = []
    with open(json_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            if not isinstance(msg, dict):
                continue
            if "$set" in msg or "kind" in msg or "sessionId" in msg:
                continue

            m_role = msg.get("type") or msg.get("role")
            if not m_role:
                continue
            ts = msg.get("timestamp", "Unknown")

            fragment = {"role": m_role, "timestamp": ts}
            tokens = msg.get("tokens", {})
            if tokens:
                fragment["tokens"] = tokens

            if m_role in ("user", "system"):
                fragment["text"] = _process_content(msg.get("content"))
            elif m_role in ("gemini", "model"):
                fragment["text"] = _process_content(msg.get("content"))
                fragment["thoughts"] = msg.get("thoughts", [])

                tool_calls = msg.get("toolCalls", []) or msg.get("tool_calls", [])
                fragment["actions"] = []
                for call in tool_calls:
                    if not isinstance(call, dict):
                        continue
                    name = call.get("name") or call.get("function", {}).get("name")
                    args = call.get("args") or call.get("function", {}).get("arguments")
                    fragment["actions"].append({
                        "tool": name,
                        "intent": str(args)[:200],
                    })
            else:
                continue

            signal.append(fragment)
    return signal


def _extract_opencode(json_path):
    """Extract signal from an OpenCode export JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    messages = data.get("messages", [])
    signal = []

    for msg in messages:
        if not isinstance(msg, dict):
            continue

        info = msg.get("info", {})
        if not isinstance(info, dict):
            continue

        m_role = info.get("role")
        if not m_role:
            continue

        ts_raw = info.get("time", {})
        ts = ts_raw.get("created", "Unknown") if isinstance(ts_raw, dict) else "Unknown"

        fragment = {"role": m_role, "timestamp": ts}
        content = msg.get("content")

        if m_role in ("user", "system"):
            fragment["text"] = _process_content(content)
        elif m_role in ("gemini", "model", "assistant"):
            fragment["text"] = _process_content(content)
            fragment["thoughts"] = msg.get("thoughts", [])

            tool_calls = msg.get("toolCalls", []) or msg.get("tool_calls", [])
            fragment["actions"] = []
            for call in tool_calls:
                if not isinstance(call, dict):
                    continue
                name = call.get("name") or call.get("function", {}).get("name")
                args = call.get("args") or call.get("function", {}).get("arguments")
                fragment["actions"].append({
                    "tool": name,
                    "intent": str(args)[:200],
                })
        else:
            continue

        signal.append(fragment)
    return signal


# ── Public API ─────────────────────────────────────────────────────

def extract_signal(json_path):
    """
    Auto-detects session file format and extracts the architectural signal.

    Supports:
      - Gemini CLI JSONL (line-delimited)
      - OpenCode export JSON ({info, messages})

    Returns a list of fragments: [{role, timestamp, text, thoughts?, actions?}]
    """
    try:
        fmt = detect_format(json_path)
        if fmt == "opencode":
            return _extract_opencode(json_path)
        else:
            return _extract_gemini(json_path)
    except Exception as e:
        return f"Extraction Error: {e}"


# ── Markdown Renderer ──────────────────────────────────────────────

def skeleton_to_markdown(skeleton, session_id):
    """
    Converts a JSON signal skeleton into a beautifully formatted
    Obsidian-native Markdown string.  Zero API cost.
    """
    md = (
        f"---\nSession: {session_id}\nType: Raw Backup\n---\n\n"
        f"# A.I.M. Signal Skeleton\n\n"
    )
    for turn in skeleton:
        if not isinstance(turn, dict):
            continue
        role = turn.get("role", "unknown").upper()
        text = turn.get("text", "").strip()
        ts = turn.get("timestamp", "")

        if role == "USER":
            md += f"## 👤 USER ({ts})\n"
            if text:
                md += f"{text}\n\n"

        elif role in ("GEMINI", "MODEL"):
            md += f"## 🤖 A.I.M. ({ts})\n"
            md += _render_thoughts_and_actions(turn)
            if text:
                md += f"{text}\n\n"

        elif role == "ASSISTANT":
            md += f"## 🤖 AGENT ({ts})\n"
            md += _render_thoughts_and_actions(turn)
            if text:
                md += f"{text}\n\n"

        md += "---\n\n"
    return md


def _render_thoughts_and_actions(turn):
    out = ""
    thoughts = turn.get("thoughts", [])
    if thoughts:
        out += "> **Internal Monologue:**\n"
        for thought in thoughts:
            if isinstance(thought, dict):
                desc = thought.get("description", "") or thought.get("text", "")
                out += f"> * {desc}\n"
            else:
                out += f"> * {thought}\n"
        out += "\n"

    actions = turn.get("actions", [])
    if actions:
        out += "**Tools Executed:**\n"
        for action in actions:
            tool = action.get("tool", "unknown")
            intent = action.get("intent", "")
            out += f"- `{tool}`: {intent}\n"
        out += "\n"
    return out


# ── CLI Entry Point ────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_signal.py <path_to_json_or_jsonl>")
        sys.exit(1)

    result = extract_signal(sys.argv[1])
    print(json.dumps(result, indent=2))
