import unittest
import os
import sys
import inspect
from unittest.mock import patch, MagicMock

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AIM_ROOT, "aim_core"))
sys.path.insert(0, os.path.join(AIM_ROOT, "hooks"))


class TestSessionSummarizerFallback(unittest.TestCase):
    """Phase 3, Issue #9: Remove gemini Popen fallback from session summarizer."""

    def test_no_gemini_popen_in_source(self):
        """Session summarizer source must not contain Popen(['gemini'...])."""
        from hooks.session_summarizer import process_transcript
        source = inspect.getsource(process_transcript)
        self.assertNotIn("['gemini'", source,
                         "process_transcript must not spawn gemini CLI")
        self.assertNotIn('["gemini"', source)

    @patch("subprocess.Popen")
    @patch("hooks.session_summarizer.ingest_file_to_db")
    @patch("hooks.session_summarizer.ForensicDB")
    @patch("hooks.session_summarizer.generate_reasoning")
    @patch("hooks.session_summarizer.process_wiki")
    @patch("hooks.session_summarizer.chunk_text")
    @patch("hooks.session_summarizer.get_embedding")
    def test_no_subprocess_popen_for_gemini(self, mock_emb, mock_chunk,
                                              mock_wiki, mock_gen, mock_db_class,
                                              mock_ingest, mock_popen):
        """process_transcript() must not spawn gemini subprocess."""
        from hooks.session_summarizer import process_transcript

        mock_db_instance = MagicMock()
        mock_db_class.return_value = mock_db_instance
        mock_chunk.return_value = []
        mock_gen.return_value = "Error: API timeout"

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as tf:
            tf.write("# Test")
            md_path = tf.name

        try:
            result = process_transcript(md_path)
        finally:
            os.unlink(md_path)

        gemini_calls = [
            c for c in mock_popen.call_args_list
            if isinstance(c[0][0], list) and "gemini" in c[0][0]
        ]
        self.assertEqual(len(gemini_calls), 0,
                         "must not spawn gemini subprocess")

    @patch("subprocess.Popen")
    @patch("hooks.session_summarizer.ingest_file_to_db")
    @patch("hooks.session_summarizer.ForensicDB")
    @patch("hooks.session_summarizer.generate_reasoning")
    @patch("hooks.session_summarizer.process_wiki")
    @patch("hooks.session_summarizer.chunk_text")
    @patch("hooks.session_summarizer.get_embedding")
    def test_fallback_handles_error_gracefully(self, mock_emb, mock_chunk,
                                                 mock_wiki, mock_gen, mock_db_class,
                                                 mock_ingest, mock_popen):
        """When generate_reasoning fails, process_transcript handles it without crash."""
        from hooks.session_summarizer import process_transcript

        mock_db_instance = MagicMock()
        mock_db_class.return_value = mock_db_instance
        mock_chunk.return_value = ["chunk"]
        mock_gen.return_value = "Error: something went wrong"

        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as tf:
            tf.write("# Content")
            md_path = tf.name

        try:
            result = process_transcript(md_path)
            self.assertIsNotNone(result)
        finally:
            os.unlink(md_path)


if __name__ == "__main__":
    unittest.main()
