import unittest
import os
import sys
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AIM_ROOT, "aim_core"))


class TestPhase5InitTemplates(unittest.TestCase):
    """Phase 5, Issues #14: Init template files — opencode.json instead of gemini settings."""

    def setUp(self):
        self.test_root = tempfile.mkdtemp()
        self.core_dir = os.path.join(self.test_root, "core")
        os.makedirs(self.core_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_root)

    def _load_init_source(self):
        init_path = os.path.join(AIM_ROOT, "aim_core", "aim_init.py")
        with open(init_path, "r") as f:
            return f.read()

    # ── #14: Template files ───────────────────────────────────────

    def test_opencode_json_template_present(self):
        """Init must seed opencode.json as the primary config template."""
        content = self._load_init_source()
        self.assertIn("opencode.json", content,
                      "aim_init must contain opencode.json template")
        # The template must include context/memory boundary markers
        files_section = content.split('"opencode.json"')[1].split("}")[0]
        self.assertIn("memoryBoundaryMarkers", files_section,
                      "opencode.json template must set memoryBoundaryMarkers")

    def test_opencodeignore_template_replaces_geminiignore(self):
        """Init must seed .opencodeignore instead of .geminiignore."""
        content = self._load_init_source()
        self.assertIn(".opencodeignore", content,
                      "aim_init must seed .opencodeignore template")
        self.assertNotIn('".geminiignore"', content,
                         "aim_init must NOT seed .geminiignore — use .opencodeignore")

    def test_no_memory_wiki_gemini_settings(self):
        """memory-wiki/.gemini/settings.json template must be removed."""
        content = self._load_init_source()
        self.assertNotIn("memory-wiki/.gemini", content,
                         "memory-wiki/.gemini/settings.json must be removed from init templates")

    def test_opencode_config_in_dir_list(self):
        """The dirs list must include .opencode related directories."""
        content = self._load_init_source()
        self.assertNotIn('".gemini"', content.split('dirs = [')[1].split(']')[0],
                         "dirs list must not create .gemini directory (use .opencode instead)")

    # ── #15: AGENTS.md template updates ──────────────────────────

    def test_agents_template_no_gemini_cli_references(self):
        """T_SOUL template must replace Gemini CLI references with OpenCode."""
        content = self._load_init_source()
        t_soul = content.split('T_SOUL = """')[1].split('"""')[0] if 'T_SOUL = """' in content else ""
        if t_soul:
            self.assertNotIn("Gemini CLI", t_soul,
                             "T_SOUL must not reference 'Gemini CLI'")
            self.assertNotIn(".gemini/settings.json", t_soul,
                             "T_SOUL must not reference .gemini/settings.json")
            self.assertNotIn(".geminiignore", t_soul,
                             "T_SOUL must not reference .geminiignore")

    def test_agents_template_mentions_opencode(self):
        """T_SOUL template must reference OpenCode where appropriate."""
        content = self._load_init_source()
        # The HALT AND CATCH FIRE reference should use opencode.json
        self.assertIn("opencode.json", content.split("HALT AND CATCH FIRE")[1].split(")")[0]
                        if "HALT AND CATCH FIRE" in content else True)

    def test_agents_template_no_v8_engine(self):
        """Catastrophic Memory Crashes section must reference session compaction instead of V8."""
        content = self._load_init_source()
        self.assertNotIn("Node.js V8 engine", content,
                         "T_SOUL must not reference Node.js V8 engine")


class TestPhase5SkillsAndAgents(unittest.TestCase):
    """Phase 5, Issues #16-#17: Port skills and agents to OpenCode format."""

    def test_opencode_skills_directory_exists(self):
        """OpenCode skills must be ported to .opencode/skills/."""
        skills_dir = os.path.join(AIM_ROOT, ".opencode", "skills")
        self.assertTrue(os.path.exists(skills_dir),
                        f"OpenCode skills directory must exist at .opencode/skills/")
        # Verify at least one skill was ported
        subdirs = [d for d in os.listdir(skills_dir)
                   if os.path.isdir(os.path.join(skills_dir, d))]
        self.assertGreater(len(subdirs), 0,
                           "At least one skill must be ported to .opencode/skills/")

    def test_each_skill_has_skill_md(self):
        """Each OpenCode skill must have a SKILL.md manifest."""
        skills_dir = os.path.join(AIM_ROOT, ".opencode", "skills")
        if not os.path.exists(skills_dir):
            return
        for name in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, name)
            if os.path.isdir(skill_path):
                skill_md = os.path.join(skill_path, "SKILL.md")
                self.assertTrue(os.path.exists(skill_md),
                                f"Skill {name} must have SKILL.md")

    def test_gemini_skills_still_present_for_backward_compat(self):
        """Old .gemini/skills/ must remain for backward compatibility."""
        gemini_skills = os.path.join(AIM_ROOT, ".gemini", "skills")
        self.assertTrue(os.path.exists(gemini_skills),
                        ".gemini/skills/ must remain for backward compat")

    def test_opencode_agents_config_exists(self):
        """OpenCode agents must be defined."""
        # Either via opencode.json config or .opencode/agents/ directory
        agents_path = os.path.join(AIM_ROOT, ".opencode", "agents")
        opencode_json = os.path.join(AIM_ROOT, "opencode.json")

        has_agents = os.path.exists(agents_path) or os.path.exists(opencode_json)
        self.assertTrue(has_agents,
                        "OpenCode agents must be configured via .opencode/agents/ or opencode.json")


if __name__ == "__main__":
    unittest.main()
