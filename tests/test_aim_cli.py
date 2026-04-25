from unittest.mock import patch, MagicMock
import unittest
import subprocess
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
aim_root = os.path.dirname(current_dir)
cli_script = os.path.join(aim_root, "aim_core", "aim_cli.py")
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
    @patch('aim_core.aim_cli.subprocess.run')
    @patch('aim_core.aim_cli.os.getcwd')
    def test_cmd_promote_worktree_resolution(self, mock_getcwd, mock_run):
        """Verify cmd_promote correctly resolves repo_root when run inside a worktree."""
        from aim_core.aim_cli import cmd_promote, BASE_DIR
        
        # Simulate being inside a worktree
        worktree_dir = os.path.join(BASE_DIR, 'workspace', 'issue-999')
        mock_getcwd.return_value = worktree_dir
        
        # Mock git branch --show-current
        mock_result = MagicMock()
        mock_result.stdout = 'fix/issue-999\\n'
        mock_run.return_value = mock_result
        
        args = MagicMock()
        
        # Run promote
        try:
            cmd_promote(args)
        except Exception:
            pass # Ignore cleanup errors if any
            
        # The first call is 'git branch --show-current' in BASE_DIR (which is the worktree)
        # The second call is 'git fetch origin' in repo_root
        
        # Find the fetch call
        fetch_call = None
        for call in mock_run.call_args_list:
            if call[0][0] == ['git', 'fetch', 'origin']:
                fetch_call = call
                break
                
        self.assertIsNotNone(fetch_call, 'git fetch origin was not called')
        
        # Assert cwd is the parent of workspace, not BASE_DIR
        expected_repo_root = os.path.dirname(os.path.dirname(BASE_DIR))
        self.assertEqual(fetch_call[1].get('cwd'), expected_repo_root, 'cmd_promote did not use the correct repo_root')
