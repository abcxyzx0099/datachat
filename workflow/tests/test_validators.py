"""
Unit tests for validators.

Tests the validation logic for:
- Recoding rules (Step 4)
- Indicators (Step 8)
- Table specifications (Step 9)
"""

import pytest
from workflow.validators import (
    RecodingValidator,
    IndicatorValidator,
    TableSpecsValidator,
    validate_recoding_rules,
    validate_indicators,
    validate_table_specs,
)


# ============================================================================
# TEST DATA
# ============================================================================

SAMPLE_METADATA = [
    {
        "name": "age",
        "label": "Age",
        "variable_type": "numeric",
        "min_value": 18,
        "max_value": 99
    },
    {
        "name": "gender",
        "label": "Gender",
        "variable_type": "numeric",
        "min_value": 1,
        "max_value": 2,
        "value_labels": {1: "Male", 2: "Female"}
    },
    {
        "name": "satisfaction",
        "label": "Satisfaction Rating",
        "variable_type": "numeric",
        "min_value": 1,
        "max_value": 10
    }
]

SAMPLE_INDICATORS = [
    {
        "id": "IND_001",
        "description": "Age distribution",
        "metric": "distribution",
        "underlying_variables": ["age"]
    },
    {
        "id": "IND_002",
        "description": "Gender distribution",
        "metric": "distribution",
        "underlying_variables": ["gender"]
    }
]

SAMPLE_TABLE_SPECS = {
    "tables": [
        {
            "id": "TABLE_001",
            "description": "Age by Gender",
            "row_indicators": ["IND_001"],
            "column_indicators": ["IND_002"],
            "sort_rows": "none",
            "sort_columns": "none",
            "min_count": 30
        }
    ],
    "weighting_variable": None
}


# ============================================================================
# RECODING VALIDATOR TESTS
# ============================================================================

class TestRecodingValidator:
    """Tests for RecodingValidator."""

    def test_valid_recoding_rules(self):
        """Test validation of valid recoding rules."""
        rules = [
            {
                "source_variable": "age",
                "target_variable": "age_group",
                "rule_type": "range",
                "transformations": [
                    {"source": [18, 24], "target": 1, "label": "18-24"},
                    {"source": [25, 34], "target": 2, "label": "25-34"}
                ]
            }
        ]

        result = validate_recoding_rules(rules, SAMPLE_METADATA)

        assert result.is_valid
        assert len(result.errors) == 0
        assert "Source variables exist" in result.checks_performed

    def test_invalid_source_variable(self):
        """Test that non-existent source variables are caught."""
        rules = [
            {
                "source_variable": "nonexistent_var",
                "target_variable": "new_var",
                "rule_type": "range",
                "transformations": []
            }
        ]

        result = validate_recoding_rules(rules, SAMPLE_METADATA)

        assert not result.is_valid
        assert any("not found in metadata" in e for e in result.errors)

    def test_invalid_range(self):
        """Test that invalid ranges are caught."""
        rules = [
            {
                "source_variable": "age",
                "target_variable": "age_group",
                "rule_type": "range",
                "transformations": [
                    {"source": [99, 18], "target": 1, "label": "Invalid"}  # start > end
                ]
            }
        ]

        result = validate_recoding_rules(rules, SAMPLE_METADATA)

        assert not result.is_valid
        assert any("start > end" in e for e in result.errors)

    def test_duplicate_target_variables(self):
        """Test that duplicate target variables are caught."""
        rules = [
            {
                "source_variable": "age",
                "target_variable": "duplicate_var",
                "rule_type": "range",
                "transformations": []
            },
            {
                "source_variable": "gender",
                "target_variable": "duplicate_var",  # Duplicate!
                "rule_type": "mapping",
                "transformations": []
            }
        ]

        result = validate_recoding_rules(rules, SAMPLE_METADATA)

        assert not result.is_valid
        assert any("Duplicate target variables" in e for e in result.errors)


# ============================================================================
# INDICATOR VALIDATOR TESTS
# ============================================================================

class TestIndicatorValidator:
    """Tests for IndicatorValidator."""

    def test_valid_indicators(self):
        """Test validation of valid indicators."""
        result = validate_indicators(SAMPLE_INDICATORS, SAMPLE_METADATA)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_nonexistent_variable(self):
        """Test that non-existent variables are caught."""
        indicators = [
            {
                "id": "IND_001",
                "description": "Test",
                "metric": "distribution",
                "underlying_variables": ["nonexistent_var"]
            }
        ]

        result = validate_indicators(indicators, SAMPLE_METADATA)

        assert not result.is_valid
        assert any("non-existent variable" in e for e in result.errors)

    def test_invalid_metric(self):
        """Test that invalid metrics are caught."""
        indicators = [
            {
                "id": "IND_001",
                "description": "Test",
                "metric": "invalid_metric",
                "underlying_variables": ["age"]
            }
        ]

        result = validate_indicators(indicators, SAMPLE_METADATA)

        assert not result.is_valid
        assert any("invalid metric" in e for e in result.errors)

    def test_duplicate_indicator_ids(self):
        """Test that duplicate indicator IDs are caught."""
        indicators = [
            {
                "id": "IND_001",
                "description": "First",
                "metric": "distribution",
                "underlying_variables": ["age"]
            },
            {
                "id": "IND_001",  # Duplicate!
                "description": "Second",
                "metric": "distribution",
                "underlying_variables": ["gender"]
            }
        ]

        result = validate_indicators(indicators, SAMPLE_METADATA)

        assert not result.is_valid
        assert any("Duplicate indicator IDs" in e for e in result.errors)

    def test_empty_variables(self):
        """Test that empty variable lists are caught."""
        indicators = [
            {
                "id": "IND_001",
                "description": "Test",
                "metric": "distribution",
                "underlying_variables": []  # Empty!
            }
        ]

        result = validate_indicators(indicators, SAMPLE_METADATA)

        assert not result.is_valid
        assert any("no underlying variables" in e for e in result.errors)


# ============================================================================
# TABLE SPECS VALIDATOR TESTS
# ============================================================================

class TestTableSpecsValidator:
    """Tests for TableSpecsValidator."""

    def test_valid_table_specs(self):
        """Test validation of valid table specifications."""
        result = validate_table_specs(
            SAMPLE_TABLE_SPECS,
            SAMPLE_METADATA,
            SAMPLE_INDICATORS
        )

        assert result.is_valid
        assert len(result.errors) == 0

    def test_nonexistent_indicator(self):
        """Test that non-existent indicators are caught."""
        table_specs = {
            "tables": [
                {
                    "id": "TABLE_001",
                    "description": "Test",
                    "row_indicators": ["NONEXISTENT_IND"],
                    "column_indicators": [],
                    "sort_rows": "none",
                    "sort_columns": "none",
                    "min_count": 30
                }
            ],
            "weighting_variable": None
        }

        result = validate_table_specs(
            table_specs,
            SAMPLE_METADATA,
            SAMPLE_INDICATORS
        )

        assert not result.is_valid
        assert any("non-existent indicator" in e for e in result.errors)

    def test_overlapping_indicators(self):
        """Test that overlapping row/column indicators are caught."""
        table_specs = {
            "tables": [
                {
                    "id": "TABLE_001",
                    "description": "Test",
                    "row_indicators": ["IND_001"],
                    "column_indicators": ["IND_001"],  # Overlap!
                    "sort_rows": "none",
                    "sort_columns": "none",
                    "min_count": 30
                }
            ],
            "weighting_variable": None
        }

        result = validate_table_specs(
            table_specs,
            SAMPLE_METADATA,
            SAMPLE_INDICATORS
        )

        assert not result.is_valid
        assert any("overlapping indicators" in e for e in result.errors)

    def test_invalid_sort_option(self):
        """Test that invalid sort options are caught."""
        table_specs = {
            "tables": [
                {
                    "id": "TABLE_001",
                    "description": "Test",
                    "row_indicators": ["IND_001"],
                    "column_indicators": ["IND_002"],
                    "sort_rows": "invalid_sort",  # Invalid!
                    "sort_columns": "none",
                    "min_count": 30
                }
            ],
            "weighting_variable": None
        }

        result = validate_table_specs(
            table_specs,
            SAMPLE_METADATA,
            SAMPLE_INDICATORS
        )

        assert not result.is_valid
        assert any("invalid sort_rows" in e for e in result.errors)

    def test_min_count_too_low(self):
        """Test that min_count <= 0 is caught."""
        table_specs = {
            "tables": [
                {
                    "id": "TABLE_001",
                    "description": "Test",
                    "row_indicators": ["IND_001"],
                    "column_indicators": ["IND_002"],
                    "sort_rows": "none",
                    "sort_columns": "none",
                    "min_count": 0  # Invalid!
                }
            ],
            "weighting_variable": None
        }

        result = validate_table_specs(
            table_specs,
            SAMPLE_METADATA,
            SAMPLE_INDICATORS
        )

        assert not result.is_valid
        assert any("must be greater than 0" in e for e in result.errors)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
