import unittest
from unittest.mock import patch, mock_open, call, MagicMock
import os
import sys

# Add aim_core and hooks to path
AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(AIM_ROOT)
sys.path.append(os.path.join(AIM_ROOT, "aim_core"))
sys.path.append(os.path.join(AIM_ROOT, "hooks"))

# Mock to prevent config loading crash
import builtins
real_open = builtins.open
real_exists = os.path.exists

def mock_open_wrapper(filename, *args, **kwargs):
    if "CONFIG.json" in str(filename):
        return mock_open(read_data='{"settings": {}}')()
    return real_open(filename, *args, **kwargs)

def mock_exists_wrapper(path):
    if "CONFIG.json" in str(path):
        return True
    return real_exists(path)

with patch('builtins.open', mock_open_wrapper), patch('os.path.exists', mock_exists_wrapper):
    import session_summarizer

class TestSessionSummarizer(unittest.TestCase):
    @patch("session_summarizer.generate_reasoning")
    @patch("session_summarizer.process_wiki")
    @patch("session_summarizer.ForensicDB")
    @patch("session_summarizer.ingest_file_to_db")
    @patch("os.makedirs")
    def test_chunking_massive_transcript(self, mock_makedirs, mock_ingest, mock_db, mock_process_wiki, mock_generate):
        mock_generate.return_value = "Summary chunk"
        
        # Create a mock transcript with 250 turns
        transcript = ""
        for i in range(1250):
            transcript += f"Turn {i}\n---\n\n"
            
        with patch('builtins.open', mock_open(read_data=transcript)) as m_open:
            session_summarizer.process_transcript("dummy_session.md")
            
        # The script should chunk by 1000 turns, meaning 1250 turns = 2 chunks.
        # generate_reasoning should be called 2 times.
        self.assertEqual(mock_generate.call_count, 2)
        
        # It should have attempted to open and write 2 summary files
        # The files should end with _part1_summary.md, _part2_summary.md
        write_calls = [c for c in m_open.mock_calls if 'w' in c.args or 'w' in c.kwargs.get('mode', '')]
        self.assertTrue(any("_part1_summary.md" in str(c) for c in m_open.mock_calls))
        self.assertTrue(any("_part2_summary.md" in str(c) for c in m_open.mock_calls))
        
if __name__ == "__main__":
    unittest.main()
