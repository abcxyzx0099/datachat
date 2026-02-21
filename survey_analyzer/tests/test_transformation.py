"""
Tests for survey_analyzer.analysis.transformation module.

Tests variable transformation and recoding functionality.
"""

import pytest
import pandas as pd
import numpy as np

from survey_analyzer.analysis.transformation import (
    TransformationEngine,
    TransformationRule,
    parse_transformation_rules,
    apply_recode
)


# ============================================================================
# TransformationRule Tests
# ============================================================================

class TestTransformationRule:
    """Test TransformationRule dataclass."""

    def test_rule_creation_with_rules(self):
        """Test creating a rule with recoding rules."""
        rule = TransformationRule(
            source="q1",
            target="q1_recoded",
            rules="(1=10) (2=20)"
        )
        assert rule.source == "q1"
        assert rule.target == "q1_recoded"
        assert rule.rules == "(1=10) (2=20)"

    def test_rule_creation_with_mapping(self):
        """Test creating a rule with explicit mapping."""
        rule = TransformationRule(
            source="q1",
            target="q1_mapped",
            mapping={1: "Yes", 2: "No"}
        )
        assert rule.source == "q1"
        assert rule.mapping == {1: "Yes", 2: "No"}

    def test_rule_creation_with_compute(self):
        """Test creating a rule with compute expression."""
        rule = TransformationRule(
            source="var1",
            target="var_sum",
            compute="var1 + var2"
        )
        assert rule.compute == "var1 + var2"

    def test_has_rules_method(self):
        """Test has_rules() method."""
        rule_with_rules = TransformationRule(
            source="q1",
            target="q1_r",
            rules="(1=10)"
        )
        assert rule_with_rules.has_rules() is True

        rule_without_rules = TransformationRule(
            source="q1",
            target="q1_copy"
        )
        assert rule_without_rules.has_rules() is False


# ============================================================================
# TransformationEngine Tests
# ============================================================================

class TestTransformationEngine:
    """Test TransformationEngine class."""

    def test_default_initialization(self):
        """Test default initialization."""
        engine = TransformationEngine()
        assert engine.copy is True

    def test_no_copy_initialization(self):
        """Test initialization without copying."""
        engine = TransformationEngine(copy=False)
        assert engine.copy is False

    def test_apply_recode_single_value(self):
        """Test recoding single values."""
        engine = TransformationEngine()
        series = pd.Series([1, 2, 3, 1, 2, 3])
        rules = "(1=10) (2=20)"
        result = engine._apply_recode(series, rules)

        assert result.iloc[0] == 10
        assert result.iloc[1] == 20
        assert result.iloc[2] == 3  # Not in rules, stays same

    def test_apply_recode_with_thru(self):
        """Test recoding with THRU range."""
        engine = TransformationEngine()
        series = pd.Series([1, 2, 3, 4, 5])
        rules = "(1 THRU 3=99)"
        result = engine._apply_recode(series, rules)

        assert result.iloc[0] == 99
        assert result.iloc[1] == 99
        assert result.iloc[2] == 99
        assert result.iloc[3] == 4
        assert result.iloc[4] == 5

    def test_apply_recode_missing_values_preserved(self):
        """Test that NaN values are preserved."""
        engine = TransformationEngine()
        series = pd.Series([1, 2, np.nan, 4])
        rules = "(1=10) (2=20)"
        result = engine._apply_recode(series, rules)

        assert result.iloc[0] == 10
        assert result.iloc[1] == 20
        assert pd.isna(result.iloc[2])
        assert result.iloc[3] == 4

    def test_apply_compute_sum(self):
        """Test COMPUTE with SUM."""
        engine = TransformationEngine()
        df = pd.DataFrame({"q1": [1, 2, 3], "q2": [4, 5, 6]})
        rules = "q1 + q2"
        result = engine._apply_compute(df, rules, "sum_var")

        assert list(result) == [5, 7, 9]

    def test_apply_compute_mean(self):
        """Test COMPUTE with MEAN."""
        engine = TransformationEngine()
        df = pd.DataFrame({"q1": [1.0, 2.0, 3.0], "q2": [4.0, 5.0, 6.0]})
        # Simple mean calculation
        rules = "(q1 + q2) / 2"
        result = engine._apply_compute(df, rules, "mean_var")

        assert list(result) == [2.5, 3.5, 4.5]

    def test_apply_transformations_single_indicator(self):
        """Test apply_transformations with single indicator."""
        engine = TransformationEngine()
        df = pd.DataFrame({"age": [25, 35, 55, 65]})

        indicators = [
            {
                "indicator_code": "age_group",
                "base_variables": [
                    {
                        "name": "age_group",
                        "generation": "RECODE age (25 THRU 35=1) (36 THRU 55=2) (56 THRU 65=3) INTO age_group"
                    }
                ]
            }
        ]

        result = engine.apply_transformations(df, indicators)

        assert "age_group" in result.columns
        assert result.iloc[0]["age_group"] == 1
        assert result.iloc[1]["age_group"] == 1
        assert result.iloc[2]["age_group"] == 2
        assert result.iloc[3]["age_group"] == 3

    def test_apply_transformations_raw_variable(self):
        """Test that raw variables (no transformation) are handled."""
        engine = TransformationEngine()
        df = pd.DataFrame({"gender": ["Male", "Female", "Male"]})

        indicators = [
            {
                "indicator_code": "gender_raw",
                "base_variables": [
                    {
                        "name": "gender_raw",
                        "generation": None  # Raw variable
                    }
                ]
            }
        ]

        result = engine.apply_transformations(df, indicators)

        # Raw variable with no generation should not create new column
        # The source variable should remain unchanged
        assert list(result["gender"]) == ["Male", "Female", "Male"]

    def test_apply_transformations_null_generation(self):
        """Test with 'null' string as generation."""
        engine = TransformationEngine()
        df = pd.DataFrame({"q1": [1, 2, 3]})

        indicators = [
            {
                "indicator_code": "q1_raw",
                "base_variables": [
                    {
                        "name": "q1_raw",
                        "generation": "null"  # String 'null' means no transformation
                    }
                ]
            }
        ]

        result = engine.apply_transformations(df, indicators)

        # null generation should not create new variable
        assert "q1_raw" not in result.columns

    def test_apply_transformations_copy_false(self):
        """Test with copy=False modifies original DataFrame."""
        engine = TransformationEngine(copy=False)
        df = pd.DataFrame({"age": [25, 35, 55]})
        original_id = id(df)

        indicators = [
            {
                "indicator_code": "age_recoded",
                "base_variables": [
                    {
                        "name": "age_recoded",
                        "generation": "RECODE age (25 THRU 35=1) (36 THRU 55=2) INTO age_recoded"
                    }
                ]
            }
        ]

        result = engine.apply_transformations(df, indicators)

        # Should be same object
        assert id(result) == original_id

    def test_apply_transformations_copy_true(self):
        """Test with copy=True creates new DataFrame."""
        engine = TransformationEngine(copy=True)
        df = pd.DataFrame({"age": [25, 35, 55]})
        original_id = id(df)

        indicators = [
            {
                "indicator_code": "age_recoded",
                "base_variables": [
                    {
                        "name": "age_recoded",
                        "generation": "RECODE age (25 THRU 35=1) (36 THRU 55=2) INTO age_recoded"
                    }
                ]
            }
        ]

        result = engine.apply_transformations(df, indicators)

        # Should be different object
        assert id(result) != original_id

    def test_apply_recode_method(self):
        """Test apply_recode convenience method."""
        engine = TransformationEngine()
        df = pd.DataFrame({"source": [1, 2, 3]})

        result = engine.apply_recode(df, "source", "target", "(1=10) (2=20)")

        # apply_recode returns a Series
        assert isinstance(result, pd.Series)
        assert result.iloc[0] == 10
        assert result.iloc[1] == 20

    def test_parse_value_as_int(self):
        """Test parsing numeric string value."""
        engine = TransformationEngine()
        assert engine._parse_value("123") == 123
        assert engine._parse_value("12.5") == 12.5
        assert engine._parse_value("hello") == "hello"

    def test_parse_rules_with_multiple_mappings(self):
        """Test parsing complex recode rules."""
        engine = TransformationEngine()
        rules = "(1=100) (2 THRU 4=200) (5=300)"
        mapping = engine._parse_rules(rules)

        assert mapping[1] == 100
        assert mapping[2] == 200
        assert mapping[3] == 200
        assert mapping[4] == 200
        assert mapping[5] == 300


# ============================================================================
# Convenience Functions Tests
# ============================================================================

class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_parse_transformation_rules_function(self):
        """Test parse_transformation_rules standalone function."""
        rules = "(1=2) (3 THRU 5=99)"
        mapping = parse_transformation_rules(rules)

        assert mapping[1] == 2
        assert mapping[3] == 99
        assert mapping[4] == 99
        assert mapping[5] == 99

    def test_apply_recode_function(self):
        """Test apply_recode standalone function."""
        series = pd.Series([1, 2, 3, 4, 5])
        rules = "(1 THRU 2=1) (3 THRU 5=2)"
        result = apply_recode(series, rules)

        assert result.iloc[0] == 1
        assert result.iloc[1] == 1
        assert result.iloc[2] == 2
        assert result.iloc[3] == 2
        assert result.iloc[4] == 2


# ============================================================================
# Module Tests
# ============================================================================

class TestTransformationModule:
    """Test transformation module imports."""

    def test_import_transformation_engine(self):
        """Test TransformationEngine can be imported."""
        from survey_analyzer.analysis.transformation import TransformationEngine
        assert TransformationEngine is not None

    def test_import_transformation_rule(self):
        """Test TransformationRule can be imported."""
        from survey_analyzer.analysis.transformation import TransformationRule
        assert TransformationRule is not None

    def test_import_convenience_functions(self):
        """Test convenience functions can be imported."""
        from survey_analyzer.analysis.transformation import (
            apply_recode,
            parse_transformation_rules
        )
        assert callable(apply_recode)
        assert callable(parse_transformation_rules)
