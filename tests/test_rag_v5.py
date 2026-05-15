import unittest
from unittest.mock import patch, MagicMock
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
if aim_root not in sys.path:
    sys.path.append(aim_root)

src_dir = os.path.join(aim_root, "aim_core")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from aim_core.legacy_sqlite import ForensicDB
from aim_core.retriever import expand_sandwich_context

class TestRAGv5Ingestion(unittest.TestCase):
    @patch('aim_core.plugins.datajack.forensic_utils.get_embedding', return_value=[0.1]*768)
    def test_dynamic_chunking_massive_document(self, mock_get_embedding):
        db = ForensicDB(":memory:")
        massive_text = "A" * 3000
        db.ingest_document("test_session_1", massive_text, record_type="session_history")
        
        db.cursor.execute("SELECT id, parent_id, content FROM fragments WHERE session_id='test_session_1'")
        rows = db.cursor.fetchall()
        
        parents = [r for r in rows if r[1] is None]
        children = [r for r in rows if r[1] is not None]
        
        self.assertEqual(len(parents), 1, "Should have 1 parent for massive text")
        self.assertGreater(len(children), 1, "Should have multiple overlapping children chunks")

    @patch('aim_core.plugins.datajack.forensic_utils.get_embedding', return_value=[0.1]*768)
    def test_contextual_embedding(self, mock_get_embedding):
        db = ForensicDB(":memory:")
        text = "Small conversational turn."
        db.ingest_document("test_session_2", text, record_type="session_history", context_header="[Test Session Context]")
        
        db.cursor.execute("SELECT content FROM fragments WHERE session_id='test_session_2'")
        rows = db.cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "Small conversational turn.")
        
        mock_get_embedding.assert_called_with("[Test Session Context]\nSmall conversational turn.", task_type='RETRIEVAL_DOCUMENT')

    @patch('aim_core.retriever.get_federated_dbs', return_value=[])
    def test_sandwich_retrieval(self, mock_get_federated_dbs):
        db = ForensicDB(":memory:")
        db.add_session("sess1", "test.md", 12345.0)
        
        # Insert N-1, N, N+1
        db.cursor.execute("INSERT INTO fragments (session_id, type, content, parent_id) VALUES ('sess1', 'session_history', 'Turn 1', NULL)")
        t1_id = db.cursor.lastrowid
        db.cursor.execute("INSERT INTO fragments (session_id, type, content, parent_id) VALUES ('sess1', 'session_history', 'Turn 2', NULL)")
        t2_id = db.cursor.lastrowid
        db.cursor.execute("INSERT INTO fragments (session_id, type, content, parent_id) VALUES ('sess1', 'session_history', 'Turn 3', NULL)")
        t3_id = db.cursor.lastrowid
        db.conn.commit()
        
        results = [{
            "id": t2_id,
            "session_id": "sess1",
            "type": "session_history",
            "content": "Turn 2",
            "timestamp": None,
            "metadata": "{}",
            "parent_id": None,
            "filename": "test.md"
        }]
        
        # Mock get_federated_dbs to return a path that causes expand_sandwich_context to use our in-memory DB logic
        # For testing, we can patch the db_cache inside expand_sandwich_context or just pass the ForensicDB instance.
        # Since we use ForensicDB(db_path), we'll mock ForensicDB to return our memory db
        with patch('aim_core.retriever.ForensicDB', return_value=db):
            mock_get_federated_dbs.return_value = ["test.md"]
            expanded = expand_sandwich_context(results)
            
            self.assertEqual(len(expanded), 1)
            self.assertIn("Turn 1", expanded[0]['content'])
            self.assertIn("Turn 2", expanded[0]['content'])
            self.assertIn("Turn 3", expanded[0]['content'])

if __name__ == '__main__':
    unittest.main()
