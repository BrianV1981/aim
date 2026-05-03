import os
import glob
import sqlite3
import requests
from aim_core.reasoning_utils import generate_reasoning

def get_base_dir():
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
        if os.path.basename(file_path) == "AGENT.md": continue
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

    # Ensure wiki_agent session exists, dynamically named by project directory
    session_name = f"wiki_agent_{os.path.basename(base_dir)}"
    try:
        subprocess.run(["tmux", "has-session", "-t", session_name], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print(f"Starting new '{session_name}' tmux session in YOLO mode...")
        subprocess.run(["tmux", "new-session", "-d", "-s", session_name, "-c", base_dir, "gemini", "--yolo"])
        import time
        time.sleep(2) # Give it time to boot

    print(f"Handing off {len(files)} file(s) to {session_name} for processing...")
    
    prompt = "Please read the new files in memory-wiki/_ingest/ and securely weave their insights into the project lore by updating memory-wiki/index.md, memory-wiki/log.md, and creating/updating any relevant concept pages. Delete the files from _ingest/ when you are done."
    
    try:
        subprocess.run(["tmux", "set-buffer", prompt], check=True)
        subprocess.run(["tmux", "paste-buffer", "-t", session_name], check=True)
        import time; time.sleep(0.5)
        subprocess.run(["tmux", "send-keys", "-t", session_name, "Enter"], check=True)
        print(f"[SUCCESS] Directives dispatched to {session_name}.")
    except Exception as e:
        print(f"[ERROR] Failed to hand off to {session_name}: {e}")
