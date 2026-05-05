#!/usr/bin/env python3
import sys
import json
import os
import time
import glob
import subprocess
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

from plugins.datajack.forensic_utils import ForensicDB, chunk_text, get_embedding
from wiki_tools import process_wiki

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

def ingest_file_to_db(db, filepath, record_type="session_history"):
    session_id = os.path.basename(filepath).replace('.md', '')
    mtime = os.path.getmtime(filepath)
    db.add_session(session_id, filepath, mtime)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    chunks = chunk_text(text)
    fragments = []
    for chunk in chunks:
        vec = get_embedding(chunk)
        fragments.append({
            'type': record_type,
            'content': chunk,
            'embedding': vec
        })
        
    db.add_fragments(session_id, fragments)

def process_transcript(md_path):
    try:
        print(f"[DAEMON] Beginning Deep Memory Synthesis for: {os.path.basename(md_path)}")
        session_id = os.path.basename(md_path).replace('.md', '')
        
        # 1. Embed raw flight recorder into project_core.db
        db_path = os.path.join(AIM_ROOT, "archive", "project_core.db")
        db = ForensicDB(db_path)
        
        print(f"[DAEMON] Ingesting flight recorder into {db_path}...")
        ingest_file_to_db(db, md_path, record_type="session_history")
        
        # 2. Extract Signal Skeleton — chunk oversized transcripts (500 turns each)
        with open(md_path, 'r', encoding='utf-8') as f:
            transcript = f.read()

        # Chunk the transcript by turns to avoid overwhelming the LLM
        turns = transcript.split('\n---\n\n')
        chunk_size = 500
        
        ingest_dir = os.path.join(AIM_ROOT, "memory-wiki", "_ingest")
        os.makedirs(ingest_dir, exist_ok=True)
        fallback_spawned = False

        print(f"[DAEMON] Transcript has {len(turns)} turns. Chunking by {chunk_size} turns...")
        
        for i in range(0, len(turns), chunk_size):
            chunk_turns = turns[i:i + chunk_size]
            chunk_transcript = '\n---\n\n'.join(chunk_turns)
            part_suffix = f"_part{i//chunk_size + 1}" if len(turns) > chunk_size else ""
            
            print(f"[DAEMON] Extracting Signal Skeleton{part_suffix} via OpenCode agent...")
            
            try:
                import tempfile
                tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
                tmp.write(f"# SUBCONSCIOUS SCRIBE\n\n{EXTRACTOR_SYSTEM}\n\n---\n\n{chunk_transcript}")
                tmp.close()

                out_path = os.path.join(ingest_dir, f"{session_id}{part_suffix}_summary.md")
                prompt = (
                    f"Read the file at {tmp.name}. It contains a Subconscious Scribe mandate "
                    f"followed by a session transcript. Extract 5-7 bullet points of the most "
                    f"critical architectural decisions, bug fixes, patterns, and context. "
                    f"Output RAW markdown only. Save to {out_path}. Do NOT add conversation."
                )
                subprocess.run(
                    ["opencode", "run", "--dangerously-skip-permissions", prompt],
                    capture_output=True, text=True, timeout=180
                )
                
                if os.path.exists(out_path):
                    with open(out_path, 'r') as f:
                        summary = f.read().strip()
                    if summary and not summary.startswith("Error"):
                        print(f"[DAEMON] Signal Skeleton dropped into {out_path}")
                    else:
                        raise Exception(f"Summary invalid: {summary[:50]}")
                else:
                    raise Exception("OpenCode agent did not save summary file.")
                    
                os.unlink(tmp.name)
            except Exception as e:
                print(f"[WARNING] OpenCode extraction failed for chunk{part_suffix}: {e}")
                # Fallback: use generate_reasoning with DeepSeek API
                print(f"[DAEMON] Falling back to DeepSeek API extraction...")
                time.sleep(10)  # Rate limit stagger
                try:
                    summary = generate_reasoning(
                        f"### SESSION TRANSCRIPT PART\n{chunk_transcript}",
                        system_instruction=EXTRACTOR_SYSTEM,
                        brain_type="default_reasoning"
                    )
                    if summary and not summary.startswith("Error"):
                        ingest_path = os.path.join(ingest_dir, f"{session_id}{part_suffix}_summary.md")
                        with open(ingest_path, "w", encoding="utf-8") as f_out:
                            f_out.write(summary)
                        print(f"[DAEMON] Signal Skeleton dropped into {ingest_path} (API fallback)")
                    else:
                        fallback_spawned = True
                except Exception as api_err:
                    print(f"[FATAL] API fallback also failed: {api_err}")
                    fallback_spawned = True
        
        if fallback_spawned:
            print("[DAEMON] Some chunks failed extraction. Triggering wiki process for completed chunks.")
            process_wiki()
            db.close()
            return True
        
        # 4. Trigger Wiki Synthesis
        print("[DAEMON] Triggering Persistent LLM Wiki Synthesis...")
        process_wiki()
        
        # 5. Re-embed the updated Wiki into project_core.db
        print("[DAEMON] Re-embedding updated Wiki pages into vector store...")
        wiki_dir = os.path.join(AIM_ROOT, "memory-wiki")
        for md_file in glob.glob(os.path.join(wiki_dir, "*.md")):
            if "_ingest" not in md_file:
                ingest_file_to_db(db, md_file, record_type="wiki_knowledge")
                
        db.rebuild_fts()
        db.close()
        
        print("[SUCCESS] Reincarnation Memory Pipeline Complete.")
        return True

    except Exception as e:
        print(f"[FATAL] Subconscious Pipeline Error: {e}")
        return False

def main(args):
    if os.environ.get('AIM_INTERNAL_REASONING'):
        print(json.dumps({"decision": "skip", "reason": "internal_reasoning_loop_prevented"}))
        return
    
    is_light_mode = "--light" in args
    if is_light_mode:
        print(json.dumps({"decision": "skip", "reason": "light_mode_active"}))
        return

    cognitive_mode = CONFIG.get('settings', {}).get('cognitive_mode', 'monolithic')
    if cognitive_mode == 'frontline':
        print(json.dumps({"decision": "skip", "reason": "frontline_mode_offloads_compute"}))
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
        print(json.dumps({"decision": "skip", "reason": "no_transcript_found"}))
        return

    if "--bg" not in args:
        cmd = [sys.executable, os.path.abspath(__file__), "--bg"] + args[1:]
        subprocess.Popen(cmd, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(json.dumps({"decision": "proceed", "status": "background_task_spawned"}))
        return

    updated = 1 if process_transcript(md_path) else 0
    if "--bg" not in args:
        print(json.dumps({"decision": "proceed", "updated": updated}))

if __name__ == "__main__":
    main(sys.argv)
