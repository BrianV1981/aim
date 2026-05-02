import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock, call

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AIM_ROOT, "aim_core"))


class TestDaemonPulseInjection(unittest.TestCase):
    """Phase 3, Issue #7: Daemon inject_pulse writes file, doesn't spawn gemini."""

    def setUp(self):
        self.test_root = tempfile.mkdtemp()
        self.core_dir = os.path.join(self.test_root, "core")
        os.makedirs(self.core_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_root)

    @patch("aim_core.daemon.subprocess.Popen")
    @patch("aim_core.daemon.log")
    @patch("aim_core.daemon.AIM_ROOT")
    def test_inject_pulse_does_not_spawn_gemini(self, mock_root, mock_log, mock_popen):
        """After Phase 3 #7, inject_pulse must NOT call Popen(['gemini', ...])."""
        mock_root.__str__ = lambda x: self.test_root
        import aim_core.daemon as daemon

        daemon.AIM_ROOT = self.test_root
        daemon.inject_pulse("Test agent, fix the tests.")

        # Check that Popen was never called with gemini
        gemini_calls = [
            c for c in mock_popen.call_args_list
            if isinstance(c[0][0], list) and "gemini" in c[0][0]
        ]
        self.assertEqual(len(gemini_calls), 0,
                         "inject_pulse must not spawn gemini chat process")

    @patch("aim_core.daemon.subprocess.Popen")
    @patch("aim_core.daemon.log")
    @patch("aim_core.daemon.AIM_ROOT")
    def test_inject_pulse_still_writes_daemon_pulse_file(self, mock_root, mock_log, mock_popen):
        """DAEMON_PULSE.md must still be written — the file is the communication channel."""
        mock_root.__str__ = lambda x: self.test_root
        import aim_core.daemon as daemon

        daemon.AIM_ROOT = self.test_root
        daemon.inject_pulse("Fix the combat loop.")

        pulse_file = os.path.join(self.test_root, "core", "DAEMON_PULSE.md")
        self.assertTrue(os.path.exists(pulse_file),
                        "inject_pulse must write core/DAEMON_PULSE.md")
        with open(pulse_file, "r") as f:
            content = f.read()
        self.assertIn("Fix the combat loop.", content)
        self.assertIn("AUTONOMIC HEARTBEAT", content)

    @patch("aim_core.daemon.subprocess.Popen")
    @patch("aim_core.daemon.log")
    @patch("aim_core.daemon.AIM_ROOT")
    def test_no_gemini_chat_anywhere(self, mock_root, mock_log, mock_popen):
        """Verify complete absence of gemini chat reference in inject_pulse source."""
        mock_root.__str__ = lambda x: self.test_root
        import aim_core.daemon as daemon
        import inspect

        daemon.AIM_ROOT = self.test_root
        source = inspect.getsource(daemon.inject_pulse)
        self.assertNotIn("gemini", source.lower(),
                         "inject_pulse source must not reference gemini")


if __name__ == "__main__":
    unittest.main()
