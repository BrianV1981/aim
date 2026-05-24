#!/usr/bin/env python3
import sys
import json
import os
import time
import glob
import re
from datetime import datetime

# --- DYNAMIC ROOT DISCOVERY ---
def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core", "CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
sys.path.append(AIM_ROOT)
sys.path.append(os.path.join(AIM_ROOT, "aim_core"))

from reasoning_utils import generate_reasoning
from plugins.datajack.forensic_utils import chunk_text, get_embedding
from wiki_tools import process_wiki
from blackbox_vault import vault_session

CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
if not os.path.exists(CONFIG_PATH):
    sys.exit(0)

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

# --- THE SUBCONSCIOUS EXTRACTION PROMPT ---
EXTRACTOR_SYSTEM = """You are the Subconscious Scribe. Analyze the following session transcript and extract the "Signal Skeleton" - the core architectural decisions, major bug fixes, newly established patterns, or important context that MUST be remembered for the future.
OUTPUT RULES:
- Output RAW Markdown only.
- Do NOT output conversational fluff.
- Be concise, direct, and factual.
- Limit to 5-7 bullet points of the most critical takeaways.
"""

def ingest_file_to_db(backend, filepath, record_type="session_history"):
    session_id = os.path.basename(filepath).replace('.md', '')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    chunks = chunk_text(text)
    fragments = []
    
    # Test embedding first to fail fast
    if chunks:
        test_vec = get_embedding(chunks[0])
        if not test_vec:
            print("[WARNING] Embedding provider is unreachable. Skipping native LanceDB ingestion.")
            return

    for chunk in chunks:
        vec = get_embedding(chunk)
        if vec and len(vec) == 768:
            fragments.append({
                'session_id': session_id,
                'type': record_type,
                'content': chunk,
                'vector': vec
            })
        
    if fragments:
        backend.add_fragments(fragments)

def process_transcript(md_path):
    try:
        print(f"[DAEMON] Beginning Deep Memory Synthesis for: {os.path.basename(md_path)}")
        session_id = os.path.basename(md_path).replace('.md', '')
        
        # --- PHASE 0: Immutable Black Box Vaulting ---
        match = re.search(r'(session-[a-zA-Z0-9T:-]+)', os.path.basename(md_path))
        if match:
            jsonl_filename = match.group(1) + ".jsonl"
            project_name = os.path.basename(AIM_ROOT)
            jsonl_path = os.path.expanduser(f"~/.gemini/tmp/{project_name}/chats/{jsonl_filename}")
            print(f"[DAEMON] Securing {jsonl_filename} into the Immutable Black Box...")
            vault_session(jsonl_path)
            
        # 1. Extract Signal Skeleton First (Unblocks Wiki Pipeline)
        with open(md_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
            
        # Chunk the transcript by turns to avoid overwhelming the LLM
        turns = transcript.split('\n---\n\n')
        chunk_size = 1000
        
        ingest_dir = os.path.join(AIM_ROOT, "memory-wiki", "_ingest")
        os.makedirs(ingest_dir, exist_ok=True)
        
        print(f"[DAEMON] Transcript has {len(turns)} turns. Chunking by {chunk_size} turns...")
        
        for i in range(0, len(turns), chunk_size):
            chunk_turns = turns[i:i + chunk_size]
            chunk_transcript = '\n---\n\n'.join(chunk_turns)
            part_suffix = f"_part{i//chunk_size + 1}" if len(turns) > chunk_size else ""
            
            print(f"[DAEMON] Extracting Signal Skeleton{part_suffix} via LLM...")
            
            max_retries = 10
            summary = ""
            for attempt in range(max_retries):
                summary = generate_reasoning(f"### SESSION TRANSCRIPT PART\n{chunk_transcript}", system_instruction=EXTRACTOR_SYSTEM, brain_type="default_reasoning")
                
                if not summary or summary.startswith("Error") or summary.startswith("Gemini CLI Error") or summary.startswith("Native CLI Exception") or summary.startswith("[ERROR:"):
                    print(f"[WARNING] Subconscious extraction failed for chunk{part_suffix}: {summary[:100] if summary else 'None'}")
                    
                    reset_match = re.search(r"reset after (?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", summary if summary else "")
                    if reset_match or "QUOTA_EXHAUSTED" in (summary or "") or "CAPACITY_LOCKOUT" in (summary or ""):
                        hours = int(reset_match.group(1)) if reset_match and reset_match.group(1) else 0
                        minutes = int(reset_match.group(2)) if reset_match and reset_match.group(2) else 60 # Default 1 hour
                        seconds = int(reset_match.group(3)) if reset_match and reset_match.group(3) else 0
                        total_sleep = (hours * 3600) + (minutes * 60) + seconds + 60 # Add 60s buffer
                        if total_sleep < 300: total_sleep = 3600 # Force at least 1 hr if parsing failed/was too small
                        print(f"[DAEMON] Quota exhausted! API needs to reset. Sleeping for {total_sleep} seconds...")
                        time.sleep(total_sleep)
                    else:
                        backoff = 30 + (attempt * 60) # 30s, 90s, 150s...
                        print(f"[DAEMON] Graceful fallback: Sleeping for {backoff} seconds before retry ({attempt+1}/{max_retries})...")
                        time.sleep(backoff)
                    continue
                else:
                    break
                    
            if not summary or summary.startswith("Error") or summary.startswith("Gemini CLI Error") or summary.startswith("Native CLI Exception") or summary.startswith("[ERROR:"):
                print(f"[FATAL] Exhausted all retries for chunk{part_suffix}. Skipping to prevent crash.")
                continue

            # 2. Drop into memory-wiki/_ingest/
            ingest_path = os.path.join(ingest_dir, f"{session_id}{part_suffix}_summary.md")
            with open(ingest_path, "w", encoding="utf-8") as f_out:
                f_out.write(summary)
            print(f"[DAEMON] Signal Skeleton dropped into {ingest_path}")
            time.sleep(5) # Pacing delay between chunks to avoid rate limits
            
        # 3. Trigger Wiki Synthesis
        print("[DAEMON] Triggering Persistent LLM Wiki Synthesis...")
        process_wiki()
        
        # 4. Embed raw flight recorder natively into LanceDB (Slow Process)
        from lance_backend import VectorBackend
        backend = VectorBackend()
        
        print(f"[DAEMON] Ingesting flight recorder natively into LanceDB...")
        ingest_file_to_db(backend, md_path, record_type="session_history")
        
        # 5. Re-embed the updated Wiki natively into LanceDB
        print("[DAEMON] Re-embedding updated Wiki pages into native LanceDB...")
        wiki_dir = os.path.join(AIM_ROOT, "memory-wiki")
        for md_file in glob.glob(os.path.join(wiki_dir, "*.md")):
            if "_ingest" not in md_file:
                ingest_file_to_db(backend, md_file, record_type="wiki_knowledge")
        
        print("[SUCCESS] Reincarnation Memory Pipeline Complete.")
        return True

    except Exception as e:
        print(f"[FATAL] Subconscious Pipeline Error: {e}")
        return False

def main(args):
    if "--reincarnate" not in args:
        print(json.dumps({}))
        return

    if os.environ.get('AIM_INTERNAL_REASONING'):
        print(json.dumps({}))
        return
    
    is_light_mode = "--light" in args
    if is_light_mode:
        print(json.dumps({}))
        return

    cognitive_mode = CONFIG.get('settings', {}).get('cognitive_mode', 'monolithic')
    if cognitive_mode == 'frontline':
        print(json.dumps({}))
        return

    md_path = None
    for arg in args[1:]:
        if arg.endswith('.md') and os.path.exists(arg):
            md_path = arg
            break
            
    if not md_path:
        history_dir = os.path.join(AIM_ROOT, "archive", "history")
        if os.path.exists(history_dir):
            transcripts = glob.glob(os.path.join(history_dir, "*.md"))
            if transcripts:
                md_path = max(transcripts, key=os.path.getmtime)
                
    if not md_path:
        print(json.dumps({}))
        return

    if "--bg" not in args:
        import subprocess
        cmd = [sys.executable, os.path.abspath(__file__), "--bg"] + args[1:]
        subprocess.Popen(cmd, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
        print(json.dumps({}))
        return

    updated = 1 if process_transcript(md_path) else 0
    if "--bg" not in args:
        print(json.dumps({}))

if __name__ == "__main__":
    main(sys.argv)
