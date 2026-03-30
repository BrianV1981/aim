import unittest
from unittest.mock import patch, MagicMock
import os
import json
import tempfile
import sys
import shutil
from datetime import datetime, timedelta

# --- ROOT DISCOVERY ---
AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(AIM_ROOT, "src"))

import memory_utils

class TestWaterfallPipeline(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "core/CONFIG.json")
        self.state_path = os.path.join(self.test_dir, "archive/scrivener_state.json")
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        
        # Mock AIM_ROOT in memory_utils
        self.original_aim_root = memory_utils.AIM_ROOT
        self.original_state_file = memory_utils.STATE_FILE
        memory_utils.AIM_ROOT = self.test_dir
        memory_utils.STATE_FILE = self.state_path

    def tearDown(self):
        memory_utils.AIM_ROOT = self.original_aim_root
        memory_utils.STATE_FILE = self.original_state_file
        shutil.rmtree(self.test_dir)

    def test_should_run_tier_logic(self):
        # Case 1: No state file exists
        self.assertTrue(memory_utils.should_run_tier("tier1", 1))
        
        # Case 2: Interval NOT met
        now = datetime.now()
        with open(self.state_path, 'w') as f:
            json.dump({"tiers": {"tier1": {"last_run": now.isoformat()}}}, f)
        
        self.assertFalse(memory_utils.should_run_tier("tier1", 1))
        
        # Case 3: Interval IS met
        last_run = now - timedelta(hours=2)
        with open(self.state_path, 'w') as f:
            json.dump({"tiers": {"tier1": {"last_run": last_run.isoformat()}}}, f)
            
        self.assertTrue(memory_utils.should_run_tier("tier1", 1))

    def test_consume_and_clean_archive(self):
        hourly_dir = os.path.join(self.test_dir, "memory/hourly")
        archive_dir = os.path.join(self.test_dir, "memory/archive")
        os.makedirs(hourly_dir, exist_ok=True)
        
        test_file = os.path.join(hourly_dir, "test_report.md")
        with open(test_file, 'w') as f:
            f.write("test content")
            
        # Execute Archive
        memory_utils.cleanup_consumed_files([test_file], cleanup_mode="archive")
        
        # Verify moved to archive
        self.assertFalse(os.path.exists(test_file))
        self.assertTrue(os.path.exists(os.path.join(archive_dir, "test_report.md")))

    def test_consume_and_clean_delete(self):
        hourly_dir = os.path.join(self.test_dir, "memory/hourly")
        os.makedirs(hourly_dir, exist_ok=True)
        
        test_file = os.path.join(hourly_dir, "test_delete.md")
        with open(test_file, 'w') as f:
            f.write("test content")
            
        # Execute Delete
        memory_utils.cleanup_consumed_files([test_file], cleanup_mode="delete")
        
        # Verify deleted
        self.assertFalse(os.path.exists(test_file))

if __name__ == '__main__':
    unittest.main()
