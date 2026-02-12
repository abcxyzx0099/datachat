"""
Tests for survey_analyzer.specification.validator module.

Tests validation functionality.
"""

import pytest


# ============================================================================
# Validator Tests
# ============================================================================

class TestValidatorFunctions:
    """Test validator functions."""

    def test_validate_specification(self):
        """Test validate_specification function."""
        from survey_analyzer.specification.validator import validate_specification
        assert callable(validate_specification)

    def test_is_valid_specification(self):
        """Test is_valid_specification function."""
        from survey_analyzer.specification.validator import is_valid_specification
        assert callable(is_valid_specification)


# ============================================================================
# Module Level Tests
# ============================================================================

class TestValidatorModule:
    """Test validator module imports."""

    def test_import_validation_error(self):
        """Test ValidationError can be imported."""
        from survey_analyzer.specification.validator import ValidationError
        assert ValidationError is not None

    def test_import_validation_result(self):
        """Test ValidationResult can be imported."""
        from survey_analyzer.specification.validator import ValidationResult
        assert ValidationResult is not None

    def test_import_table_specification_validator(self):
        """Test TableSpecificationValidator can be imported."""
        from survey_analyzer.specification.validator import TableSpecificationValidator
        assert TableSpecificationValidator is not None

    def test_module_exports(self):
        """Test module exports expected functions."""
        from survey_analyzer import specification
        expected_exports = [
            "ValidationError",
            "ValidationResult",
            "TableSpecificationValidator",
            "validate_specification",
            "is_valid_specification",
        ]
        for export in expected_exports:
            assert hasattr(specification, export)
