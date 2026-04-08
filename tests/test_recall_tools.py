import unittest
from unittest.mock import patch, MagicMock
import os
import sqlite3
import tempfile

from src.recall_tools import run_recall

class TestRecallTools(unittest.TestCase):
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
        c.execute('''CREATE VIRTUAL TABLE history_fts USING fts5(
                        session_id UNINDEXED, 
                        timestamp UNINDEXED, 
                        content
                    )''')
        
        # Insert test data
        c.execute("INSERT INTO history VALUES ('sess1', '2023-10-01', 'Discussed the decoupled brain architecture.')")
        c.execute("INSERT INTO history_fts (session_id, timestamp, content) VALUES ('sess1', '2023-10-01', 'Discussed the decoupled brain architecture.')")
        
        c.execute("INSERT INTO history VALUES ('sess2', '2023-10-02', 'Fixed a bug with the router.')")
        c.execute("INSERT INTO history_fts (session_id, timestamp, content) VALUES ('sess2', '2023-10-02', 'Fixed a bug with the router.')")
        
        conn.commit()
        conn.close()

    def tearDown(self):
        self.test_dir.cleanup()

    @patch('src.recall_tools.get_base_dir')
    @patch('src.recall_tools.generate_reasoning')
    def test_run_recall(self, mock_generate, mock_get_base_dir):
        mock_get_base_dir.return_value = self.base_dir
        mock_generate.return_value = "The decoupled brain architecture was discussed in session sess1."

        # Act
        result = run_recall("decoupled brain architecture", limit=5)

        # Assert
        mock_generate.assert_called_once()
        args, kwargs = mock_generate.call_args
        prompt = args[0]
        
        # Check if the prompt contains the injected session that matched
        self.assertIn("sess1", prompt)
        self.assertNotIn("sess2", prompt) # sess2 doesn't match the query
        
        # Check return value
        self.assertEqual(result, "The decoupled brain architecture was discussed in session sess1.")

    @patch('src.recall_tools.get_base_dir')
    @patch('builtins.print')
    def test_run_recall_no_db(self, mock_print, mock_get_base_dir):
        mock_get_base_dir.return_value = "/fake/dir/that/does/not/exist"
        result = run_recall("query")
        self.assertIsNone(result)
        mock_print.assert_any_call("Error: Database not found at /fake/dir/that/does/not/exist/archive/history.db")

    @patch('src.recall_tools.get_base_dir')
    @patch('builtins.print')
    def test_run_recall_no_results(self, mock_print, mock_get_base_dir):
        mock_get_base_dir.return_value = self.base_dir
        result = run_recall("quantum computing", limit=5)
        self.assertIsNone(result)
        mock_print.assert_any_call("No historical context found for 'quantum computing'.")

if __name__ == '__main__':
    unittest.main()
