import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AIM_ROOT, "aim_core"))


class TestWikiAgentCLISpawn(unittest.TestCase):
    """Phase 3, Issue #6: Wiki agent tmux spawns opencode run, not gemini."""

    @patch("glob.glob")
    @patch("subprocess.run")
    def test_wiki_agent_spawns_opencode_not_gemini(self, mock_run, mock_glob):
        """New wiki_agent tmux session spawns opencode run, not gemini --yolo."""
        mock_glob.return_value = ["test.md"]

        def run_side(*args, **kwargs):
            cmd = args[0]
            if isinstance(cmd, list) and "has-session" in cmd:
                raise __import__("subprocess").CalledProcessError(1, cmd)
            return MagicMock(returncode=0)

        mock_run.side_effect = run_side

        from aim_core.wiki_tools import process_wiki
        process_wiki()

        new_session_cmd = None
        for call_args in mock_run.call_args_list:
            args = call_args[0][0]
            if isinstance(args, list) and "new-session" in args:
                new_session_cmd = args
                break

        self.assertIsNotNone(new_session_cmd, "Expected tmux new-session")
        cmd_str = " ".join(new_session_cmd)
        self.assertIn("opencode", new_session_cmd)
        self.assertIn("run", new_session_cmd)
        self.assertIn("--dangerously-skip-permissions", new_session_cmd)
        self.assertNotIn("gemini", cmd_str.lower())
        self.assertNotIn("--yolo", cmd_str)


if __name__ == "__main__":
    unittest.main()
