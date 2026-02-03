"""
Examples demonstrating fixture usage from tests/conftest.py

Run examples with: pytest tests/test_fixture_examples.py -v
"""

import pytest
import pandas as pd
from typing import Dict, Any


# =============================================================================
# Basic Fixture Usage Examples
# =============================================================================

def test_sample_dataframe_size(sample_dataframe: pd.DataFrame):
    """Example: Using sample_dataframe fixture."""
    assert len(sample_dataframe) == 50
    assert "age" in sample_dataframe.columns
    assert sample_dataframe["age"].min() >= 18


def test_small_dataframe_quick(small_dataframe: pd.DataFrame):
    """Example: Using small_dataframe for quick tests."""
    assert len(small_dataframe) == 10  # Fast: only 10 rows
    assert "age" in small_dataframe.columns


def test_metadata_structure(sample_metadata: Dict[str, Any]):
    """Example: Using sample_metadata fixture."""
    assert sample_metadata["n_rows"] == 50
    assert "gender" in sample_metadata["column_labels"]
    assert sample_metadata["column_value_labels"]["gender"][1] == "Male"


def test_initial_state(sample_state):
    """Example: Using sample_state fixture."""
    assert sample_state["current_step"] == 0
    assert "input_file_path" in sample_state


# =============================================================================
# Composing Multiple Fixtures
# =============================================================================

def test_data_with_metadata(sample_dataframe: pd.DataFrame, sample_metadata: Dict[str, Any]):
    """Example: Using multiple fixtures together."""
    # Verify dataframe and metadata match
    assert len(sample_dataframe) == sample_metadata["n_rows"]
    assert len(sample_dataframe.columns) == sample_metadata["n_columns"]

    # Verify variable labels match
    for var in sample_dataframe.columns:
        assert var in sample_metadata["column_labels"]


def test_workflow_phase_state(recoding_state):
    """Example: Using workflow state after recoding phase."""
    # Should be at step 8
    assert recoding_state["current_step"] == 8

    # Should have recoding completed
    assert recoding_state["recoding_approved"] is True
    assert "new_metadata" in recoding_state


# =============================================================================
# Artifact Testing Examples
# =============================================================================

def test_valid_recoding_rules(valid_recoding_rules: Dict[str, Any]):
    """Example: Testing with valid recoding rules."""
    rules = valid_recoding_rules["recoding_rules"]
    assert len(rules) >= 1

    # Check structure
    for rule in rules:
        assert "source_variable" in rule
        assert "target_variable" in rule
        assert "transformation_type" in rule
        assert "rules" in rule


def test_invalid_recoding_rules_error_detection(invalid_recoding_rules: Dict[str, Any]):
    """Example: Testing error detection with invalid rules."""
    rules = invalid_recoding_rules["recoding_rules"]

    # Should have invalid ranges (min > max)
    for rule in rules:
        for r in rule.get("rules", []):
            if "source_min" in r and "source_max" in r:
                # Invalid: min > max
                assert r["source_min"] > r["source_max"]


# =============================================================================
# Mock Usage Examples
# =============================================================================

def test_mock_llm_client(mock_llm_client):
    """Example: Using mock LLM client."""
    # Configure custom response
    from unittest.mock import Mock
    mock_response = Mock()
    mock_response.content = '{"status": "success"}'
    mock_llm_client.invoke.return_value = mock_response

    # Use in test
    result = mock_llm_client.invoke("test prompt")
    assert result.content == '{"status": "success"}'


def test_validation_result(valid_validation_result):
    """Example: Using validation result fixtures."""
    assert valid_validation_result.is_valid is True
    assert len(valid_validation_result.errors) == 0
    assert len(valid_validation_result.warnings) >= 0


def test_invalid_validation_result(invalid_validation_result):
    """Example: Testing with invalid validation result."""
    assert invalid_validation_result.is_valid is False
    assert len(invalid_validation_result.errors) > 0


# =============================================================================
# Temporary Directory Usage Examples
# =============================================================================

def test_temp_output_dir(temp_output_dir):
    """Example: Using temporary output directory."""
    # Create test file
    test_file = temp_output_dir / "test_output.txt"
    test_file.write_text("test data")

    # Verify file exists
    assert test_file.exists()
    assert test_file.read_text() == "test data"

    # Directory auto-cleanup after test


# =============================================================================
# Edge Case Testing Examples
# =============================================================================

def test_edge_case_dataframe(edge_case_dataframe: pd.DataFrame):
    """Example: Testing with edge case data."""
    # Should have missing values
    assert edge_case_dataframe.isna().any().any()

    # Should have outliers (income > 900k)
    assert edge_case_dataframe["income"].max() > 900000


# =============================================================================
# State Evolution Examples
# =============================================================================

def test_state_evolution_sequence():
    """Example: Demonstrating state evolution through phases."""
    # This would normally use fixtures from different phases
    phases = [
        "sample_state",      # Step 0
        "extraction_state",  # Step 3
        "recoding_state",    # Step 8
        "indicator_state",   # Step 11
        "table_state",       # Step 16
        "statistics_state",  # Step 18
        "filtering_state",   # Step 20
        "presentation_state", # Step 22
    ]

    # Verify expected steps for each phase
    expected_steps = [0, 3, 8, 11, 16, 18, 20, 22]

    for phase, expected_step in zip(phases, expected_steps):
        # In real test, you'd use the fixture
        # state = request.getfixturevalue(phase)
        # assert state["current_step"] == expected_step
        pass


# =============================================================================
# Parametrized Tests with Fixtures
# =============================================================================

@pytest.mark.parametrize("fixture_name", [
    "small_dataframe",
    "sample_dataframe",
    "large_dataframe",
])
def test_multiple_dataframes(request, fixture_name):
    """Example: Parametrized test with different dataframe fixtures."""
    df = request.getfixturevalue(fixture_name)

    # All dataframes should have 'age' column
    assert "age" in df.columns

    # All dataframes should have valid age range
    assert df["age"].min() >= 18
    assert df["age"].max() <= 100


# =============================================================================
# Configuration Testing Examples
# =============================================================================

def test_sample_config_auto_approval(sample_config):
    """Example: Testing with auto-approval config."""
    assert sample_config["auto_approve_recoding"] is True
    assert sample_config["auto_approve_indicators"] is True
    assert sample_config["auto_approve_table_specs"] is True


def test_human_review_config(human_review_config):
    """Example: Testing with human review config."""
    assert human_review_config["enable_human_review"] is True
    assert human_review_config["auto_approve_recoding"] is False
    assert human_review_config["auto_approve_indicators"] is False


# =============================================================================
# PSPP Output Testing Examples
# =============================================================================

def test_pspp_recoding_syntax(sample_pspp_recoding_syntax: str):
    """Example: Testing PSPP syntax fixture."""
    assert "RECODE" in sample_pspp_recoding_syntax
    assert "age_group" in sample_pspp_recoding_syntax
    assert "EXECUTE" in sample_pspp_recoding_syntax


def test_pspp_success_output(sample_pspp_output: Dict[str, Any]):
    """Example: Testing PSPP success output."""
    assert sample_pspp_output["exit_code"] == 0
    assert sample_pspp_output["output_file"] is not None
    assert len(sample_pspp_output["stderr"]) == 0


def test_pspp_error_output(sample_pspp_error: Dict[str, Any]):
    """Example: Testing PSPP error output."""
    assert sample_pspp_error["exit_code"] != 0
    assert len(sample_pspp_error["stderr"]) > 0


# =============================================================================
# Markers Usage Examples
# =============================================================================

@pytest.mark.unit
def test_unit_example(sample_dataframe):
    """Example: Marked as unit test."""
    assert len(sample_dataframe) == 50


@pytest.mark.slow
def test_slow_example(large_dataframe):
    """Example: Marked as slow test (uses large dataset)."""
    assert len(large_dataframe) == 500
    # This would normally do more complex processing


# =============================================================================
# Summary
# =============================================================================

def test_fixture_availability_summary():
    """
    Summary of available fixtures.

    All fixtures are defined in tests/conftest.py
    """
    fixtures_available = {
        # Data fixtures
        "sample_dataframe": "50 rows, 6 variables",
        "small_dataframe": "10 rows, 4 variables",
        "large_dataframe": "500 rows, 15 variables",
        "edge_case_dataframe": "12 rows with missing values",

        # Metadata fixtures
        "sample_metadata": "SPSS metadata structure",
        "variable_centered_metadata": "Variable-centered format",
        "filtered_metadata": "After filtering",
        "new_metadata": "After recoding",

        # State fixtures
        "sample_state": "Step 0: Initial state",
        "extraction_state": "Step 3: After extraction",
        "recoding_state": "Step 8: After recoding",
        "indicator_state": "Step 11: After indicators",
        "table_state": "Step 16: After tables",
        "statistics_state": "Step 18: After statistics",
        "filtering_state": "Step 20: After filtering",
        "presentation_state": "Step 22: Final state",

        # Artifact fixtures
        "valid_recoding_rules": "Valid recoding JSON",
        "invalid_recoding_rules": "Invalid recoding JSON",
        "valid_indicators": "Valid indicators JSON",
        "invalid_indicators": "Invalid indicators JSON",
        "valid_table_specs": "Valid table specs JSON",
        "invalid_table_specs": "Invalid table specs JSON",

        # LLM fixtures
        "mock_llm_client": "Mocked LLM client",
        "valid_recoding_llm_response": "Valid LLM JSON string",
        "invalid_json_llm_response": "Invalid JSON string",

        # PSPP fixtures
        "mock_pspp_wrapper": "Mocked PSPP wrapper",
        "sample_pspp_recoding_syntax": "PSPP RECODE syntax",
        "sample_pspp_table_syntax": "PSPP CTABLES syntax",
        "sample_pspp_output": "PSPP success result",
        "sample_pspp_error": "PSPP error result",

        # Validation fixtures
        "valid_validation_result": "Valid ValidationResult",
        "invalid_validation_result": "Invalid ValidationResult",

        # Config fixtures
        "sample_config": "Standard test config",
        "minimal_config": "Minimal config",
        "human_review_config": "Human review config",

        # Path fixtures
        "sample_sav_path": "Path to sample_data.sav",
        "small_sav_path": "Path to small_data.sav",
        "large_sav_path": "Path to large_data.sav",
        "edge_case_sav_path": "Path to edge_case_data.sav",
        "temp_output_dir": "Temporary output directory",
        "temp_checkpoint_db": "Temporary checkpoint DB",
    }

    # Just to show the summary exists
    assert len(fixtures_available) > 0
