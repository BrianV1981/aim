import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import json

from aim_core.plugins.datajack import aim_exchange

class TestDataJackNativeROM(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.cartridge_path = os.path.join(self.test_dir, "test.parquet")
        
        # Create dummy parquet file
        with open(self.cartridge_path, "w") as f:
            f.write("dummy parquet data")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("aim_core.plugins.datajack.aim_exchange.AIM_ROOT")
    @patch("shutil.copy2")
    def test_import_parquet_cartridge(self, mock_copy2, mock_aim_root):
        mock_aim_root = self.test_dir
        # Needs to temporarily override the global AIM_ROOT inside aim_exchange
        original_aim_root = aim_exchange.AIM_ROOT
        aim_exchange.AIM_ROOT = self.test_dir
        
        try:
            aim_exchange.import_cartridge(self.cartridge_path)
            
            expected_target = os.path.join(self.test_dir, "archive", "cartridges", "test.parquet")
            mock_copy2.assert_called_once_with(self.cartridge_path, expected_target)
        finally:
            aim_exchange.AIM_ROOT = original_aim_root

    @patch("aim_core.plugins.datajack.aim_exchange.AIM_ROOT")
    @patch("shutil.copy2")
    def test_import_engram_renamed_to_parquet(self, mock_copy2, mock_aim_root):
        original_aim_root = aim_exchange.AIM_ROOT
        aim_exchange.AIM_ROOT = self.test_dir
        
        engram_path = os.path.join(self.test_dir, "test2.engram")
        with open(engram_path, "w") as f:
            f.write("dummy")
            
        try:
            aim_exchange.import_cartridge(engram_path)
            
            expected_target = os.path.join(self.test_dir, "archive", "cartridges", "test2.parquet")
            mock_copy2.assert_called_once_with(engram_path, expected_target)
        finally:
            aim_exchange.AIM_ROOT = original_aim_root

if __name__ == "__main__":
    unittest.main()