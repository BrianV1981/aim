#!/usr/bin/env python3
import os
import sys
import json
import subprocess

# --- VENV BOOTSTRAP ---
hook_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(hook_dir)
venv_python = os.path.join(aim_root, "venv/bin/python3")

input_data = sys.stdin.read()

if os.path.exists(venv_python) and sys.executable != venv_python:
    try:
        process = subprocess.run([venv_python] + sys.argv, input=input_data, text=True, capture_output=True)
        print(process.stdout)
        sys.exit(process.returncode)
    except Exception as e:
        import sys; print(f"Hook bootstrap error: {e}", file=sys.stderr)
        sys.exit(1)

# --- LOGIC ---
src_dir = os.path.join(aim_root, "aim_core")
if src_dir not in sys.path: sys.path.append(src_dir)

try:
    from reasoning_utils import generate_reasoning
    from config_utils import CONFIG
except ImportError:
    print("{}")
    sys.exit(0)

def main():
    if not input_data:
        print("{}")
        return
        
    try:
        data = json.loads(input_data)
    except json.JSONDecodeError:
        print("{}")
        return
        
    user_message = data.get("message", "")
    history = data.get("messages", []) or data.get("session_history", [])
    
    if not user_message or not history:
        print("{}")
        return
        
    # Quick heuristic check for pronouns/ambiguity
    # We also check for 'it', 'this', 'that' etc.
    pronouns = {"it", "this", "that", "these", "those", "he", "she", "they", "him", "her", "them"}
    words = set(user_message.lower().replace("?", "").replace(".", "").split())
    has_pronoun = bool(pronouns.intersection(words))
    
    if not has_pronoun or len(history) < 2:
        print("{}")
        return
        
    # Build history context (last 5 turns)
    history_text = ""
    for msg in history[-5:]:
        role = msg.get("role", "unknown")
        parts = msg.get("parts", [])
        text = "".join([p.get("text", "") for p in parts])
        history_text += f"{role}: {text}\n"
        
    prompt = f"""You are a Query Rewriter. Look at the chat history and rewrite the final user message so it is completely standalone and contains no pronouns. Replace pronouns with the exact entities they refer to from the history. Do NOT answer the question. Just output the rewritten question string.

--- CHAT HISTORY ---
{history_text}

--- FINAL USER MESSAGE ---
User: {user_message}

Rewritten Query:"""

    try:
        # Epic 508 explicitly mandates qwen3.5:4b for the rewriting to stay sovereign.
        # We temporarly override the reasoning provider to ensure it stays local for this micro-task.
        # We don't want to use the cloud for coreference if possible, but we'll use default_reasoning.
        # Actually, let's just pass brain_type="default_reasoning" but force the prompt.
        rewritten = generate_reasoning(prompt, system_instruction="You are a Query Rewriter. Output ONLY the rewritten string without quotes or explanations.", brain_type="coreference_engine").strip()
        rewritten = rewritten.replace('"', '').replace('Rewritten Query:', '').strip()
        
        if rewritten and len(rewritten) > 5 and "Error" not in rewritten:
            # Overwrite the user's message with the resolved query
            print(json.dumps({"message": rewritten}))
        else:
            print("{}")
    except Exception as e:
        sys.stderr.write(f"[Coreference Error] {e}\n")
        print("{}")

if __name__ == "__main__":
    main()
