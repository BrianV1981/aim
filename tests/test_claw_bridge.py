import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
import claw_bridge

class TestClawBridge(unittest.IsolatedAsyncioTestCase):
    @patch('claw_bridge.subprocess.run')
    @patch('claw_bridge.asyncio.sleep')
    async def test_tmux_send_basic(self, mock_sleep, mock_run):
        await claw_bridge.tmux_send("test_session", "hi")
        
        # Should call mock_run for 'h', 'i', and 'C-m'
        self.assertEqual(mock_run.call_count, 3)
        calls = mock_run.call_args_list
        self.assertEqual(calls[0][0][0], ["tmux", "send-keys", "-t", "test_session", "h"])
        self.assertEqual(calls[1][0][0], ["tmux", "send-keys", "-t", "test_session", "i"])
        self.assertEqual(calls[2][0][0], ["tmux", "send-keys", "-t", "test_session", "C-m"])

    @patch('claw_bridge.subprocess.run')
    @patch('claw_bridge.asyncio.sleep')
    async def test_tmux_send_special_chars(self, mock_sleep, mock_run):
        await claw_bridge.tmux_send("test_session", 'a " $')
        
        self.assertEqual(mock_run.call_count, 6)
        calls = mock_run.call_args_list
        self.assertEqual(calls[0][0][0], ["tmux", "send-keys", "-t", "test_session", "a"])
        self.assertEqual(calls[1][0][0], ["tmux", "send-keys", "-t", "test_session", "Space"])
        self.assertEqual(calls[2][0][0], ["tmux", "send-keys", "-t", "test_session", '\\"'])
        self.assertEqual(calls[3][0][0], ["tmux", "send-keys", "-t", "test_session", "Space"])
        self.assertEqual(calls[4][0][0], ["tmux", "send-keys", "-t", "test_session", "\\$"])
        self.assertEqual(calls[5][0][0], ["tmux", "send-keys", "-t", "test_session", "C-m"])

if __name__ == '__main__':
    unittest.main()
