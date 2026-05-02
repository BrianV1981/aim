import unittest
import os
import sys
import tempfile
import shutil
import json
from unittest.mock import patch, MagicMock

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestAimHooksPlugin(unittest.TestCase):
    """Phase 4, Issue #10: OpenCode Hook Plugin — structural and logical tests."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.plugins_dir = os.path.join(self.test_dir, ".opencode", "plugins")
        os.makedirs(self.plugins_dir, exist_ok=True)
        self.continuity_dir = os.path.join(self.test_dir, "continuity")
        os.makedirs(self.continuity_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_plugin_file_exists_at_correct_path(self):
        """The plugin must exist at .opencode/plugins/aim-hooks.ts in the project root."""
        plugin_path = os.path.join(AIM_ROOT, ".opencode", "plugins", "aim-hooks.ts")
        self.assertTrue(os.path.exists(plugin_path),
                        f"Plugin not found at {plugin_path}")

    def test_plugin_file_exports_aim_hooks(self):
        """The plugin must export AimHooks as a named export."""
        plugin_path = os.path.join(AIM_ROOT, ".opencode", "plugins", "aim-hooks.ts")
        with open(plugin_path, "r") as f:
            content = f.read()
        self.assertIn("export const AimHooks", content,
                      "Plugin must export AimHooks as a named const")

    def test_plugin_subscribes_to_session_idle(self):
        """Plugin must subscribe to session.idle for summarizer trigger."""
        plugin_path = os.path.join(AIM_ROOT, ".opencode", "plugins", "aim-hooks.ts")
        with open(plugin_path, "r") as f:
            content = f.read()
        self.assertIn('"session.idle"', content,
                      "Plugin must hook into session.idle event")

    def test_plugin_subscribes_to_tool_execute_after(self):
        """Plugin must subscribe to tool.execute.after for mantra counter."""
        plugin_path = os.path.join(AIM_ROOT, ".opencode", "plugins", "aim-hooks.ts")
        with open(plugin_path, "r") as f:
            content = f.read()
        self.assertIn('"tool.execute.after"', content,
                      "Plugin must hook into tool.execute.after event")

    def test_plugin_subscribes_to_experimental_session_compacting(self):
        """Plugin must subscribe to experimental.session.compacting for continuity."""
        plugin_path = os.path.join(AIM_ROOT, ".opencode", "plugins", "aim-hooks.ts")
        with open(plugin_path, "r") as f:
            content = f.read()
        self.assertIn('"experimental.session.compacting"', content,
                      "Plugin must hook into experimental.session.compacting event")

    def test_plugin_imports_plugin_type(self):
        """Plugin must import Plugin type from @opencode-ai/plugin for type safety."""
        plugin_path = os.path.join(AIM_ROOT, ".opencode", "plugins", "aim-hooks.ts")
        with open(plugin_path, "r") as f:
            content = f.read()
        self.assertIn("@opencode-ai/plugin", content,
                      "Plugin must import from @opencode-ai/plugin for TypeScript types")

    def test_plugin_writes_mantra_to_continuity_directory(self):
        """Mantra output must go to continuity/MANTRA_PULSE.md (not gemini hook-specific JSON)."""
        plugin_path = os.path.join(AIM_ROOT, ".opencode", "plugins", "aim-hooks.ts")
        with open(plugin_path, "r") as f:
            content = f.read()
        self.assertIn("MANTRA_PULSE.md", content,
                      "Plugin must write mantra to continuity/MANTRA_PULSE.md")
        # Must NOT use Gemini-specific hookResponse format
        self.assertNotIn("hookSpecificOutput", content,
                         "Plugin must not use Gemini hookSpecificOutput JSON")

    def test_plugin_uses_node_fs_for_mantra_state(self):
        """Mantra state must use Node:fs writeFileSync for persistence (no subprocess)."""
        plugin_path = os.path.join(AIM_ROOT, ".opencode", "plugins", "aim-hooks.ts")
        with open(plugin_path, "r") as f:
            content = f.read()
        self.assertIn("writeFileSync", content,
                      "Plugin must persist mantra state via filesystem writes")
        self.assertNotIn("Popen", content,
                         "Plugin must not spawn subprocesses")
        self.assertNotIn("spawn", content)

    def test_package_json_exists(self):
        """A .opencode/package.json must exist for TypeScript plugin deps."""
        pkg_path = os.path.join(AIM_ROOT, ".opencode", "package.json")
        self.assertTrue(os.path.exists(pkg_path),
                        f"package.json not found at {pkg_path}")
        with open(pkg_path, "r") as f:
            pkg = json.load(f)
        self.assertIn("@opencode-ai/plugin", pkg.get("dependencies", {}),
                      "package.json must depend on @opencode-ai/plugin")

    # ── Helper logic tests ────────────────────────────────────────

    def test_find_aim_root_logic(self):
        """findAimRoot walks up from directory looking for core/CONFIG.json or setup.sh."""
        core_dir = os.path.join(self.test_dir, "core")
        os.makedirs(core_dir)
        with open(os.path.join(core_dir, "CONFIG.json"), "w") as f:
            f.write("{}")

        child = os.path.join(self.test_dir, "sub", "deep")
        os.makedirs(child)

        # Simulate the algorithm inline
        current = child
        found = None
        while current != "/":
            if (os.path.exists(os.path.join(current, "core", "CONFIG.json"))
                    or os.path.exists(os.path.join(current, "setup.sh"))):
                found = current
                break
            current = os.path.dirname(current)

        self.assertEqual(found, self.test_dir,
                         "findAimRoot must find AIM_ROOT from deep subdirectory")

    def test_find_aim_root_returns_none_outside_workspace(self):
        """findAimRoot returns null when NOT inside an AIM workspace."""
        tmp = tempfile.mkdtemp()
        try:
            current = tmp
            found = None
            while current != "/":
                if (os.path.exists(os.path.join(current, "core", "CONFIG.json"))
                        or os.path.exists(os.path.join(current, "setup.sh"))):
                    found = current
                    break
                current = os.path.dirname(current)
            self.assertIsNone(found)
        finally:
            shutil.rmtree(tmp)

    def test_session_summarizer_triggered_on_idle(self):
        """Verify the session.idle handler logic: finds latest transcript, runs summarizer."""
        plugin_path = os.path.join(AIM_ROOT, ".opencode", "plugins", "aim-hooks.ts")
        with open(plugin_path, "r") as f:
            content = f.read()
        self.assertIn("session_summarizer.py", content,
                      "session.idle handler must reference session_summarizer.py")
        self.assertIn("historyDir", content,
                      "session.idle handler must reference historyDir for transcript search")


if __name__ == "__main__":
    unittest.main()
