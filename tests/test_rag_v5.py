import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile
import shutil
import lancedb

current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
if aim_root not in sys.path:
    sys.path.append(aim_root)

src_dir = os.path.join(aim_root, "aim_core")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from aim_core.lance_backend import VectorBackend
from aim_core.retriever import expand_sandwich_context

class TestRAGv5Sandwich(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.lance_path = os.path.join(self.test_dir, "memory_lance")
        
        self.backend = VectorBackend(path=self.lance_path)
        
        # Insert N-1, N, N+1
        fragments = [
            {
                "sqlite_id": 1,
                "session_id": "sess1",
                "type": "session_history",
                "content": "Turn 1",
                "parent_id": None,
                "vector": [0.1] * 768
            },
            {
                "sqlite_id": 2,
                "session_id": "sess1",
                "type": "session_history",
                "content": "Turn 2",
                "parent_id": None,
                "vector": [0.1] * 768
            },
            {
                "sqlite_id": 3,
                "session_id": "sess1",
                "type": "session_history",
                "content": "Turn 3",
                "parent_id": None,
                "vector": [0.1] * 768
            }
        ]
        self.backend.add_fragments(fragments)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_sandwich_retrieval_lancedb(self):
        results = [{
            "id": 2,
            "session_id": "sess1",
            "type": "session_history",
            "content": "Turn 2",
            "timestamp": None,
            "metadata": "{}",
            "parent_id": None,
            "filename": "live_session"
        }]
        
        with patch('aim_core.lance_backend.VectorBackend', side_effect=lambda path=None: VectorBackend(path=self.lance_path)):
            expanded = expand_sandwich_context(results)
            
            self.assertEqual(len(expanded), 1)
            self.assertIn("Turn 1", expanded[0]['content'])
            self.assertIn("Turn 2", expanded[0]['content'])
            self.assertIn("Turn 3", expanded[0]['content'])

if __name__ == '__main__':
    unittest.main()
