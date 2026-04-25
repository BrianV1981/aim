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

class TestCognitiveMantra(unittest.TestCase):
    def setUp(self):
        os.makedirs(state_dir, exist_ok=True)
        if os.path.exists(state_file):
            os.remove(state_file)

    def tearDown(self):
        if os.path.exists(state_file):
            os.remove(state_file)

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
        
        # Execute the hook
        result = subprocess.run(
            [sys.executable, hook_script],
            input=json.dumps(payload),
            text=True,
            capture_output=True
        )
        
        self.assertEqual(result.returncode, 0, f"Hook failed with error: {result.stderr}")
        
        try:
            output = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            self.fail(f"Hook returned invalid JSON: {result.stdout}")
        
        # Verify hookSpecificOutput is present
        self.assertIn("hookSpecificOutput", output)
        self.assertIn("additionalContext", output["hookSpecificOutput"])
        
        context = output["hookSpecificOutput"]["additionalContext"]
        
        # Verify the new anti-chunking instruction is present
        self.assertIn("Do NOT split the recitation into multiple parts", context)
        self.assertIn("Output the entire mantra in a single, continuous block", context)
        
        # Verify state file was updated
        self.assertTrue(os.path.exists(state_file))
        with open(state_file, 'r') as f:
            state = json.load(f)
            self.assertEqual(state["last_mantra"], 51)
            self.assertEqual(state["session_id"], "test-session-123")

if __name__ == '__main__':
    unittest.main()
