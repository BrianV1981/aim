#!/usr/bin/env python3
import sys
import json
import os
import glob
from datetime import datetime

# --- DYNAMIC ROOT DISCOVERY ---
def find_aim_root():
    current = os.path.abspath(os.getcwd())
    while current != '/':
        if os.path.exists(os.path.join(current, "core", "CONFIG.json")):
            return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
sys.path.append(os.path.join(AIM_ROOT, "src"))

from reasoning_utils import generate_reasoning
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
        fragments.append((session_id, record_type, chunk, vec))
        
    db.add_fragments(fragments)

def process_transcript(md_path):
    try:
        print(f"[DAEMON] Beginning Deep Memory Synthesis for: {os.path.basename(md_path)}")
        session_id = os.path.basename(md_path).replace('.md', '')
        
        # 1. Embed raw flight recorder into project_core.db
        db_path = os.path.join(AIM_ROOT, "archive", "project_core.db")
        db = ForensicDB(db_path)
        
        print(f"[DAEMON] Ingesting flight recorder into {db_path}...")
        ingest_file_to_db(db, md_path, record_type="session_history")
        
        # 2. Extract Signal Skeleton
        with open(md_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
            
        print("[DAEMON] Extracting Signal Skeleton via LLM...")
        summary = generate_reasoning(f"### SESSION TRANSCRIPT\n{transcript}", system_instruction=EXTRACTOR_SYSTEM, brain_type="tier1")
        
        if not summary or summary.startswith("Error"):
            print(f"[ERROR] Subconscious extraction failed: {summary}")
            db.close()
            return False
            
        # 3. Drop into wiki/_ingest/
        ingest_dir = os.path.join(AIM_ROOT, "wiki", "_ingest")
        os.makedirs(ingest_dir, exist_ok=True)
        ingest_path = os.path.join(ingest_dir, f"{session_id}_summary.md")
        
        with open(ingest_path, "w", encoding="utf-8") as f:
            f.write(summary)
            
        print(f"[DAEMON] Signal Skeleton dropped into {ingest_path}")
        
        # 4. Trigger Wiki Synthesis
        print("[DAEMON] Triggering Persistent LLM Wiki Synthesis...")
        process_wiki()
        
        # 5. Re-embed the updated Wiki into project_core.db
        print("[DAEMON] Re-embedding updated Wiki pages into vector store...")
        wiki_dir = os.path.join(AIM_ROOT, "wiki")
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

    updated = 1 if process_transcript(md_path) else 0
    print(json.dumps({"decision": "proceed", "updated": updated}))

if __name__ == "__main__":
    main(sys.argv)
