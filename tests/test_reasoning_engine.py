import unittest
import os
import sys
import inspect
from unittest.mock import patch, MagicMock

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AIM_ROOT, "aim_core"))


class TestReasoningEngineGeminiRemoval(unittest.TestCase):
    """Phase 3, Issue #8: Remove Gemini CLI OAuth bridge from reasoning engine."""

    @patch("aim_core.reasoning_utils.keyring.get_password")
    @patch("aim_core.reasoning_utils.requests.post")
    def test_execute_google_no_subprocess(self, mock_post, mock_keyring):
        """execute_google() should NOT use subprocess (no Gemini CLI calls)."""
        mock_keyring.return_value = "fake-api-key"
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Response OK"}]}}]
        }
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        from aim_core.reasoning_utils import execute_google

        with patch("aim_core.reasoning_utils.subprocess") as mock_sp:
            result = execute_google("Test prompt", "System instruction", "gemini-2.5-flash")
            # subprocess should NOT be called
            mock_sp.run.assert_not_called()
            self.assertIn("Response OK", result)

    @patch("aim_core.reasoning_utils.keyring.get_password")
    @patch("aim_core.reasoning_utils.requests.post")
    def test_execute_google_api_key_path_works(self, mock_post, mock_keyring):
        """The API Key REST path (Route 2) must still function."""
        mock_keyring.return_value = "fake-api-key"
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "API Key Response"}]}}]
        }
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        from aim_core.reasoning_utils import execute_google
        result = execute_google("Q", "Sys", "gemini-2.5-flash")
        self.assertIn("API Key Response", result)
        mock_post.assert_called_once()

    def test_no_gemini_cli_references_in_source(self):
        """execute_google source must not reference 'gemini' CLI commands."""
        from aim_core.reasoning_utils import execute_google
        source = inspect.getsource(execute_google)
        # The word "gemini" only appears in model names, NOT as a CLI call
        self.assertNotIn('"gemini"', source.split("gemini")[-1] if "gemini" in source else "")

    def test_no_gemini_env_vars_in_source(self):
        """Source must not reference GEMINI_CLI_TMP_DIR or GEMINI_CLI_DISABLE_CHECKPOINT."""
        from aim_core.reasoning_utils import execute_google
        source = inspect.getsource(execute_google)
        self.assertNotIn("GEMINI_CLI_TMP_DIR", source)
        self.assertNotIn("GEMINI_CLI_DISABLE_CHECKPOINT", source)

    def test_generate_reasoning_google_routes_to_api(self):
        """When provider=google with API Key auth, uses REST API (not CLI)."""
        from aim_core.reasoning_utils import execute_google

        with patch("aim_core.reasoning_utils.keyring.get_password", return_value="key"):
            with patch("aim_core.reasoning_utils.requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.json.return_value = {
                    "candidates": [{"content": {"parts": [{"text": "OK"}]}}]
                }
                mock_resp.ok = True
                mock_resp.status_code = 200
                mock_post.return_value = mock_resp

                result = execute_google("P", "S", "gemini-pro")
                self.assertEqual(result, "OK")
                mock_post.assert_called_once()


if __name__ == "__main__":
    unittest.main()
