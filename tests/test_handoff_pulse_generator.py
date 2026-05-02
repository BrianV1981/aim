import unittest
from unittest.mock import patch, MagicMock
import os
import json
import tempfile
import sys
import shutil

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(AIM_ROOT, "aim_core"))

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

    @patch("config_utils.resolve_session_sources")
    @patch("handoff_pulse_generator.extract_signal")
    def test_handoff_full_history_generation(self, mock_extract, mock_resolve):
        handoff_pulse_generator.CONTINUITY_DIR = self.continuity_dir
        handoff_pulse_generator.ARCHIVE_RAW_DIR = self.archive_dir
        handoff_pulse_generator.PULSES_DIR = self.pulses_dir
        handoff_pulse_generator.AIM_ROOT = self.test_dir

        # Mock resolve_session_sources to return a single test source
        mock_resolve.return_value = [
            ("opencode", self.archive_dir, "*.json"),
        ]

        # Create a fake raw JSON transcript to be found by glob
        transcript_path = os.path.join(self.archive_dir, "session_123.json")
        with open(transcript_path, 'w') as f:
            json.dump({"test": "data"}, f)

        mock_extract.return_value = [
            {"role": "user", "text": "Msg 1"},
            {"role": "gemini", "text": "Msg 2"},
            {"role": "user", "text": "Msg 3"},
            {"role": "gemini", "text": "Msg 4"},
            {"role": "user", "text": "Msg 5"},
        ]

        handoff_pulse_generator.generate_handoff_pulse()

        clean_path = os.path.join(self.continuity_dir, "LAST_SESSION_FLIGHT_RECORDER.md")
        self.assertTrue(os.path.exists(clean_path))

        with open(clean_path, 'r') as f:
            clean_content = f.read()

        self.assertIn("showing the entire session", clean_content)
        self.assertIn("Msg 1", clean_content)
        self.assertIn("Msg 2", clean_content)
        self.assertIn("Msg 3", clean_content)
        self.assertIn("Msg 4", clean_content)
        self.assertIn("Msg 5", clean_content)

        pulse_path = os.path.join(self.continuity_dir, "CURRENT_PULSE.md")
        self.assertTrue(os.path.exists(pulse_path))
        with open(pulse_path, 'r') as f:
            pulse_content = f.read()
            self.assertIn("Msg 1", pulse_content)
            self.assertIn("Msg 5", pulse_content)


if __name__ == "__main__":
    unittest.main()
