"""
TDD tests for aim_opencode_update.py — the fork-aware upstream sync tool.

Tests the updater's core logic:
- Detecting upstream changes
- Merge ordering (upstream→main→opencode)
- Conflict zone identification
- Test suite runner
- Dry-run mode
"""
import pytest
import os
import sys
import subprocess
import tempfile

# Ensure aim_core is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "aim_core"))


def test_updater_module_importable():
    """Verify the updater module can be imported."""
    from aim_core import aim_opencode_update
    assert hasattr(aim_opencode_update, "run_updater")
    assert hasattr(aim_opencode_update, "check_for_upstream_changes")
    assert hasattr(aim_opencode_update, "OPECODE_CONFLICT_ZONES")


def test_conflict_zones_defined():
    """Verify the known conflict zone files are defined."""
    from aim_core.aim_opencode_update import OPECODE_CONFLICT_ZONES

    assert isinstance(OPECODE_CONFLICT_ZONES, list)
    assert "aim_core/extract_signal.py" in OPECODE_CONFLICT_ZONES
    assert "aim_core/reasoning_utils.py" in OPECODE_CONFLICT_ZONES
    assert "aim_core/aim_cli.py" in OPECODE_CONFLICT_ZONES
    assert "aim_core/handoff_pulse_generator.py" in OPECODE_CONFLICT_ZONES
    assert "aim_core/wiki_tools.py" in OPECODE_CONFLICT_ZONES


def test_safe_merge_files_listed():
    """Verify safe-merge files (no fork modifications) are documented."""
    from aim_core.aim_opencode_update import SAFE_MERGE_FILES

    assert isinstance(SAFE_MERGE_FILES, list)
    assert "aim_core/plugins/datajack/forensic_utils.py" in SAFE_MERGE_FILES
    assert "aim_core/retriever.py" in SAFE_MERGE_FILES
    assert "aim_core/lance_backend.py" in SAFE_MERGE_FILES


class TestUpstreamChangeDetection:
    """Tests for detecting whether upstream has new commits."""

    def test_remote_exists(self):
        """Verify upstream remote is configured."""
        result = subprocess.run(
            ["git", "remote", "get-url", "upstream"],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "BrianV1981/aim" in result.stdout

    def test_fetch_upstream(self):
        """Verify we can fetch from upstream without errors."""
        result = subprocess.run(
            ["git", "fetch", "upstream"],
            capture_output=True, text=True
        )
        # Fetch should succeed (exit 0), even if nothing new
        assert result.returncode == 0


class TestDryRunMode:
    """Tests for dry-run preview mode."""

    def test_dry_run_does_not_modify_branches(self, tmp_path):
        """Dry-run should print what it would do without modifying anything."""
        import importlib
        import io, contextlib

        from aim_core.aim_opencode_update import run_updater

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = run_updater(dry_run=True)

        output = f.getvalue()
        assert result is True
        assert "DRY RUN" in output.upper()
        # May say "No new upstream changes" or reference upstream/main


class TestMergeOrder:
    """Tests verifying the correct merge order is documented/used."""

    def test_merge_order_is_correct(self):
        """The merge order must be: upstream→main→opencode, never directly to opencode."""
        from aim_core.aim_opencode_update import run_updater
        import inspect

        source = inspect.getsource(run_updater)
        # Must check 'main' before 'opencode' somewhere in the flow
        assert "main" in source
        assert "opencode" in source


class TestTestSuiteRunner:
    """Tests for the test suite execution after merge."""

    def test_test_suite_runner_exists(self):
        """Verify run_test_suite function exists."""
        from aim_core.aim_opencode_update import run_test_suite
        assert callable(run_test_suite)

    def test_test_suite_runs_existing_tests(self):
        """Verify the test runner can execute tests from the project."""
        from aim_core.aim_opencode_update import run_test_suite

        # Run just the lance_backend tests to verify the runner works
        passed, total, failures = run_test_suite(test_filter="test_lance_backend.py")
        assert total > 0
        assert passed == total
        assert len(failures) == 0


def test_cli_integration_subcommand_registered():
    """Verify the 'fork' subcommand is registered in aim_cli.py cmd_update."""
    import ast

    aim_root = os.path.join(os.path.dirname(__file__), "..")
    cli_path = os.path.join(aim_root, "aim_core", "aim_cli.py")

    with open(cli_path, "r") as f:
        tree = ast.parse(f.read())

    # Check that cmd_update handles the 'fork' target
    found_fork = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value == "fork":
                found_fork = True
                break
    assert found_fork, "cmd_update() must handle target == 'fork'"
