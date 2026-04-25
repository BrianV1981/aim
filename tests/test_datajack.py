import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile
import shutil
import json
import hashlib
import zipfile

current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
if aim_root not in sys.path:
    sys.path.append(aim_root)
    
src_dir = os.path.join(aim_root, "aim_core")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from aim_core.plugins.datajack import aim_exchange

class TestDataJackChecksums(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.cartridge_path = os.path.join(self.test_dir, "test.engram")
        self.import_dir = os.path.join(self.test_dir, "archive", "tmp_engram_import")
        aim_exchange.AIM_ROOT = self.test_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("plugins.datajack.aim_exchange.ForensicDB")
    @patch("builtins.input", return_value="y")
    def test_import_cartridge_checksum_valid(self, mock_input, mock_db):
        jsonl_path = os.path.join(self.test_dir, "session1.jsonl")
        
        content = json.dumps({"_record_type": "session", "session_id": "session1", "filename": "test.md", "mtime": 100}) + "\n"
        content += json.dumps({"_record_type": "fragment", "text": "test data", "type": "knowledge", "embedding": [0.1, 0.2], "metadata": {}}) + "\n"
        
        with open(jsonl_path, 'w') as f:
            f.write(content)
            
        hasher = hashlib.sha256()
        hasher.update(content.encode('utf-8'))
        valid_hash = hasher.hexdigest()
        
        metadata = {
            "keyword": "test",
            "payload_hash": valid_hash
        }
        with open(os.path.join(self.test_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f)
            
        with zipfile.ZipFile(self.cartridge_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(os.path.join(self.test_dir, "metadata.json"), "metadata.json")
            zf.write(jsonl_path, "session1.jsonl")
            
        aim_exchange.import_cartridge(self.cartridge_path)
        
        mock_instance = mock_db.return_value
        mock_instance.add_session.assert_called_once()
        mock_instance.add_fragments.assert_called_once()
        mock_instance.rebuild_fts.assert_called_once()

    @patch("plugins.datajack.aim_exchange.ForensicDB")
    @patch("builtins.input", return_value="y")
    def test_import_cartridge_checksum_invalid(self, mock_input, mock_db):
        jsonl_path = os.path.join(self.test_dir, "session1.jsonl")
        
        content = json.dumps({"_record_type": "session", "session_id": "session1", "filename": "test.md", "mtime": 100}) + "\n"
        with open(jsonl_path, 'w') as f:
            f.write(content)
            
        metadata = {
            "keyword": "test",
            "payload_hash": "bad_hash_12345"
        }
        with open(os.path.join(self.test_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f)
            
        with zipfile.ZipFile(self.cartridge_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(os.path.join(self.test_dir, "metadata.json"), "metadata.json")
            zf.write(jsonl_path, "session1.jsonl")
            
        aim_exchange.import_cartridge(self.cartridge_path)
        mock_db.assert_not_called()


    @patch("plugins.datajack.aim_exchange.ForensicDB")
    @patch("builtins.input", return_value="n")
    def test_import_cartridge_model_mismatch_abort(self, mock_input, mock_db):
        jsonl_path = os.path.join(self.test_dir, "session1.jsonl")
        
        content = json.dumps({"_record_type": "session", "session_id": "session1", "filename": "test.md", "mtime": 100}) + "\n"
        with open(jsonl_path, 'w') as f:
            f.write(content)
            
        hasher = hashlib.sha256()
        hasher.update(content.encode('utf-8'))
        valid_hash = hasher.hexdigest()
        
        metadata = {
            "keyword": "test",
            "payload_hash": valid_hash,
            "manifest": {
                "embedding_model": "incompatible_model_123"
            }
        }
        with open(os.path.join(self.test_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f)
            
        with zipfile.ZipFile(self.cartridge_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(os.path.join(self.test_dir, "metadata.json"), "metadata.json")
            zf.write(jsonl_path, "session1.jsonl")
            
        aim_exchange.import_cartridge(self.cartridge_path)
        mock_db.assert_not_called()

if __name__ == "__main__":
    unittest.main()
