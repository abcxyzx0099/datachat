"""
Tests for survey_analyzer.filtering module.

Tests significance filtering functionality.
"""

import pytest
from survey_analyzer.filtering import filter_significant, SignificanceFilter, FilterCriteria


# ============================================================================
# FilterCriteria Tests
# ============================================================================

class TestFilterCriteria:
    """Test FilterCriteria dataclass."""

    def test_default_criteria(self):
        """Test FilterCriteria with default values."""
        from survey_analyzer.filtering import FilterCriteria
        criteria = FilterCriteria()

        assert criteria.significance_level == 0.05
        assert criteria.min_cramers_v == 0.1
        assert criteria.min_cell_count == 10
        assert criteria.require_valid is True

    def test_custom_criteria(self):
        """Test FilterCriteria with custom values."""
        from survey_analyzer.filtering import FilterCriteria
        criteria = FilterCriteria(
            significance_level=0.01,
            min_cramers_v=0.2,
            min_cell_count=20,
            require_valid=False
        )

        assert criteria.significance_level == 0.01
        assert criteria.min_cramers_v == 0.2
        assert criteria.min_cell_count == 20
        assert criteria.require_valid is False

    def test_filter_criteria_to_dict(self):
        """Test FilterCriteria.to_dict() method."""
        from survey_analyzer.filtering import FilterCriteria
        criteria = FilterCriteria(significance_level=0.01)
        criteria_dict = criteria.to_dict()

        assert criteria_dict["significance_level"] == 0.01
        assert "min_cramers_v" in criteria_dict


# ============================================================================
# SignificanceFilter Tests
# ============================================================================

class TestSignificanceFilterInstantiation:
    """Test SignificanceFilter class instantiation."""

    def test_default_initialization(self):
        """Test SignificanceFilter with default criteria."""
        from survey_analyzer.filtering import SignificanceFilter
        filter_obj = SignificanceFilter()
        assert filter_obj is not None
        assert filter_obj.criteria.significance_level == 0.05

    def test_custom_criteria_initialization(self):
        """Test SignificanceFilter with custom criteria."""
        from survey_analyzer.filtering import SignificanceFilter, FilterCriteria
        criteria = FilterCriteria(significance_level=0.01)
        filter_obj = SignificanceFilter(criteria)
        assert filter_obj.criteria.significance_level == 0.01


class TestSignificanceFilterFilterTables:
    """Test SignificanceFilter.filter_tables() method."""

    def test_filter_tables_all_significant(self):
        """Test filtering tables where all are significant."""
        from survey_analyzer.filtering import SignificanceFilter

        tables = [
            {"table_name": "t1", "p_value": 0.01, "cramers_v": 0.3, "is_valid": True},
            {"table_name": "t2", "p_value": 0.02, "cramers_v": 0.4, "is_valid": True},
            {"table_name": "t3", "p_value": 0.03, "cramers_v": 0.5, "is_valid": True},
        ]

        filter_obj = SignificanceFilter()
        result = filter_obj.filter_tables(tables)

        assert result.summary.included == 3
        assert result.summary.excluded == 0
        assert len(result.included_tables) == 3

    def test_filter_tables_none_significant(self):
        """Test filtering tables where none are significant."""
        from survey_analyzer.filtering import SignificanceFilter

        tables = [
            {"table_name": "t1", "p_value": 0.15, "cramers_v": 0.05, "is_valid": True},
            {"table_name": "t2", "p_value": 0.20, "cramers_v": 0.02, "is_valid": True},
        ]

        filter_obj = SignificanceFilter()
        result = filter_obj.filter_tables(tables)

        assert result.summary.included == 0
        assert result.summary.excluded == 2
        assert len(result.included_tables) == 0

    def test_filter_tables_mixed_significance(self):
        """Test filtering tables with mixed significance."""
        from survey_analyzer.filtering import SignificanceFilter

        tables = [
            {"table_name": "t1", "p_value": 0.01, "cramers_v": 0.3, "is_valid": True},  # Significant
            {"table_name": "t2", "p_value": 0.15, "cramers_v": 0.05, "is_valid": True},  # Not significant (p-value)
            {"table_name": "t3", "p_value": 0.03, "cramers_v": 0.05, "is_valid": True},  # Not significant (Cramer's V)
            {"table_name": "t4", "p_value": 0.02, "cramers_v": 0.4, "is_valid": False},  # Invalid
        ]

        filter_obj = SignificanceFilter()
        result = filter_obj.filter_tables(tables)

        assert result.summary.included == 1  # Only t1 passes all filters
        assert result.summary.excluded == 3

    def test_filter_tables_with_none_p_value(self):
        """Test filtering tables with None p-value."""
        from survey_analyzer.filtering import SignificanceFilter

        tables = [
            {"table_name": "t1", "p_value": None, "cramers_v": 0.3, "is_valid": True},
        ]

        filter_obj = SignificanceFilter()
        result = filter_obj.filter_tables(tables)

        # None should be treated as 1.0 (not significant)
        assert result.summary.included == 0

    def test_filter_tables_to_dict(self):
        """Test FilterList.to_dict() method."""
        from survey_analyzer.filtering import SignificanceFilter

        tables = [
            {"table_name": "t1", "p_value": 0.01, "cramers_v": 0.3, "is_valid": True},
        ]

        filter_obj = SignificanceFilter()
        result = filter_obj.filter_tables(tables)
        result_dict = result.to_dict()

        assert "filters" in result_dict
        assert "summary" in result_dict


class TestSignificanceFilterApplyFilter:
    """Test SignificanceFilter.apply_filter() method."""

    def test_apply_filter_returns_included_tables(self):
        """Test apply_filter() returns only included tables."""
        from survey_analyzer.filtering import SignificanceFilter

        tables = [
            {"table_name": "t1", "p_value": 0.01, "cramers_v": 0.3, "is_valid": True},
            {"table_name": "t2", "p_value": 0.15, "cramers_v": 0.05, "is_valid": True},
        ]

        filter_obj = SignificanceFilter()
        filter_result = filter_obj.filter_tables(tables)
        filtered_tables = filter_obj.apply_filter(tables, filter_result.filters)

        assert len(filtered_tables) == 1
        assert filtered_tables[0]["table_name"] == "t1"


# ============================================================================
# FilterSignificance Convenience Function
# ============================================================================

class TestFilterSignificanceFunction:
    """Test filter_significant() convenience function."""

    def test_filter_significant_function(self):
        """Test filter_significant() convenience function."""
        from survey_analyzer.filtering import filter_significant

        tables = [
            {"table_name": "t1", "p_value": 0.01, "cramers_v": 0.3, "is_valid": True},
            {"table_name": "t2", "p_value": 0.15, "cramers_v": 0.05, "is_valid": True},
        ]

        result = filter_significant(tables, significance_level=0.05, min_cramers_v=0.1)

        assert result.summary.included == 1
        assert result.summary.excluded == 1
        # Check that filters is a list of dicts (to_dict() was called)
        assert isinstance(result.filters, list)
        # Verify each filter in the list is a dict (to_dict() was called)
        for f in result.filters:
            assert isinstance(f, dict), f"Filter {f} is not a dict: {f.__class__.__name__}"


# ============================================================================
# Module Level Tests
# ============================================================================

class TestFilteringModule:
    """Test filtering module imports."""

    def test_import_significance_filter(self):
        """Test SignificanceFilter can be imported."""
        from survey_analyzer.filtering import SignificanceFilter
        assert SignificanceFilter is not None

    def test_import_filter_criteria(self):
        """Test FilterCriteria can be imported."""
        from survey_analyzer.filtering import FilterCriteria
        assert FilterCriteria is not None

    def test_import_filter_significance_function(self):
        """Test filter_significant can be imported."""
        from survey_analyzer.filtering import filter_significant
        assert callable(filter_significant)

    def test_module_exports(self):
        """Test module exports expected classes."""
        from survey_analyzer import filtering
        expected_exports = ["SignificanceFilter", "FilterCriteria", "filter_significant"]
        for export in expected_exports:
            assert hasattr(filtering, export)
