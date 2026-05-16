import os
import sys
import subprocess
from unittest import mock
import pytest

# Add worktree root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aim_core import aim_reincarnate

@mock.patch('aim_core.aim_reincarnate.subprocess.Popen')
@mock.patch('aim_core.aim_reincarnate.subprocess.run')
@mock.patch('aim_core.aim_reincarnate.os.path.exists')
@mock.patch('aim_core.aim_reincarnate.os.path.getmtime')
@mock.patch('aim_core.aim_reincarnate.time.time')
@mock.patch('aim_core.aim_reincarnate.time.sleep')
def test_aim_reincarnate_tmux_native_prompt(mock_sleep, mock_time, mock_getmtime, mock_exists, mock_run, mock_popen):
    # Setup mocks
    mock_exists.return_value = True
    mock_getmtime.return_value = 1000
    mock_time.return_value = 1010
    
    # We want to catch sys.exit(1) if it happens unexpectedly
    with mock.patch.dict('os.environ', {'TMUX': 'yes'}):
        try:
            aim_reincarnate.main()
        except SystemExit:
            pass
            
    # Check that subprocess.run was called with 'tmux new-session' and '-i'
    tmux_spawn_called = False
    for call in mock_run.call_args_list:
        args, kwargs = call
        if args and isinstance(args[0], list) and args[0][0] == 'tmux' and 'new-session' in args[0]:
            assert '-i' in args[0], "Native prompt flag '-i' is missing from tmux spawn command"
            assert any("Wake up. MANDATE" in str(arg) for arg in args[0]), "Wake up prompt text is missing from tmux spawn command"
            tmux_spawn_called = True
            
        # Verify load-buffer is no longer called
        if args and isinstance(args[0], list) and args[0][0] == 'tmux' and 'load-buffer' in args[0]:
            pytest.fail("load-buffer was called, but should have been removed for native prompt injection")
            
    assert tmux_spawn_called, "tmux new-session was not called"
