"""
Unit Tests for Validation Layer

This module contains comprehensive unit tests for all validation functions:
- agent/validation/recoding.py: Recoding rule validation
- agent/validation/indicators.py: Indicator validation
- agent/validation/tables.py: Table specification validation

Test Coverage:
1. Recoding Rules Validation (8 validation checks)
2. Indicators Validation (6 validation checks)
3. Table Specifications Validation (7 validation checks)
4. ValidationResult dataclass behavior
5. Edge cases and error scenarios
6. Metadata normalization (various input formats)
"""

import pytest
from typing import Dict, Any, List
from agent.validation.recoding import (
    ValidationResult,
    validate_recoding_rules,
    _check_structure_completeness,
    _check_source_variables_exist,
    _check_target_variable_uniqueness,
    _check_transformation_type_match,
    _check_target_uniqueness_within_rule,
    check_numeric_ranges,
    check_range_overlap,
    check_coverage_completeness,
    _normalize_metadata,
)
from agent.validation.indicators import (
    validate_indicators,
    _check_structure_completeness as _check_indicators_structure,
    _check_variables_exist,
    _check_indicator_name_uniqueness,
    _check_indicator_sizes,
    _check_variable_uniqueness_within_indicator,
    _extract_variable_names,
)
from agent.validation.tables import (
    validate_table_specs,
    _check_structure_completeness as _check_tables_structure,
    _check_row_variables_exist,
    _check_column_variables_exist,
    _check_variables_are_categorical,
    _check_statistics_are_valid,
    _check_table_id_uniqueness,
    _check_weight_variables,
    _normalize_metadata as _normalize_tables_metadata,
)


# =============================================================================
# Test Fixtures for Validation Artifacts
# =============================================================================

@pytest.fixture
def sample_variable_metadata() -> Dict[str, Dict[str, Any]]:
    """
    Sample variable metadata for validation testing.

    Includes:
    - Numeric variables (age, income)
    - Categorical variables (gender, education, satisfaction)
    - Binary variable (employed)
    """
    return {
        "age": {
            "name": "age",
            "label": "Respondent Age",
            "variable_type": "numeric",
            "min_value": 18,
            "max_value": 99,
            "value_labels": {},
        },
        "income": {
            "name": "income",
            "label": "Annual Income",
            "variable_type": "numeric",
            "min_value": 20000,
            "max_value": 150000,
            "value_labels": {},
        },
        "gender": {
            "name": "gender",
            "label": "Gender",
            "variable_type": "numeric",
            "min_value": 1,
            "max_value": 3,
            "value_labels": {1: "Male", 2: "Female", 3: "Other"},
        },
        "education": {
            "name": "education",
            "label": "Education Level",
            "variable_type": "numeric",
            "min_value": 1,
            "max_value": 5,
            "value_labels": {1: "Less than HS", 2: "HS", 3: "College", 4: "Bachelor", 5: "Graduate"},
        },
        "satisfaction": {
            "name": "satisfaction",
            "label": "Satisfaction",
            "variable_type": "numeric",
            "min_value": 1,
            "max_value": 5,
            "value_labels": {1: "Very Dissatisfied", 5: "Very Satisfied"},
        },
        "weight": {
            "name": "weight",
            "label": "Survey Weight",
            "variable_type": "numeric",
            "min_value": 0.5,
            "max_value": 2.0,
            "value_labels": {},
        },
    }


@pytest.fixture
def valid_recoding_rules() -> Dict[str, Any]:
    """
    Valid recoding rules for testing.

    Includes:
    - Range grouping for age
    - Range grouping for income
    """
    return {
        "recoding_rules": [
            {
                "source_variable": "age",
                "target_variable": "age_group",
                "transformation_type": "range_grouping",
                "rules": [
                    {"source_min": 18, "source_max": 24, "target_value": 1, "target_label": "18-24"},
                    {"source_min": 25, "source_max": 34, "target_value": 2, "target_label": "25-34"},
                    {"source_min": 35, "source_max": 44, "target_value": 3, "target_label": "35-44"},
                    {"source_min": 45, "source_max": 99, "target_value": 4, "target_label": "45+"},
                ],
                "description": "Group age into meaningful ranges",
            },
            {
                "source_variable": "income",
                "target_variable": "income_group",
                "transformation_type": "range_grouping",
                "rules": [
                    {"source_min": 20000, "source_max": 40000, "target_value": 1, "target_label": "Low"},
                    {"source_min": 40001, "source_max": 70000, "target_value": 2, "target_label": "Medium"},
                    {"source_min": 70001, "source_max": 150000, "target_value": 3, "target_label": "High"},
                ],
                "description": "Group income into brackets",
            },
        ]
    }


@pytest.fixture
def invalid_recoding_rules() -> Dict[str, Any]:
    """
    Invalid recoding rules for testing error detection.

    Includes various validation errors:
    - Missing source variable
    - Invalid ranges (min > max)
    - Overlapping ranges
    - Duplicate target values
    """
    return {
        "recoding_rules": [
            {
                "source_variable": "nonexistent_var",
                "target_variable": "target1",
                "transformation_type": "range_grouping",
                "rules": [
                    {"source_min": 30, "source_max": 20, "target_value": 1, "target_label": "Invalid range"},  # min > max
                    {"source_min": 25, "source_max": 35, "target_value": 1, "target_label": "Dup target"},  # Duplicate target
                ],
                "description": "Invalid rule example",
            },
        ]
    }


@pytest.fixture
def valid_indicators() -> Dict[str, Any]:
    """
    Valid indicators for testing.

    Includes:
    - Customer satisfaction indicator (3 variables)
    - Demographic indicator (2 variables)
    """
    return {
        "indicators": [
            {
                "indicator_name": "Customer_Satisfaction",
                "description": "Overall customer satisfaction score",
                "variables": ["satisfaction", "quality", "service"],
            },
            {
                "indicator_name": "Demographic_Profile",
                "description": "Key demographic variables",
                "variables": ["gender", "age_group"],
            },
        ]
    }


@pytest.fixture
def invalid_indicators() -> Dict[str, Any]:
    """
    Invalid indicators for testing error detection.

    Includes:
    - Duplicate indicator names
    - Too few variables
    - Nonexistent variables
    - Duplicate variables within indicator
    """
    return {
        "indicators": [
            {
                "indicator_name": "Duplicate_Name",
                "description": "First instance",
                "variables": ["satisfaction"],
            },
            {
                "indicator_name": "Duplicate_Name",  # Duplicate name
                "description": "Second instance",
                "variables": ["quality"],
            },
            {
                "indicator_name": "Invalid_Variables",
                "description": "References nonexistent variables",
                "variables": ["nonexistent1", "nonexistent2"],
            },
            {
                "indicator_name": "Duplicate_Vars",
                "description": "Has duplicate variables",
                "variables": ["gender", "gender", "age"],
            },
        ]
    }


@pytest.fixture
def valid_table_specs() -> Dict[str, Any]:
    """
    Valid table specifications for testing.

    Includes:
    - Gender x Satisfaction cross-tab
    - Age Group x Indicator cross-tab with weight
    """
    return {
        "tables": [
            {
                "table_id": "gender_x_satisfaction",
                "row_variable": "gender",
                "column_variable": "Customer_Satisfaction",
                "weight_variable": None,
                "statistics": ["count", "columnpct", "chisq", "cramersv"],
            },
            {
                "table_id": "age_x_satisfaction",
                "row_variable": "age_group",
                "column_variable": "Customer_Satisfaction",
                "weight_variable": "weight",
                "statistics": ["count", "columnpct"],
            },
        ]
    }


@pytest.fixture
def invalid_table_specs() -> Dict[str, Any]:
    """
    Invalid table specifications for testing error detection.

    Includes:
    - Duplicate table IDs
    - Nonexistent variables
    - Non-categorical variables
    - Invalid statistics
    """
    return {
        "tables": [
            {
                "table_id": "duplicate_table",
                "row_variable": "gender",
                "column_variable": "satisfaction",
                "weight_variable": None,
                "statistics": ["count", "columnpct"],
            },
            {
                "table_id": "duplicate_table",  # Duplicate ID
                "row_variable": "nonexistent_var",  # Nonexistent variable
                "column_variable": "Customer_Satisfaction",
                "weight_variable": "nonexistent_weight",  # Nonexistent weight
                "statistics": ["invalid_statistic"],  # Invalid statistic
            },
        ]
    }


@pytest.fixture
def new_metadata_format() -> Dict[str, Any]:
    """
    Metadata in the new_metadata format (from Step 8).

    Used for testing metadata normalization.
    """
    return {
        "variable_names": ["gender", "education", "satisfaction", "age_group"],
        "variable_labels": {
            "gender": "Gender",
            "education": "Education Level",
            "satisfaction": "Satisfaction",
            "age_group": "Age Group",
        },
        "value_labels": {
            "gender": {1: "Male", 2: "Female"},
            "education": {1: "Low", 2: "Medium", 3: "High"},
            "satisfaction": {1: "Low", 5: "High"},
            "age_group": {1: "18-24", 2: "25-34", 3: "35-44", 4: "45+"},
        },
    }


# =============================================================================
# Recoding Rules Validation Tests
# =============================================================================

class TestRecodingRulesValidation:
    """Test suite for recoding rules validation."""

    def test_valid_recoding_rules_pass(self, valid_recoding_rules, sample_variable_metadata, new_metadata_format):
        """Test that valid recoding rules pass validation."""
        result = validate_recoding_rules(valid_recoding_rules, sample_variable_metadata)

        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.checks_performed) > 0
        assert "structure_completeness" in result.checks_performed
        assert "source_variable_exists" in result.checks_performed

    def test_structure_completeness_missing_key(self, sample_variable_metadata, new_metadata_format):
        """Test that missing 'recoding_rules' key is detected."""
        invalid_rules = {}
        result = validate_recoding_rules(invalid_rules, sample_variable_metadata)

        assert not result.is_valid
        assert any("Missing required key 'recoding_rules'" in e for e in result.errors)

    def test_structure_completeness_not_list(self, new_metadata_format, sample_variable_metadata):
        """Test that non-list recoding_rules is detected."""
        invalid_rules = {"recoding_rules": "not_a_list"}
        result = validate_recoding_rules(invalid_rules, sample_variable_metadata)

        assert not result.is_valid
        assert any("'recoding_rules' must be a list" in e for e in result.errors)

    def test_structure_completeness_missing_required_fields(self, new_metadata_format, sample_variable_metadata):
        """Test that missing required fields in a rule are detected."""
        invalid_rules = {
            "recoding_rules": [
                {
                    "source_variable": "age",
                    # Missing target_variable
                    # Missing transformation_type
                    # Missing rules
                }
            ]
        }
        result = validate_recoding_rules(invalid_rules, sample_variable_metadata)

        assert not result.is_valid
        assert len(result.errors) >= 3  # At least 3 missing fields
        assert any("missing required field 'target_variable'" in e for e in result.errors)

    def test_structure_completeness_invalid_transformation_type(self, sample_variable_metadata):
        """Test that invalid transformation_type is detected."""
        invalid_rules = {
            "recoding_rules": [
                {
                    "source_variable": "age",
                    "target_variable": "age_group",
                    "transformation_type": "invalid_type",
                    "rules": [{"source_min": 18, "source_max": 24, "target_value": 1}],
                }
            ]
        }
        result = validate_recoding_rules(invalid_rules, sample_variable_metadata)

        assert not result.is_valid
        assert any("invalid transformation_type" in e.lower() for e in result.errors)

    def test_structure_completeness_empty_rules_array(self, sample_variable_metadata):
        """Test that empty rules array is detected."""
        invalid_rules = {
            "recoding_rules": [
                {
                    "source_variable": "age",
                    "target_variable": "age_group",
                    "transformation_type": "range_grouping",
                    "rules": [],
                }
            ]
        }
        result = validate_recoding_rules(invalid_rules, sample_variable_metadata)

        assert not result.is_valid
        assert any("empty 'rules' array" in e for e in result.errors)

    def test_source_variable_exists_missing(self, sample_variable_metadata):
        """Test that missing source variable is detected."""
        invalid_rules = {
            "recoding_rules": [
                {
                    "source_variable": "nonexistent_var",
                    "target_variable": "target1",
                    "transformation_type": "range_grouping",
                    "rules": [{"source_min": 1, "source_max": 10, "target_value": 1}],
                }
            ]
        }
        result = validate_recoding_rules(invalid_rules, sample_variable_metadata)

        assert not result.is_valid
        assert any("not found in metadata" in e for e in result.errors)

    def test_source_variable_exists_empty(self, sample_variable_metadata):
        """Test that empty source_variable is detected."""
        invalid_rules = {
            "recoding_rules": [
                {
                    "source_variable": "",
                    "target_variable": "target1",
                    "transformation_type": "range_grouping",
                    "rules": [{"source_min": 1, "source_max": 10, "target_value": 1}],
                }
            ]
        }
        result = validate_recoding_rules(invalid_rules, sample_variable_metadata)

        assert not result.is_valid
        assert any("empty or missing source_variable" in e for e in result.errors)

    def test_target_variable_uniqueness_duplicates(self, sample_variable_metadata):
        """Test that duplicate target variables are detected."""
        invalid_rules = {
            "recoding_rules": [
                {
                    "source_variable": "age",
                    "target_variable": "age_group",  # First use
                    "transformation_type": "range_grouping",
                    "rules": [{"source_min": 18, "source_max": 24, "target_value": 1}],
                },
                {
                    "source_variable": "income",
                    "target_variable": "age_group",  # Duplicate
                    "transformation_type": "range_grouping",
                    "rules": [{"source_min": 20000, "source_max": 50000, "target_value": 1}],
                },
            ]
        }
        result = validate_recoding_rules(invalid_rules, sample_variable_metadata)

        assert not result.is_valid
        assert any("Duplicate target variable" in e for e in result.errors)

    def test_target_variable_uniqueness_empty(self, sample_variable_metadata):
        """Test that empty target_variable is detected."""
        invalid_rules = {
            "recoding_rules": [
                {
                    "source_variable": "age",
                    "target_variable": "",
                    "transformation_type": "range_grouping",
                    "rules": [{"source_min": 18, "source_max": 24, "target_value": 1}],
                }
            ]
        }
        result = validate_recoding_rules(invalid_rules, sample_variable_metadata)

        assert not result.is_valid
        assert any("empty or missing target_variable" in e for e in result.errors)

    def test_transformation_type_match_range_on_non_numeric(self, sample_variable_metadata):
        """Test that range_grouping on non-numeric variable is detected."""
        metadata = {
            "gender": {
                "name": "gender",
                "variable_type": "string",  # Not numeric
                "value_labels": {1: "Male", 2: "Female"},
            }
        }
        invalid_rules = {
            "recoding_rules": [
                {
                    "source_variable": "gender",
                    "target_variable": "gender_group",
                    "transformation_type": "range_grouping",  # Requires numeric
                    "rules": [{"source_min": 1, "source_max": 2, "target_value": 1}],
                }
            ]
        }
        result = validate_recoding_rules(invalid_rules, metadata)

        assert not result.is_valid
        assert any("Invalid transformation type" in e for e in result.errors)

    def test_transformation_type_match_top_bottom_box_on_non_numeric(self):
        """Test that top_bottom_box on non-numeric variable is detected."""
        metadata = {
            "satisfaction": {
                "name": "satisfaction",
                "variable_type": "string",
                "value_labels": {},
            }
        }
        invalid_rules = {
            "recoding_rules": [
                {
                    "source_variable": "satisfaction",
                    "target_variable": "sat_top2box",
                    "transformation_type": "top_bottom_box",  # Requires numeric
                    "rules": [{"source_min": 4, "source_max": 5, "target_value": 1}],
                }
            ]
        }
        result = validate_recoding_rules(invalid_rules, metadata)

        assert not result.is_valid
        assert any("Invalid transformation type" in e for e in result.errors)

    def test_numeric_ranges_missing_source_min(self):
        """Test that missing source_min is detected."""
        rule_list = [
            {"source_max": 24, "target_value": 1, "target_label": "18-24"}
        ]
        errors = check_numeric_ranges(rule_list, "age")

        assert len(errors) > 0
        assert any("missing 'source_min'" in e for e in errors)

    def test_numeric_ranges_missing_source_max(self):
        """Test that missing source_max is detected."""
        rule_list = [
            {"source_min": 18, "target_value": 1, "target_label": "18-24"}
        ]
        errors = check_numeric_ranges(rule_list, "age")

        assert len(errors) > 0
        assert any("missing 'source_max'" in e for e in errors)

    def test_numeric_ranges_non_numeric_values(self):
        """Test that non-numeric range values are detected."""
        rule_list = [
            {"source_min": "not_a_number", "source_max": 24, "target_value": 1}
        ]
        errors = check_numeric_ranges(rule_list, "age")

        assert len(errors) > 0
        assert any("must be numeric" in e for e in errors)

    def test_numeric_ranges_min_greater_than_max(self):
        """Test that min > max is detected."""
        rule_list = [
            {"source_min": 30, "source_max": 20, "target_value": 1}
        ]
        errors = check_numeric_ranges(rule_list, "age")

        assert len(errors) > 0
        assert any("source_min must be <= source_max" in e for e in errors)

    def test_numeric_ranges_valid(self):
        """Test that valid ranges pass validation."""
        rule_list = [
            {"source_min": 18, "source_max": 24, "target_value": 1},
            {"source_min": 25, "source_max": 34, "target_value": 2},
        ]
        errors = check_numeric_ranges(rule_list, "age")

        assert len(errors) == 0

    def test_range_overlap_detected(self):
        """Test that overlapping ranges are detected."""
        rule_list = [
            {"source_min": 18, "source_max": 30, "target_value": 1},
            {"source_min": 25, "source_max": 35, "target_value": 2},  # Overlaps with first
        ]
        errors = check_range_overlap(rule_list, "age")

        assert len(errors) > 0
        assert any("Overlapping ranges" in e for e in errors)

    def test_range_adjacent_not_overlap(self):
        """Test that adjacent ranges (end == start) are not considered overlapping."""
        rule_list = [
            {"source_min": 18, "source_max": 24, "target_value": 1},
            {"source_min": 25, "source_max": 34, "target_value": 2},
        ]
        errors = check_range_overlap(rule_list, "age")

        assert len(errors) == 0

    def test_coverage_completeness_gap_detected(self):
        """Test that gaps in coverage are detected as warnings."""
        rule_list = [
            {"source_min": 18, "source_max": 24, "target_value": 1},
            {"source_min": 30, "source_max": 40, "target_value": 2},  # Gap: 25-29
        ]
        warnings = check_coverage_completeness(rule_list, "age", 18, 99)

        assert len(warnings) > 0
        assert any("Gap in coverage" in w for w in warnings)

    def test_coverage_completeness_start_gap(self):
        """Test that gap at start is detected."""
        rule_list = [
            {"source_min": 25, "source_max": 34, "target_value": 1},
        ]
        warnings = check_coverage_completeness(rule_list, "age", 18, 99)

        assert len(warnings) > 0
        assert any("starts at" in w and "but variable minimum is" in w for w in warnings)

    def test_coverage_completeness_end_gap(self):
        """Test that gap at end is detected."""
        rule_list = [
            {"source_min": 18, "source_max": 65, "target_value": 1},
        ]
        warnings = check_coverage_completeness(rule_list, "age", 18, 99)

        assert len(warnings) > 0
        assert any("ends at" in w and "but variable maximum is" in w for w in warnings)

    def test_target_uniqueness_within_rule_duplicates(self):
        """Test that duplicate target values within a rule are detected."""
        rule_list = [
            {"source_min": 18, "source_max": 24, "target_value": 1},
            {"source_min": 25, "source_max": 34, "target_value": 1},  # Duplicate target_value
        ]
        errors = _check_target_uniqueness_within_rule(rule_list, "age")

        assert len(errors) > 0
        assert any("Duplicate target value" in e for e in errors)

    def test_target_uniqueness_within_rule_unique(self):
        """Test that unique target values pass validation."""
        rule_list = [
            {"source_min": 18, "source_max": 24, "target_value": 1},
            {"source_min": 25, "source_max": 34, "target_value": 2},
        ]
        errors = _check_target_uniqueness_within_rule(rule_list, "age")

        assert len(errors) == 0

    def test_normalize_metadata_dict_format(self, sample_variable_metadata):
        """Test metadata normalization from dict format."""
        result = _normalize_metadata(sample_variable_metadata)

        assert isinstance(result, dict)
        assert "age" in result
        assert "gender" in result
        assert result["age"]["name"] == "age"

    def test_normalize_metadata_list_format(self, sample_variable_metadata):
        """Test metadata normalization from list format."""
        list_metadata = [
            {"name": "age", "variable_type": "numeric", "min_value": 18, "max_value": 99},
            {"name": "gender", "variable_type": "numeric", "min_value": 1, "max_value": 3},
        ]
        result = _normalize_metadata(list_metadata)

        assert isinstance(result, dict)
        assert "age" in result
        assert "gender" in result

    def test_normalize_metadata_empty_list(self):
        """Test metadata normalization with empty list."""
        result = _normalize_metadata([])

        assert result == {}

    def test_empty_recoding_rules_valid(self):
        """Test that empty recoding_rules list is valid."""
        empty_rules = {"recoding_rules": []}
        result = validate_recoding_rules(empty_rules, sample_variable_metadata)

        assert result.is_valid
        assert len(result.errors) == 0


# =============================================================================
# Indicators Validation Tests
# =============================================================================

class TestIndicatorsValidation:
    """Test suite for indicators validation."""

    def test_valid_indicators_pass(self, valid_indicators, new_metadata_format, sample_variable_metadata):
        """Test that valid indicators pass validation."""
        # Extend metadata to include all referenced variables
        metadata = {
            **new_metadata_format,
            "variable_names": [
                "gender", "education", "satisfaction", "quality",
                "service", "age_group"
            ],
        }
        result = validate_indicators(valid_indicators, metadata)

        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.checks_performed) > 0

    def test_structure_completeness_missing_key(self):
        """Test that missing 'indicators' key is detected."""
        invalid_indicators = {}
        result = validate_indicators(invalid_indicators, new_metadata_format)

        assert not result.is_valid
        assert any("Missing required key 'indicators'" in e for e in result.errors)

    def test_structure_completeness_not_list(self):
        """Test that non-list indicators is detected."""
        invalid_indicators = {"indicators": "not_a_list"}
        result = validate_indicators(invalid_indicators, new_metadata_format)

        assert not result.is_valid
        assert any("'indicators' must be a list" in e for e in result.errors)

    def test_structure_completeness_missing_required_fields(self):
        """Test that missing required fields are detected."""
        invalid_indicators = {
            "indicators": [
                {
                    "indicator_name": "Test_Indicator",
                    # Missing 'description'
                    # Missing 'variables'
                }
            ]
        }
        result = validate_indicators(invalid_indicators, new_metadata_format)

        assert not result.is_valid
        assert any("missing required field 'description'" in e for e in result.errors)
        assert any("missing required field 'variables'" in e for e in result.errors)

    def test_structure_completeness_variables_not_list(self, new_metadata_format):
        """Test that non-list variables field is detected."""
        invalid_indicators = {
            "indicators": [
                {
                    "indicator_name": "Test_Indicator",
                    "description": "Test",
                    "variables": "not_a_list",
                }
            ]
        }
        result = validate_indicators(invalid_indicators, new_metadata_format)

        assert not result.is_valid
        assert any("'variables' field must be a list" in e for e in result.errors)

    def test_variables_exist_missing(self, new_metadata_format):
        """Test that missing variables are detected."""
        metadata = {"variable_names": ["gender", "education"]}
        invalid_indicators = {
            "indicators": [
                {
                    "indicator_name": "Test_Indicator",
                    "description": "Test",
                    "variables": ["gender", "nonexistent_var"],
                }
            ]
        }
        result = validate_indicators(invalid_indicators, metadata)

        assert not result.is_valid
        assert any("not found in metadata" in e for e in result.errors)

    def test_variables_exist_non_string(self):
        """Test that non-string variables are detected."""
        metadata = {"variable_names": ["gender"]}
        invalid_indicators = {
            "indicators": [
                {
                    "indicator_name": "Test_Indicator",
                    "description": "Test",
                    "variables": ["gender", 123, None],  # Non-string values
                }
            ]
        }
        result = validate_indicators(invalid_indicators, metadata)

        assert not result.is_valid
        assert any("is not a string" in e for e in result.errors)

    def test_indicator_name_uniqueness_duplicates(self):
        """Test that duplicate indicator names are detected."""
        invalid_indicators = {
            "indicators": [
                {
                    "indicator_name": "Duplicate_Name",
                    "description": "First",
                    "variables": ["gender"],
                },
                {
                    "indicator_name": "Duplicate_Name",
                    "description": "Second",
                    "variables": ["education"],
                },
            ]
        }
        result = validate_indicators(invalid_indicators, {"variable_names": ["gender", "education"]})

        assert not result.is_valid
        assert any("Duplicate indicator name" in e for e in result.errors)

    def test_indicator_name_uniqueness_empty(self):
        """Test that empty indicator_name is detected."""
        invalid_indicators = {
            "indicators": [
                {
                    "indicator_name": "",
                    "description": "Test",
                    "variables": ["gender"],
                }
            ]
        }
        result = validate_indicators(invalid_indicators, {"variable_names": ["gender"]})

        assert not result.is_valid
        assert any("empty or missing indicator_name" in e for e in result.errors)

    def test_indicator_sizes_too_few_variables(self):
        """Test that indicators with < 2 variables are rejected."""
        invalid_indicators = {
            "indicators": [
                {
                    "indicator_name": "Single_Var",
                    "description": "Test",
                    "variables": ["gender"],  # Only 1 variable
                }
            ]
        }
        result = validate_indicators(invalid_indicators, {"variable_names": ["gender"]})

        assert not result.is_valid
        assert any("only 1 variable" in e or "minimum: 2" in e for e in result.errors)

    def test_indicator_sizes_too_many_variables_warning(self):
        """Test that indicators with > 10 variables generate a warning."""
        many_vars = [f"var{i}" for i in range(15)]
        indicators = {
            "indicators": [
                {
                    "indicator_name": "Many_Vars",
                    "description": "Test",
                    "variables": many_vars,
                }
            ]
        }
        metadata = {"variable_names": many_vars}
        result = validate_indicators(indicators, metadata)

        # Should be valid but with a warning
        assert result.is_valid
        assert len(result.warnings) > 0
        assert any("recommended max: 10" in w for w in result.warnings)

    def test_indicator_sizes_valid(self):
        """Test that indicators with 2-10 variables pass validation."""
        indicators = {
            "indicators": [
                {
                    "indicator_name": "Valid_Indicator",
                    "description": "Test",
                    "variables": ["gender", "education", "satisfaction"],  # 3 variables
                }
            ]
        }
        result = validate_indicators(indicators, {"variable_names": ["gender", "education", "satisfaction"]})

        assert result.is_valid
        assert len(result.errors) == 0

    def test_variable_uniqueness_within_indicator_duplicates(self):
        """Test that duplicate variables within indicator are detected."""
        invalid_indicators = {
            "indicators": [
                {
                    "indicator_name": "Duplicate_Vars",
                    "description": "Test",
                    "variables": ["gender", "gender", "education"],  # gender duplicated
                }
            ]
        }
        result = validate_indicators(invalid_indicators, {"variable_names": ["gender", "education"]})

        assert not result.is_valid
        assert any("Duplicate variable" in e for e in result.errors)

    def test_variable_uniqueness_within_indicator_unique(self):
        """Test that unique variables pass validation."""
        indicators = {
            "indicators": [
                {
                    "indicator_name": "Unique_Vars",
                    "description": "Test",
                    "variables": ["gender", "education", "satisfaction"],
                }
            ]
        }
        result = validate_indicators(indicators, {"variable_names": ["gender", "education", "satisfaction"]})

        assert result.is_valid
        assert len(result.errors) == 0

    def test_extract_variable_names_new_metadata_format(self, new_metadata_format):
        """Test variable name extraction from new_metadata format."""
        names = _extract_variable_names(new_metadata_format)

        assert "gender" in names
        assert "education" in names
        assert "satisfaction" in names

    def test_extract_variable_names_variable_centered_format(self, new_metadata_format):
        """Test variable name extraction from variable-centered format."""
        metadata = {
            "variables": {
                "gender": {"name": "gender", "variable_type": "numeric"},
                "age": {"name": "age", "variable_type": "numeric"},
            }
        }
        names = _extract_variable_names(metadata)

        assert "gender" in names
        assert "age" in names

    def test_extract_variable_names_list_format(self):
        """Test variable name extraction from list format."""
        metadata = [
            {"name": "gender", "variable_type": "numeric"},
            {"name": "age", "variable_type": "numeric"},
        ]
        names = _extract_variable_names(metadata)

        assert "gender" in names
        assert "age" in names

    def test_empty_indicators_valid(self):
        """Test that empty indicators list is valid."""
        empty_indicators = {"indicators": []}
        result = validate_indicators(empty_indicators, {"variable_names": []})

        assert result.is_valid
        assert len(result.errors) == 0


# =============================================================================
# Table Specifications Validation Tests
# =============================================================================

class TestTableSpecificationsValidation:
    """Test suite for table specifications validation."""

    def test_valid_table_specs_pass(self, valid_table_specs, new_metadata_format):
        """Test that valid table specs pass validation."""
        # Add weight variable and indicator to metadata
        metadata = {
            **new_metadata_format,
            "variable_names": [
                "gender", "education", "satisfaction", "age_group", "weight"
            ],
            "indicators": [
                {"name": "Customer_Satisfaction", "variables": ["satisfaction", "quality", "service"]}
            ],
        }
        result = validate_table_specs(valid_table_specs, metadata)

        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.checks_performed) > 0

    def test_structure_completeness_missing_key(self):
        """Test that missing 'tables' key is detected."""
        invalid_specs = {}
        result = validate_table_specs(invalid_specs, new_metadata_format)

        assert not result.is_valid
        assert any("Missing required key 'tables'" in e for e in result.errors)

    def test_structure_completeness_not_list(self):
        """Test that non-list tables is detected."""
        invalid_specs = {"tables": "not_a_list"}
        result = validate_table_specs(invalid_specs, new_metadata_format)

        assert not result.is_valid
        assert any("'tables' must be a list" in e for e in result.errors)

    def test_structure_completeness_missing_required_fields(self):
        """Test that missing required fields are detected."""
        invalid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    # Missing row_variable
                    # Missing column_variable
                    # Missing statistics
                }
            ]
        }
        result = validate_table_specs(invalid_specs, new_metadata_format)

        assert not result.is_valid
        assert any("missing required field 'row_variable'" in e for e in result.errors)
        assert any("missing required field 'column_variable'" in e for e in result.errors)
        assert any("missing required field 'statistics'" in e for e in result.errors)

    def test_structure_completeness_statistics_not_list(self, new_metadata_format):
        """Test that non-list statistics field is detected."""
        invalid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "gender",
                    "column_variable": "satisfaction",
                    "statistics": "not_a_list",
                }
            ]
        }
        result = validate_table_specs(invalid_specs, new_metadata_format)

        assert not result.is_valid
        assert any("'statistics' field must be a list" in e for e in result.errors)

    def test_structure_completeness_weight_variable_invalid_type(self, new_metadata_format):
        """Test that invalid weight_variable type is detected."""
        invalid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "gender",
                    "column_variable": "satisfaction",
                    "weight_variable": ["not_a_string"],  # Should be string or None
                    "statistics": ["count"],
                }
            ]
        }
        result = validate_table_specs(invalid_specs, new_metadata_format)

        assert not result.is_valid
        assert any("'weight_variable' must be null or a string" in e for e in result.errors)

    def test_row_variables_exist_missing(self, new_metadata_format):
        """Test that missing row variables are detected."""
        metadata = {"variable_names": ["gender"], "indicators": []}
        invalid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "nonexistent_var",
                    "column_variable": "gender",
                    "statistics": ["count"],
                }
            ]
        }
        result = validate_table_specs(invalid_specs, metadata)

        assert not result.is_valid
        assert any("not found in metadata" in e for e in result.errors)

    def test_row_variables_exist_empty(self):
        """Test that empty row_variable is detected."""
        invalid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "",
                    "column_variable": "gender",
                    "statistics": ["count"],
                }
            ]
        }
        result = validate_table_specs(invalid_specs, {"variable_names": ["gender"], "indicators": []})

        assert not result.is_valid
        assert any("empty or missing row_variable" in e for e in result.errors)

    def test_column_variables_exist_missing(self):
        """Test that missing column variables are detected."""
        metadata = {"variable_names": ["gender"], "indicators": []}
        invalid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "gender",
                    "column_variable": "nonexistent_var",
                    "statistics": ["count"],
                }
            ]
        }
        result = validate_table_specs(invalid_specs, metadata)

        assert not result.is_valid
        assert any("not found in metadata" in e or "not found in metadata or indicators" in e for e in result.errors)

    def test_column_variables_can_be_indicators(self, new_metadata_format):
        """Test that column variables can reference indicators."""
        metadata = {
            "variable_names": ["gender"],
            "value_labels": {"gender": {1: "Male", 2: "Female"}},
            "indicators": [
                {"name": "Customer_Satisfaction", "variables": ["sat1", "sat2"]}
            ]
        }
        valid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "gender",
                    "column_variable": "Customer_Satisfaction",  # Indicator
                    "statistics": ["count"],
                }
            ]
        }
        result = validate_table_specs(valid_specs, metadata)

        assert result.is_valid

    def test_variables_are_categorical_continuous_rejected(self):
        """Test that continuous (non-categorical) variables are rejected."""
        metadata = {
            "variable_names": ["income"],
            "variable_types": {"income": "numeric"},
            "indicators": [],
        }
        invalid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "income",  # Continuous, no value labels
                    "column_variable": "gender",
                    "statistics": ["count"],
                }
            ]
        }
        result = validate_table_specs(invalid_specs, metadata)

        assert not result.is_valid
        assert any("not categorical" in e for e in result.errors)

    def test_variables_are_categorical_recoded_accepted(self, new_metadata_format):
        """Test that recoded variables are treated as categorical."""
        metadata = {
            "variable_names": ["age_group", "gender"],
            "value_labels": {
                "gender": {1: "Male", 2: "Female"},
            },
            "indicators": [],
        }
        valid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "age_group",  # Has "_group" suffix
                    "column_variable": "gender",
                    "statistics": ["count"],
                }
            ]
        }
        result = validate_table_specs(valid_specs, metadata)

        assert result.is_valid

    def test_indicators_always_categorical(self):
        """Test that indicators are always considered categorical."""
        metadata = {
            "variable_names": [],
            "variable_types": {},
            "indicators": [
                {"name": "Composite_Score", "variables": ["var1", "var2"]}
            ],
        }
        valid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "Composite_Score",  # Indicator
                    "column_variable": "Another_Indicator",
                    "statistics": ["count"],
                }
            ]
        }
        result = validate_table_specs(valid_specs, metadata)

        # Should not have categorical error for indicators
        assert not any("not categorical" in e for e in result.errors)

    def test_statistics_are_valid_invalid_statistic(self):
        """Test that invalid statistics are detected."""
        invalid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "gender",
                    "column_variable": "education",
                    "statistics": ["count", "invalid_stat", "another_invalid"],
                }
            ]
        }
        result = validate_table_specs(invalid_specs, new_metadata_format)

        assert not result.is_valid
        assert any("Invalid statistic" in e for e in result.errors)

    def test_statistics_are_valid_all_valid(self, new_metadata_format):
        """Test that all valid statistics pass validation."""
        valid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "gender",
                    "column_variable": "education",
                    "statistics": ["count", "columnpct", "chisq", "cramersv"],
                }
            ]
        }
        result = validate_table_specs(valid_specs, new_metadata_format)

        assert result.is_valid or not any("Invalid statistic" in e for e in result.errors)

    def test_table_id_uniqueness_duplicates(self, new_metadata_format):
        """Test that duplicate table IDs are detected."""
        invalid_specs = {
            "tables": [
                {
                    "table_id": "duplicate_id",
                    "row_variable": "gender",
                    "column_variable": "education",
                    "statistics": ["count"],
                },
                {
                    "table_id": "duplicate_id",  # Duplicate
                    "row_variable": "age_group",
                    "column_variable": "satisfaction",
                    "statistics": ["count"],
                },
            ]
        }
        result = validate_table_specs(invalid_specs, new_metadata_format)

        assert not result.is_valid
        assert any("Duplicate table_id" in e for e in result.errors)

    def test_table_id_uniqueness_empty(self, new_metadata_format):
        """Test that empty table_id is detected."""
        invalid_specs = {
            "tables": [
                {
                    "table_id": "",
                    "row_variable": "gender",
                    "column_variable": "education",
                    "statistics": ["count"],
                }
            ]
        }
        result = validate_table_specs(invalid_specs, new_metadata_format)

        assert not result.is_valid
        assert any("empty or missing table_id" in e for e in result.errors)

    def test_weight_variables_missing_detected(self, new_metadata_format):
        """Test that missing weight variables are detected."""
        invalid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "gender",
                    "column_variable": "education",
                    "weight_variable": "nonexistent_weight",
                    "statistics": ["count"],
                }
            ]
        }
        result = validate_table_specs(invalid_specs, new_metadata_format)

        assert not result.is_valid
        assert any("not found" in e and "Weight variable" in e for e in result.errors)

    def test_weight_variables_valid(self, new_metadata_format):
        """Test that valid weight variables pass validation."""
        metadata = {
            "variable_names": ["gender", "education", "weight_var"],
            "value_labels": {
                "gender": {1: "Male", 2: "Female"},
                "education": {1: "Low", 2: "High"},
            },
            "indicators": [],
        }
        valid_specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "gender",
                    "column_variable": "education",
                    "weight_variable": "weight_var",
                    "statistics": ["count"],
                }
            ]
        }
        result = validate_table_specs(valid_specs, metadata)

        # Should be valid but have a warning about weight bias
        assert len([e for e in result.errors if "not found" in e]) == 0
        # Should have warning about weight bias
        assert len(result.warnings) > 0

    def test_normalize_tables_metadata_new_format(self, new_metadata_format):
        """Test metadata normalization from new_metadata format."""
        var_names, var_types, indicators = _normalize_tables_metadata(new_metadata_format)

        assert "gender" in var_names
        assert "education" in var_names
        assert isinstance(var_types, dict)

    def test_normalize_tables_metadata_with_indicators(self, new_metadata_format):
        """Test metadata normalization with indicators."""
        metadata = {
            "indicators": [
                {"name": "Indicator1", "variables": ["var1", "var2"]},
                {"indicator_name": "Indicator2", "variables": ["var3", "var4"]},
            ]
        }
        var_names, var_types, indicators = _normalize_tables_metadata(metadata)

        assert "Indicator1" in indicators
        assert "Indicator2" in indicators

    def test_normalize_tables_metadata_variable_centered(self):
        """Test metadata normalization from variable-centered format."""
        metadata = {
            "variables": {
                "gender": {"name": "gender", "variable_type": "string"},
                "age": {"name": "age", "variable_type": "numeric"},
            }
        }
        var_names, var_types, indicators = _normalize_tables_metadata(metadata)

        assert "gender" in var_names
        assert "age" in var_names
        assert var_types["gender"] == "string"
        assert var_types["age"] == "numeric"

    def test_empty_tables_valid_with_warning(self):
        """Test that empty tables list is valid but generates warning."""
        empty_specs = {"tables": []}
        result = validate_table_specs(empty_specs, new_metadata_format)

        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) > 0
        assert any("No table specifications" in w for w in result.warnings)


# =============================================================================
# ValidationResult Tests
# =============================================================================

class TestValidationResult:
    """Test suite for ValidationResult dataclass behavior."""

    def test_validation_result_creation(self, new_metadata_format):
        """Test ValidationResult creation with all fields."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Minor warning"],
            checks_performed=["check1", "check2"]
        )

        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 1
        assert len(result.checks_performed) == 2

    def test_validation_result_is_valid_true_with_no_errors(self):
        """Test that is_valid is True when there are no errors."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Warning 1", "Warning 2"],
            checks_performed=[]
        )

        assert result.is_valid

    def test_validation_result_is_valid_false_with_errors(self):
        """Test that is_valid is False when there are errors."""
        result = ValidationResult(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning"],
            checks_performed=[]
        )

        assert not result.is_valid

    def test_validation_result_errors_vs_warnings_distinction(self):
        """Test that errors and warnings are tracked separately."""
        result = ValidationResult(
            is_valid=False,
            errors=["Critical error message"],
            warnings=["Informational warning message"],
            checks_performed=[]
        )

        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert "error" in result.errors[0].lower()
        assert "warning" in result.warnings[0].lower()

    def test_validation_result_checks_performed_tracking(self):
        """Test that checks_performed tracks all validation checks."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            checks_performed=["structure_check", "reference_check", "business_rule_check"]
        )

        assert len(result.checks_performed) == 3
        assert "structure_check" in result.checks_performed


# =============================================================================
# Edge Cases and Error Scenarios
# =============================================================================

class TestValidationEdgeCases:
    """Test suite for edge cases and error scenarios."""

    # Recoding Rules Edge Cases

    def test_recoding_null_input(self):
        """Test recoding validation with None input."""
        result = validate_recoding_rules(None, {})

        assert not result.is_valid

    def test_recoding_malformed_json_string(self):
        """Test recoding validation with malformed JSON string as input."""
        # Input should be dict, not string
        result = validate_recoding_rules("not a dict", {})

        assert not result.is_valid

    def test_recoding_unicode_in_descriptions(self):
        """Test recoding validation with Unicode characters in descriptions."""
        unicode_rules = {
            "recoding_rules": [
                {
                    "source_variable": "age",
                    "target_variable": "age_group",
                    "transformation_type": "range_grouping",
                    "rules": [
                        {"source_min": 18, "source_max": 24, "target_value": 1, "target_label": "日本語"},
                        {"source_min": 25, "source_max": 34, "target_value": 2, "target_label": "العربية"},
                    ],
                    "description": "Test with émojis 🎉 and spëcial çharacters",
                }
            ]
        }
        result = validate_recoding_rules(unicode_rules, sample_variable_metadata)

        # Should pass structure validation (Unicode is allowed)
        assert len([e for e in result.errors if "structure" in e.lower()]) == 0

    def test_recoding_zero_ranges(self, sample_variable_metadata):
        """Test recoding validation with zero-width ranges (min == max)."""
        rules = {
            "recoding_rules": [
                {
                    "source_variable": "age",
                    "target_variable": "age_exact",
                    "transformation_type": "range_grouping",
                    "rules": [
                        {"source_min": 25, "source_max": 25, "target_value": 1, "target_label": "Exactly 25"},
                    ],
                    "description": "Single value ranges",
                }
            ]
        }
        result = validate_recoding_rules(rules, sample_variable_metadata)

        # Zero-width ranges are valid (min == max)
        assert not any("source_min must be <=" in e for e in result.errors)

    def test_recoding_negative_ranges(self, sample_variable_metadata):
        """Test recoding validation with negative values."""
        metadata = {
            "temperature": {
                "name": "temperature",
                "variable_type": "numeric",
                "min_value": -50,
                "max_value": 50,
                "value_labels": {},
            }
        }
        rules = {
            "recoding_rules": [
                {
                    "source_variable": "temperature",
                    "target_variable": "temp_group",
                    "transformation_type": "range_grouping",
                    "rules": [
                        {"source_min": -50, "source_max": -10, "target_value": 1, "target_label": "Freezing"},
                        {"source_min": -9, "source_max": 10, "target_value": 2, "target_label": "Cold"},
                        {"source_min": 11, "source_max": 50, "target_value": 3, "target_label": "Warm"},
                    ],
                    "description": "Temperature ranges",
                }
            ]
        }
        result = validate_recoding_rules(rules, metadata)

        # Negative ranges should be valid
        assert len([e for e in result.errors if "range" in e.lower()]) == 0

    # Indicators Edge Cases

    def test_indicators_null_input(self):
        """Test indicators validation with None input."""
        result = validate_indicators(None, {})

        assert not result.is_valid

    def test_indicators_empty_variables_list(self):
        """Test indicators validation with empty variables list."""
        invalid_indicators = {
            "indicators": [
                {
                    "indicator_name": "Empty_Indicator",
                    "description": "Test",
                    "variables": [],  # Empty list
                }
            ]
        }
        result = validate_indicators(invalid_indicators, {"variable_names": []})

        assert not result.is_valid
        assert any("minimum: 2" in e or "0 variable" in e for e in result.errors)

    def test_indicators_very_long_name(self):
        """Test indicators validation with very long name."""
        long_name = "A" * 1000
        indicators = {
            "indicators": [
                {
                    "indicator_name": long_name,
                    "description": "Test",
                    "variables": ["gender", "education"],
                }
            ]
        }
        result = validate_indicators(indicators, {"variable_names": ["gender", "education"]})

        # Long names should be valid (no length restriction)
        assert result.is_valid

    # Table Specs Edge Cases

    def test_tables_null_input(self):
        """Test tables validation with None input."""
        result = validate_table_specs(None, {})

        assert not result.is_valid

    def test_tables_same_row_and_column_variable(self):
        """Test tables validation with same variable for row and column."""
        specs = {
            "tables": [
                {
                    "table_id": "same_var_table",
                    "row_variable": "gender",
                    "column_variable": "gender",  # Same as row
                    "statistics": ["count"],
                }
            ]
        }
        result = validate_table_specs(specs, {"variable_names": ["gender"], "indicators": []})

        # Same variable for row and column is structurally valid
        # (Business logic may reject it later)
        assert len(result.errors) == 0 or not any("same" in e.lower() for e in result.errors)

    def test_tables_empty_statistics_list(self):
        """Test tables validation with empty statistics list."""
        specs = {
            "tables": [
                {
                    "table_id": "no_stats_table",
                    "row_variable": "gender",
                    "column_variable": "education",
                    "statistics": [],  # Empty
                }
            ]
        }
        result = validate_table_specs(specs, new_metadata_format)

        # Empty statistics is structurally valid (no statistics requested)
        # May be a warning or business rule issue
        assert len([e for e in result.errors if "statistic" in e.lower()]) == 0

    # Metadata Normalization Edge Cases

    def test_normalize_metadata_empty_dict(self, new_metadata_format):
        """Test metadata normalization with empty dict."""
        result = _normalize_metadata({})

        assert result == {}

    def test_normalize_metadata_none_input(self):
        """Test metadata normalization with None input."""
        result = _normalize_metadata(None)

        assert result == {}

    def test_extract_variable_names_empty_metadata(self):
        """Test variable name extraction from empty metadata."""
        names = _extract_variable_names({})

        assert names == []

    def test_normalize_tables_metadata_empty(self):
        """Test tables metadata normalization with empty input."""
        var_names, var_types, indicators = _normalize_tables_metadata({})

        assert var_names == set()
        assert var_types == {}
        assert indicators == set()

    # Special Characters and Formatting

    def test_validation_with_special_characters_in_names(self):
        """Test validation with special characters in variable names."""
        metadata = {
            "variable_names": ["q1_yes/no", "q2_score-1", "q3_yes/no"],
        }
        indicators = {
            "indicators": [
                {
                    "indicator_name": "Indicator_With-Special/Chars",
                    "description": "Test",
                    "variables": ["q1_yes/no", "q2_score-1"],
                }
            ]
        }
        result = validate_indicators(indicators, metadata)

        # Special characters in names are allowed
        assert result.is_valid or not any("invalid" in e.lower() for e in result.errors)

    def test_validation_with_leading_trailing_whitespace(self):
        """Test validation with leading/trailing whitespace in values."""
        # Whitespace might be trimmed or preserved depending on implementation
        # This test documents current behavior
        rules = {
            "recoding_rules": [
                {
                    "source_variable": "  age  ",  # Leading/trailing spaces
                    "target_variable": "age_group",
                    "transformation_type": "range_grouping",
                    "rules": [{"source_min": 18, "source_max": 24, "target_value": 1}],
                    "description": "Test",
                }
            ]
        }
        result = validate_recoding_rules(rules, sample_variable_metadata)

        # Behavior may vary - test documents what happens
        # If "  age  " doesn't match "age" in metadata, will fail
        # This is expected behavior


# =============================================================================
# Parametrized Tests
# =============================================================================

class TestValidationParametrized:
    """Parametrized tests for validation functions."""

    @pytest.mark.parametrize("invalid_type", [
        "not_a_dict",
        ["list", "not", "dict"],
        123,
        None,
        True,
    ])
    def test_recoding_invalid_input_types(self, invalid_type):
        """Test recoding validation with various invalid input types."""
        result = validate_recoding_rules(invalid_type, {})

        assert not result.is_valid

    @pytest.mark.parametrize("invalid_type", [
        "not_a_dict",
        ["list", "not", "dict"],
        123,
        None,
    ])
    def test_indicators_invalid_input_types(self, invalid_type):
        """Test indicators validation with various invalid input types."""
        result = validate_indicators(invalid_type, {})

        assert not result.is_valid

    @pytest.mark.parametrize("invalid_type", [
        "not_a_dict",
        ["list", "not", "dict"],
        123,
        None,
    ])
    def test_tables_invalid_input_types(self, invalid_type):
        """Test tables validation with various invalid input types."""
        result = validate_table_specs(invalid_type, {})

        assert not result.is_valid

    @pytest.mark.parametrize("transformation_type,variable_type,should_pass", [
        ("range_grouping", "numeric", True),
        ("range_grouping", "string", False),
        ("top_bottom_box", "numeric", True),
        ("top_bottom_box", "string", False),
        ("category_consolidation", "numeric", True),
        ("category_consolidation", "string", True),
        ("derived", "numeric", True),
        ("derived", "string", True),
    ])
    def test_transformation_type_matching(
        self, transformation_type, variable_type, should_pass
    ):
        """Test that transformation types match variable types appropriately."""
        metadata = {
            "test_var": {
                "name": "test_var",
                "variable_type": variable_type,
                "value_labels": {} if variable_type == "numeric" else {},
            }
        }
        rules = {
            "recoding_rules": [
                {
                    "source_variable": "test_var",
                    "target_variable": "test_target",
                    "transformation_type": transformation_type,
                    "rules": [{"source_min": 1, "source_max": 10, "target_value": 1}],
                }
            ]
        }
        result = validate_recoding_rules(rules, metadata)

        if should_pass:
            # Should not have type mismatch error
            assert not any("Invalid transformation type" in e for e in result.errors)
        else:
            # Should have type mismatch error
            assert any("Invalid transformation type" in e for e in result.errors)

    @pytest.mark.parametrize("statistic", [
        "count",
        "columnpct",
        "chisq",
        "cramersv",
    ])
    def test_valid_statistics(self, statistic):
        """Test that all valid statistics are accepted."""
        specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "gender",
                    "column_variable": "education",
                    "statistics": [statistic],
                }
            ]
        }
        result = validate_table_specs(specs, new_metadata_format)

        # Should not have invalid statistic error
        assert not any("Invalid statistic" in e for e in result.errors)

    @pytest.mark.parametrize("invalid_statistic", [
        "invalid",
        "COUNT",  # Case sensitive
        "row_percent",  # Not in allowed list
        "mean",  # Not applicable for crosstabs
        "stddev",  # Not applicable for crosstabs
    ])
    def test_invalid_statistics(self, invalid_statistic, new_metadata_format):
        """Test that invalid statistics are rejected."""
        specs = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "gender",
                    "column_variable": "education",
                    "statistics": [invalid_statistic],
                }
            ]
        }
        result = validate_table_specs(specs, new_metadata_format)

        # Should have invalid statistic error
        assert any("Invalid statistic" in e for e in result.errors)
