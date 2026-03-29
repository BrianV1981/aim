import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
import aim_swarm

class TestAimSwarm(unittest.TestCase):
    @patch('aim_swarm.subprocess.run')
    @patch('aim_swarm.os.path.exists')
    def test_cmd_down_without_synapse(self, mock_exists, mock_run):
        mock_exists.return_value = False
        aim_swarm.cmd_down()
        
        # Verify it tries to kill claw95 using tmux directly
        mock_run.assert_any_call(["tmux", "kill-session", "-t", "claw95"], stdout=aim_swarm.subprocess.DEVNULL, stderr=aim_swarm.subprocess.DEVNULL)
        # Verify it kills the nodes
        mock_run.assert_any_call(["tmux", "kill-session", "-t", "backend_node"], stdout=aim_swarm.subprocess.DEVNULL, stderr=aim_swarm.subprocess.DEVNULL)
        mock_run.assert_any_call(["tmux", "kill-session", "-t", "frontend_node"], stdout=aim_swarm.subprocess.DEVNULL, stderr=aim_swarm.subprocess.DEVNULL)
        # Verify it kills the python bridges
        mock_run.assert_any_call(["pkill", "-f", "claw_bridge.py"], stdout=aim_swarm.subprocess.DEVNULL, stderr=aim_swarm.subprocess.DEVNULL)

    @patch('aim_swarm.os.system')
    @patch('aim_swarm.subprocess.Popen')
    @patch('aim_swarm.subprocess.run')
    @patch('aim_swarm.os.path.exists')
    @patch('aim_swarm.time.sleep')
    @patch('aim_swarm.cmd_down')
    def test_cmd_up(self, mock_cmd_down, mock_sleep, mock_exists, mock_run, mock_popen, mock_system):
        mock_exists.return_value = True
        aim_swarm.cmd_up()
        
        # Verify it cleans up first
        mock_cmd_down.assert_called_once()
        
        # Verify node creation
        mock_run.assert_any_call(["tmux", "new-session", "-d", "-s", "backend_node", "bash -c 'cd ~/aim_benchmarks/swarm_backend && source venv/bin/activate && gemini'"], check=True)
        mock_run.assert_any_call(["tmux", "new-session", "-d", "-s", "frontend_node", "bash -c 'cd ~/aim_benchmarks/swarm_frontend && source venv/bin/activate && gemini'"], check=True)
        
        # Verify bridges are booted
        self.assertEqual(mock_popen.call_count, 2)
        
        # Verify synapse launch
        self.assertTrue(mock_system.call_args[0][0].endswith("dev-stack.sh"))

if __name__ == '__main__':
    unittest.main()
