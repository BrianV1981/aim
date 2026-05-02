import unittest
import os
import sys
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AIM_ROOT, "aim_core"))


class TestCognitiveMantraOutputFormat(unittest.TestCase):
    """Phase 4, Issue #11: Cognitive mantra writes to MANTRA_PULSE.md (not Gemini JSON)."""

    def setUp(self):
        self.test_root = tempfile.mkdtemp()
        self.continuity_dir = os.path.join(self.test_root, "continuity")
        self.private_dir = os.path.join(self.test_root, "hooks", ".state")
        os.makedirs(self.continuity_dir, exist_ok=True)
        os.makedirs(self.private_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_root)

    def test_mantra_writes_to_continuity_dir(self):
        """Cognitive mantra output goes to continuity/MANTRA_PULSE.md, not hook-specific JSON."""
        mantra_path = os.path.join(AIM_ROOT, "hooks", "cognitive_mantra.py")
        self.assertTrue(os.path.exists(mantra_path))
        with open(mantra_path, "r") as f:
            content = f.read()
        # The file should reference MANTRA_PULSE.md in continuity/
        self.assertIn("MANTRA_PULSE.md", content,
                      "cognitive_mantra.py must write to continuity/MANTRA_PULSE.md")
        # Must not emit Gemini-specific JSON format
        self.assertNotIn("hookSpecificOutput", content,
                         "cognitive_mantra.py must not emit Gemini hookSpecificOutput JSON")


class TestInitPluginInstallation(unittest.TestCase):
    """Phase 4, Issue #12: aim_init installs .opencode plugins instead of Gemini hooks."""

    def test_register_hooks_replaced_by_install_opencode_plugins(self):
        """aim_init must expose install_opencode_plugins() as the plugin installer."""
        init_path = os.path.join(AIM_ROOT, "aim_core", "aim_init.py")
        self.assertTrue(os.path.exists(init_path))
        with open(init_path, "r") as f:
            content = f.read()
        self.assertIn("install_opencode_plugins", content,
                      "aim_init must define install_opencode_plugins()")

    def test_install_plugin_seeds_hook_file(self):
        """install_opencode_plugins() must create .opencode/plugins/aim-hooks.ts."""
        init_path = os.path.join(AIM_ROOT, "aim_core", "aim_init.py")
        with open(init_path, "r") as f:
            content = f.read()
        self.assertIn("aim-hooks.ts", content,
                      "install_opencode_plugins must seed aim-hooks.ts")

    def test_install_plugin_seeds_package_json(self):
        """install_opencode_plugins() must seed .opencode/package.json."""
        init_path = os.path.join(AIM_ROOT, "aim_core", "aim_init.py")
        with open(init_path, "r") as f:
            content = f.read()
        self.assertIn("opencode/package.json", content,
                      "install_opencode_plugins must seed .opencode/package.json")


class TestCliHookValidation(unittest.TestCase):
    """Phase 4, Issue #13: CLI validates .opencode plugins, not Gemini settings.json."""

    def test_ensure_hooks_mapped_checks_opencode_plugins(self):
        """CLI must check .opencode/plugins/aim-hooks.ts existence, not ~/.gemini/settings.json."""
        cli_path = os.path.join(AIM_ROOT, "aim_core", "aim_cli.py")
        self.assertTrue(os.path.exists(cli_path))
        with open(cli_path, "r") as f:
            content = f.read()
        # The function should reference the plugin path (may be constructed via os.path.join)
        self.assertTrue(
            "aim-hooks.ts" in content or ".opencode" in content,
            "ensure_hooks_mapped must reference aim-hooks.ts plugin path"
        )
        # Primary check is for .opencode plugins, not .gemini settings
        hooks_mapped_source = content.split("def ensure_hooks_mapped")[1].split("\ndef ")[0]
        self.assertIn(".opencode", hooks_mapped_source,
                      "ensure_hooks_mapped primary logic must check .opencode directory")

    def test_cli_no_longer_refers_to_gemini_settings_json(self):
        """CLI ensure_hooks_mapped primary path must not be gated on Gemini settings."""
        cli_path = os.path.join(AIM_ROOT, "aim_core", "aim_cli.py")
        with open(cli_path, "r") as f:
            content = f.read()
        hooks_mapped_source = content.split("def ensure_hooks_mapped")[1].split("\ndef ")[0]
        # Primary logic should not start by checking .gemini/settings.json existence
        first_check = hooks_mapped_source.strip().split("\n")[0].strip()
        self.assertNotIn("~/.gemini/settings.json", first_check,
                         "ensure_hooks_mapped primary check must not be gated on Gemini settings.json")


if __name__ == "__main__":
    unittest.main()
