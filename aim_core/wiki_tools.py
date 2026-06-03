import os
import glob
import sqlite3
import requests
try:
    from aim_core.reasoning_utils import generate_reasoning
except ImportError:
    from reasoning_utils import generate_reasoning

def get_base_dir():
    # First, try to resolve from the current working directory (crucial for decoupled child projects)
    current = os.path.abspath(os.getcwd())
    while current != '/' and not (os.path.exists(os.path.join(current, "core/CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh"))):
        current = os.path.dirname(current)
    if current != '/': return current
    
    # Fallback to the global engine path
    current = os.path.dirname(os.path.abspath(__file__))
    while current != '/' and not (os.path.exists(os.path.join(current, "core/CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh"))):
        current = os.path.dirname(current)
    return current if current != '/' else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def search_wiki(query):
    """
    Performs a lightning-fast local search over the memory-wiki/ directory
    using an in-memory SQLite FTS5 database.
    """
    base_dir = get_base_dir()
    wiki_dir = os.path.join(base_dir, "memory-wiki")
    
    if not os.path.exists(wiki_dir):
        print("Error: memory-wiki/ directory not found. Please initialize the wiki first.")
        return

    # In-memory FTS5 search
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()
    c.execute('''CREATE VIRTUAL TABLE wiki_fts USING fts5(filepath, content)''')

    # Load markdown files
    md_files = glob.glob(os.path.join(wiki_dir, "*.md"))
    for file_path in md_files:
        if os.path.basename(file_path) == "GEMINI.md": continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                c.execute("INSERT INTO wiki_fts (filepath, content) VALUES (?, ?)", (os.path.basename(file_path), content))
        except Exception as e:
            import sys; print(f"[WARN] Failed to read {file_path}: {e}", file=sys.stderr)
    
    # Query
    try:
        c.execute("SELECT filepath, snippet(wiki_fts, 1, '>>', '<<', '...', 64) FROM wiki_fts WHERE wiki_fts MATCH ? ORDER BY rank LIMIT 5", (query,))
        results = c.fetchall()
    except sqlite3.OperationalError:
        # Fallback to basic LIKE if query is invalid FTS syntax
        c.execute("SELECT filepath, substr(content, 1, 200) FROM wiki_fts WHERE content LIKE ? LIMIT 5", (f"%{query}%",))
        results = c.fetchall()
        
    conn.close()

    if not results:
        print(f"No results found in Wiki for '{query}'.")
        return

    print(f"\\n--- 🔍 WIKI SEARCH RESULTS: '{query}' ---")
    for filepath, snippet in results:
        print(f"\\n📄 {filepath}:\\n{snippet}\\n")
    print("-----------------------------------")


def process_wiki():
    """
    Hands off the ingest processing to a dedicated 'wiki_agent' tmux session
    running the gemini CLI in YOLO mode, allowing it to natively read and write 
    the markdown files.
    """
    import subprocess
    base_dir = get_base_dir()
    ingest_dir = os.path.join(base_dir, "memory-wiki/_ingest")
    
    if not os.path.exists(ingest_dir):
        print("Error: memory-wiki/_ingest/ directory not found.")
        return

    files = glob.glob(os.path.join(ingest_dir, "*.*"))
    if not files:
        print("No files found in memory-wiki/_ingest/ to process.")
        return

    # Enforce a single static Subconscious Scribe to prevent file collisions
    session_name = f"wiki_agent_{os.path.basename(base_dir)}"
    wiki_dir = os.path.join(base_dir, "memory-wiki")
    
    # Check if the agent is already running and processing the queue
    check_cmd = subprocess.run(["tmux", "has-session", "-t", session_name], capture_output=True)
    if check_cmd.returncode == 0:
        print(f"[{session_name}] is already active and processing the queue. Skipping new spawn.")
        return
        
    print(f"Starting fresh '{session_name}' tmux session in YOLO mode...")
    subprocess.run(["tmux", "new-session", "-d", "-s", session_name, "-c", wiki_dir, "bash", "-c", "cd {} && source ~/.bashrc 2>/dev/null; gemini --yolo".format(wiki_dir)])
    import time
    time.sleep(5) # Give it time to boot

    print(f"Handing off {len(files)} file(s) to {session_name} for processing...")

    prompt = f"Wake up. You are the LLM Wiki Maintainer. 1. IMMEDIATELY read `AGENT.md` in this directory to understand your core directives for building a persistent, compounding knowledge base. 2. You have new session chunks waiting in the `_ingest/` directory. You MUST process them methodically ONE BY ONE: 3. Read the first chunk. 4. Weave its architectural insights into `index.md`, `log.md`, entity pages, or relevant concept pages. Ensure cross-references are actively updated. 5. Immediately DELETE that specific chunk from `_ingest/` before moving to the next. 6. Repeat until the `_ingest/` directory is completely empty. 7. Once empty, use run_shell_command to execute: `tmux kill-session -t {session_name}` to cleanly terminate this container."

    try:
        subprocess.run(["tmux", "set-buffer", prompt], check=True)
        subprocess.run(["tmux", "paste-buffer", "-t", session_name], check=True)
        import time; time.sleep(1)
        subprocess.run(["tmux", "send-keys", "-t", session_name, "Enter"], check=True)
        print(f"[SUCCESS] Directives dispatched to {session_name}.")
    except Exception as e:
        print(f"[ERROR] Failed to hand off to {session_name}: {e}")
