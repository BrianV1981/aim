import unittest
from unittest.mock import patch, MagicMock
import os
import sqlite3
import tempfile

from aim_core.audit_tools import run_audit

class TestAuditTools(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.base_dir = self.test_dir.name
        
        # Create mock archive directory and db
        os.makedirs(os.path.join(self.base_dir, "archive"), exist_ok=True)
        self.db_path = os.path.join(self.base_dir, "archive/history.db")
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE history (
                        session_id TEXT PRIMARY KEY,
                        timestamp TEXT,
                        content TEXT
                    )''')
        c.execute("INSERT INTO history VALUES ('sess1', '2023-10-01', 'Did some work on phase 1.')")
        c.execute("INSERT INTO history VALUES ('sess2', '2023-10-02', 'Fixed a bug.')")
        conn.commit()
        conn.close()

    def tearDown(self):
        self.test_dir.cleanup()

    @patch('aim_core.audit_tools.get_base_dir')
    @patch('aim_core.audit_tools.generate_reasoning')
    def test_run_audit(self, mock_generate, mock_get_base_dir):
        mock_get_base_dir.return_value = self.base_dir
        mock_generate.return_value = "# WEEKLY_SITREP\n\nAll good."

        run_audit(2)

        mock_generate.assert_called_once()
        args, kwargs = mock_generate.call_args
        prompt = args[0]
        
        # Check if the prompt contains the injected sessions
        self.assertIn("sess1", prompt)
        self.assertIn("sess2", prompt)
        
        # Check if file was created
        report_path = os.path.join(self.base_dir, "WEEKLY_SITREP.md")
        self.assertTrue(os.path.exists(report_path))
        
        with open(report_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, "# WEEKLY_SITREP\n\nAll good.")

    @patch('aim_core.audit_tools.get_base_dir')
    @patch('builtins.print')
    def test_run_audit_no_db(self, mock_print, mock_get_base_dir):
        mock_get_base_dir.return_value = "/fake/dir/that/does/not/exist"
        run_audit(2)
        mock_print.assert_any_call("Error: Database not found at /fake/dir/that/does/not/exist/archive/history.db")

if __name__ == '__main__':
    unittest.main()
