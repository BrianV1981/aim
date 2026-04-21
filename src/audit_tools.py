import os
import sqlite3
from src.reasoning_utils import generate_reasoning

def get_base_dir():
    current = os.path.dirname(os.path.abspath(__file__))
    while current != '/' and not (os.path.exists(os.path.join(current, "core/CONFIG.json")) or os.path.exists(os.path.join(current, "setup.sh"))):
        current = os.path.dirname(current)
    return current if current != '/' else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_audit(n_sessions=5):
    """
    Pulls the last N sessions from archive/history.db and generates
    a WEEKLY_SITREP.md report for the human operator.
    """
    base_dir = get_base_dir()
    db_path = os.path.join(base_dir, "archive/history.db")
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return
        
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT session_id, timestamp, content FROM history ORDER BY timestamp DESC LIMIT ?", (n_sessions,))
        rows = c.fetchall()
        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")
        return

    if not rows:
        print("No historical sessions found to audit.")
        return

    # Combine sessions into a single context
    context = ""
    for row in reversed(rows):
        session_id, timestamp, content = row
        context += f"--- Session: {session_id} | Date: {timestamp} ---\n{content}\n\n"

    print(f"Auditing last {len(rows)} sessions. Generating Strategic Synthesis...")
    
    prompt = f"Analyze the following {len(rows)} recent A.I.M. sessions and generate a comprehensive strategic synthesis.\n\n"
    prompt += "Output a WEEKLY_SITREP.md formatted report containing:\n"
    prompt += "1. Executive Summary\n2. Key Achievements & Completed Tasks\n3. Outstanding Issues & Blockers\n4. Recommended Next Steps (Roadmap Proposal)\n\n"
    prompt += "Do not include any introductory conversation. Output pure markdown.\n\n"
    prompt += f"SESSIONS CONTEXT:\n{context}"

    system_instruction = "You are A.I.M. (Actual Intelligent Memory), a senior technical lead. Your job is to analyze historical terminal sessions and synthesize a high-level strategic report."
    
    report_content = generate_reasoning(prompt, system_instruction=system_instruction)

    report_path = os.path.join(base_dir, "WEEKLY_SITREP.md")
    with open(report_path, "w") as f:
        f.write(report_content)
        
    print(f"\n[SUCCESS] Strategic Synthesis complete! Report generated at: {report_path}")
    print("Please review the WEEKLY_SITREP.md file and create new `aim bug` tickets based on the insights.")
