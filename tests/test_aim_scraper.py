import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure aim_root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
if aim_root not in sys.path:
    sys.path.append(aim_root)

# Import the script
from aim_core import aim_scraper

class TestAimScraper(unittest.TestCase):
    def test_clean_html(self):
        """Verify HTML cleaning logic."""
        raw = "<p>This is <b>bold</b> text &amp; a test.</p>"
        cleaned = aim_scraper.clean_html(raw)
        self.assertEqual(cleaned, "This is bold text & a test.")

    @patch('aim_core.aim_scraper.requests.get')
    def test_fetch_stackoverflow_threads_success(self, mock_get):
        """Verify fetch_stackoverflow_threads handles successful API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"items": [{"question_id": 123, "title": "Test Query"}]}
        mock_get.return_value = mock_response
        
        threads = aim_scraper.fetch_stackoverflow_threads("test", limit=1)
        
        self.assertEqual(len(threads), 1)
        self.assertEqual(threads[0]["question_id"], 123)
        mock_get.assert_called_once()
        
    @patch('aim_core.aim_scraper.requests.get')
    def test_fetch_stackoverflow_threads_failure(self, mock_get):
        """Verify fetch_stackoverflow_threads handles API errors gracefully."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Rate Limit")
        mock_get.return_value = mock_response
        
        threads = aim_scraper.fetch_stackoverflow_threads("test", limit=1)
        
        self.assertEqual(len(threads), 0)
        mock_get.assert_called_once()

    @patch('aim_core.aim_scraper.run_gh_command')
    def test_fetch_closed_issues_success(self, mock_gh):
        """Verify fetch_closed_issues parses github CLI JSON."""
        mock_gh.return_value = '[{"number": 1, "title": "A Bug", "stateReason": "COMPLETED"}, {"number": 2, "stateReason": "NOT_PLANNED"}]'
        
        issues = aim_scraper.fetch_closed_issues("test/repo", limit=10)
        
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["number"], 1)


    def test_format_issue_adds_frontmatter(self):
        """Verify YAML frontmatter is injected into the markdown file."""
        import tempfile
        import hashlib
        
        issue = {'number': 42, 'title': 'Test', 'url': 'http://test', 'body': 'body content'}
        comments = [{'body': 'this is a long enough comment to pass the length check'}]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            aim_scraper.format_issue_as_markdown(issue, comments, tmpdir)
            filepath = os.path.join(tmpdir, "issue_42.md")
            self.assertTrue(os.path.exists(filepath))
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.assertIn("type: community_knowledge", content)
            self.assertIn("source: github#42", content)
            self.assertIn("content_hash:", content)
            self.assertIn("# Q: Test", content)
            
            # Verify skipping logic
            # Running again with same data should return False (skip)
            result = aim_scraper.format_issue_as_markdown(issue, comments, tmpdir)
            self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
