"""
Tests for survey_analyzer.analysis module.

Tests statistics calculation and indicator generation.
"""

import pytest
import numpy as np


# ============================================================================
# StatisticsCalculator Tests
# ============================================================================

class TestStatisticsCalculatorInstantiation:
    """Test StatisticsCalculator class instantiation."""

    def test_default_initialization(self):
        """Test StatisticsCalculator with default parameters."""
        from survey_analyzer.analysis import StatisticsCalculator
        calc = StatisticsCalculator()
        assert calc.significance_level == 0.05
        assert calc.min_expected_frequency == 5.0
        assert calc.min_cell_count == 10

    def test_custom_significance_level(self):
        """Test StatisticsCalculator with custom significance level."""
        from survey_analyzer.analysis import StatisticsCalculator
        calc = StatisticsCalculator(significance_level=0.01)
        assert calc.significance_level == 0.01

    def test_custom_min_expected_frequency(self):
        """Test StatisticsCalculator with custom min_expected_frequency."""
        from survey_analyzer.analysis import StatisticsCalculator
        calc = StatisticsCalculator(min_expected_frequency=10.0)
        assert calc.min_expected_frequency == 10.0


class TestStatisticsCalculatorAnalyzeTable:
    """Test StatisticsCalculator.analyze_table() method."""

    def test_analyze_table_2x2(self):
        """Test analyzing a valid 2x2 table."""
        from survey_analyzer.analysis import StatisticsCalculator
        calc = StatisticsCalculator()

        result = calc.analyze_table(
            counts=[[45, 32], [52, 28]],
            row_labels=["Male", "Female"],
            column_labels=["Yes", "No"]
        )

        assert result.is_valid is True
        assert result.chi_square > 0
        assert 0 <= result.p_value <= 1
        assert 0 <= result.cramers_v <= 1
        assert result.interpretation in ["negligible", "small", "medium", "large"]

    def test_analyze_table_with_significant_result(self):
        """Test analyzing a table with significant association."""
        from survey_analyzer.analysis import StatisticsCalculator
        calc = StatisticsCalculator()

        # Strong association data (p < 0.05)
        result = calc.analyze_table(
            counts=[[100, 20], [30, 90]],
            row_labels=["Group A", "Group B"],
            column_labels=["Option 1", "Option 2"]
        )

        assert result.is_valid is True
        assert result.p_value < 0.05  # Should be significant
        # Use == for comparison (handles both bool and np.bool_)
        assert result.is_significant == True

    def test_analyze_table_empty_table(self):
        """Test analyzing an empty table returns invalid result."""
        from survey_analyzer.analysis import StatisticsCalculator
        calc = StatisticsCalculator()

        result = calc.analyze_table(
            counts=[],
            row_labels=[],
            column_labels=[]
        )

        assert result.is_valid is False
        assert result.error is not None

    def test_analyze_table_with_negative_values(self):
        """Test analyzing table with negative values returns invalid."""
        from survey_analyzer.analysis import StatisticsCalculator
        calc = StatisticsCalculator()

        result = calc.analyze_table(
            counts=[[-1, 10], [20, 30]],
            row_labels=["A", "B"],
            column_labels=["X", "Y"]
        )

        assert result.is_valid is False
        assert "negative" in result.error.lower()

    def test_analyze_table_small_cell_counts(self):
        """Test analyzing table with small cell counts returns invalid."""
        from survey_analyzer.analysis import StatisticsCalculator
        calc = StatisticsCalculator(min_cell_count=50)

        result = calc.analyze_table(
            counts=[[10, 20], [30, 40]],
            row_labels=["A", "B"],
            column_labels=["X", "Y"]
        )

        assert result.is_valid is False
        assert "below minimum" in result.error.lower()

    def test_analyze_table_to_dict(self):
        """Test ChiSquareResult.to_dict() method."""
        from survey_analyzer.analysis import StatisticsCalculator
        calc = StatisticsCalculator()

        result = calc.analyze_table(
            counts=[[45, 32], [52, 28]],
            row_labels=["Male", "Female"],
            column_labels=["Yes", "No"]
        )

        result_dict = result.to_dict()
        assert "chi_square" in result_dict
        assert "p_value" in result_dict
        assert "cramers_v" in result_dict
        assert "is_significant" in result_dict


class TestStatisticsCalculatorCramersV:
    """Test Cramer's V effect size calculation."""

    def test_cramers_v_small_effect(self):
        """Test Cramer's V with small effect."""
        from survey_analyzer.analysis import StatisticsCalculator
        calc = StatisticsCalculator()

        result = calc.analyze_table(
            counts=[[100, 100], [100, 100]],
            row_labels=["A", "B"],
            column_labels=["X", "Y"]
        )

        # No association should give V near 0
        assert result.cramers_v < 0.1
        assert result.interpretation == "negligible"

    def test_cramers_v_medium_effect(self):
        """Test Cramer's V with medium effect."""
        from survey_analyzer.analysis import StatisticsCalculator
        calc = StatisticsCalculator()

        # Strong association
        result = calc.analyze_table(
            counts=[[80, 20], [20, 80]],
            row_labels=["A", "B"],
            column_labels=["X", "Y"]
        )

        # Should give V around 0.3-0.5 for strong association
        assert result.cramers_v >= 0.3


class TestChiSquareConvenienceFunction:
    """Test chi_square_test() convenience function."""

    def test_chi_square_test_function(self):
        """Test chi_square_test() convenience function."""
        from survey_analyzer.analysis import chi_square_test

        result = chi_square_test(
            counts=[[45, 32], [52, 28]],
            row_labels=["Male", "Female"],
            column_labels=["Yes", "No"],
            significance_level=0.05
        )

        assert result["chi_square"] > 0
        assert 0 <= result["p_value"] <= 1
        assert result["is_significant"] in [True, False]


# ============================================================================
# IndicatorGenerator Tests
# ============================================================================

class TestIndicatorGenerator:
    """Test IndicatorGenerator class."""

    def test_indicator_generator_instantiation(self):
        """Test IndicatorGenerator can be instantiated."""
        from survey_analyzer.analysis import IndicatorGenerator
        gen = IndicatorGenerator()
        assert gen is not None


# ============================================================================
# Module Level Tests
# ============================================================================

class TestAnalysisModule:
    """Test analysis module imports."""

    def test_import_statistics_calculator(self):
        """Test StatisticsCalculator can be imported."""
        from survey_analyzer.analysis import StatisticsCalculator
        assert StatisticsCalculator is not None

    def test_import_indicator_generator(self):
        """Test IndicatorGenerator can be imported."""
        from survey_analyzer.analysis import IndicatorGenerator
        assert IndicatorGenerator is not None

    def test_import_chi_square_function(self):
        """Test chi_square_test can be imported."""
        from survey_analyzer.analysis import chi_square_test
        assert callable(chi_square_test)

    def test_module_exports(self):
        """Test module exports expected classes."""
        from survey_analyzer import analysis
        expected_exports = [
            "StatisticsCalculator",
            "IndicatorGenerator",
            "chi_square_test"
        ]
        for export in expected_exports:
            assert hasattr(analysis, export)
