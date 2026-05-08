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

from aim_core.legacy_sqlite import ForensicDB

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



    def test_ollama_embedding_exponential_backoff(self):
        from unittest.mock import patch, MagicMock
        from aim_core.plugins.datajack.forensic_utils import get_embedding
        import aim_core.plugins.datajack.forensic_utils as fu
        
        # Save original settings
        orig_type = fu.PROVIDER_TYPE
        fu.PROVIDER_TYPE = 'local'
        
        with patch('aim_core.plugins.datajack.forensic_utils.requests.post') as mock_post,              patch('time.sleep') as mock_sleep:
            
            # Setup mock to fail 2 times then succeed
            mock_response_fail = MagicMock()
            mock_response_fail.raise_for_status.side_effect = Exception("500 Server Error")
            
            mock_response_success = MagicMock()
            mock_response_success.raise_for_status.return_value = None
            mock_response_success.json.return_value = {'embedding': [0.1, 0.2, 0.3]}
            
            mock_post.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]
            
            res = get_embedding("test query")
            
            self.assertEqual(res, [0.1, 0.2, 0.3])
            self.assertEqual(mock_post.call_count, 3)
            self.assertEqual(mock_sleep.call_count, 2)
            
            # Test backoff times (1 * 2^0 = 1, 1 * 2^1 = 2)
            mock_sleep.assert_any_call(1)
            mock_sleep.assert_any_call(2)
            
        # Restore
        fu.PROVIDER_TYPE = orig_type

if __name__ == "__main__":
    unittest.main()