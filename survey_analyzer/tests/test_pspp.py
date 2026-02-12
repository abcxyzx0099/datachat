"""
Tests for survey_analyzer.pspp module.

Tests PSPP syntax generation and execution.
"""

import pytest


# ============================================================================
# CTablesSyntaxGenerator Tests
# ============================================================================

class TestCTablesSyntaxGenerator:
    """Test CTablesSyntaxGenerator class."""

    def test_default_initialization(self):
        """Test CTablesSyntaxGenerator with default parameters."""
        from survey_analyzer.pspp import CTablesSyntaxGenerator
        gen = CTablesSyntaxGenerator()

        assert gen is not None

    def test_import_pspp_executor(self):
        """Test PSPPExecutor can be imported."""
        from survey_analyzer.pspp import PSPPExecutor
        assert PSPPExecutor is not None

    def test_module_exports(self):
        """Test module exports expected classes."""
        from survey_analyzer import pspp
        expected_exports = [
            "CTablesSyntaxGenerator",
            "PSPPExecutor"
        ]
        for export in expected_exports:
            assert hasattr(pspp, export)

    def test_generate_syntax_method(self):
        """Test generating crosstab syntax."""
        from survey_analyzer.pspp import CTablesSyntaxGenerator
        gen = CTablesSyntaxGenerator()

        # Use a list of table specifications
        table_specs = [
            {
                "table_id": "table1",
                "row_variable": "gender",
                "column_variable": "satisfaction",
                "statistics": ["count", "columnpct"]
            }
        ]
        syntax = gen.generate_syntax(table_specs)

        assert isinstance(syntax, str)
        assert "CTABLES" in syntax.upper()
        assert "/TABLE" in syntax.upper()


# ============================================================================
# PSPPExecutor Tests
# ============================================================================

class TestPSPPExecutor:
    """Test PSPPExecutor class."""

    def test_default_initialization(self):
        """Test PSPPExecutor with default parameters."""
        from survey_analyzer.pspp import PSPPExecutor
        executor = PSPPExecutor()

        assert executor.config is not None
        assert executor.config.pspp_path == "pspp"

    def test_execute_syntax_method(self):
        """Test execute_syntax method exists."""
        from survey_analyzer.pspp import PSPPExecutor
        executor = PSPPExecutor()

        # Test that method exists
        assert hasattr(executor, "execute_syntax")
        assert callable(executor.execute_syntax)

    def test_check_pspp_available(self):
        """Test check_pspp_available method."""
        from survey_analyzer.pspp import PSPPExecutor
        executor = PSPPExecutor()

        # Test that method exists and returns a boolean
        result = executor.check_pspp_available()
        assert isinstance(result, bool)

    def test_get_pspp_version(self):
        """Test get_pspp_version method."""
        from survey_analyzer.pspp import PSPPExecutor
        executor = PSPPExecutor()

        # Test that method exists
        assert hasattr(executor, "get_pspp_version")
        # Version will be None if pspp is not installed
        version = executor.get_pspp_version()
        assert version is None or isinstance(version, str)


# ============================================================================
# Module Level Tests
# ============================================================================

class TestPSPPModule:
    """Test PSPP module imports."""

    def test_import_ctables_syntax_generator(self):
        """Test CTablesSyntaxGenerator can be imported."""
        from survey_analyzer.pspp import CTablesSyntaxGenerator
        assert CTablesSyntaxGenerator is not None

    def test_import_pspp_executor(self):
        """Test PSPPExecutor can be imported."""
        from survey_analyzer.pspp import PSPPExecutor
        assert PSPPExecutor is not None

    def test_module_exports(self):
        """Test module exports expected classes."""
        from survey_analyzer import pspp
        expected_exports = [
            "CTablesSyntaxGenerator",
            "PSPPExecutor"
        ]
        for export in expected_exports:
            assert hasattr(pspp, export)
