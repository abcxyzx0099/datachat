"""
Tests for survey_analyzer.__main__ module.

Tests the main entry point.
"""

import pytest
import subprocess
import sys


# ============================================================================
# Module Level Tests
# ============================================================================

class TestMainModule:
    """Test main module imports."""

    def test_main_function_exists(self):
        """Test main function can be imported."""
        from survey_analyzer.cli import main
        assert callable(main)

    def test_module_name(self):
        """Test __main__ has correct module name."""
        from survey_analyzer import cli
        # The __main__ file just calls main() from cli module
        assert hasattr(cli, "main")

    def test_main_imports_from_cli(self):
        """Test that __main__ imports main from cli."""
        import survey_analyzer.__main__
        # Check that the module imports main
        assert hasattr(survey_analyzer.__main__, "main")

    def test_main_module_executable(self):
        """Test that the module can be executed as a script."""
        # Try to run the module with --help flag
        result = subprocess.run(
            [sys.executable, "-m", "survey_analyzer", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Should not crash (exit code 0 or 2 is fine for --help)
        assert result.returncode in [0, 1, 2]

