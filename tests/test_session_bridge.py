import unittest
import os
import sys
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AIM_ROOT, "aim_core"))

import session_bridge


SAMPLE_SESSION_LIST = (
    "Session ID                      Title                                     Updated\n"
    "─────────────────────────────────────────────────────────────────────────────────\n"
    "ses_abc123def456AB1CdEfGhIjKlMn  Fix authentication bug                    10:30 PM\n"
    "ses_xyz789ghi012XY3ZwVuTsRqPoN  Refactor config loader                     09:15 PM\n"
    "ses_qwe456rty789QW4ErTyUiOpAsD  Add TDD test suite                         08:00 PM\n"
)

SAMPLE_EXPORT_JSON = {
    "info": {
        "id": "ses_abc123def456AB1CdEfGhIjKlMn",
        "title": "Fix authentication bug",
        "directory": "/home/user/project",
        "version": "1.14.31",
        "summary": {"additions": 50, "deletions": 10, "files": 3},
        "time": {"created": 1700000000000, "updated": 1700000100000},
    },
    "messages": [
        {"info": {"role": "user"}, "id": "msg_1", "content": "Hello"},
        {
            "info": {"role": "assistant"},
            "id": "msg_2",
            "content": "Hi there, how can I help?",
        },
    ],
}


class TestSessionBridge(unittest.TestCase):
    """Phase 2, Issue #2: OpenCode Session Bridge — TDD tests."""

    def setUp(self):
        self.test_root = tempfile.mkdtemp()
        self.archive_dir = os.path.join(self.test_root, "archive", "raw")
        os.makedirs(self.archive_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_root)

    @patch("session_bridge.subprocess.run")
    def test_list_sessions_parses_table(self, mock_run):
        """list_sessions() parses opencode session list table output."""
        mock_run.return_value = MagicMock(
            stdout=SAMPLE_SESSION_LIST, stderr="", returncode=0
        )
        sessions = session_bridge.list_sessions()
        self.assertEqual(len(sessions), 3)
        self.assertEqual(sessions[0]["id"], "ses_abc123def456AB1CdEfGhIjKlMn")
        self.assertEqual(sessions[0]["title"], "Fix authentication bug")
        self.assertEqual(sessions[1]["id"], "ses_xyz789ghi012XY3ZwVuTsRqPoN")
        self.assertEqual(sessions[2]["id"], "ses_qwe456rty789QW4ErTyUiOpAsD")

    @patch("session_bridge.subprocess.run")
    def test_list_sessions_empty_output(self, mock_run):
        """list_sessions() returns empty list when no sessions."""
        mock_run.return_value = MagicMock(
            stdout="Session ID  Title  Updated\n", stderr="", returncode=0
        )
        sessions = session_bridge.list_sessions()
        self.assertEqual(len(sessions), 0)

    @patch("session_bridge.subprocess.run")
    def test_export_session_returns_parsed_json(self, mock_run):
        """export_session() calls opencode export and returns parsed JSON."""
        mock_run.return_value = MagicMock(
            stdout=json.dumps(SAMPLE_EXPORT_JSON), stderr="Exporting session: ses_abc\n", returncode=0
        )
        data = session_bridge.export_session("ses_abc123def456AB1CdEfGhIjKlMn")
        self.assertEqual(data["info"]["id"], "ses_abc123def456AB1CdEfGhIjKlMn")
        self.assertEqual(len(data["messages"]), 2)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn("opencode", args)
        self.assertIn("export", args)
        self.assertIn("ses_abc123def456AB1CdEfGhIjKlMn", args)

    @patch("session_bridge.subprocess.run")
    def test_export_session_handles_stderr_noise(self, mock_run):
        """export_session() ignores stderr noise when parsing JSON from stdout."""
        mock_run.return_value = MagicMock(
            stdout='{"info": {"id": "ses_x"}}\n', stderr="Exporting session: ses_x\nSome warning\n", returncode=0
        )
        data = session_bridge.export_session("ses_x")
        self.assertEqual(data["info"]["id"], "ses_x")

    @patch("session_bridge.subprocess.run")
    def test_export_session_raises_on_failure(self, mock_run):
        """export_session() raises RuntimeError when subprocess fails."""
        mock_run.return_value = MagicMock(
            stdout="", stderr="Error: session not found", returncode=1
        )
        with self.assertRaises(RuntimeError):
            session_bridge.export_session("nonexistent")

    @patch("session_bridge.export_session")
    def test_bridge_to_archive_writes_json_file(self, mock_export):
        """bridge_to_archive() exports a session and writes session-<id>.json to archive."""
        mock_export.return_value = SAMPLE_EXPORT_JSON
        path = session_bridge.bridge_to_archive(
            "ses_abc123def456AB1CdEfGhIjKlMn", self.archive_dir
        )
        expected_path = os.path.join(
            self.archive_dir, "session-ses_abc123def456AB1CdEfGhIjKlMn.json"
        )
        self.assertEqual(path, expected_path)
        self.assertTrue(os.path.exists(path))
        with open(path, "r") as f:
            data = json.load(f)
        self.assertEqual(data["info"]["id"], "ses_abc123def456AB1CdEfGhIjKlMn")

    @patch("session_bridge.export_session")
    def test_bridge_to_archive_skips_if_exists(self, mock_export):
        """bridge_to_archive() skips export if session file already exists."""
        existing_path = os.path.join(
            self.archive_dir, "session-ses_xyz789ghi012XY3ZwVuTsRqPoN.json"
        )
        with open(existing_path, "w") as f:
            json.dump({"cached": True}, f)
        mtime_before = os.path.getmtime(existing_path)

        path = session_bridge.bridge_to_archive(
            "ses_xyz789ghi012XY3ZwVuTsRqPoN", self.archive_dir
        )
        self.assertEqual(path, existing_path)
        self.assertEqual(os.path.getmtime(path), mtime_before)
        mock_export.assert_not_called()

    @patch("session_bridge.export_session")
    @patch("session_bridge.list_sessions")
    def test_bridge_all_exports_every_session(self, mock_list, mock_export):
        """bridge_all() exports all listed sessions to archive."""
        mock_list.return_value = [
            {"id": "ses_a", "title": "A"},
            {"id": "ses_b", "title": "B"},
            {"id": "ses_c", "title": "C"},
        ]
        mock_export.return_value = {"info": {"id": "ses_x"}, "messages": []}
        count = session_bridge.bridge_all(self.archive_dir)
        self.assertEqual(count, 3)
        self.assertEqual(mock_export.call_count, 3)
        for sid in ["ses_a", "ses_b", "ses_c"]:
            fpath = os.path.join(self.archive_dir, f"session-{sid}.json")
            self.assertTrue(os.path.exists(fpath))

    @patch("session_bridge.export_session")
    @patch("session_bridge.list_sessions")
    def test_bridge_latest_exports_n_most_recent(self, mock_list, mock_export):
        """bridge_latest(N) exports only the N most recent sessions."""
        mock_list.return_value = [
            {"id": "ses_first", "title": "First"},
            {"id": "ses_second", "title": "Second"},
            {"id": "ses_third", "title": "Third"},
        ]
        mock_export.return_value = {"info": {"id": "ses_x"}, "messages": []}
        paths = session_bridge.bridge_latest(self.archive_dir, count=2)
        self.assertEqual(len(paths), 2)
        self.assertEqual(mock_export.call_count, 2)


if __name__ == "__main__":
    unittest.main()
