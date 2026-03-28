import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile
import shutil
import json
import hashlib
import zipfile

# Ensure aim_root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
if aim_root not in sys.path:
    sys.path.append(aim_root)
    
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Now we can safely import the plugins
from plugins.datajack import aim_exchange

class TestDataJackChecksums(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.cartridge_path = os.path.join(self.test_dir, "test.engram")
        self.import_dir = os.path.join(self.test_dir, "archive", "tmp_engram_import")
        
        # Override paths to avoid nuking real directories
        aim_exchange.AIM_ROOT = self.test_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch("plugins.datajack.aim_exchange.ForensicDB")
    @patch("builtins.input", return_value="y")
    def test_import_cartridge_checksum_valid(self, mock_input, mock_db):
        """Tests that a cartridge with a valid SHA256 payload_hash successfully imports."""
        
        # Create a fake cartridge structure
        os.makedirs(os.path.join(self.test_dir, "chunks"))
        jsonl_path = os.path.join(self.test_dir, "chunks", "session1.jsonl")
        
        # Write valid JSONL content
        content = json.dumps({"session_id": "session1", "filename": "test.md", "mtime": 100}) + "\n"
        content += json.dumps({"content": "test data", "type": "knowledge", "embedding": [0.1, 0.2], "metadata": {}}) + "\n"
        
        with open(jsonl_path, 'w') as f:
            f.write(content)
            
        # Calculate the real hash of this content
        hasher = hashlib.sha256()
        hasher.update(content.encode('utf-8'))
        valid_hash = hasher.hexdigest()
        
        # Write the metadata.json
        metadata = {
            "keyword": "test",
            "payload_hash": valid_hash
        }
        with open(os.path.join(self.test_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f)
            
        # Zip it into an engram
        with zipfile.ZipFile(self.cartridge_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(os.path.join(self.test_dir, "metadata.json"), "metadata.json")
            zf.write(jsonl_path, "chunks/session1.jsonl")
            
        # Run import
        aim_exchange.import_cartridge(self.cartridge_path)
        
        # Assert the DB was called to add the fragments (meaning it passed the checksum)
        mock_instance = mock_db.return_value
        mock_instance.add_session.assert_called_once()
        mock_instance.add_fragments.assert_called_once()
        mock_instance.rebuild_fts.assert_called_once()

    @patch("plugins.datajack.aim_exchange.ForensicDB")
    @patch("builtins.input", return_value="y")
    def test_import_cartridge_checksum_invalid(self, mock_input, mock_db):
        """Tests that a cartridge with an invalid SHA256 payload_hash aborts before touching the DB."""
        
        # Create a fake cartridge structure
        os.makedirs(os.path.join(self.test_dir, "chunks"))
        jsonl_path = os.path.join(self.test_dir, "chunks", "session1.jsonl")
        
        # Write JSONL content
        content = json.dumps({"session_id": "session1", "filename": "test.md", "mtime": 100}) + "\n"
        with open(jsonl_path, 'w') as f:
            f.write(content)
            
        # Write metadata.json with a COMPLETELY WRONG hash
        metadata = {
            "keyword": "test",
            "payload_hash": "bad_hash_12345"
        }
        with open(os.path.join(self.test_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f)
            
        # Zip it
        with zipfile.ZipFile(self.cartridge_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(os.path.join(self.test_dir, "metadata.json"), "metadata.json")
            zf.write(jsonl_path, "chunks/session1.jsonl")
            
        # Run import
        aim_exchange.import_cartridge(self.cartridge_path)
        
        # Assert the DB was NEVER instantiated or called because the checksum failed
        mock_db.assert_not_called()

if __name__ == "__main__":
    unittest.main()