"""
Tests for survey_analyzer.specification.validator module - Phase 2.

Tests focusing on covering validation logic, edge cases, and complex scenarios.
"""

import pytest


# ============================================================================
# Validation Logic Edge Cases
# ============================================================================

class TestValidationLogicEdgeCases:
    """Test edge cases in validation logic."""

    def test_validate_with_empty_spec(self):
        """Test validation with completely empty spec."""
        from survey_analyzer.specification.validator import TableSpecificationValidator

        validator = TableSpecificationValidator()

        result = validator.validate({})

        # Empty spec should fail - missing required sections
        assert result.is_valid is False
        assert len(result.errors) > 0


# ============================================================================
# Reference Validation Edge Cases
# ============================================================================

class TestReferenceValidationEdgeCases:
    """Test edge cases in reference validation."""

    def test_variable_source_raw(self):
        """Test RAW variable source is valid."""
        from survey_analyzer.specification.validator import TableSpecificationValidator, VariableSource

        validator = TableSpecificationValidator(metadata={"q1": {"label": "Q1"}})

        spec = {
            "metadata": {"version": "1.0"},
            "tables": [{
                "id": "t1",
                "type": "crosstab",
                "rows": {
                    "variable": "q1",
                    "source": VariableSource.RAW.value
                }
            }]
        }

        result = validator.validate(spec)

        # RAW source reference should pass
        assert result.is_valid is True

    def test_recoded_variable_in_metadata(self):
        """Test warning when recoded variable IS in metadata."""
        from survey_analyzer.specification.validator import TableSpecificationValidator

        validator = TableSpecificationValidator(
            metadata={"q1": {"label": "Q1"}, "q1_recoded": {"label": "Recoded Q1"}}
        )

        spec = {
            "metadata": {"version": "1.0"},
            "tables": [],
            "global_recodings": [{
                "variable": "q1_recoded",
                "type": "value_map",
                "value_mappings": {"1": "Yes"}
            }]
        }

        result = validator.validate(spec)

        # Should be valid - recoded variable is in metadata
        assert result.is_valid is True
        assert len(result.warnings) > 0


# ============================================================================
# Syntax Validation Edge Cases
# ============================================================================

class TestSyntaxValidationEdgeCases:
    """Test edge cases in PSPP syntax validation."""

    def test_crosstab_requires_dimensions(self):
        """Test crosstab requires rows or columns."""
        from survey_analyzer.specification.validator import TableSpecificationValidator, TableType

        validator = TableSpecificationValidator(
            metadata={"q1": {"label": "Q1"}}
        )

        spec = {
            "metadata": {"version": "1.0"},
            "tables": [{
                "id": "t1",
                "type": TableType.CROSSTAB.value
            }]
        }

        result = validator.validate(spec)

        assert result.is_valid is False
        assert any("requires 'rows' or 'columns'" in e.message for e in result.errors)


# ============================================================================
# Complex Integration Tests
# ============================================================================

class TestValidatorIntegration:
    """Integration tests combining multiple validation stages."""

    def test_crosstab_without_title_fails(self):
        """Test crosstab without title field fails validation."""
        from survey_analyzer.specification.validator import TableSpecificationValidator, TableType

        validator = TableSpecificationValidator(
            metadata={"q1": {"label": "Q1"}}
        )

        spec = {
            "metadata": {"version": "1.0"},
            "tables": [{
                "id": "t1",
                "type": TableType.CROSSTAB.value
            }]
        }

        result = validator.validate(spec)

        # Should fail - missing required title field
        assert result.is_valid is False
        assert any("title" in e.message.lower() for e in result.errors)

    def test_valid_spec_with_metadata(self):
        """Test complete valid spec with metadata reference."""
        from survey_analyzer.specification.validator import TableSpecificationValidator

        validator = TableSpecificationValidator(
            metadata={"q1": {"label": "Q1"}, "q2": {"label": "Q2"}}
        )

        spec = {
            "metadata": {"version": "1.0"},
            "tables": [{
                "id": "t1",
                "type": "crosstab",
                "rows": {
                    "variable": "q1",
                    "source": "raw"
                },
                "columns": {
                    "variable": "q2",
                    "source": "raw"
                }
            }],
            "indicators": [{
                "id": "sat_ind",
                "name": "Satisfaction",
                "variables": ["q1"]
            }],
            "global_recodings": [],
            "output_settings": {}
        }

        result = validator.validate(spec)

        # Should be valid - metadata is provided, references are valid
        assert result.is_valid is True
        assert len(result.errors) == 0
