import unittest
from unittest.mock import patch, MagicMock
import os
import json
import shutil
import tempfile
import sys

# --- ROOT DISCOVERY ---
AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(AIM_ROOT, "hooks"))
sys.path.append(os.path.join(AIM_ROOT, "src"))

import session_summarizer

class TestMemoryPipeline(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.archive_raw = os.path.join(self.test_dir, "archive/raw")
        self.hourly_log = os.path.join(self.test_dir, "memory/hourly")
        self.core_dir = os.path.join(self.test_dir, "core")
        os.makedirs(self.archive_raw)
        os.makedirs(self.hourly_log)
        os.makedirs(self.core_dir)
        
        # Create a dummy CONFIG.json
        self.config_path = os.path.join(self.core_dir, "CONFIG.json")
        self.config = {
            "paths": {
                "memory_dir": os.path.join(self.test_dir, "memory"),
                "src_dir": os.path.join(self.test_dir, "src")
            },
            "settings": {
                "archive_retention_days": 1
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("session_summarizer.generate_reasoning")
    @patch("session_summarizer.extract_signal")
    @patch("session_summarizer.AIM_ROOT")
    @patch("session_summarizer.CONFIG_PATH")
    @patch("session_summarizer.ARCHIVE_RAW_DIR")
    @patch("session_summarizer.STATE_FILE")
    @patch("session_summarizer.HOURLY_LOG_DIR")
    def test_session_summarizer_processes_transcript(self, mock_hourly, mock_state, mock_raw, mock_config_path, mock_aim_root, mock_extract, mock_generate):
        # Setup mocks
        mock_aim_root.return_value = self.test_dir
        mock_config_path.__str__.return_value = self.config_path
        mock_raw.__get__ = MagicMock(return_value=self.archive_raw) # This is tricky for constants
        
        # Instead of mocking constants, let's override them in the module
        session_summarizer.AIM_ROOT = self.test_dir
        session_summarizer.CONFIG_PATH = self.config_path
        session_summarizer.ARCHIVE_RAW_DIR = self.archive_raw
        session_summarizer.STATE_FILE = os.path.join(self.test_dir, "archive/scrivener_state.json")
        session_summarizer.HOURLY_LOG_DIR = self.hourly_log
        session_summarizer.LOCK_FILE = os.path.join(self.test_dir, ".aim.lock")
        
        # Create a fake transcript
        transcript = {
            "sessionId": "test-session-123",
            "messages": [
                {"role": "user", "content": "Hello", "timestamp": "2026-03-26T10:00:00Z"},
                {"role": "assistant", "content": "Hi", "timestamp": "2026-03-26T10:00:01Z"}
            ]
        }
        transcript_path = os.path.join(self.archive_raw, "test.json")
        with open(transcript_path, 'w') as f:
            json.dump(transcript, f)
            
        mock_extract.return_value = [{"role": "user", "content": "Hello"}]
        mock_generate.return_value = "The user said hello and the assistant replied."
        
        # Run process
        result = session_summarizer.process_local_transcript(transcript_path)
        
        self.assertTrue(result)
        
        # Verify output
        logs = os.listdir(self.hourly_log)
        self.assertEqual(len(logs), 1)
        with open(os.path.join(self.hourly_log, logs[0]), 'r') as f:
            content = f.read()
            self.assertIn("The user said hello", content)
            self.assertIn("test-session-123", content)

if __name__ == "__main__":
    unittest.main()
