import unittest
import os
import sys
import json
import tempfile
import time
from unittest.mock import patch, MagicMock

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AIM_ROOT, "aim_core"))


class TestReincarnationCLISpawn(unittest.TestCase):
    """Phase 3, Issue #5: Reincarnation spawns opencode run instead of gemini."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.continuity_dir = os.path.join(self.test_dir, "continuity")
        os.makedirs(self.continuity_dir, exist_ok=True)
        self.gameplan_path = os.path.join(self.continuity_dir, "REINCARNATION_GAMEPLAN.md")
        with open(self.gameplan_path, "w") as f:
            f.write("# Gameplan\nProceed to next issue.")

    def _capture_tmux_cmd(self, mock_run):
        """Extract the tmux new-session command from all subprocess.run calls."""
        for call_args in mock_run.call_args_list:
            args = call_args[0][0]
            if isinstance(args, list) and args[0] == "tmux" and "new-session" in args:
                return args
        return None

    @patch("builtins.input", return_value="")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {}, clear=True)
    def test_spawns_opencode_not_gemini(self, mock_exit, mock_run, mock_input):
        """The reincarnation tmux session spawns opencode, not gemini."""
        from aim_core import aim_reincarnate
        aim_reincarnate.AIM_ROOT = self.test_dir

        def safe_run(*args, **kwargs):
            if isinstance(args[0], list) and "handoff_pulse" in str(args[0]):
                return MagicMock(returncode=0)
            return MagicMock(returncode=0)

        mock_run.side_effect = safe_run

        try:
            aim_reincarnate.main()
        except SystemExit:
            pass

        tmux_cmd = self._capture_tmux_cmd(mock_run)
        self.assertIsNotNone(tmux_cmd, "Expected a tmux new-session command")
        self.assertIn("opencode", tmux_cmd)
        self.assertNotIn("gemini", tmux_cmd)

    @patch("builtins.input", return_value="")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {}, clear=True)
    def test_spawns_with_run_subcommand(self, mock_exit, mock_run, mock_input):
        """The opencode invocation uses the 'run' subcommand."""
        from aim_core import aim_reincarnate
        aim_reincarnate.AIM_ROOT = self.test_dir

        def safe_run(*args, **kwargs):
            if isinstance(args[0], list) and "handoff_pulse" in str(args[0]):
                return MagicMock(returncode=0)
            return MagicMock(returncode=0)

        mock_run.side_effect = safe_run

        try:
            aim_reincarnate.main()
        except SystemExit:
            pass

        tmux_cmd = self._capture_tmux_cmd(mock_run)
        self.assertIn("run", tmux_cmd)

    @patch("builtins.input", return_value="")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {}, clear=True)
    def test_spawns_with_dangerously_skip_permissions(self, mock_exit, mock_run, mock_input):
        """Autonomous mode uses --dangerously-skip-permissions (openCode equivalent of --yolo)."""
        from aim_core import aim_reincarnate
        aim_reincarnate.AIM_ROOT = self.test_dir

        def safe_run(*args, **kwargs):
            if isinstance(args[0], list) and "handoff_pulse" in str(args[0]):
                return MagicMock(returncode=0)
            return MagicMock(returncode=0)

        mock_run.side_effect = safe_run

        try:
            aim_reincarnate.main()
        except SystemExit:
            pass

        tmux_cmd = self._capture_tmux_cmd(mock_run)
        self.assertIn("--dangerously-skip-permissions", tmux_cmd)

    @patch("builtins.input", return_value="")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {}, clear=True)
    def test_wake_up_prompt_is_passed(self, mock_exit, mock_run, mock_input):
        """The wake-up prompt is passed as an argument to opencode run."""
        from aim_core import aim_reincarnate
        aim_reincarnate.AIM_ROOT = self.test_dir

        def safe_run(*args, **kwargs):
            if isinstance(args[0], list) and "handoff_pulse" in str(args[0]):
                return MagicMock(returncode=0)
            return MagicMock(returncode=0)

        mock_run.side_effect = safe_run

        try:
            aim_reincarnate.main()
        except SystemExit:
            pass

        tmux_cmd = self._capture_tmux_cmd(mock_run)
        self.assertIn("Wake up", str(tmux_cmd))
        self.assertIn("AGENTS.md", str(tmux_cmd))

    @patch("builtins.input", return_value="")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {}, clear=True)
    def test_no_gemini_references_in_spawn(self, mock_exit, mock_run, mock_input):
        """The entire tmux spawn command contains zero gemini references."""
        from aim_core import aim_reincarnate
        aim_reincarnate.AIM_ROOT = self.test_dir

        def safe_run(*args, **kwargs):
            if isinstance(args[0], list) and "handoff_pulse" in str(args[0]):
                return MagicMock(returncode=0)
            return MagicMock(returncode=0)

        mock_run.side_effect = safe_run

        try:
            aim_reincarnate.main()
        except SystemExit:
            pass

        tmux_cmd = self._capture_tmux_cmd(mock_run)
        cmd_str = " ".join(tmux_cmd)
        self.assertNotIn("gemini", cmd_str.lower())
        self.assertNotIn("--yolo", cmd_str)
        self.assertNotIn("--prompt-interactive", cmd_str)


if __name__ == "__main__":
    unittest.main()
