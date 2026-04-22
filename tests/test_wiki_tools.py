import unittest
from unittest.mock import patch, MagicMock
import os
import sqlite3
import tempfile

from src.wiki_tools import search_wiki, process_wiki

class TestWikiTools(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.base_dir = self.test_dir.name
        
        # Create mock wiki directories
        self.wiki_dir = os.path.join(self.base_dir, "memory-wiki")
        self.ingest_dir = os.path.join(self.wiki_dir, "_ingest")
        os.makedirs(self.ingest_dir, exist_ok=True)
        
        # Create some markdown files
        with open(os.path.join(self.wiki_dir, "test1.md"), "w") as f:
            f.write("# Page 1\\nThis is about the Decoupled Brain.")
            
        with open(os.path.join(self.wiki_dir, "WIKI_SCHEMA.md"), "w") as f:
            f.write("System Prompt")

    def tearDown(self):
        self.test_dir.cleanup()

if __name__ == '__main__':
    unittest.main()
