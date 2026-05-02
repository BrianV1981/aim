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
    Spawns a persistent OpenCode TUI co-agent in the memory-wiki directory.
    The agent reads memory-wiki/AGENT.md for wiki processing rules,
    processes _ingest/ files, and updates index.md + log.md.
    """
    import subprocess
    base_dir = get_base_dir()
    wiki_dir = os.path.join(base_dir, "memory-wiki")
    ingest_dir = os.path.join(wiki_dir, "_ingest")

    if not os.path.exists(ingest_dir):
        print("Error: memory-wiki/_ingest/ directory not found.")
        return

    files = glob.glob(os.path.join(ingest_dir, "*.*"))
    files = [f for f in files if not f.endswith('.gitkeep')]
    if not files:
        print("No files found in memory-wiki/_ingest/ to process.")
        return

    SESSION = "wiki_agent"

    # Ensure persistent wiki_agent TUI session exists (NOT run mode)
    try:
        subprocess.run(["tmux", "has-session", "-t", SESSION], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print(f"Starting persistent '{SESSION}' tmux session in memory-wiki directory...")
        subprocess.run(["tmux", "new-session", "-d", "-s", SESSION, "-c", wiki_dir, "opencode"])
        import time
        time.sleep(3)  # Wait for TUI to render and accept input

    print(f"Handing off {len(files)} file(s) to wiki_agent for processing...")

    prompt = (
        "Read AGENT.md for your wiki processing rules. "
        "Process ALL new files in _ingest/: extract key insights, "
        "update index.md and log.md, create/update relevant concept pages. "
        "Delete processed files from _ingest/ when done."
    )

    try:
        subprocess.run(["tmux", "set-buffer", prompt], check=True)
        subprocess.run(["tmux", "paste-buffer", "-t", SESSION], check=True)
        import time; time.sleep(0.5)
        subprocess.run(["tmux", "send-keys", "-t", SESSION, "Enter"], check=True)
        print("[SUCCESS] Directives dispatched to wiki_agent.")
    except Exception as e:
        print(f"[ERROR] Failed to hand off to wiki_agent: {e}")
