import importlib
import json
import os
import sys
import tempfile
import unittest
from unittest import mock


sys.path.append("/home/kingb/aim/scripts")
aim_init = importlib.import_module("aim_init")


class TestAimInit(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.base_dir = self.temp_dir.name
        for rel_path in ["core", "docs", "archive", "hooks", "src", "synapse"]:
            os.makedirs(os.path.join(self.base_dir, rel_path), exist_ok=True)

        self.originals = {
            "BASE_DIR": aim_init.BASE_DIR,
            "CORE_DIR": aim_init.CORE_DIR,
            "DOCS_DIR": aim_init.DOCS_DIR,
            "ARCHIVE_DIR": aim_init.ARCHIVE_DIR,
            "HOOKS_DIR": aim_init.HOOKS_DIR,
            "SRC_DIR": aim_init.SRC_DIR,
            "VENV_PYTHON": aim_init.VENV_PYTHON,
        }

        aim_init.BASE_DIR = self.base_dir
        aim_init.CORE_DIR = os.path.join(self.base_dir, "core")
        aim_init.DOCS_DIR = os.path.join(self.base_dir, "docs")
        aim_init.ARCHIVE_DIR = os.path.join(self.base_dir, "archive")
        aim_init.HOOKS_DIR = os.path.join(self.base_dir, "hooks")
        aim_init.SRC_DIR = os.path.join(self.base_dir, "src")
        aim_init.VENV_PYTHON = "/usr/bin/python3"

    def tearDown(self):
        for name, value in self.originals.items():
            setattr(aim_init, name, value)

    def _run_init(self, responses):
        with mock.patch.object(aim_init, "register_hooks"), mock.patch.object(
            aim_init, "trigger_bootstrap"
        ), mock.patch("builtins.input", side_effect=responses):
            aim_init.init_workspace()

    def test_init_persists_behavior_and_profile_answers(self):
        self._run_init(
            [
                "n",  # wipe docs
                "n",  # wipe brain
                "",  # configure behavior now
                "1",  # cognitive level: Novice
                "y",  # concise
                "2",  # execution mode: Cautious
                "2",  # lightweight guardrails
                "Brian",  # name
                "Python",  # stack
                "Direct",  # style
                "6ft/200",  # physical
                "No nonsense",  # rules
                "Ship it",  # goals
                "Acme Corp",  # business
                "Systems-minded builder",  # grok profile
                "/vault",  # obsidian path
                "",  # allowed root default
            ]
        )

        with open(os.path.join(self.base_dir, "GEMINI.md"), "r", encoding="utf-8") as f:
            gemini = f.read()
        with open(
            os.path.join(self.base_dir, "core", "OPERATOR.md"), "r", encoding="utf-8"
        ) as f:
            operator_md = f.read()
        with open(
            os.path.join(self.base_dir, "core", "OPERATOR_PROFILE.md"),
            "r",
            encoding="utf-8",
        ) as f:
            profile = f.read()
        with open(
            os.path.join(self.base_dir, "core", "CONFIG.json"), "r", encoding="utf-8"
        ) as f:
            config = json.load(f)

        self.assertIn("- **Operator:** Brian", gemini)
        self.assertIn("- **Execution Mode:** Cautious", gemini)
        self.assertIn("- **Cognitive Level:** Novice", gemini)
        self.assertIn("- **Conciseness:** True", gemini)
        self.assertIn("## ⚠️ EXPLICIT GUARDRAILS", gemini)

        self.assertIn("- **Name:** Brian", operator_md)
        self.assertIn("- **Tech Stack:** Python", operator_md)
        self.assertIn("- **Style:** Direct", operator_md)
        self.assertIn("- **Age/Height/Weight:** 6ft/200", operator_md)
        self.assertIn("- **Life Rules:** No nonsense", operator_md)
        self.assertIn("- **Primary Goal:** Ship it", operator_md)
        self.assertIn("Acme Corp", operator_md)
        self.assertIn("See core/OPERATOR_PROFILE.md", operator_md)

        self.assertEqual(profile, "Systems-minded builder")
        self.assertEqual(config["settings"]["obsidian_vault_path"], "/vault")
        self.assertEqual(config["settings"]["archive_retention_days"], 30)
        self.assertEqual(config["settings"]["auto_distill_tier"], "T4")
        self.assertIn("tiers", config["models"])
        self.assertEqual(config["models"]["tiers"]["default_reasoning"]["provider"], "google")

    def test_init_skip_behavior_keeps_defaults_and_inserts_warning(self):
        self._run_init(
            [
                "n",  # wipe docs
                "n",  # wipe brain
                "SKIP",  # skip behavior
                "Operator",  # name
                "General",  # stack
                "Direct",  # style
                "N/A",  # physical
                "N/A",  # rules
                "N/A",  # goals
                "None provided.",  # business
                "None.",  # grok profile
                "",  # obsidian path
                "",  # allowed root default
            ]
        )

        with open(os.path.join(self.base_dir, "GEMINI.md"), "r", encoding="utf-8") as f:
            gemini = f.read()

        self.assertIn("- **Execution Mode:** Autonomous", gemini)
        self.assertIn("- **Cognitive Level:** Technical", gemini)
        self.assertIn("- **Conciseness:** False", gemini)
        self.assertIn("Behavioral guardrails skipped", gemini)


if __name__ == "__main__":
    unittest.main()
