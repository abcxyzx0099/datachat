"""
Test Crosstab Scenarios

Tests for all 4 crosstab scenarios:
1. Single Categorical × Single Categorical
2. Multiple Binary (Multiple Choice) × Single Categorical
3. Single Scalar × Single Categorical
4. Multiple Scalar (Rating Scale) × Single Categorical
"""

import pytest
import pandas as pd
import numpy as np
from survey_analyzer.analysis import (
    CrosstabProcessor,
    ScenarioDetector,
    IndicatorSpec
)


class TestScenarioDetector:
    """Test scenario detection logic."""

    def test_cat_single_detection(self):
        """Detect single categorical variable."""
        indicator = IndicatorSpec(
            indicator_code="Q1_GENDER",
            statistic_type="categorical",
            source_variables=["Q1_GENDER"],
            question_type="Single Choice",
            transformation_rules=None
        )
        scenario = ScenarioDetector.detect(indicator)
        assert scenario == ScenarioDetector.CAT_SINGLE

    def test_cat_multi_detection(self):
        """Detect multiple binary variables (Multiple Choice)."""
        indicator = IndicatorSpec(
            indicator_code="S1_BRAND_AWARENESS",
            statistic_type="categorical",
            source_variables=["S1_BRAND_A", "S1_BRAND_B", "S1_BRAND_C"],
            question_type="Multiple Choice",
            transformation_rules=None
        )
        scenario = ScenarioDetector.detect(indicator)
        assert scenario == ScenarioDetector.CAT_MULTI

    def test_scalar_single_detection(self):
        """Detect single scalar variable."""
        indicator = IndicatorSpec(
            indicator_code="SAT_OVERALL",
            statistic_type="scalar",
            source_variables=["SAT_OVERALL"],
            question_type="Numeric Input",
            transformation_rules=None
        )
        scenario = ScenarioDetector.detect(indicator)
        assert scenario == ScenarioDetector.SCALAR_SINGLE

    def test_scalar_multi_detection(self):
        """Detect multiple scalar variables (Rating Scale)."""
        indicator = IndicatorSpec(
            indicator_code="D1_RATINGS",
            statistic_type="scalar",
            source_variables=["D1_QUALITY", "D1_PRICE", "D1_SERVICE"],
            question_type="Rating Scale",
            transformation_rules=None
        )
        scenario = ScenarioDetector.detect(indicator)
        assert scenario == ScenarioDetector.SCALAR_MULTI


class TestCrosstabProcessor:
    """Test crosstab processor for all scenarios."""

    @pytest.fixture
    def sample_data(self):
        """Create sample survey data."""
        np.random.seed(42)
        n = 350

        data = {
            # Demographics (column indicator)
            "Q1_GENDER": np.random.choice(["Male", "Female"], size=n, p=[0.51, 0.49]),

            # Single categorical (row indicator)
            "Q2_SATISFACTION": np.random.choice(
                ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied"],
                size=n,
                p=[0.35, 0.44, 0.17, 0.04]
            ),

            # Multiple binary variables (Multiple Choice)
            "S1_BRAND_A": np.random.choice([0, 1], size=n, p=[0.35, 0.65]),
            "S1_BRAND_B": np.random.choice([0, 1], size=n, p=[0.40, 0.60]),
            "S1_BRAND_C": np.random.choice([0, 1], size=n, p=[0.30, 0.70]),
            "S1_BRAND_D": np.random.choice([0, 1], size=n, p=[0.50, 0.50]),

            # Single scalar
            "SAT_OVERALL": np.random.normal(7.5, 1.8, size=n).clip(0, 10),

            # Multiple scalar (Rating Scale)
            "D1_QUALITY": np.random.normal(7.4, 1.5, size=n).clip(1, 10),
            "D1_PRICE": np.random.normal(7.0, 1.6, size=n).clip(1, 10),
            "D1_SERVICE": np.random.normal(7.3, 1.4, size=n).clip(1, 10),
            "D1_SELECTION": np.random.normal(7.1, 1.5, size=n).clip(1, 10),
            "D1_VALUE": np.random.normal(7.2, 1.5, size=n).clip(1, 10),
        }

        return pd.DataFrame(data)

    @pytest.fixture
    def processor(self):
        """Create crosstab processor instance."""
        return CrosstabProcessor()

    def test_scenario_1_cat_single(self, processor, sample_data):
        """Test Scenario 1: Single Categorical × Single Categorical."""
        row_indicator = {
            "indicator_code": "Q2_SATISFACTION",
            "statistic_type": "categorical",
            "source_variables": ["Q2_SATISFACTION"],
            "question_type": "Single Choice",
            "transformation_rules": None
        }

        col_indicator = {
            "indicator_code": "Q1_GENDER",
            "statistic_type": "categorical",
            "source_variables": ["Q1_GENDER"],
            "question_type": "Single Choice",
            "transformation_rules": None
        }

        result = processor.generate(sample_data, row_indicator, col_indicator)

        # Verify result structure
        assert result.is_valid is True
        assert result.row_scenario == ScenarioDetector.CAT_SINGLE
        assert result.col_scenario == ScenarioDetector.CAT_SINGLE
        assert result.has_total_column is True
        assert result.has_total_row is True
        assert result.total_row_type == "full"

        # Verify data structure
        assert "rows" in result.data
        assert "total_row" in result.data
        assert len(result.data["rows"]) > 0

        # Verify total row has base_n
        assert "base_n" in result.data["total_row"]
        assert "Male" in result.data["total_row"]["base_n"]
        assert "Female" in result.data["total_row"]["base_n"]
        assert "Total" in result.data["total_row"]["base_n"]

        # Verify total row has values (100%)
        assert result.data["total_row"]["values"] is not None
        assert result.data["total_row"]["values"]["Total"] == 100.0

        # Verify statistics
        assert "chi_square" in result.statistics
        assert "p_value" in result.statistics
        assert "cramers_v" in result.statistics

    def test_scenario_2_cat_multi(self, processor, sample_data):
        """Test Scenario 2: Multiple Binary × Single Categorical."""
        row_indicator = {
            "indicator_code": "S1_BRAND_AWARENESS",
            "statistic_type": "categorical",
            "source_variables": ["S1_BRAND_A", "S1_BRAND_B", "S1_BRAND_C", "S1_BRAND_D"],
            "question_type": "Multiple Choice",
            "transformation_rules": None
        }

        col_indicator = {
            "indicator_code": "Q1_GENDER",
            "statistic_type": "categorical",
            "source_variables": ["Q1_GENDER"],
            "question_type": "Single Choice",
            "transformation_rules": None
        }

        result = processor.generate(sample_data, row_indicator, col_indicator)

        # Verify result structure
        assert result.is_valid is True
        assert result.row_scenario == ScenarioDetector.CAT_MULTI
        assert result.col_scenario == ScenarioDetector.CAT_SINGLE
        assert result.has_total_column is True
        assert result.has_total_row is True
        assert result.total_row_type == "base_only"

        # Verify each row corresponds to a source variable
        assert len(result.data["rows"]) == 4
        row_labels = [r["label"] for r in result.data["rows"]]
        assert "S1_BRAND_A" in row_labels
        assert "S1_BRAND_B" in row_labels
        assert "S1_BRAND_C" in row_labels
        assert "S1_BRAND_D" in row_labels

        # Verify total row has no values (base only)
        assert result.data["total_row"]["values"] is None
        assert "base_n" in result.data["total_row"]

    def test_scenario_3_scalar_single(self, processor, sample_data):
        """Test Scenario 3: Single Scalar × Single Categorical."""
        row_indicator = {
            "indicator_code": "SAT_OVERALL",
            "statistic_type": "scalar",
            "source_variables": ["SAT_OVERALL"],
            "question_type": "Numeric Input",
            "transformation_rules": None
        }

        col_indicator = {
            "indicator_code": "Q1_GENDER",
            "statistic_type": "categorical",
            "source_variables": ["Q1_GENDER"],
            "question_type": "Single Choice",
            "transformation_rules": None
        }

        result = processor.generate(sample_data, row_indicator, col_indicator)

        # Verify result structure
        assert result.is_valid is True
        assert result.row_scenario == ScenarioDetector.SCALAR_SINGLE
        assert result.col_scenario == ScenarioDetector.CAT_SINGLE

        # Verify statistics rows
        row_labels = [r["label"] for r in result.data["rows"]]
        assert "Mean" in row_labels
        assert "Median" in row_labels
        assert "Standard Deviation" in row_labels
        assert "Minimum" in row_labels
        assert "Maximum" in row_labels

        # Verify total row has base N only
        assert result.data["total_row"]["values"] is None
        assert "base_n" in result.data["total_row"]

    def test_scenario_4_scalar_multi(self, processor, sample_data):
        """Test Scenario 4: Multiple Scalar × Single Categorical."""
        row_indicator = {
            "indicator_code": "D1_RATINGS",
            "statistic_type": "scalar",
            "source_variables": ["D1_QUALITY", "D1_PRICE", "D1_SERVICE", "D1_SELECTION", "D1_VALUE"],
            "question_type": "Rating Scale",
            "transformation_rules": None
        }

        col_indicator = {
            "indicator_code": "Q1_GENDER",
            "statistic_type": "categorical",
            "source_variables": ["Q1_GENDER"],
            "question_type": "Single Choice",
            "transformation_rules": None
        }

        result = processor.generate(sample_data, row_indicator, col_indicator)

        # Verify result structure
        assert result.is_valid is True
        assert result.row_scenario == ScenarioDetector.SCALAR_MULTI
        assert result.col_scenario == ScenarioDetector.CAT_SINGLE

        # Verify each row corresponds to a source variable
        assert len(result.data["rows"]) == 5
        row_labels = [r["label"] for r in result.data["rows"]]
        assert "D1_QUALITY" in row_labels
        assert "D1_PRICE" in row_labels
        assert "D1_SERVICE" in row_labels
        assert "D1_SELECTION" in row_labels
        assert "D1_VALUE" in row_labels

        # Verify each row has mean values
        for row in result.data["rows"]:
            assert "values" in row
            assert "Male" in row["values"]
            assert "Female" in row["values"]
            assert "Total" in row["values"]

        # Verify total row has base N only
        assert result.data["total_row"]["values"] is None
        assert "base_n" in result.data["total_row"]

    def test_generate_batch(self, processor, sample_data):
        """Test generating multiple crosstabs at once."""
        row_indicators = [
            {
                "indicator_code": "Q2_SATISFACTION",
                "statistic_type": "categorical",
                "source_variables": ["Q2_SATISFACTION"],
                "question_type": "Single Choice",
                "transformation_rules": None
            }
        ]

        col_indicators = [
            {
                "indicator_code": "Q1_GENDER",
                "statistic_type": "categorical",
                "source_variables": ["Q1_GENDER"],
                "question_type": "Single Choice",
                "transformation_rules": None
            }
        ]

        results = processor.generate_batch(sample_data, row_indicators, col_indicators)

        # Verify batch results
        assert len(results) == 1
        assert results[0].is_valid is True


if __name__ == "__main__":
    # Run tests manually
    pytest.main([__file__, "-v"])
