import unittest
from unittest.mock import patch, MagicMock
import os
import json
import tempfile
import sys
import shutil

# --- ROOT DISCOVERY ---
AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(AIM_ROOT, "src"))
sys.path.append(os.path.join(AIM_ROOT, "scripts"))

import handoff_pulse_generator

class TestHandoffPulseGenerator(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.continuity_dir = os.path.join(self.test_dir, "continuity")
        self.archive_dir = os.path.join(self.test_dir, "archive", "raw")
        self.pulses_dir = os.path.join(self.test_dir, "pulses")
        os.makedirs(self.continuity_dir)
        os.makedirs(self.archive_dir)
        os.makedirs(self.pulses_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("handoff_pulse_generator.generate_reasoning")
    @patch("handoff_pulse_generator.extract_signal")
    def test_handoff_context_tail_limit(self, mock_extract, mock_generate):
        # Override module constants for testing
        handoff_pulse_generator.CONTINUITY_DIR = self.continuity_dir
        handoff_pulse_generator.ARCHIVE_RAW_DIR = self.archive_dir
        handoff_pulse_generator.PULSES_DIR = self.pulses_dir
        handoff_pulse_generator.AIM_ROOT = self.test_dir
        
        # Override config to set a custom tail limit (e.g., 2)
        handoff_pulse_generator.CONFIG = {
            "settings": {
                "handoff_context_tail": 2
            }
        }
        
        # Create a fake raw JSON transcript to be found by glob
        transcript_path = os.path.join(self.archive_dir, "session_123.json")
        with open(transcript_path, 'w') as f:
            json.dump({"test": "data"}, f)
            
        # Mock extract_signal to return a list of 5 messages
        mock_extract.return_value = [
            {"role": "user", "text": "Msg 1"},
            {"role": "gemini", "text": "Msg 2"},
            {"role": "user", "text": "Msg 3"},
            {"role": "gemini", "text": "Msg 4"},
            {"role": "user", "text": "Msg 5"}
        ]
        
        # Mock LLM generation
        mock_generate.return_value = "Test Pulse Output"
        
        # We need to mock glob to ensure it finds our fake file instead of native cli dir
        with patch('handoff_pulse_generator.glob.glob') as mock_glob:
            # First call is for native_cli_dir, return empty. Second is for ARCHIVE_RAW_DIR.
            mock_glob.side_effect = [[], [transcript_path]]
            
            # Execute
            handoff_pulse_generator.generate_handoff_pulse()
            
        # Verify LAST_SESSION_CLEAN.md respects the tail limit of 2
        clean_path = os.path.join(self.continuity_dir, "LAST_SESSION_CLEAN.md")
        self.assertTrue(os.path.exists(clean_path))
        
        with open(clean_path, 'r') as f:
            clean_content = f.read()
            
        # It should contain the header
        self.assertIn("showing only the last 2 turns", clean_content)
        
        # It should ONLY contain Msg 4 and Msg 5 (the last 2 turns)
        self.assertNotIn("Msg 1", clean_content)
        self.assertNotIn("Msg 2", clean_content)
        self.assertNotIn("Msg 3", clean_content)
        self.assertIn("Msg 4", clean_content)
        self.assertIn("Msg 5", clean_content)
        
        # Verify the CURRENT_PULSE.md was created
        pulse_path = os.path.join(self.continuity_dir, "CURRENT_PULSE.md")
        self.assertTrue(os.path.exists(pulse_path))
        with open(pulse_path, 'r') as f:
            self.assertIn("Test Pulse Output", f.read())

if __name__ == "__main__":
    unittest.main()