"""
Tests for survey_analyzer.__main__ module.

Tests the main entry point.
"""

import pytest


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
