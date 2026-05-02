import unittest
import os
import sys
import inspect

AIM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AIM_ROOT, "aim_core"))


class TestPhase6VariableRenames(unittest.TestCase):
    """Phase 6, Issue #18: gemini_path → agents_path variable renames."""

    def test_aim_config_no_gemini_path_variable(self):
        """aim_config.py must not use gemini_path as a variable name."""
        config_path = os.path.join(AIM_ROOT, "aim_core", "aim_config.py")
        with open(config_path, "r") as f:
            content = f.read()
        self.assertNotIn("gemini_path =", content,
                         "gemini_path variable must be renamed to agents_path")
        self.assertIn("agents_path =", content,
                      "agents_path variable must be introduced")

    def test_update_agents_file_function_name(self):
        """Function must be renamed from update_gemini_behavior_file."""
        config_path = os.path.join(AIM_ROOT, "aim_core", "aim_config.py")
        with open(config_path, "r") as f:
            content = f.read()
        self.assertNotIn("def update_gemini_behavior_file", content,
                         "Must rename to update_agents_file")
        self.assertIn("def update_agents_file", content,
                      "update_agents_file function must exist")

    def test_aim_init_no_gemini_path_variable(self):
        """aim_init.py must not use gemini_path as a variable name."""
        init_path = os.path.join(AIM_ROOT, "aim_core", "aim_init.py")
        with open(init_path, "r") as f:
            content = f.read()
        self.assertNotIn("gemini_path =", content,
                         "gemini_path must be renamed to agents_path in aim_init")
        self.assertIn("agents_path =", content,
                      "agents_path must be used in aim_init")

    def test_cognitive_mantra_no_gemini_variables(self):
        """cognitive_mantra.py must not use gemini_path or gemini_content."""
        mantra_path = os.path.join(AIM_ROOT, "hooks", "cognitive_mantra.py")
        with open(mantra_path, "r") as f:
            content = f.read()
        self.assertNotIn("gemini_path", content,
                         "gemini_path must be renamed in cognitive_mantra")
        self.assertNotIn("gemini_content", content,
                         "gemini_content must be renamed in cognitive_mantra")


class TestPhase6SetupScript(unittest.TestCase):
    """Phase 6, Issue #19: setup.sh cleanup."""

    def test_no_node_options_v8_patch(self):
        """setup.sh must not have NODE_OPTIONS V8 memory patch."""
        setup_path = os.path.join(AIM_ROOT, "setup.sh")
        self.assertTrue(os.path.exists(setup_path))
        with open(setup_path, "r") as f:
            content = f.read()
        self.assertNotIn("NODE_OPTIONS", content,
                         "NODE_OPTIONS V8 memory patch must be removed from setup.sh")
        self.assertNotIn("max-old-space-size", content,
                         "V8 memory limit must be removed from setup.sh")

    def test_setup_has_opencode_json_seeding(self):
        """setup.sh must include opencode.json seeding step."""
        setup_path = os.path.join(AIM_ROOT, "setup.sh")
        with open(setup_path, "r") as f:
            content = f.read()
        self.assertIn("opencode.json", content,
                      "setup.sh must seed opencode.json")


class TestPhase6Economics(unittest.TestCase):
    """Phase 6, Issue #21: DeepSeek pricing in calculate_economics.py."""

    def test_deepseek_pricing_in_economics(self):
        """calculate_economics.py must include DeepSeek pricing."""
        econ_path = os.path.join(AIM_ROOT, "aim_core", "calculate_economics.py")
        self.assertTrue(os.path.exists(econ_path))
        with open(econ_path, "r") as f:
            content = f.read()
        self.assertIn("deepseek", content.lower(),
                      "calculate_economics.py must include DeepSeek pricing")

    def test_generic_function_name(self):
        """Function name should be generic (not gemini-specific)."""
        econ_path = os.path.join(AIM_ROOT, "aim_core", "calculate_economics.py")
        with open(econ_path, "r") as f:
            content = f.read()
        self.assertNotIn("calculate_gemini_session_cost", content,
                         "Function name must be generic (not gemini-specific)")


class TestPhase6Docs(unittest.TestCase):
    """Phase 6, Issue #22: Documentation Gemini → OpenCode references."""

    def test_docs_no_inaccurate_gemini_cli_claims(self):
        """Aerospace doc must not claim .gemini/settings.json as active config."""
        aero_path = os.path.join(AIM_ROOT, "docs", "aerospace.md")
        if not os.path.exists(aero_path):
            return  # skip if file doesn't exist
        with open(aero_path, "r") as f:
            content = f.read()
        self.assertNotIn(".gemini/settings.json", content,
                         "aerospace.md must reference opencode.json")


if __name__ == "__main__":
    unittest.main()
