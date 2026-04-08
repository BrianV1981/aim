import unittest
from unittest.mock import patch
import os
import sys
import tempfile
import sqlite3

current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
src_dir = os.path.join(aim_root, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from plugins.datajack.forensic_utils import ForensicDB
import retriever

class TestFederatedDB(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db1_path = os.path.join(self.test_dir, "project_core.db")
        self.db2_path = os.path.join(self.test_dir, "global_skills.db")

        # Setup mock data in DB 1
        db1 = ForensicDB(self.db1_path)
        db1.add_session("sess1", "core_file.md", 100)
        db1.add_fragments("sess1", [{
            "type": "foundation_knowledge",
            "content": "Core logic here",
            "timestamp": "2026-04-06T12:00:00Z",
            "embedding": [0.1, 0.1],
            "metadata": {}
        }])
        db1.close()

        # Setup mock data in DB 2
        db2 = ForensicDB(self.db2_path)
        db2.add_session("sess2", "skill_file.md", 200)
        db2.add_fragments("sess2", [{
            "type": "expert_knowledge",
            "content": "Universal skill logic",
            "timestamp": "2026-04-06T12:00:00Z",
            "embedding": [0.9, 0.9],
            "metadata": {}
        }])
        db2.close()

    def tearDown(self):
        for f in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, f))
        os.rmdir(self.test_dir)

    def test_forensic_db_custom_path(self):
        """Test that ForensicDB accepts and creates databases at modular paths."""
        self.assertTrue(os.path.exists(self.db1_path))
        self.assertTrue(os.path.exists(self.db2_path))

    def test_retriever_multiple_dbs(self):
        """Test that retriever can fetch from a list of federated databases."""
        original_get_dbs = getattr(retriever, "get_federated_dbs", None)
        retriever.get_federated_dbs = lambda: [self.db1_path, self.db2_path]

        try:
            # Test getting the aggregated knowledge map
            k_map = retriever.get_aggregated_knowledge_map()
            
            # DB1 has 1 foundation knowledge
            self.assertEqual(len(k_map["foundation_knowledge"]), 1)
            self.assertEqual(k_map["foundation_knowledge"][0]["filename"], "core_file.md")
            
            # DB2 has 1 expert knowledge
            self.assertEqual(len(k_map["expert_knowledge"]), 1)
            self.assertEqual(k_map["expert_knowledge"][0]["filename"], "skill_file.md")
            
            with patch('retriever.get_embedding', return_value=[0.1, 0.1]):
                # Test performing search to ensure both DBs are hit
                # perform_search_internal should return a list of matches without printing
                results = retriever.perform_search_internal("logic", top_k=10)
                
                # Should contain results from both DBs
                contents = [res['content'] for res in results]
                self.assertIn("Core logic here", contents)
                self.assertIn("Universal skill logic", contents)
                
        finally:
            if original_get_dbs:
                retriever.get_federated_dbs = original_get_dbs
            else:
                delattr(retriever, "get_federated_dbs")

if __name__ == "__main__":
    unittest.main()