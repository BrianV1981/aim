import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from pathlib import Path

# --- BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
src_dir = os.path.join(aim_root, "aim_core")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from mcp_server import get_project_context, _parse_skill_manifest, AIM_ROOT

class TestMCPServerExtended(unittest.TestCase):
    
    @patch("mcp_server.os.path.exists")
    @patch("builtins.open", new_callable=MagicMock)
    def test_get_project_context_fallback(self, mock_open, mock_exists):
        # Setup mock to only return True for CLAUDE.md
        def exists_side_effect(path):
            if path.endswith("CLAUDE.md"):
                return True
            return False
            
        mock_exists.side_effect = exists_side_effect
        mock_file = MagicMock()
        mock_file.read.return_value = "Claude context content"
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = get_project_context()
        self.assertEqual(result, "Claude context content")
        
        # Verify open was called with CLAUDE.md
        mock_open.assert_called_once_with(os.path.join(AIM_ROOT, "CLAUDE.md"), 'r')

    @patch("mcp_server.Path.exists", return_value=True)
    @patch("mcp_server.Path.read_text", return_value="**Name:** Python Skill\n**Description:** Runs python")
    def test_parse_skill_manifest_python_suffix(self, mock_read, mock_exists):
        # We test that passing a .py skill doesn't crash on .with_suffix
        skill_path = Path("/mock/skills/my_skill.py")
        
        # This function should not throw ValueError about suffix
        result = _parse_skill_manifest(skill_path)
        
        self.assertEqual(result["name"], "Python Skill")
        self.assertEqual(result["description"], "Runs python")

if __name__ == "__main__":
    unittest.main()