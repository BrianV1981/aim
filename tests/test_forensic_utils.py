import unittest
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
if aim_root not in sys.path:
    sys.path.append(aim_root)
    
src_dir = os.path.join(aim_root, "aim_core")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from aim_core.plugins.datajack.forensic_utils import ForensicDB

class TestForensicUtils(unittest.TestCase):
    def test_expand_and_deduplicate_unpacking(self):
        db = ForensicDB(":memory:")
        
        # Simulate 8-element row: frag_id, sess_id, frag_type, content, timestamp, emb_blob, filename, parent_id
        dummy_row = (1, "sess_1", "knowledge", "content", "2026-05-01", b"emb", "test.md", None)
        
        # Insert it into the DB so the context query finds it
        db.cursor.execute("INSERT INTO fragments (id, session_id, type, content, timestamp, embedding, parent_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (1, "sess_1", "knowledge", "content", "2026-05-01", b"emb", None))
        db.conn.commit()
        
        hit_scores = [(0.95, dummy_row)]
        
        try:
            results = db._expand_and_deduplicate(hit_scores, is_lexical=False)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["content"], "content")
        except ValueError as e:
            self.fail(f"_expand_and_deduplicate raised ValueError unexpectedly: {e}")

if __name__ == "__main__":
    unittest.main()