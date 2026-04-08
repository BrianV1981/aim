import unittest
from unittest.mock import patch, MagicMock
import os
import sqlite3
import tempfile

from src.wiki_tools import search_wiki, process_wiki, _subconscious_worker_logic

class TestWikiTools(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.base_dir = self.test_dir.name
        
        # Create mock wiki directories
        self.wiki_dir = os.path.join(self.base_dir, "wiki")
        self.ingest_dir = os.path.join(self.wiki_dir, "_ingest")
        os.makedirs(self.ingest_dir, exist_ok=True)
        
        # Create some markdown files
        with open(os.path.join(self.wiki_dir, "test1.md"), "w") as f:
            f.write("# Page 1\\nThis is about the Decoupled Brain.")
            
        with open(os.path.join(self.wiki_dir, "WIKI_SCHEMA.md"), "w") as f:
            f.write("System Prompt")

    def tearDown(self):
        self.test_dir.cleanup()

    @patch('src.wiki_tools.get_base_dir')
    @patch('builtins.print')
    def test_search_wiki_success(self, mock_print, mock_get_base_dir):
        mock_get_base_dir.return_value = self.base_dir
        search_wiki("decoupled")
        
        # Check that it printed results containing "test1.md"
        called_with_test1 = any("test1.md" in str(call) for call in mock_print.call_args_list)
        self.assertTrue(called_with_test1)

    @patch('src.wiki_tools.get_base_dir')
    @patch('builtins.print')
    def test_search_wiki_not_found(self, mock_print, mock_get_base_dir):
        mock_get_base_dir.return_value = "/fake/dir"
        search_wiki("decoupled")
        mock_print.assert_any_call("Error: wiki/ directory not found. Please initialize the wiki first.")

    @patch('src.wiki_tools.get_base_dir')
    @patch('src.wiki_tools.generate_reasoning')
    def test_process_wiki_worker_logic(self, mock_generate, mock_get_base_dir):
        mock_get_base_dir.return_value = self.base_dir
        mock_generate.return_value = "# Synthesized Content"
        
        # Create an ingest file
        ingest_file = os.path.join(self.ingest_dir, "raw_notes.txt")
        with open(ingest_file, "w") as f:
            f.write("Some raw notes here.")
            
        _subconscious_worker_logic(self.base_dir, [ingest_file])
        
        # File should be removed
        self.assertFalse(os.path.exists(ingest_file))
        
        # Markdown file should be created in wiki/
        dest_md = os.path.join(self.wiki_dir, "raw_notes.md")
        self.assertTrue(os.path.exists(dest_md))
        with open(dest_md, "r") as f:
            self.assertEqual(f.read(), "# Synthesized Content")
            
        # Log should be updated
        log_path = os.path.join(self.wiki_dir, "log.md")
        self.assertTrue(os.path.exists(log_path))

if __name__ == '__main__':
    unittest.main()
