import unittest
import os
import sys
import json
import shutil
from pathlib import Path

# --- CONFIG BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
sys.path.append(os.path.join(aim_root, "aim_core"))

from mcp_server import run_skill
from mcp_server import _build_sandbox_command

class TestUniversalSkills(unittest.TestCase):
    def test_sandbox_command_preserves_repo_paths(self):
        root_path = Path(aim_root)
        script_path = root_path / "skills" / "list_recent_sessions.py"
        cmd = _build_sandbox_command(script_path, {"limit": 2})

        self.assertIn(str(root_path), cmd)
        self.assertIn(str(root_path / "archive"), cmd)
        self.assertIn(str(script_path), cmd)
        self.assertIn(sys.executable, cmd)

    
    def test_run_skill_not_found(self):
        result_json = run_skill("non_existent_skill_xyz", "{}")
        result = json.loads(result_json)
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])

    def test_list_recent_sessions_skill(self):
        # We assume project_core.db exists since it's the core of the project
        # This is a light integration test
        args_json = json.dumps({"limit": 2})
        result_str = run_skill("list_recent_sessions", args_json)
        
        # The result should be parsable JSON containing 'sessions'
        try:
            result = json.loads(result_str)
            self.assertIn("sessions", result)
            self.assertTrue(isinstance(result["sessions"], list))
            self.assertLessEqual(len(result["sessions"]), 2)
        except json.JSONDecodeError:
            self.fail(f"Skill returned invalid JSON: {result_str}")

    def test_advanced_memory_search_skill(self):
        args_json = json.dumps({"query": "A.I.M."})
        result_str = run_skill("advanced_memory_search", args_json)
        
        try:
            result = json.loads(result_str)
            self.assertIn("results", result)
            self.assertTrue(isinstance(result["results"], list))
        except json.JSONDecodeError:
            self.fail(f"Skill returned invalid JSON: {result_str}")

if __name__ == '__main__':
    unittest.main()
