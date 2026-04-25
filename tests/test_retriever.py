import unittest
import os
import sys

# --- BOOTSTRAP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
src_dir = os.path.join(aim_root, "aim_core")
if src_dir not in sys.path:
    sys.path.append(src_dir)

class TestRetriever(unittest.TestCase):
    
    def test_import_retriever(self):
        """Verifies that retriever.py can be imported without ModuleNotFoundError crashes."""
        try:
            import retriever
            self.assertTrue(hasattr(retriever, "perform_search"))
        except ModuleNotFoundError as e:
            self.fail(f"Failed to import retriever due to missing module: {e}")

if __name__ == "__main__":
    unittest.main()