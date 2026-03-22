import unittest
import os
import sqlite3
import json
import shutil
import struct

# --- CONFIG BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
import sys
sys.path.append(os.path.join(aim_root, "src"))

from forensic_utils import ForensicDB

# --- MOCK IMPORTS ---
# We will create these functions in a new file `src/sovereign_sync.py`
try:
    from sovereign_sync import export_to_jsonl, import_from_jsonl
except ImportError:
    export_to_jsonl = None
    import_from_jsonl = None

class TestSovereignSync(unittest.TestCase):
    """
    TDD Phase 19: Sovereign Sync (Git-friendly Engram DB replication)
    """
    
    def setUp(self):
        self.test_db_path = os.path.join(aim_root, "archive/test_engram.db")
        self.test_sync_dir = os.path.join(aim_root, "archive/test_sync")
        
        # Ensure clean state
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        if os.path.exists(self.test_sync_dir):
            shutil.rmtree(self.test_sync_dir)
            
        os.makedirs(self.test_sync_dir, exist_ok=True)
        
        # We need a specialized ForensicDB instance pointing to our test db
        class TestDB(ForensicDB):
            def __init__(self, db_path):
                self.db_path = db_path
                self.conn = sqlite3.connect(self.db_path)
                self.cursor = self.conn.cursor()
                self._initialize_schema()
                
        self.db = TestDB(self.test_db_path)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        if os.path.exists(self.test_sync_dir):
            shutil.rmtree(self.test_sync_dir)

    def test_export_import_cycle(self):
        """RED PHASE: Verify DB -> JSONL -> DB cycle is lossless."""
        if not export_to_jsonl or not import_from_jsonl:
            self.fail("sovereign_sync module not implemented yet.")

        # 1. Seed the test database
        session_id = "test-session-123"
        self.db.add_session(session_id, "test_file.py", 1700000000.0)
        
        fragments = [
            {
                "type": "expert_knowledge",
                "content": "def test_func(): pass",
                "timestamp": "2026-03-21T12:00:00",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"chunk": 0}
            }
        ]
        self.db.add_fragments(session_id, fragments)
        
        # 2. Export to JSONL
        exported_count = export_to_jsonl(self.db, self.test_sync_dir)
        self.assertEqual(exported_count, 1, "Should export 1 session file")
        
        jsonl_path = os.path.join(self.test_sync_dir, f"{session_id}.jsonl")
        self.assertTrue(os.path.exists(jsonl_path), "JSONL file was not created")
        
        # 3. Simulate a fresh DB (wipe it)
        self.db.cursor.execute("DELETE FROM fragments")
        self.db.cursor.execute("DELETE FROM sessions")
        self.db.conn.commit()
        
        # Verify wipe
        self.db.cursor.execute("SELECT count(*) FROM fragments")
        self.assertEqual(self.db.cursor.fetchone()[0], 0)
        
        # 4. Import from JSONL
        imported_count = import_from_jsonl(self.db, self.test_sync_dir)
        self.assertEqual(imported_count, 1, "Should import 1 session file")
        
        # 5. Verify integrity
        self.db.cursor.execute("SELECT content, embedding FROM fragments WHERE session_id = ?", (session_id,))
        row = self.db.cursor.fetchone()
        self.assertIsNotNone(row, "Fragment was not restored")
        
        restored_content = row[0]
        restored_embedding_blob = row[1]
        
        self.assertEqual(restored_content, "def test_func(): pass")
        
        # Verify binary blob decode
        n = len(restored_embedding_blob) // 4
        restored_vec = list(struct.unpack(f'{n}f', restored_embedding_blob))
        
        # Due to float precision, we check with places
        self.assertAlmostEqual(restored_vec[0], 0.1, places=5)
        self.assertAlmostEqual(restored_vec[1], 0.2, places=5)
        self.assertAlmostEqual(restored_vec[2], 0.3, places=5)

if __name__ == "__main__":
    unittest.main()
