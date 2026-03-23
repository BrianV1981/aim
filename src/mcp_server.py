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

# ====================== PHASE 29 AUTO-SKILLS SCANNER ======================
import subprocess
from pathlib import Path

SKILLS_DIR = Path(AIM_ROOT) / "skills"

def _parse_skill_manifest(skill_path: Path) -> dict:
    md_path = skill_path.with_suffix("_SKILL.md") if skill_path.suffix == ".py" else skill_path.with_name(skill_path.stem + "_SKILL.md")
    if not md_path.exists():
        return {"name": skill_path.stem, "description": "No manifest found", "args": {}}
    content = md_path.read_text()
    name = content.split("**Name:**")[1].split("\n")[0].strip() if "**Name:**" in content else skill_path.stem
    desc = content.split("**Description:**")[1].split("\n")[0].strip() if "**Description:**" in content else "No description"
    return {"name": name, "description": desc, "args": {}}

@mcp.tool()
def run_skill(skill_name: str, args_json: str = "{}") -> str:
    """Universal skill dispatcher. Call any custom script in the skills/ folder.
    Use this to run custom workflows. Check the skills/ folder for available skills."""
    script_path = SKILLS_DIR / f"{skill_name}.py"
    if not script_path.exists():
        script_path = SKILLS_DIR / f"{skill_name}.sh"
        if not script_path.exists():
            return json.dumps({"error": f"Skill '{skill_name}' not found"})
    
    try:
        if script_path.suffix == ".sh":
            cmd = ["bash", str(script_path)]
        else:
            cmd = [sys.executable, str(script_path)]
            
        args_dict = json.loads(args_json) if args_json and args_json != "{}" else {}
        if args_dict:
            # Pass as a JSON string argument so the script can parse it
            cmd.append(json.dumps(args_dict))
            
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=AIM_ROOT
        )
        return result.stdout.strip() or result.stderr.strip() or "Skill completed with no output"
    except Exception as e:
        return json.dumps({"error": str(e)})
# ====================================================================================

if __name__ == "__main__":
    # MCP servers for IDEs typically use the 'stdio' transport
    mcp.run(transport="stdio")
