import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AIM_ROOT, "aim_core"))

import config_utils


class TestResolveSessionSources(unittest.TestCase):
    """Phase 2, Issue #1: Session Data Source Abstraction — TDD tests."""

    def setUp(self):
        self.test_root = tempfile.mkdtemp()
        self.archive_raw = os.path.join(self.test_root, "archive", "raw")
        self.opencode_export_dir = os.path.join(self.test_root, "opencode_exports")
        os.makedirs(self.archive_raw, exist_ok=True)
        os.makedirs(self.opencode_export_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_root)

    def test_returns_both_sources_when_opencode_dir_exists(self):
        """Primary: opencode_export_dir exists → returns opencode first, gemini fallback."""
        sources = config_utils.resolve_session_sources(
            aim_root=self.test_root,
            opencode_export_dir=self.archive_raw,
        )
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0][0], "opencode")
        self.assertEqual(sources[1][0], "gemini")

    def test_opencode_source_has_json_pattern(self):
        """OpenCode exports use .json, not .jsonl."""
        sources = config_utils.resolve_session_sources(
            aim_root=self.test_root,
            opencode_export_dir=self.archive_raw,
        )
        self.assertEqual(sources[0][2], "*.json")

    def test_gemini_fallback_has_jsonl_pattern(self):
        """Gemini fallback uses .jsonl pattern."""
        sources = config_utils.resolve_session_sources(
            aim_root=self.test_root,
            opencode_export_dir=self.archive_raw,
        )
        self.assertEqual(sources[1][2], "*.jsonl")

    def test_gemini_fallback_path_contains_project_name(self):
        """Gemini fallback path includes project name from AIM_ROOT basename."""
        sources = config_utils.resolve_session_sources(
            aim_root=self.test_root,
            opencode_export_dir=self.archive_raw,
        )
        project_name = os.path.basename(self.test_root)
        self.assertIn(project_name, sources[1][1])
        self.assertIn(".gemini/tmp", sources[1][1])
        self.assertIn("chats", sources[1][1])

    def test_opencode_source_uses_configured_dir(self):
        """OpenCode source uses the configured opencode_export_dir, not a default."""
        custom_dir = os.path.join(self.test_root, "custom_exports")
        os.makedirs(custom_dir, exist_ok=True)
        sources = config_utils.resolve_session_sources(
            aim_root=self.test_root,
            opencode_export_dir=custom_dir,
        )
        self.assertEqual(sources[0][1], custom_dir)

    def test_returns_only_gemini_fallback_when_opencode_dir_empty_string(self):
        """When opencode_export_dir is empty string, only gemini fallback."""
        sources = config_utils.resolve_session_sources(
            aim_root=self.test_root,
            opencode_export_dir="",
        )
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0][0], "gemini")

    def test_returns_only_gemini_fallback_when_opencode_dir_none(self):
        """When opencode_export_dir is None, only gemini fallback."""
        sources = config_utils.resolve_session_sources(
            aim_root=self.test_root,
            opencode_export_dir=None,
        )
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0][0], "gemini")

    def test_each_source_is_three_tuple(self):
        """Every source entry is a 3-tuple of (type, path, pattern)."""
        sources = config_utils.resolve_session_sources(
            aim_root=self.test_root,
            opencode_export_dir=self.archive_raw,
        )
        for src in sources:
            self.assertIsInstance(src, tuple)
            self.assertEqual(len(src), 3)
            self.assertIsInstance(src[0], str)
            self.assertIsInstance(src[1], str)
            self.assertIsInstance(src[2], str)

    @patch("config_utils.CONFIG", {})
    def test_works_with_empty_config(self):
        """Should not crash with empty CONFIG dict."""
        sources = config_utils.resolve_session_sources()
        self.assertIsInstance(sources, list)
        # At minimum, gemini fallback
        self.assertGreaterEqual(len(sources), 1)


if __name__ == "__main__":
    unittest.main()
