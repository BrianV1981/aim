import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile
import shutil

# Ensure hooks dir is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
hooks_dir = os.path.join(aim_root, "hooks")
if hooks_dir not in sys.path:
    sys.path.append(hooks_dir)

# We have to mock sys.stdin before importing context_injector because it reads sys.stdin on import
import io
sys.stdin = io.StringIO("{}")

import context_injector

class TestContextInjector(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.continuity_dir = os.path.join(self.test_dir, "continuity")
        self.core_dir = os.path.join(self.test_dir, "core")
        os.makedirs(self.continuity_dir)
        os.makedirs(self.core_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("context_injector.CONFIG")
    def test_get_pulse_and_tail_returns_all_files(self, mock_config):
        mock_config.__getitem__.return_value = {
            'continuity_dir': self.continuity_dir,
            'core_dir': self.core_dir
        }
        mock_config.get.return_value = {
            'continuity_dir': self.continuity_dir,
            'core_dir': self.core_dir
        }
        
        # Create the fake files
        pulse_path = os.path.join(self.continuity_dir, "CURRENT_PULSE.md")
        tail_path = os.path.join(self.continuity_dir, "FALLBACK_TAIL.md")
        core_mem_path = os.path.join(self.continuity_dir, "CORE_MEMORY.md")
        anchor_path = os.path.join(self.core_dir, "ANCHOR.md")
        
        with open(pulse_path, 'w') as f: f.write("PULSE DATA")
        with open(tail_path, 'w') as f: f.write("TAIL DATA")
        with open(core_mem_path, 'w') as f: f.write("CORE MEMORY DATA")
        with open(anchor_path, 'w') as f: f.write("ANCHOR DATA")
        
        pulse, tail, anchor, core_mem = context_injector.get_pulse_and_tail()
        
        self.assertEqual(pulse, "PULSE DATA")
        self.assertEqual(tail, "TAIL DATA")
        self.assertEqual(anchor, "ANCHOR DATA")
        self.assertEqual(core_mem, "CORE MEMORY DATA")

    @patch("context_injector.CONFIG")
    def test_get_pulse_and_tail_handles_missing_files(self, mock_config):
        mock_config.__getitem__.return_value = {
            'continuity_dir': self.continuity_dir,
            'core_dir': self.core_dir
        }
        mock_config.get.return_value = {
            'continuity_dir': self.continuity_dir,
            'core_dir': self.core_dir
        }
        
        # We don't create any files. They should return None without crashing
        pulse, tail, anchor, core_mem = context_injector.get_pulse_and_tail()
        
        self.assertIsNone(pulse)
        self.assertIsNone(tail)
        self.assertIsNone(anchor)
        self.assertIsNone(core_mem)

if __name__ == "__main__":
    unittest.main()