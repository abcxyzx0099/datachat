"""
Unit Tests for Phase 6: Filtering Nodes (Steps 19-20)

This module contains comprehensive unit tests for the filtering node functions:
- Step 19: generate_filter_list_node - Generate filter criteria for tables
- Step 20: apply_filter_to_tables_node - Apply filters to keep significant tables
- Helper: _should_include_table - Evaluate table against criteria
- Helper: validate_filtering_results - Validate filtering completeness

Test Coverage:
- All filtering criteria (p-value, Cramer's V, validity)
- Edge cases (empty tables, no significant tables, all significant)
- Error handling (missing inputs, invalid data)
- State transitions and immutability
- File output (JSON, CSV)
- Validation logic
- Warning generation

Current coverage target: 80%+ for agent/nodes/phase6_filtering.py
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, Mock
from typing import Dict, Any
import pandas as pd
from datetime import datetime

from agent.nodes.phase6_filtering import (
    generate_filter_list_node,
    apply_filter_to_tables_node,
    _should_include_table,
    validate_filtering_results,
)
from agent.state import (
    WorkflowState,
    STEP_0_INITIAL, STEP_1_EXTRACT_SPSS,
    STEP_4_GENERATE_RECODING_RULES, STEP_5_VALIDATE_RECODING_RULES, STEP_6_REVIEW_RECODING_RULES,
    STEP_18_EXECUTE_STATISTICS_SCRIPT, STEP_19_GENERATE_FILTER_LIST, STEP_20_APPLY_FILTER_TO_TABLES
)


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_statistical_summary() -> Dict[str, Any]:
    """
    Sample statistical summary for testing.

    Contains a mix of significant and insignificant tables with various
    combinations of p-values, Cramer's V, and validity flags.
    """
    return {
        "tables": [
            {
                "table_name": "gender_x_satisfaction",
                "chi_square": 15.3,
                "p_value": 0.002,
                "degrees_of_freedom": 4,
                "cramers_v": 0.45,
                "is_valid": True,
            },
            {
                "table_name": "age_x_education",
                "chi_square": 8.2,
                "p_value": 0.08,
                "degrees_of_freedom": 6,
                "cramers_v": 0.15,
                "is_valid": True,
            },
            {
                "table_name": "income_x_brand",
                "chi_square": 25.6,
                "p_value": 0.0001,
                "degrees_of_freedom": 3,
                "cramers_v": 0.08,  # Too small effect size
                "is_valid": True,
            },
            {
                "table_name": "region_x_product",
                "chi_square": 12.1,
                "p_value": 0.03,
                "degrees_of_freedom": 5,
                "cramers_v": 0.25,
                "is_valid": False,  # Invalid table
                "error": "Expected cell count < 5",
            },
        ]
    }


@pytest.fixture
def all_significant_summary() -> Dict[str, Any]:
    """Statistical summary where all tables pass filtering criteria."""
    return {
        "tables": [
            {
                "table_name": "table1",
                "p_value": 0.001,
                "cramers_v": 0.5,
                "is_valid": True,
            },
            {
                "table_name": "table2",
                "p_value": 0.01,
                "cramers_v": 0.3,
                "is_valid": True,
            },
        ]
    }


@pytest.fixture
def none_significant_summary() -> Dict[str, Any]:
    """Statistical summary where no tables pass filtering criteria."""
    return {
        "tables": [
            {
                "table_name": "table1",
                "p_value": 0.15,  # Not significant
                "cramers_v": 0.05,  # Too small
                "is_valid": False,  # Invalid
                "error": "Small sample size",
            },
            {
                "table_name": "table2",
                "p_value": 0.25,
                "cramers_v": 0.08,
                "is_valid": True,
            },
        ]
    }


@pytest.fixture
def empty_statistical_summary() -> Dict[str, Any]:
    """Empty statistical summary for edge case testing."""
    return {"tables": []}


@pytest.fixture
def filter_list(sample_statistical_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sample filter list for testing apply_filter_to_tables_node.

    Based on sample_statistical_summary with filter decisions applied.
    """
    return {
        "filters": [
            {
                "table_id": "gender_x_satisfaction",
                "include": True,
                "p_value": 0.002,
                "cramers_v": 0.45,
                "is_valid": True,
                "passes_significance": True,
                "passes_cramers_v": True,
                "passes_validity": True,
                "reason": "Passed all filters",
            },
            {
                "table_id": "age_x_education",
                "include": False,
                "p_value": 0.08,
                "cramers_v": 0.15,
                "is_valid": True,
                "passes_significance": False,
                "passes_cramers_v": True,
                "passes_validity": True,
                "reason": "Not statistically significant (p=0.0800 >= 0.05)",
            },
        ],
        "summary": {
            "total_tables": 4,
            "included": 1,
            "excluded": 3,
            "inclusion_rate": 25.0,
            "exclusion_reasons": {
                "not_significant": 1,
                "effect_size_too_small": 1,
                "invalid_table": 1,
                "multiple_failures": 0,
            },
            "criteria": {
                "significance_level": 0.05,
                "min_cramers_v": 0.1,
                "min_cell_count": 10,
            }
        },
        "generated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def filtering_state(statistics_state: WorkflowState) -> WorkflowState:
    """State ready for filtering (after Step 18)."""
    return {
        **statistics_state,
        "current_step": STEP_18_EXECUTE_STATISTICS_SCRIPT,
        "warnings": [],
        "errors": [],
    }


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Sample configuration for filtering tests."""
    from agent.config import DEFAULT_CONFIG
    config = DEFAULT_CONFIG.copy()
    config["temp_dir"] = "temp"
    config["output_dir"] = "output"
    return config


# =============================================================================
# _should_include_table Helper Function Tests
# =============================================================================

class TestShouldIncludeTable:
    """Tests for the _should_include_table helper function."""

    def test_passes_all_criteria(self):
        """Test table that passes all filtering criteria."""
        table_stats = {
            "table_name": "significant_table",
            "p_value": 0.01,
            "cramers_v": 0.3,
            "is_valid": True,
        }

        result = _should_include_table(table_stats, 0.05, 0.1)

        assert result["include"] is True
        assert result["passes_significance"] is True
        assert result["passes_cramers_v"] is True
        assert result["passes_validity"] is True
        assert result["reason"] == "Passed all filters"

    def test_fails_significance_only(self):
        """Test table that fails only significance check."""
        table_stats = {
            "table_name": "not_significant",
            "p_value": 0.15,
            "cramers_v": 0.3,
            "is_valid": True,
        }

        result = _should_include_table(table_stats, 0.05, 0.1)

        assert result["include"] is False
        assert result["passes_significance"] is False
        assert result["passes_cramers_v"] is True
        assert result["passes_validity"] is True
        assert "not statistically significant" in result["reason"].lower()
        assert "p=0.1500" in result["reason"]

    def test_fails_cramers_v_only(self):
        """Test table that fails only Cramer's V check."""
        table_stats = {
            "table_name": "small_effect",
            "p_value": 0.01,
            "cramers_v": 0.05,
            "is_valid": True,
        }

        result = _should_include_table(table_stats, 0.05, 0.1)

        assert result["include"] is False
        assert result["passes_significance"] is True
        assert result["passes_cramers_v"] is False
        assert result["passes_validity"] is True
        assert "effect size too small" in result["reason"].lower()
        assert "cramer's v=0.0500" in result["reason"].lower()

    def test_fails_validity_only(self):
        """Test table that fails only validity check."""
        table_stats = {
            "table_name": "invalid_table",
            "p_value": 0.01,
            "cramers_v": 0.3,
            "is_valid": False,
            "error": "Expected cell count < 5",
        }

        result = _should_include_table(table_stats, 0.05, 0.1)

        assert result["include"] is False
        assert result["passes_significance"] is True
        assert result["passes_cramers_v"] is True
        assert result["passes_validity"] is False
        assert "invalid table" in result["reason"].lower()
        assert "expected cell count" in result["reason"].lower()

    def test_fails_validity_no_error_message(self):
        """Test invalid table without specific error message."""
        table_stats = {
            "table_name": "invalid_no_error",
            "p_value": 0.01,
            "cramers_v": 0.3,
            "is_valid": False,
        }

        result = _should_include_table(table_stats, 0.05, 0.1)

        assert result["include"] is False
        assert result["reason"] == "Invalid table"

    def test_fails_multiple_criteria(self):
        """Test table that fails multiple criteria."""
        table_stats = {
            "table_name": "multiple_failures",
            "p_value": 0.15,
            "cramers_v": 0.05,
            "is_valid": False,
        }

        result = _should_include_table(table_stats, 0.05, 0.1)

        assert result["include"] is False
        assert result["passes_significance"] is False
        assert result["passes_cramers_v"] is False
        assert result["passes_validity"] is False
        # Should have combined reason
        assert "invalid table" in result["reason"].lower()

    def test_missing_fields_default_values(self):
        """Test table with missing fields uses appropriate defaults."""
        table_stats = {
            "table_name": "missing_fields",
            # Missing p_value, cramers_v, is_valid
        }

        result = _should_include_table(table_stats, 0.05, 0.1)

        assert result["include"] is False
        assert result["passes_significance"] is False  # Default p_value=1.0
        assert result["passes_cramers_v"] is False  # Default cramers_v=0.0
        assert result["passes_validity"] is True  # Default is_valid=True

    def test_custom_thresholds(self):
        """Test filtering with custom thresholds."""
        table_stats = {
            "table_name": "custom_thresholds",
            "p_value": 0.03,
            "cramers_v": 0.08,
            "is_valid": True,
        }

        # With default thresholds (p < 0.05, V >= 0.1)
        result_default = _should_include_table(table_stats, 0.05, 0.1)
        assert result_default["include"] is False
        assert result_default["passes_significance"] is True
        assert result_default["passes_cramers_v"] is False

        # With custom thresholds (p < 0.01, V >= 0.05)
        result_custom = _should_include_table(table_stats, 0.01, 0.05)
        assert result_custom["include"] is False
        assert result_custom["passes_significance"] is False
        assert result_custom["passes_cramers_v"] is True

    def test_boundary_values(self):
        """Test boundary values for thresholds."""
        # Exactly at threshold
        table_stats = {
            "table_name": "boundary",
            "p_value": 0.05,  # Exactly at threshold
            "cramers_v": 0.1,  # Exactly at threshold
            "is_valid": True,
        }

        result = _should_include_table(table_stats, 0.05, 0.1)

        # p_value < threshold (strict inequality)
        assert result["passes_significance"] is False
        # cramers_v >= threshold (inclusive)
        assert result["passes_cramers_v"] is True


# =============================================================================
# generate_filter_list_node Tests (Step 19)
# =============================================================================

class TestGenerateFilterListNode:
    """Tests for generate_filter_list_node (Step 19)."""

    def test_success_with_mixed_tables(
        self,
        filtering_state: WorkflowState,
        sample_statistical_summary: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test successful filter list generation with mixed significant/insignificant tables."""
        state = {
            **filtering_state,
            "statistical_summary": sample_statistical_summary,
            "config": {**sample_config, "temp_dir": str(tmp_path)},
        }

        result = generate_filter_list_node(state)

        # Check state transition
        assert result["current_step"] == STEP_19_GENERATE_FILTER_LIST

        # Check filter list structure
        assert "filter_list" in result
        filter_list = result["filter_list"]

        assert "filters" in filter_list
        assert "summary" in filter_list
        assert "generated_at" in filter_list

        # Check filters
        filters = filter_list["filters"]
        assert len(filters) == 4  # 4 tables in sample

        # Check first table (should pass)
        gender_satisfaction = next(f for f in filters if f["table_id"] == "gender_x_satisfaction")
        assert gender_satisfaction["include"] is True
        assert gender_satisfaction["passes_significance"] is True
        assert gender_satisfaction["passes_cramers_v"] is True
        assert gender_satisfaction["passes_validity"] is True

        # Check second table (should fail - not significant)
        age_education = next(f for f in filters if f["table_id"] == "age_x_education")
        assert age_education["include"] is False
        assert age_education["passes_significance"] is False

        # Check summary
        summary = filter_list["summary"]
        assert summary["total_tables"] == 4
        assert summary["included"] == 1
        assert summary["excluded"] == 3
        assert "inclusion_rate" in summary

        # Note: filter_list_json_path is not returned in state,
        # but the file is created on disk
        json_path = Path(tmp_path) / "filters" / "filter_list.json"
        assert json_path.exists()

        with open(json_path, 'r') as f:
            saved_data = json.load(f)
        assert saved_data == filter_list

    def test_empty_statistical_summary(
        self,
        filtering_state: WorkflowState,
        empty_statistical_summary: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test handling of empty statistical summary."""
        state = {
            **filtering_state,
            "statistical_summary": empty_statistical_summary,
            "config": {**sample_config, "temp_dir": str(tmp_path)},
        }

        result = generate_filter_list_node(state)

        assert result["current_step"] == STEP_19_GENERATE_FILTER_LIST
        assert result["filter_list"]["summary"]["total_tables"] == 0
        assert result["filter_list"]["summary"]["included"] == 0
        assert len(result.get("warnings", [])) >= 1
        assert "no tables found" in result.get("warnings", [])[0].lower()

    def test_no_significant_tables(
        self,
        filtering_state: WorkflowState,
        none_significant_summary: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test when no tables pass filtering criteria."""
        state = {
            **filtering_state,
            "statistical_summary": none_significant_summary,
            "config": {**sample_config, "temp_dir": str(tmp_path)},
        }

        result = generate_filter_list_node(state)

        assert result["current_step"] == STEP_19_GENERATE_FILTER_LIST
        assert result["filter_list"]["summary"]["included"] == 0
        assert result["filter_list"]["summary"]["excluded"] == 2

        # Should have warning about no tables passing
        assert len(result.get("warnings", [])) >= 1
        assert "no tables passed" in result.get("warnings", [])[0].lower()

    def test_all_tables_significant(
        self,
        filtering_state: WorkflowState,
        all_significant_summary: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test when all tables pass filtering criteria."""
        state = {
            **filtering_state,
            "statistical_summary": all_significant_summary,
            "config": {**sample_config, "temp_dir": str(tmp_path)},
        }

        result = generate_filter_list_node(state)

        assert result["current_step"] == STEP_19_GENERATE_FILTER_LIST
        assert result["filter_list"]["summary"]["included"] == 2
        assert result["filter_list"]["summary"]["excluded"] == 0
        assert result["filter_list"]["summary"]["inclusion_rate"] == 100.0

    def test_custom_config_thresholds(
        self,
        filtering_state: WorkflowState,
        sample_statistical_summary: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test filtering with custom configuration thresholds."""
        custom_config = {
            **sample_config,
            "temp_dir": str(tmp_path),
            "significance_level": 0.01,  # Stricter
            "min_cramers_v": 0.3,  # Stricter
        }

        state = {
            **filtering_state,
            "statistical_summary": sample_statistical_summary,
            "config": custom_config,
        }

        result = generate_filter_list_node(state)

        # Check that custom thresholds were used
        summary = result["filter_list"]["summary"]
        assert summary["criteria"]["significance_level"] == 0.01
        assert summary["criteria"]["min_cramers_v"] == 0.3

        # With stricter thresholds, fewer tables should pass
        assert result["filter_list"]["summary"]["included"] <= 1

    def test_missing_statistical_summary(
        self,
        filtering_state: WorkflowState,
    ):
        """Test error handling when statistical_summary is missing."""
        state = {
            **filtering_state,
            "statistical_summary": None,
        }

        result = generate_filter_list_node(state)

        assert result["current_step"] == STEP_19_GENERATE_FILTER_LIST
        assert len(result.get("errors", [])) == 1
        assert "statistical_summary" in result.get("errors", [])[0].lower()

    def test_state_immutability(
        self,
        filtering_state: WorkflowState,
        sample_statistical_summary: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test that input state is not mutated."""
        # Create a fresh state without filter_list key
        state = {
            **{k: v for k, v in filtering_state.items() if k != "filter_list"},
            "statistical_summary": sample_statistical_summary.copy(),
            "config": {**sample_config, "temp_dir": str(tmp_path)},
            "warnings": ["existing warning"],
        }

        original_warnings = list(state.get("warnings", []))
        original_summary = state["statistical_summary"].copy()

        result = generate_filter_list_node(state)

        # Input state should be unchanged
        assert state.get("warnings", []) == original_warnings
        assert state["statistical_summary"] == original_summary
        assert "filter_list" not in state

        # Result should have new filter_list
        assert "filter_list" in result

    def test_exclusion_reason_tracking(
        self,
        filtering_state: WorkflowState,
        sample_statistical_summary: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test that exclusion reasons are properly tracked."""
        state = {
            **filtering_state,
            "statistical_summary": sample_statistical_summary,
            "config": {**sample_config, "temp_dir": str(tmp_path)},
        }

        result = generate_filter_list_node(state)

        exclusion_reasons = result["filter_list"]["summary"]["exclusion_reasons"]

        # Check that all exclusion reasons are tracked
        assert "not_significant" in exclusion_reasons
        assert "effect_size_too_small" in exclusion_reasons
        assert "invalid_table" in exclusion_reasons
        assert "multiple_failures" in exclusion_reasons

        # Verify counts (based on sample_statistical_summary)
        assert exclusion_reasons["not_significant"] == 1  # age_x_education
        assert exclusion_reasons["effect_size_too_small"] == 1  # income_x_brand
        assert exclusion_reasons["invalid_table"] == 1  # region_x_product

    def test_low_inclusion_rate_warning(
        self,
        filtering_state: WorkflowState,
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test warning generation for low inclusion rate."""
        # Create summary with low inclusion rate (< 20%)
        # 2 significant out of 11 total = ~18.18%
        low_inclusion_summary = {
            "tables": [
                {"table_name": f"table{i}", "p_value": 0.001, "cramers_v": 0.5, "is_valid": True}
                for i in range(2)  # 2 significant
            ] + [
                {"table_name": f"table{i}", "p_value": 0.5, "cramers_v": 0.05, "is_valid": True}
                for i in range(2, 11)  # 9 not significant
            ]
        }

        state = {
            **filtering_state,
            "statistical_summary": low_inclusion_summary,
            "config": {**sample_config, "temp_dir": str(tmp_path)},
        }

        result = generate_filter_list_node(state)

        # Inclusion rate should be < 20% (2/11 ≈ 18.18%)
        inclusion_rate = result["filter_list"]["summary"]["inclusion_rate"]
        assert inclusion_rate < 20.0

        # Should have warning about low inclusion rate
        warning_messages = [w.lower() for w in result.get("warnings", [])]
        low_inclusion_warning = any("low inclusion rate" in w for w in warning_messages)
        assert low_inclusion_warning


# =============================================================================
# validate_filtering_results Tests
# =============================================================================

class TestValidateFilteringResults:
    """Tests for validate_filtering_results function."""

    def test_valid_filtering(
        self,
        sample_statistical_summary: Dict[str, Any],
    ):
        """Test validation of successful filtering."""
        # Create a complete filter_list matching all tables
        complete_filter_list = {
            "filters": [
                {"table_id": "gender_x_satisfaction", "include": True, "reason": "Passed"},
                {"table_id": "age_x_education", "include": False, "reason": "Not significant"},
                {"table_id": "income_x_brand", "include": False, "reason": "Small effect"},
                {"table_id": "region_x_product", "include": False, "reason": "Invalid"},
            ]
        }

        # Create filtered_tables with only significant table
        filtered_tables = {
            "tables": [sample_statistical_summary["tables"][0]]  # Only gender_x_satisfaction
        }

        is_valid, errors, warnings = validate_filtering_results(
            sample_statistical_summary,
            complete_filter_list,
            filtered_tables,
        )

        assert is_valid is True
        assert len(errors) == 0
        # May have warnings (e.g., about filtered out tables)

    def test_empty_inputs(self):
        """Test validation with empty inputs."""
        is_valid, errors, warnings = validate_filtering_results({}, {}, {})

        assert is_valid is False
        assert len(errors) >= 1
        assert any("empty" in e.lower() for e in errors)

    def test_missing_filters_error(
        self,
        sample_statistical_summary: Dict[str, Any],
    ):
        """Test validation detects missing filters for tables."""
        # Create filter_list missing one table
        incomplete_filter_list = {
            "filters": [
                {"table_id": "gender_x_satisfaction", "include": True, "reason": "Passed"},
                # Missing: age_x_education, income_x_brand, region_x_product
            ]
        }

        filtered_tables = {"tables": []}

        is_valid, errors, warnings = validate_filtering_results(
            sample_statistical_summary,
            incomplete_filter_list,
            filtered_tables,
        )

        assert is_valid is False
        assert any("missing filters" in e.lower() for e in errors)

    def test_no_significant_tables_warning(
        self,
        sample_statistical_summary: Dict[str, Any],
    ):
        """Test validation warning when no significant tables found."""
        # Create a complete filter_list matching all tables
        complete_filter_list = {
            "filters": [
                {"table_id": "gender_x_satisfaction", "include": False, "reason": "Failed"},
                {"table_id": "age_x_education", "include": False, "reason": "Failed"},
                {"table_id": "income_x_brand", "include": False, "reason": "Failed"},
                {"table_id": "region_x_product", "include": False, "reason": "Failed"},
            ]
        }

        filtered_tables = {"tables": []}  # Empty

        is_valid, errors, warnings = validate_filtering_results(
            sample_statistical_summary,
            complete_filter_list,
            filtered_tables,
        )

        # Should be valid (no tables is not an error, just a warning)
        assert is_valid is True
        assert len(errors) == 0
        assert any("no significant tables" in w.lower() for w in warnings)

    def test_tables_with_errors(
        self,
        sample_statistical_summary: Dict[str, Any],
    ):
        """Test validation detects tables dropped due to errors."""
        # Create filter_list with error in reason
        filter_list_with_errors = {
            "filters": [
                {"table_id": "gender_x_satisfaction", "include": True, "reason": "Passed"},
                {"table_id": "age_x_education", "include": False, "reason": "Calculation error in chi-square"},
            ]
        }

        filtered_tables = {"tables": [sample_statistical_summary["tables"][0]]}

        is_valid, errors, warnings = validate_filtering_results(
            sample_statistical_summary,
            filter_list_with_errors,
            filtered_tables,
        )

        assert is_valid is False
        assert any("dropped due to errors" in e.lower() for e in errors)

    def test_extra_filters_warning(
        self,
        sample_statistical_summary: Dict[str, Any],
    ):
        """Test validation warning for filters without corresponding tables."""
        filter_list_extra = {
            "filters": [
                {"table_id": "gender_x_satisfaction", "include": True, "reason": "Passed"},
                {"table_id": "nonexistent_table", "include": False, "reason": "Unknown"},
            ]
        }

        filtered_tables = {"tables": [sample_statistical_summary["tables"][0]]}

        is_valid, errors, warnings = validate_filtering_results(
            sample_statistical_summary,
            filter_list_extra,
            filtered_tables,
        )

        # Extra filters should generate a warning, not an error
        assert any("without corresponding tables" in w.lower() for w in warnings)


# =============================================================================
# apply_filter_to_tables_node Tests (Step 20)
# =============================================================================

class TestApplyFilterToTablesNode:
    """Tests for apply_filter_to_tables_node (Step 20)."""

    def test_success_significant_tables(
        self,
        filtering_state: WorkflowState,
        sample_statistical_summary: Dict[str, Any],
        filter_list: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test successful filter application with significant tables."""
        state = {
            **filtering_state,
            "current_step": STEP_19_GENERATE_FILTER_LIST,
            "statistical_summary": sample_statistical_summary,
            "filter_list": filter_list,
            "config": {**sample_config, "output_dir": str(tmp_path)},
        }

        result = apply_filter_to_tables_node(state)

        # Check state transition
        assert result["current_step"] == STEP_20_APPLY_FILTER_TO_TABLES

        # Check filtered_tables structure
        assert "filtered_tables" in result
        filtered = result["filtered_tables"]

        assert "tables" in filtered
        assert "summary" in filtered
        assert "filtered_at" in filtered

        # Check that only significant tables are included
        # Based on filter_list, only gender_x_satisfaction is included
        assert len(filtered["tables"]) == 1
        assert filtered["tables"][0]["table_name"] == "gender_x_satisfaction"

        # Check summary
        summary = filtered["summary"]
        assert summary["original_count"] == 4
        assert summary["filtered_count"] == 1
        assert summary["excluded_count"] == 3
        assert "inclusion_rate" in summary

        # Check file paths
        assert "significant_tables_json_path" in result
        assert "significant_tables_csv_path" in result

        # Verify files exist
        json_path = Path(result["significant_tables_json_path"])
        csv_path = Path(result["significant_tables_csv_path"])
        assert json_path.exists()
        assert csv_path.exists()

        # Verify JSON content
        with open(json_path, 'r') as f:
            saved_json = json.load(f)
        assert saved_json == filtered

        # Verify CSV content
        df = pd.read_csv(csv_path)
        assert len(df) == 1
        assert "table_name" in df.columns
        assert df.iloc[0]["table_name"] == "gender_x_satisfaction"

    def test_empty_filter_list(
        self,
        filtering_state: WorkflowState,
        sample_statistical_summary: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test handling of empty filter list."""
        state = {
            **filtering_state,
            "current_step": STEP_19_GENERATE_FILTER_LIST,
            "statistical_summary": sample_statistical_summary,
            "filter_list": {"filters": [], "summary": {"criteria": {}}},
            "config": {**sample_config, "output_dir": str(tmp_path)},
        }

        result = apply_filter_to_tables_node(state)

        assert result["current_step"] == STEP_20_APPLY_FILTER_TO_TABLES
        assert result["filtered_tables"]["summary"]["filtered_count"] == 0
        assert len(result.get("warnings", [])) >= 1
        assert "no filters found" in result.get("warnings", [])[0].lower()

    def test_no_significant_tables_after_filtering(
        self,
        filtering_state: WorkflowState,
        none_significant_summary: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test when no tables pass filtering."""
        # Create filter_list where all tables are excluded
        filter_list_none = {
            "filters": [
                {"table_id": "table1", "include": False, "reason": "Not significant"},
                {"table_id": "table2", "include": False, "reason": "Not significant"},
            ],
            "summary": {
                "total_tables": 2,
                "included": 0,
                "excluded": 2,
                "criteria": {},
            },
        }

        state = {
            **filtering_state,
            "current_step": STEP_19_GENERATE_FILTER_LIST,
            "statistical_summary": none_significant_summary,
            "filter_list": filter_list_none,
            "config": {**sample_config, "output_dir": str(tmp_path)},
        }

        result = apply_filter_to_tables_node(state)

        assert result["current_step"] == STEP_20_APPLY_FILTER_TO_TABLES
        assert result["filtered_tables"]["summary"]["filtered_count"] == 0

        # Should have warning about no significant tables
        warnings_text = " ".join([w.lower() for w in result.get("warnings", [])])
        assert "no significant tables" in warnings_text

    def test_missing_filter_list(
        self,
        filtering_state: WorkflowState,
        sample_statistical_summary: Dict[str, Any],
    ):
        """Test error handling when filter_list is missing."""
        state = {
            **filtering_state,
            "current_step": STEP_19_GENERATE_FILTER_LIST,
            "statistical_summary": sample_statistical_summary,
            "filter_list": None,
        }

        result = apply_filter_to_tables_node(state)

        assert result["current_step"] == STEP_20_APPLY_FILTER_TO_TABLES
        assert len(result.get("errors", [])) == 1
        assert "filter_list" in result.get("errors", [])[0].lower()

    def test_missing_statistical_summary(
        self,
        filtering_state: WorkflowState,
        filter_list: Dict[str, Any],
    ):
        """Test error handling when statistical_summary is missing."""
        state = {
            **filtering_state,
            "current_step": STEP_19_GENERATE_FILTER_LIST,
            "statistical_summary": None,
            "filter_list": filter_list,
        }

        result = apply_filter_to_tables_node(state)

        assert result["current_step"] == STEP_20_APPLY_FILTER_TO_TABLES
        assert len(result.get("errors", [])) == 1
        assert "statistical_summary" in result.get("errors", [])[0].lower()

    def test_state_immutability(
        self,
        filtering_state: WorkflowState,
        sample_statistical_summary: Dict[str, Any],
        filter_list: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test that input state is not mutated."""
        # Create a fresh state without filtered_tables key
        state = {
            **{k: v for k, v in filtering_state.items() if k not in ("filter_list", "filtered_tables")},
            "current_step": STEP_19_GENERATE_FILTER_LIST,
            "statistical_summary": sample_statistical_summary.copy(),
            "filter_list": filter_list.copy(),
            "config": {**sample_config, "output_dir": str(tmp_path)},
            "errors": ["existing error"],
            "warnings": ["existing warning"],
        }

        original_errors = list(state.get("errors", []))
        original_warnings = list(state.get("warnings", []))

        result = apply_filter_to_tables_node(state)

        # Input state should be unchanged
        assert state.get("errors", []) == original_errors
        assert state.get("warnings", []) == original_warnings
        assert "filtered_tables" not in state

        # Result should have filtered_tables
        assert "filtered_tables" in result

    def test_validation_passed_to_state(
        self,
        filtering_state: WorkflowState,
        sample_statistical_summary: Dict[str, Any],
        filter_list: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test that validation results are added to state."""
        state = {
            **filtering_state,
            "current_step": STEP_19_GENERATE_FILTER_LIST,
            "statistical_summary": sample_statistical_summary,
            "filter_list": filter_list,
            "config": {**sample_config, "output_dir": str(tmp_path)},
        }

        result = apply_filter_to_tables_node(state)

        # Check that validation summary fields are in state
        assert "total_tables_evaluated" in result
        assert "significant_tables_count" in result
        assert "filtering_valid" in result

        assert result["total_tables_evaluated"] == 4
        assert result["significant_tables_count"] == 1

    def test_csv_column_structure(
        self,
        filtering_state: WorkflowState,
        sample_statistical_summary: Dict[str, Any],
        filter_list: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test that CSV output has correct column structure."""
        state = {
            **filtering_state,
            "current_step": STEP_19_GENERATE_FILTER_LIST,
            "statistical_summary": sample_statistical_summary,
            "filter_list": filter_list,
            "config": {**sample_config, "output_dir": str(tmp_path)},
        }

        result = apply_filter_to_tables_node(state)

        csv_path = Path(result["significant_tables_csv_path"])
        df = pd.read_csv(csv_path)

        # Check required columns
        required_columns = [
            "table_name",
            "p_value",
            "cramers_v",
            "is_valid",
            "chi_square",
            "degrees_of_freedom",
        ]
        for col in required_columns:
            assert col in df.columns

    def test_empty_csv_when_no_tables(
        self,
        filtering_state: WorkflowState,
        sample_statistical_summary: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test that empty CSV is created when no tables pass filtering."""
        empty_filter_list = {
            "filters": [
                {"table_id": "table1", "include": False, "reason": "Failed"},
            ],
            "summary": {"criteria": {}},
        }

        state = {
            **filtering_state,
            "current_step": STEP_19_GENERATE_FILTER_LIST,
            "statistical_summary": sample_statistical_summary,
            "filter_list": empty_filter_list,
            "config": {**sample_config, "output_dir": str(tmp_path)},
        }

        result = apply_filter_to_tables_node(state)

        csv_path = Path(result["significant_tables_csv_path"])
        df = pd.read_csv(csv_path)

        # Should have headers but no data rows
        assert len(df) == 0
        assert len(df.columns) > 0


# =============================================================================
# Integration Tests
# =============================================================================

class TestFilteringIntegration:
    """Integration tests for the complete filtering workflow."""

    def test_complete_filtering_workflow(
        self,
        filtering_state: WorkflowState,
        sample_statistical_summary: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test complete filtering workflow from Step 19 to Step 20."""
        state = {
            **filtering_state,
            "current_step": STEP_18_EXECUTE_STATISTICS_SCRIPT,
            "statistical_summary": sample_statistical_summary,
            "config": {**sample_config, "temp_dir": str(tmp_path), "output_dir": str(tmp_path)},
        }

        # Step 19: Generate filter list
        state_after_step19 = generate_filter_list_node(state)
        assert state_after_step19["current_step"] == STEP_19_GENERATE_FILTER_LIST
        assert "filter_list" in state_after_step19

        # Step 20: Apply filter
        # Note: With new LangGraph pattern, we manually merge state for testing
        # In production, LangGraph would automatically merge these
        state_for_step20 = {**state, **state_after_step19}
        state_after_step20 = apply_filter_to_tables_node(state_for_step20)
        assert state_after_step20["current_step"] == STEP_20_APPLY_FILTER_TO_TABLES
        assert "filtered_tables" in state_after_step20

        # Verify end state
        assert state_after_step20["total_tables_evaluated"] == 4
        assert state_after_step20["significant_tables_count"] == 1
        assert state_after_step20["filtering_valid"] is True

        # Verify files created
        filter_json_path = Path(tmp_path) / "filters" / "filter_list.json"
        assert filter_json_path.exists()
        assert Path(state_after_step20["significant_tables_json_path"]).exists()
        assert Path(state_after_step20["significant_tables_csv_path"]).exists()

    def test_state_accumulation_across_steps(
        self,
        filtering_state: WorkflowState,
        sample_statistical_summary: Dict[str, Any],
        sample_config: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test that state properly accumulates across filtering steps."""
        initial_warnings = ["initial warning"]
        initial_errors = ["initial error"]

        state = {
            **filtering_state,
            "current_step": STEP_18_EXECUTE_STATISTICS_SCRIPT,
            "statistical_summary": sample_statistical_summary,
            "config": {**sample_config, "temp_dir": str(tmp_path), "output_dir": str(tmp_path)},
            "warnings": list(initial_warnings),
            "errors": list(initial_errors),
        }

        # Step 19
        # Note: With new LangGraph pattern, manually merge state for testing
        state_after_step19 = generate_filter_list_node(state)

        # Warnings should be accumulated
        # Merge state to simulate LangGraph's automatic state merging
        state = {**state, **state_after_step19}
        assert "initial warning" in state.get("warnings", [])
        assert len(state.get("warnings", [])) >= 1

        # Errors should be unchanged (no new errors in step 19)
        # Note: With reducer pattern, if node doesn't return errors, original are preserved
        # But in this direct test, we need to check the merged state
        assert "initial error" in state.get("errors", [])

        # Step 20
        state_after_step20 = apply_filter_to_tables_node(state)
        state = {**state, **state_after_step20}

        # Initial warnings/errors should still be present
        assert "initial warning" in state.get("warnings", [])
        assert "initial error" in state.get("errors", [])
