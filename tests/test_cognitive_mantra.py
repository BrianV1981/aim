import unittest
import os
import json
import sys
import subprocess

current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
hook_script = os.path.join(aim_root, "hooks", "cognitive_mantra.py")
state_dir = os.path.join(aim_root, "hooks", ".state")
state_file = os.path.join(state_dir, "mantra_state.json")
continuity_dir = os.path.join(aim_root, "continuity")
mantra_pulse_file = os.path.join(continuity_dir, "MANTRA_PULSE.md")


class TestCognitiveMantra(unittest.TestCase):
    def setUp(self):
        os.makedirs(state_dir, exist_ok=True)
        os.makedirs(continuity_dir, exist_ok=True)
        if os.path.exists(state_file):
            os.remove(state_file)
        if os.path.exists(mantra_pulse_file):
            os.remove(mantra_pulse_file)

    def tearDown(self):
        if os.path.exists(state_file):
            os.remove(state_file)
        if os.path.exists(mantra_pulse_file):
            os.remove(mantra_pulse_file)

    def test_mantra_triggers_and_contains_no_split_instruction(self):
        # Create a payload with 51 tool calls to trigger the default interval (50)
        tool_calls = [{"name": f"tool_{i}", "args": {}} for i in range(51)]
        payload = {
            "sessionId": "test-session-123",
            "messages": [
                {
                    "role": "model",
                    "toolCalls": tool_calls
                }
            ]
        }

        result = subprocess.run(
            [sys.executable, hook_script],
            input=json.dumps(payload),
            text=True,
            capture_output=True
        )

        self.assertEqual(result.returncode, 0, f"Hook failed with error: {result.stderr}")

        # Post-Phase-4: output is empty JSON (mantra is written to file instead)
        try:
            output = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            self.fail(f"Hook returned invalid JSON: {result.stdout}")

        self.assertEqual(output, {}, "Post-Phase 4: output must be empty JSON (mantra written to file)")

        # Verify mantra pulse file was written
        self.assertTrue(os.path.exists(mantra_pulse_file),
                        "Mantra must be written to continuity/MANTRA_PULSE.md")

        with open(mantra_pulse_file, "r", encoding="utf-8") as f:
            mantra_content = f.read()

        # Verify the anti-chunking instruction is present
        self.assertIn("Do NOT split the recitation into multiple parts", mantra_content)
        self.assertIn("Output the entire mantra in a single, continuous block", mantra_content)
        self.assertIn("MANTRA", mantra_content)


if __name__ == "__main__":
    unittest.main()
