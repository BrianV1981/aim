import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure scripts dir is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
scripts_dir = os.path.join(aim_root, "scripts")
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

import aim_doctor

class TestAimDoctor(unittest.TestCase):
    
    @patch("aim_doctor.subprocess.run")
    def test_check_command_success(self, mock_run):
        # Should return True if subprocess succeeds
        result = aim_doctor.check_command(["git", "--version"], "Git")
        self.assertTrue(result)
        mock_run.assert_called_once()
        
    @patch("aim_doctor.subprocess.run")
    def test_check_command_failure(self, mock_run):
        import subprocess
        # Should return False if subprocess fails
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        result = aim_doctor.check_command(["git", "--version"], "Git")
        self.assertFalse(result)

    def test_check_python_version(self):
        # We are running this in python 3.10+, so this should be True natively
        # But we can mock sys.version_info to test failure
        import collections
        VersionInfo = collections.namedtuple('VersionInfo', ['major', 'minor', 'micro', 'releaselevel', 'serial'])
        
        with patch("sys.version_info", VersionInfo(3, 9, 0, 'final', 0)):
            self.assertFalse(aim_doctor.check_python_version())
        
        with patch("sys.version_info", VersionInfo(3, 11, 0, 'final', 0)):
            self.assertTrue(aim_doctor.check_python_version())

    @patch("aim_doctor.sqlite3.connect")
    def test_check_sqlite_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("3.45.1",)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        self.assertTrue(aim_doctor.check_sqlite())

    @patch("aim_doctor.sqlite3.connect")
    def test_check_sqlite_failure(self, mock_connect):
        mock_connect.side_effect = Exception("SQLite Error")
        self.assertFalse(aim_doctor.check_sqlite())

    @patch("sys.platform", "linux")
    def test_check_keyring_deps_linux_missing(self):
        # Test when dbus is missing on linux
        with patch.dict("sys.modules", {"dbus": None}):
            # Should still return True (it just warns)
            self.assertTrue(aim_doctor.check_keyring_deps())

    @patch("sys.platform", "darwin")
    def test_check_keyring_deps_mac(self):
        self.assertTrue(aim_doctor.check_keyring_deps())

if __name__ == "__main__":
    unittest.main()