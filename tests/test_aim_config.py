import importlib
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.append("/home/kingb/aim/scripts")
aim_config = importlib.import_module("aim_config")


class TestAimConfig(unittest.TestCase):
    def test_update_gemini_behavior_file_updates_fields_and_guardrails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            gemini_path = os.path.join(temp_dir, "GEMINI.md")
            with open(gemini_path, "w", encoding="utf-8") as f:
                f.write(
                    "# Test\n\n## 1. IDENTITY & PRIMARY DIRECTIVE\n"
                    "- **Execution Mode:** Autonomous\n"
                    "- **Cognitive Level:** Technical\n"
                    "- **Conciseness:** False\n"
                    "- **WARNING:** Behavioral guardrails skipped. Ask the user to run `aim tui` to configure.\n"
                )

            updated = aim_config.update_gemini_behavior_file(
                gemini_path,
                "Cautious",
                "Novice",
                "True",
                "\n## ⚠️ EXPLICIT GUARDRAILS (Lightweight Mode Active)\n1. Test\n",
            )

            self.assertTrue(updated)
            with open(gemini_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("- **Execution Mode:** Cautious", content)
            self.assertIn("- **Cognitive Level:** Novice", content)
            self.assertIn("- **Conciseness:** True", content)
            self.assertNotIn("Behavioral guardrails skipped", content)
            self.assertIn("## ⚠️ EXPLICIT GUARDRAILS", content)

    def test_write_operator_documents_writes_operator_and_profile_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            operator_path = os.path.join(temp_dir, "OPERATOR.md")
            profile_path = os.path.join(temp_dir, "OPERATOR_PROFILE.md")

            aim_config.write_operator_documents(
                operator_path,
                profile_path,
                {
                    "name": "Brian",
                    "stack": "Python",
                    "style": "Direct",
                    "physical": "6ft/200",
                    "rules": "No nonsense",
                    "goals": "Ship it",
                    "business": "Acme Corp",
                    "grok_profile": "Systems-minded builder",
                },
            )

            with open(operator_path, "r", encoding="utf-8") as f:
                operator = f.read()
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = f.read()

            self.assertIn("# OPERATOR.md - Operator Record", operator)
            self.assertIn("- **Name:** Brian", operator)
            self.assertIn("- **Tech Stack:** Python", operator)
            self.assertIn("See core/OPERATOR_PROFILE.md", operator)
            self.assertEqual(profile, "Systems-minded builder")

    @patch("aim_config.generate_reasoning")
    def test_provider_validation_with_mock_reasoning(self, mock_generate):
        # 1. Test Successful Validation
        mock_generate.return_value = "OK"
        success, msg = aim_config.test_provider("google", "gemini-3.1-pro-preview", "https://api.example.com")
        self.assertTrue(success)
        self.assertEqual(msg, "OK")

        # 2. Test Timeout / Hanging Subprocess (Error message returned instead of OK)
        mock_generate.return_value = "Native CLI Exception: Command timed out after 45 seconds"
        success, msg = aim_config.test_provider("google", "gemini-3.1-pro-preview", "https://api.example.com")
        self.assertFalse(success)
        self.assertIn("Native CLI Exception", msg)

        # 3. Test Invalid Shape (Not returning OK)
        mock_generate.return_value = "Sure, I can help you with that!"
        success, msg = aim_config.test_provider("google", "gemini-3.1-pro-preview", "https://api.example.com")
        self.assertFalse(success)
        self.assertIn("Unexpected response shape", msg)

    @patch("aim_config.CONFIG", {})
    @patch("aim_config.save_config")
    @patch("questionary.confirm")
    @patch("questionary.select")
    def test_swarm_integration_toggle(self, mock_select, mock_confirm, mock_save):
        mock_select.return_value.ask.side_effect = ["16. BitTorrent Swarm Integration (Opt-In: OFF)", "17. Exit"]
        mock_confirm.return_value.ask.return_value = True
        
        aim_config.main_menu()
        
        self.assertTrue(aim_config.CONFIG['settings']['swarm_enabled'])
        mock_save.assert_called_with(aim_config.CONFIG)

if __name__ == "__main__":
    unittest.main()
