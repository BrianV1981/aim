import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from aim_core.sovereign_sync import export_to_parquet, import_from_parquet

class TestSovereignSync(unittest.TestCase):
    @patch('subprocess.run')
    def test_export_to_parquet(self, mock_run):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dummy memory-wiki so export_to_parquet proceeds
            wiki_dir = os.path.join(tmpdir, "memory-wiki")
            os.makedirs(wiki_dir)
            
            target_dir = os.path.join(tmpdir, "sync")
            os.makedirs(target_dir)
            
            result = export_to_parquet(tmpdir, target_dir)
            
            self.assertTrue(result)
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            self.assertEqual(args[0], "python3")
            self.assertTrue(args[1].endswith("aim_bake.py"))
            self.assertEqual(args[2], wiki_dir)
            self.assertEqual(args[3], os.path.join(target_dir, "wiki_sync.parquet"))
            
    def test_export_to_parquet_no_wiki(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = os.path.join(tmpdir, "sync")
            result = export_to_parquet(tmpdir, target_dir)
            self.assertFalse(result)

    @patch('subprocess.run')
    def test_import_from_parquet(self, mock_run):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy parquet file
            source_dir = os.path.join(tmpdir, "sync")
            os.makedirs(source_dir)
            dummy_parquet = os.path.join(source_dir, "test.parquet")
            with open(dummy_parquet, 'w') as f:
                f.write("dummy data")
                
            imported = import_from_parquet(tmpdir, source_dir)
            
            self.assertEqual(imported, 1)
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            self.assertEqual(args[0], "python3")
            self.assertTrue(args[1].endswith("aim_exchange.py"))
            self.assertEqual(args[2], "import")
            self.assertEqual(args[3], dummy_parquet)

if __name__ == "__main__":
    unittest.main()
