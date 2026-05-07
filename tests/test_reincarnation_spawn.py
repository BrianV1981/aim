import unittest
import os
import sys
import json
import tempfile
import time
from unittest.mock import patch, MagicMock, call

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

    def _any_call_matches(self, mock_run, predicate):
        """Check if any subprocess.run call matches a predicate."""
        for call_args in mock_run.call_args_list:
            args = call_args[0][0]
            if predicate(args):
                return True
        return False

    @patch("builtins.input", return_value="")
    @patch("aim_core.aim_reincarnate.time.sleep")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {}, clear=True)
    def test_spawns_opencode_not_gemini(self, mock_exit, mock_run, mock_sleep, mock_input):
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
    @patch("aim_core.aim_reincarnate.time.sleep")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {}, clear=True)
    def test_spawns_with_run_subcommand(self, mock_exit, mock_run, mock_sleep, mock_input):
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
    @patch("aim_core.aim_reincarnate.time.sleep")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {}, clear=True)
    def test_spawns_with_dangerously_skip_permissions(self, mock_exit, mock_run, mock_sleep, mock_input):
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
    @patch("aim_core.aim_reincarnate.time.sleep")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {}, clear=True)
    def test_wake_up_prompt_is_passed(self, mock_exit, mock_run, mock_sleep, mock_input):
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
    @patch("aim_core.aim_reincarnate.time.sleep")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {}, clear=True)
    def test_no_gemini_references_in_spawn(self, mock_exit, mock_run, mock_sleep, mock_input):
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


class TestReincarnationTeleportBehavior(unittest.TestCase):
    """Issue #31: Teleport (tmux switch+killsession and non-tmux guidance)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.continuity_dir = os.path.join(self.test_dir, "continuity")
        os.makedirs(self.continuity_dir, exist_ok=True)
        self.gameplan_path = os.path.join(self.continuity_dir, "REINCARNATION_GAMEPLAN.md")
        with open(self.gameplan_path, "w") as f:
            f.write("# Gameplan\nProceed to next issue.")
        self.connect_path = os.path.join(self.continuity_dir, "REINCARNATION_CONNECT.md")

    def _make_safe_run(self, extra_handlers=None):
        """Factory for a safe_run side_effect that handles handoff_pulse and returns success."""
        def safe_run(*args, **kwargs):
            cmd_args = args[0] if args else []
            if isinstance(cmd_args, list):
                cmd_str = " ".join(cmd_args)
                if "handoff_pulse" in cmd_str:
                    return MagicMock(returncode=0)
                if "sync_issue_tracker" in cmd_str:
                    return MagicMock(returncode=0)
                if "aim_scraper" in cmd_str:
                    return MagicMock(returncode=0)
                # Allow tmux new-session to succeed
                if cmd_args[0] == "tmux" and "new-session" in cmd_args:
                    return MagicMock(returncode=0)
                # Allow paste-buffer and send-keys to succeed
                if cmd_args[0] == "tmux" and ("paste-buffer" in cmd_args or "send-keys" in cmd_args or "load-buffer" in cmd_args):
                    return MagicMock(returncode=0)
                # Allow kill-session to succeed
                if cmd_args[0] == "tmux" and "kill-session" in cmd_args:
                    return MagicMock(returncode=0)
                # tmux display-message for session name capture
                if cmd_args[0] == "tmux" and "display-message" in cmd_args and "-p" in cmd_args and "#S" in cmd_args:
                    result = MagicMock(returncode=0)
                    result.stdout = "old_session_42\n"
                    return result
                # Allow list-clients
                if cmd_args[0] == "tmux" and "list-clients" in cmd_args:
                    result = MagicMock(returncode=0)
                    result.stdout = "/dev/pts/5\n"
                    return result
                if extra_handlers:
                    for pattern, handler in extra_handlers:
                        if pattern in cmd_str:
                            return handler(cmd_args, kwargs)
            return MagicMock(returncode=0)
        return safe_run

    def _call_was_made(self, mock_run, predicate_str):
        """Check if any subprocess.run call list contains the given predicate string."""
        for call_args in mock_run.call_args_list:
            args = call_args[0][0]
            if isinstance(args, list):
                if predicate_str in str(args):
                    return True
        return False

    @patch("builtins.input", return_value="")
    @patch("aim_core.aim_reincarnate.time.sleep")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}, clear=True)
    def test_tmux_verifies_switch_before_kill(self, mock_exit, mock_run, mock_sleep, mock_input):
        """TMUX path: switch verification (display-message) happens before kill-session."""
        from aim_core import aim_reincarnate
        aim_reincarnate.AIM_ROOT = self.test_dir

        switch_ok_calls = []
        captured_session_name = []

        def safe_run(*args, **kwargs):
            cmd_args = args[0] if args else []
            if isinstance(cmd_args, list):
                cmd_str = " ".join(cmd_args)
                if "handoff_pulse" in cmd_str:
                    return MagicMock(returncode=0)
                if "sync_issue_tracker" in cmd_str:
                    return MagicMock(returncode=0)
                if "aim_scraper" in cmd_str:
                    return MagicMock(returncode=0)
                if cmd_args[0] == "tmux":
                    cmd_str_full = " ".join(cmd_args)
                    switch_ok_calls.append(cmd_str_full)
                    if "new-session" in cmd_args:
                        try:
                            s_idx = cmd_args.index("-s")
                            captured_session_name.append(cmd_args[s_idx + 1])
                        except (ValueError, IndexError):
                            pass
                        return MagicMock(returncode=0)
                    if "paste-buffer" in cmd_args or "send-keys" in cmd_args or "load-buffer" in cmd_args:
                        return MagicMock(returncode=0)
                    if "display-message" in cmd_args and "-p" in cmd_args:
                        if "#{session_name}" in cmd_str_full:
                            result = MagicMock(returncode=0)
                            result.stdout = (captured_session_name[0] + "\n") if captured_session_name else "unknown\n"
                            return result
                        if "#S" in cmd_args:
                            result = MagicMock(returncode=0)
                            result.stdout = "old_session_42\n"
                            return result
                    if "list-clients" in cmd_args:
                        result = MagicMock(returncode=0)
                        result.stdout = "/dev/pts/5\n"
                        return result
                    if "switch-client" in cmd_args:
                        return MagicMock(returncode=0)
                    if "kill-session" in cmd_args:
                        return MagicMock(returncode=0)
            return MagicMock(returncode=0)

        mock_run.side_effect = safe_run

        try:
            aim_reincarnate.main()
        except SystemExit:
            pass

        # Find the indices of kill-session and the verification display-message
        kill_idx = None
        verify_idx = None
        for i, call_str in enumerate(switch_ok_calls):
            if "kill-session" in call_str:
                kill_idx = i
            if "display-message" in call_str and "#{session_name}" in call_str:
                verify_idx = i

        self.assertIsNotNone(verify_idx, "Expected a verification display-message call with #{session_name}")
        self.assertIsNotNone(kill_idx, "Expected kill-session to be called when verification passes")
        self.assertLess(verify_idx, kill_idx,
                        "Verification (display-message #{session_name}) must occur BEFORE kill-session")

    @patch("builtins.input", return_value="")
    @patch("aim_core.aim_reincarnate.time.sleep")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}, clear=True)
    def test_tmux_skip_kill_when_switch_verification_fails(self, mock_exit, mock_run, mock_sleep, mock_input):
        """TMUX path: kill-session is NOT called when switch verification returns wrong session."""
        from aim_core import aim_reincarnate
        aim_reincarnate.AIM_ROOT = self.test_dir

        def safe_run(*args, **kwargs):
            cmd_args = args[0] if args else []
            if isinstance(cmd_args, list):
                cmd_str = " ".join(cmd_args)
                if "handoff_pulse" in cmd_str:
                    return MagicMock(returncode=0)
                if "sync_issue_tracker" in cmd_str:
                    return MagicMock(returncode=0)
                if "aim_scraper" in cmd_str:
                    return MagicMock(returncode=0)
                if cmd_args[0] == "tmux":
                    if "new-session" in cmd_args:
                        return MagicMock(returncode=0)
                    if "paste-buffer" in cmd_args or "send-keys" in cmd_args or "load-buffer" in cmd_args:
                        return MagicMock(returncode=0)
                    if "display-message" in cmd_args and "-p" in cmd_args:
                        if "#{session_name}" in " ".join(cmd_args):
                            result = MagicMock(returncode=0)
                            result.stdout = "some_other_session\n"  # WRONG session — switch failed
                            return result
                        if "#S" in cmd_args:
                            result = MagicMock(returncode=0)
                            result.stdout = "old_session_42\n"
                            return result
                    if "list-clients" in cmd_args:
                        result = MagicMock(returncode=0)
                        result.stdout = "/dev/pts/5\n"
                        return result
                    if "switch-client" in cmd_args:
                        return MagicMock(returncode=0)
                    if "kill-session" in cmd_args:
                        return MagicMock(returncode=0)
            return MagicMock(returncode=0)

        mock_run.side_effect = safe_run

        try:
            aim_reincarnate.main()
        except SystemExit:
            pass

        kill_called = self._call_was_made(mock_run, "kill-session")
        self.assertFalse(kill_called,
                         "kill-session must NOT be called when switch verification returns wrong session name")

    @patch("builtins.input", return_value="")
    @patch("aim_core.aim_reincarnate.time.sleep")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}, clear=True)
    def test_tmux_teleport_failure_writes_connect_file(self, mock_exit, mock_run, mock_sleep, mock_input):
        """TMUX path: when switch verification fails, REINCARNATION_CONNECT.md is written."""
        from aim_core import aim_reincarnate
        aim_reincarnate.AIM_ROOT = self.test_dir

        def safe_run(*args, **kwargs):
            cmd_args = args[0] if args else []
            if isinstance(cmd_args, list):
                cmd_str = " ".join(cmd_args)
                if "handoff_pulse" in cmd_str:
                    return MagicMock(returncode=0)
                if "sync_issue_tracker" in cmd_str:
                    return MagicMock(returncode=0)
                if "aim_scraper" in cmd_str:
                    return MagicMock(returncode=0)
                if cmd_args[0] == "tmux":
                    if "new-session" in cmd_args:
                        return MagicMock(returncode=0)
                    if "paste-buffer" in cmd_args or "send-keys" in cmd_args or "load-buffer" in cmd_args:
                        return MagicMock(returncode=0)
                    if "display-message" in cmd_args and "-p" in cmd_args:
                        if "#{session_name}" in " ".join(cmd_args):
                            result = MagicMock(returncode=0)
                            result.stdout = "wrong_session\n"
                            return result
                        if "#S" in cmd_args:
                            result = MagicMock(returncode=0)
                            result.stdout = "old_session_42\n"
                            return result
                    if "list-clients" in cmd_args:
                        result = MagicMock(returncode=0)
                        result.stdout = "/dev/pts/5\n"
                        return result
                    if "switch-client" in cmd_args:
                        return MagicMock(returncode=0)
            return MagicMock(returncode=0)

        mock_run.side_effect = safe_run

        try:
            aim_reincarnate.main()
        except SystemExit:
            pass

        self.assertTrue(os.path.exists(self.connect_path),
                        "REINCARNATION_CONNECT.md must be written when teleport verification fails")
        with open(self.connect_path, "r") as f:
            content = f.read()
        self.assertIn("tmux attach-session", content,
                      "Connect file must contain tmux attach-session instructions")
        self.assertIn("aim_reincarnation_", content,
                      "Connect file must contain the session name")

    @patch("builtins.input", return_value="")
    @patch("aim_core.aim_reincarnate.time.sleep")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {}, clear=True)
    def test_non_tmux_writes_connect_file(self, mock_exit, mock_run, mock_sleep, mock_input):
        """Non-TMUX path: REINCARNATION_CONNECT.md is written with attach instructions."""
        from aim_core import aim_reincarnate
        aim_reincarnate.AIM_ROOT = self.test_dir

        def safe_run(*args, **kwargs):
            cmd_args = args[0] if args else []
            if isinstance(cmd_args, list):
                cmd_str = " ".join(cmd_args)
                if "handoff_pulse" in cmd_str:
                    return MagicMock(returncode=0)
                if "sync_issue_tracker" in cmd_str:
                    return MagicMock(returncode=0)
                if "aim_scraper" in cmd_str:
                    return MagicMock(returncode=0)
                if cmd_args[0] == "tmux":
                    if "paste-buffer" in cmd_args or "send-keys" in cmd_args or "load-buffer" in cmd_args:
                        return MagicMock(returncode=0)
                    if "new-session" in cmd_args:
                        return MagicMock(returncode=0)
            return MagicMock(returncode=0)

        mock_run.side_effect = safe_run

        try:
            aim_reincarnate.main()
        except SystemExit:
            pass

        self.assertTrue(os.path.exists(self.connect_path),
                        "REINCARNATION_CONNECT.md must be written in non-tmux path")
        with open(self.connect_path, "r") as f:
            content = f.read()
        self.assertIn("tmux attach-session", content)
        self.assertIn("aim_reincarnation_", content)
        self.assertIn("opencode", content.lower(),
                      "Connect instructions should mention opencode")

    @patch("builtins.input", return_value="")
    @patch("aim_core.aim_reincarnate.time.sleep")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch("aim_core.aim_reincarnate.os.kill")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {}, clear=True)
    def test_non_tmux_does_not_self_terminate(self, mock_kill, mock_exit, mock_run, mock_sleep, mock_input):
        """Non-TMUX path: os.kill (self-termination) is NOT called."""
        from aim_core import aim_reincarnate
        aim_reincarnate.AIM_ROOT = self.test_dir

        def safe_run(*args, **kwargs):
            cmd_args = args[0] if args else []
            if isinstance(cmd_args, list):
                cmd_str = " ".join(cmd_args)
                if "handoff_pulse" in cmd_str:
                    return MagicMock(returncode=0)
                if "sync_issue_tracker" in cmd_str:
                    return MagicMock(returncode=0)
                if "aim_scraper" in cmd_str:
                    return MagicMock(returncode=0)
                if cmd_args[0] == "tmux":
                    if "paste-buffer" in cmd_args or "send-keys" in cmd_args or "load-buffer" in cmd_args:
                        return MagicMock(returncode=0)
                    if "new-session" in cmd_args:
                        return MagicMock(returncode=0)
            return MagicMock(returncode=0)

        mock_run.side_effect = safe_run

        try:
            aim_reincarnate.main()
        except SystemExit:
            pass

        mock_kill.assert_not_called()

    @patch("builtins.input", return_value="")
    @patch("aim_core.aim_reincarnate.time.sleep")
    @patch("aim_core.aim_reincarnate.subprocess.run")
    @patch("aim_core.aim_reincarnate.sys.exit")
    @patch.dict("aim_core.aim_reincarnate.os.environ", {}, clear=True)
    def test_non_tmux_connect_file_contains_session_name(self, mock_exit, mock_run, mock_sleep, mock_input):
        """Non-TMUX path: the connect file contains the actual spawned session name."""
        from aim_core import aim_reincarnate
        aim_reincarnate.AIM_ROOT = self.test_dir

        captured_session_name = []

        def safe_run(*args, **kwargs):
            cmd_args = args[0] if args else []
            if isinstance(cmd_args, list):
                cmd_str = " ".join(cmd_args)
                if "handoff_pulse" in cmd_str:
                    return MagicMock(returncode=0)
                if "sync_issue_tracker" in cmd_str:
                    return MagicMock(returncode=0)
                if "aim_scraper" in cmd_str:
                    return MagicMock(returncode=0)
                if cmd_args[0] == "tmux":
                    if "new-session" in cmd_args:
                        # Extract session name: it's the arg after "-s"
                        try:
                            s_idx = cmd_args.index("-s")
                            captured_session_name.append(cmd_args[s_idx + 1])
                        except (ValueError, IndexError):
                            pass
                        return MagicMock(returncode=0)
                    if "paste-buffer" in cmd_args or "send-keys" in cmd_args or "load-buffer" in cmd_args:
                        return MagicMock(returncode=0)
            return MagicMock(returncode=0)

        mock_run.side_effect = safe_run

        try:
            aim_reincarnate.main()
        except SystemExit:
            pass

        self.assertTrue(len(captured_session_name) > 0, "Expected a tmux new-session command with a session name")
        session_name = captured_session_name[0]
        self.assertTrue(os.path.exists(self.connect_path), "Connect file must exist")
        with open(self.connect_path, "r") as f:
            content = f.read()
        self.assertIn(session_name, content,
                      f"Connect file must contain the session name '{session_name}'")


if __name__ == "__main__":
    unittest.main()
