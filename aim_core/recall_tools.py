import os
import sqlite3
from aim_core.reasoning_utils import generate_reasoning

def get_base_dir():
    current = os.path.dirname(os.path.abspath(__file__))
    while current != '/' and not (os.path.exists(os.path.join(current, "core/CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh"))):
        current = os.path.dirname(current)
    return current if current != '/' else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_recall(query, limit=5):
    """
    Queries the archive/history.db (using FTS5 if available) for the specific query.
    Synthesizes the matching session contexts to answer the user's question directly.
    """
    base_dir = get_base_dir()
    db_path = os.path.join(base_dir, "archive/history.db")
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return None
        
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # We query the FTS table
        c.execute('''
            SELECT session_id, timestamp, content 
            FROM history_fts 
            WHERE history_fts MATCH ? 
            ORDER BY rank 
            LIMIT ?
        ''', (query, limit))
        
        rows = c.fetchall()
        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")
        return None

    if not rows:
        print(f"No historical context found for '{query}'.")
        return None

    # Combine matching sessions into a single context
    context = ""
    for row in rows:
        session_id, timestamp, content = row
        context += f"--- Session: {session_id} | Date: {timestamp} ---\n{content}\n\n"

    print(f"Recalling memory from {len(rows)} historical session(s)...")
    
    prompt = f"You are tasked with answering a user's question using ONLY the provided historical session transcripts.\n"
    prompt += f"Question/Query: \"{query}\"\n\n"
    prompt += "Synthesize the findings and output a precise memory recall of the exact conversation context.\n"
    prompt += "Do not hallucinate external knowledge. If the answer is not in the context, state that you cannot recall.\n\n"
    prompt += f"HISTORICAL CONTEXT:\n{context}"

    system_instruction = "You are the A.I.M. Panopticon Protocol. You provide exact, synthesized memory recall based only on the provided session JSON transcripts."
    
    synthesis = generate_reasoning(prompt, system_instruction=system_instruction)

    print("\n--- 🧠 MEMORY RECALL ---\n")
    print(synthesis)
    print("\n------------------------")
    
    return synthesis
