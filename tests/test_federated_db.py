import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import tempfile
import lancedb
import pyarrow as pa
import shutil
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
src_dir = os.path.join(aim_root, "aim_core")
if aim_root not in sys.path:
    sys.path.append(aim_root)
if src_dir not in sys.path:
    sys.path.append(src_dir)

from aim_core import retriever
from aim_core.lance_backend import VectorBackend

class TestFederatedDB(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.lance_path = os.path.join(self.test_dir, "memory_lance")
        self.cartridges_dir = os.path.join(self.test_dir, "archive", "cartridges")
        os.makedirs(self.cartridges_dir, exist_ok=True)
        
        # Setup mock data in LanceDB (RAM)
        backend = VectorBackend(path=self.lance_path)
        backend.add_fragments([{
            "sqlite_id": 1,
            "session_id": "sess1",
            "type": "foundation_knowledge",
            "content": "Core logic here",
            "vector": [0.1] * 768,
            "source_db": "live_session",
            "metadata": "{}"
        }])

        # Setup mock data in Parquet (ROM)
        schema = pa.schema([
            pa.field("sqlite_id", pa.int64()),
            pa.field("session_id", pa.string()),
            pa.field("type", pa.string()),
            pa.field("content", pa.string()),
            pa.field("timestamp", pa.string()),
            pa.field("metadata", pa.string()),
            pa.field("parent_id", pa.int64()),
            pa.field("source_db", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), 768))
        ])
        
        records = [{
            "sqlite_id": 1,
            "session_id": "sess2",
            "type": "expert_knowledge",
            "content": "Universal skill logic",
            "timestamp": "2026-04-06T12:00:00Z",
            "metadata": "{}",
            "parent_id": None,
            "source_db": "global_skills.parquet",
            "vector": [0.9] * 768
        }]
        
        table = pa.Table.from_pylist(records, schema=schema)
        import pyarrow.parquet as pq
        self.parquet_path = os.path.join(self.cartridges_dir, "global_skills.parquet")
        pq.write_table(table, self.parquet_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_retriever_multiple_dbs(self):
        """Test that retriever can fetch from both LanceDB RAM and Parquet ROM."""
        with patch('aim_core.retriever.AIM_ROOT', self.test_dir), \
             patch('aim_core.lance_backend.AIM_ROOT', self.test_dir), \
             patch('aim_core.lance_backend.VectorBackend', side_effect=lambda path=None: VectorBackend(path=self.lance_path)):
             
            # Test getting the aggregated knowledge map
            k_map = retriever.get_aggregated_knowledge_map()
            
            # DB1 has 1 foundation knowledge
            self.assertEqual(len(k_map["foundation_knowledge"]), 1)
            self.assertEqual(k_map["foundation_knowledge"][0]["id"], "sess1")
            
            # DB2 has 1 expert knowledge
            self.assertEqual(len(k_map["expert_knowledge"]), 1)
            self.assertEqual(k_map["expert_knowledge"][0]["id"], "sess2")
            
            with patch('retriever.get_embedding', return_value=[0.1] * 768):
                # Test performing search to ensure both DBs are hit
                results = retriever.perform_search_internal("logic", top_k=10)
                
                # Should contain results from both DBs
                contents = [res['content'] for res in results]
                self.assertIn("Core logic here", contents)
                self.assertIn("Universal skill logic", contents)

if __name__ == "__main__":
    unittest.main()