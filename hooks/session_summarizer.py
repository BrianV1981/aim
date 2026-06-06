#!/usr/bin/env python3
import sys
import json
import os
import time
import glob
import re
import subprocess

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
sys.path.append(os.path.join(AIM_ROOT, ".aim_core"))

from plugins.datajack.forensic_utils import chunk_text, get_embedding
from wiki_tools import process_wiki
from blackbox_vault import vault_session

CONFIG_PATH = os.path.join(AIM_ROOT, "core/CONFIG.json")
if not os.path.exists(CONFIG_PATH):
    sys.exit(0)

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

def ingest_file_to_db(backend, filepath, record_type="session_history"):
    session_id = os.path.basename(filepath).replace('.md', '')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    chunks = chunk_text(text)
    fragments = []
    
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
        print(f"[WATCHDOG] Beginning Two-Node Swarm Sequence for: {os.path.basename(md_path)}")
        session_id = os.path.basename(md_path).replace('.md', '')
        
        # --- PHASE 0: Immutable Black Box Vaulting ---
        match = re.search(r'(session-[a-zA-Z0-9T:-]+)', os.path.basename(md_path))
        if match:
            jsonl_filename = match.group(1) + ".jsonl"
            project_name = os.path.basename(AIM_ROOT)
            jsonl_path = os.path.expanduser(f"~/.gemini/tmp/{project_name}/chats/{jsonl_filename}")
            print(f"[WATCHDOG] Securing {jsonl_filename} into the Immutable Black Box...")
            vault_session(jsonl_path)
            
        # 1. Chunk and Stage the Raw Logs
        with open(md_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
            
        turns = transcript.split('\n---\n\n')
        chunk_size = 1000
        
        raw_logs_dir = os.path.join(AIM_ROOT, "memory/wiki", "_raw_logs")
        os.makedirs(raw_logs_dir, exist_ok=True)
        
        # Clear out any old raw logs
        for old_file in glob.glob(os.path.join(raw_logs_dir, "*.md")):
            os.remove(old_file)
        
        print(f"[WATCHDOG] Transcript has {len(turns)} turns. Staging chunks in _raw_logs/...")
        
        staged_files = []
        for i in range(0, len(turns), chunk_size):
            chunk_turns = turns[i:i + chunk_size]
            chunk_transcript = '\n---\n\n'.join(chunk_turns)
            part_suffix = f"_part{i//chunk_size + 1}" if len(turns) > chunk_size else ""
            
            raw_path = os.path.join(raw_logs_dir, f"{session_id}{part_suffix}_raw.md")
            with open(raw_path, "w", encoding="utf-8") as f_out:
                f_out.write(chunk_transcript)
            staged_files.append(raw_path)
            
        if not staged_files:
            print("[WATCHDOG] No data to process.")
            return True

        # 2. Spawn the Scribe Agent
        scribe_session_name = "scribe_agent_aim"
        wiki_dir = os.path.join(AIM_ROOT, "memory/wiki")
        
        check_cmd = subprocess.run(["tmux", "has-session", "-t", scribe_session_name], capture_output=True)
        if check_cmd.returncode == 0:
            print(f"[{scribe_session_name}] is already active. Skipping Scribe spawn.")
        else:
            print(f"[WATCHDOG] Spawning Scribe Agent to process {len(staged_files)} raw chunks...")
            subprocess.run(["tmux", "new-session", "-d", "-s", scribe_session_name, "-c", wiki_dir, "gemini --yolo"], check=True)
            time.sleep(5) # Boot time
            
            scribe_prompt = f"Wake up. You are the Scribe (Hindsight Pruner). Your specific task is to read the raw log files provided in `_raw_logs/`. You are strictly forbidden from editing the main wiki files. Extract the 'Signal Skeleton' using the Eureka Protocol: If the agent thrashed, prune the intermediate failures. Extract the original Prompt, the Negative Data (failed approaches), and the Verified Fix. Output each extraction into the `_ingest/` directory as a highly structured markdown file (e.g., `synapse_1.md`), deleting each raw log file as you finish processing it. Once `_raw_logs/` is completely empty, use run_shell_command to execute: `tmux kill-session -t {scribe_session_name}` to cleanly terminate your container."
            
            subprocess.run(["tmux", "set-buffer", scribe_prompt], check=True)
            subprocess.run(["tmux", "paste-buffer", "-t", scribe_session_name], check=True)
            time.sleep(1)
            subprocess.run(["tmux", "send-keys", "-t", scribe_session_name, "Enter"], check=True)

        # 3. The Polling Loop (Wait for Scribe to finish)
        print("[WATCHDOG] Waiting for Scribe to complete extraction...")
        while True:
            check_cmd = subprocess.run(["tmux", "has-session", "-t", scribe_session_name], capture_output=True)
            if check_cmd.returncode != 0:
                print("[WATCHDOG] Scribe has terminated. Extraction complete.")
                break
            time.sleep(10) # Check every 10 seconds

        # 4. Trigger the Scrivener/Weaver
        print("[WATCHDOG] Spawning Scrivener/Weaver Agent...")
        process_wiki()
        
        # 5. Native LanceDB Ingestion (Background process continues)
        from lance_backend import VectorBackend
        backend = VectorBackend()
        print(f"[WATCHDOG] Ingesting flight recorder natively into LanceDB...")
        ingest_file_to_db(backend, md_path, record_type="session_history")
        
        print("[WATCHDOG] Re-embedding updated Wiki pages into native LanceDB...")
        for md_file in glob.glob(os.path.join(wiki_dir, "*.md")):
            if "_ingest" not in md_file and "_raw_logs" not in md_file:
                ingest_file_to_db(backend, md_file, record_type="wiki_knowledge")
        
        print("[SUCCESS] Two-Node Swarm Sequence Complete.")
        return True

    except Exception as e:
        print(f"[FATAL] Watchdog Pipeline Error: {e}")
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
        history_dir = os.path.join(AIM_ROOT, ".archive", "history")
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
