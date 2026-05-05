import unittest
from unittest.mock import patch, MagicMock
import os
from aim_core.aim_swarm import spawn_coagent, send_message, capture_output, check_coagent, kill_coagent, list_sessions

class TestAimSwarm(unittest.TestCase):
    @patch('subprocess.run')
    @patch('os.path.isdir')
    @patch('time.sleep')
    def test_spawn_coagent_success(self, mock_sleep, mock_isdir, mock_run):
        mock_isdir.return_value = True
        # Mock has-session failing (session doesn't exist)
        mock_has_session = MagicMock()
        mock_has_session.returncode = 1
        
        # Mock new-session succeeding
        mock_new_session = MagicMock()
        mock_new_session.returncode = 0
        
        mock_run.side_effect = [mock_has_session, mock_new_session]
        
        result = spawn_coagent("test_agent", "/test/dir", None)
        
        self.assertEqual(result["status"], "spawned")
        self.assertEqual(result["session"], "test_agent")
        
        # Verify new-session was called with gemini --yolo
        mock_run.assert_called_with(["tmux", "new-session", "-d", "-s", "test_agent", "-c", "/test/dir", "gemini", "--yolo"], check=True)

    @patch('subprocess.run')
    @patch('os.path.isdir')
    def test_spawn_coagent_already_exists(self, mock_isdir, mock_run):
        mock_isdir.return_value = True
        # Mock has-session succeeding (session exists)
        mock_has_session = MagicMock()
        mock_has_session.returncode = 0
        mock_run.return_value = mock_has_session
        
        result = spawn_coagent("test_agent", "/test/dir", None)
        
        self.assertIn("error", result)
        self.assertIn("already exists", result["error"])

if __name__ == '__main__':
    unittest.main()
