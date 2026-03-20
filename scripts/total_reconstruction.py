#!/usr/bin/env python3
import os
import json
import glob
import sys

# --- VENV BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

from reasoning_utils import generate_reasoning, AIM_ROOT

# --- CONFIG ---
RAW_DIR = os.path.join(AIM_ROOT, "archive/raw")
MEMORY_MD_PATH = os.path.join(AIM_ROOT, "core/MEMORY.md")

def reconstruct():
    print("--- A.I.M. TOTAL KNOWLEDGE RECONSTRUCTION ---")
    transcripts = glob.glob(os.path.join(RAW_DIR, "session-*.json"))
    transcripts.sort()
    
    print(f"Analyzing {len(transcripts)} raw transcripts...")
    all_context = ""
    for i, t_path in enumerate(transcripts):
        try:
            with open(t_path, 'r') as f:
                data = json.load(f)
            essence = f"\n### SESSION: {os.path.basename(t_path)}\n"
            for msg in data.get('messages', []):
                if msg.get('type') == 'user':
                    text = " ".join([c.get('text', '') for c in msg.get('content', []) if 'text' in c])
                    essence += f"USER: {text[:200]}...\n"
                elif msg.get('type') == 'gemini':
                    essence += f"A.I.M.: {msg.get('content', '')[:300]}...\n"
                    for call in msg.get('toolCalls', []):
                        essence += f"ACTION: {call.get('name')} {json.dumps(call.get('args'))[:100]}\n"
            all_context += essence
        except: pass

    print("\n--- Generating Final Core Memory ---")
    prompt = f"""
Analyze the following project history and generate a high-fidelity core/MEMORY.md.

HISTORY:
{all_context[-20000:]}

TASK:
Produce a lean, professional MEMORY.md that captures the current project state (v1.1 Release), the technology stack (venv, SQLite engram.db, Gemini Flash), major decisions (YOLO mode, dynamic installer), and core infrastructure (hooks, src utils).

Output ONLY markdown content.
"""
    try:
        final_memory = generate_reasoning(prompt, system_instruction="You are the lead Memory Architect.")
        
        # --- SAFETY FIX: Do not write if the response contains an error message ---
        if "Error:" in final_memory or "RESOURCE_EXHAUSTED" in final_memory:
            print(f"\n[ABORT] Distillation failed with error: {final_memory[:100]}...")
            return

        final_memory = final_memory.replace("```markdown", "").replace("```md", "").replace("```", "").strip()
        with open(MEMORY_MD_PATH, 'w') as f:
            f.write(final_memory)
        print(f"\n[SUCCESS] core/MEMORY.md reconstructed.")
    except Exception as e:
        print(f"\n[ERROR] Final distillation failed: {e}")

if __name__ == "__main__":
    reconstruct()
