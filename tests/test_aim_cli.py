import unittest
import subprocess
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
cli_script = os.path.join(aim_root, "scripts", "aim_cli.py")
venv_python = sys.executable

class TestAimCli(unittest.TestCase):
    
    def test_strict_bug_command_requires_flags(self):
        """Verify that 'aim bug' strictly requires --context, --failure, and --intent flags."""
        cmd = [venv_python, cli_script, "bug", "Test strict bug flags"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.assertNotEqual(result.returncode, 0, "aim bug should fail without explicit context flags")
        self.assertIn("MANDATE VIOLATION", result.stdout, "Should output mandate violation warning")
        self.assertIn("You MUST NOT call", result.stdout, "Should instruct the agent to use explicit flags")

    def test_bug_operator_allows_interactive(self):
        """Verify that 'aim bug-operator' exists for humans (though we can't fully test interactive input here easily, we can check it doesn't immediately fail with the same MANDATE VIOLATION)."""
        # We pass a simple echo to stdin to bypass the interactive prompt
        cmd = [venv_python, cli_script, "bug-operator", "Test interactive bug flags"]
        
        try:
            # We expect this to fail because 'gh' isn't fully mocked here or we provide garbage input, 
            # but it should NOT fail with the specific "MANDATE VIOLATION" that the strict agent version does.
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input="Context\nFailure\nIntent\n")
            
            self.assertNotIn("MANDATE VIOLATION", stdout, "Operator command should not trigger the strict agent mandate violation")
            self.assertIn("The Context", stdout, "Should prompt interactively")
        except Exception as e:
            self.fail(f"Failed to execute bug-operator test: {e}")

if __name__ == '__main__':
    unittest.main()