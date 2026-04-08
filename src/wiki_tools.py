import os
import glob
import sqlite3
import requests
from src.reasoning_utils import generate_reasoning

def get_base_dir():
    current = os.path.dirname(os.path.abspath(__file__))
    while current != '/' and not os.path.exists(os.path.join(current, "core/CONFIG.json")):
        current = os.path.dirname(current)
    return current if current != '/' else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def search_wiki(query):
    """
    Performs a lightning-fast local search over the wiki/ directory
    using an in-memory SQLite FTS5 database.
    """
    base_dir = get_base_dir()
    wiki_dir = os.path.join(base_dir, "wiki")
    
    if not os.path.exists(wiki_dir):
        print("Error: wiki/ directory not found. Please initialize the wiki first.")
        return

    # In-memory FTS5 search
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()
    c.execute('''CREATE VIRTUAL TABLE wiki_fts USING fts5(filepath, content)''')

    # Load markdown files
    md_files = glob.glob(os.path.join(wiki_dir, "*.md"))
    for file_path in md_files:
        if os.path.basename(file_path) == "WIKI_SCHEMA.md": continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                c.execute("INSERT INTO wiki_fts (filepath, content) VALUES (?, ?)", (os.path.basename(file_path), content))
        except Exception: pass
    
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
    Pings the local daemon webhook to trigger the Subconscious Daemon worker logic.
    If the daemon is unreachable, processes it directly locally.
    """
    base_dir = get_base_dir()
    ingest_dir = os.path.join(base_dir, "wiki/_ingest")
    
    if not os.path.exists(ingest_dir):
        print("Error: wiki/_ingest/ directory not found.")
        return

    files = glob.glob(os.path.join(ingest_dir, "*.*"))
    if not files:
        print("No files found in wiki/_ingest/ to process.")
        return

    print(f"Ping sent to local aim daemon webhook for {len(files)} file(s).")
    try:
        res = requests.post("http://localhost:11434/wiki-webhook", json={"action": "process_ingest"}, timeout=2)
        if res.status_code == 200:
            print("Webhook accepted. Subconscious Daemon is processing the knowledge base.")
            return
    except requests.exceptions.RequestException:
        print("Daemon unreachable on port 11434. Processing synchronously in the background (Worker mode)...")
        _subconscious_worker_logic(base_dir, files)


def _subconscious_worker_logic(base_dir, files):
    """
    The actual worker logic that reads _ingest, synthesizes markdown, and logs it.
    """
    wiki_dir = os.path.join(base_dir, "wiki")
    schema_path = os.path.join(wiki_dir, "WIKI_SCHEMA.md")
    
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            system_instruction = f.read()
    else:
        system_instruction = "You are the Subconscious Daemon. Read the raw text, synthesize into a markdown page."

    for file_path in files:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_content = f.read()
        
        prompt = f"Process this ingested file into the wiki:\\n\\nFile Name: {os.path.basename(file_path)}\\n\\nRAW CONTENT:\\n{raw_content}\\n\\nOutput ONLY the synthesized markdown content."
        
        print(f"Synthesizing {os.path.basename(file_path)}...")
        new_content = generate_reasoning(prompt, system_instruction=system_instruction)
        
        # Determine a filename (simple safe name)
        new_filename = os.path.basename(file_path).replace(".txt", ".md").replace(".json", ".md")
        if not new_filename.endswith(".md"): new_filename += ".md"
        
        dest_path = os.path.join(wiki_dir, new_filename)
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        # Log it
        log_path = os.path.join(wiki_dir, "log.md")
        with open(log_path, "a") as f:
                f.write(f"- Processed {os.path.basename(file_path)} into {new_filename}\\n")
                
        # Remove ingested file
        os.remove(file_path)
        print(f"Processed and cleaned up {os.path.basename(file_path)}")
        
    print("Wiki Knowledge Base successfully updated and synthesized.")
