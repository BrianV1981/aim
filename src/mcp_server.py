#!/usr/bin/env python3
import os
import sys
import json
from fastmcp import FastMCP

# --- CONFIG BOOTSTRAP ---
def find_aim_root():
    current = os.path.dirname(os.path.abspath(__file__))
    while current != '/':
        if os.path.exists(os.path.join(current, "core/CONFIG.json")): return current
        current = os.path.dirname(current)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AIM_ROOT = find_aim_root()
src_dir = os.path.join(AIM_ROOT, "src")
if src_dir not in sys.path: sys.path.append(src_dir)

try:
    from retriever import perform_forensic_search
except ImportError:
    perform_forensic_search = None

# --- INITIALIZE MCP ---
mcp = FastMCP("A.I.M. Forensic Server")

@mcp.tool()
def search_engram(query: str) -> str:
    """Search the A.I.M. Engram DB for historical technical knowledge, architectural decisions, and project mandates."""
    if not perform_forensic_search:
        return "Error: A.I.M. Retriever modules not found."
    
    try:
        results = perform_forensic_search(query, top_k=5)
        if not results:
            return f"No fragments found for query: '{query}'"
        
        output = f"--- A.I.M. Forensic Search Results for: '{query}' ---\n\n"
        for i, res in enumerate(results, 1):
            source = res.get('session_file', 'Unknown')
            content = res.get('content', '')
            score = res.get('score', 0.0)
            output += f"[{i}] Score: {score:.4f} | Source: {source}\n{content}\n"
            output += "-" * 45 + "\n"
        
        return output
    except Exception as e:
        return f"Retrieval Error: {str(e)}"

@mcp.resource("aim://project-context")
def get_project_context() -> str:
    """Provides the high-level project context from GEMINI.md."""
    path = os.path.join(AIM_ROOT, "GEMINI.md")
    if os.path.exists(path):
        with open(path, 'r') as f: return f.read()
    return "GEMINI.md not found."

# ====================== PROTOTYPE UNIVERSAL SKILLS REGISTRATION ======================
# (Phase 29 manual bridge — remove once auto-scanner is live)
import subprocess
from pathlib import Path

SKILLS_DIR = Path(AIM_ROOT) / "skills"

@mcp.tool()
def run_list_recent_sessions(limit: int = 5) -> str:
    """Prototype skill: List the N most recent sessions from the Engram DB.
    This will be auto-registered by the future skills/ scanner."""
    script_path = SKILLS_DIR / "list_recent_sessions.py"
    
    if not script_path.exists():
        return json.dumps({"error": "Skill not found"})
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), str(limit)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return f"Skill error: {result.stderr.strip()}"
        return result.stdout.strip()
    except Exception as e:
        return f"Execution error: {str(e)}"
# ====================================================================================

if __name__ == "__main__":
    # MCP servers for IDEs typically use the 'stdio' transport
    mcp.run(transport="stdio")
