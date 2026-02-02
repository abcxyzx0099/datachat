"""
Pytest Configuration and Fixtures for Survey Analysis Workflow Tests

This module contains shared pytest fixtures for unit tests across all test modules.
Fixtures provide test data, mocked dependencies, and common test setup.

Fixture Categories:
    - Path fixtures: Paths to test directories and files
    - Data fixtures: Sample .sav files and DataFrames
    - State fixtures: Workflow states for each phase
    - Artifact fixtures: Valid/invalid JSON artifacts (recoding, indicators, tables)
    - LLM response fixtures: Mock LLM responses for all scenarios
    - PSPP output fixtures: Mock PSPP execution results
    - Configuration fixtures: Various config options
    - Validation result fixtures: Validation outcomes
    - Mock fixtures: Mocked dependencies

Usage:
    Use fixtures in tests by adding them as function parameters:
        def test_my_function(sample_state, mock_llm_client):
            # test code here
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, MagicMock
import tempfile
import shutil

import pytest
import pandas as pd

# Add agent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.state import (
    WorkflowState,
    create_initial_state,
    ValidationResult,
)


# =============================================================================
# Path Fixtures
# =============================================================================

@pytest.fixture
def tests_dir() -> Path:
    """Path to the tests directory."""
    return Path(__file__).parent


@pytest.fixture
def fixtures_dir(tests_dir: Path) -> Path:
    """Path to the fixtures directory."""
    return tests_dir / "fixtures"


@pytest.fixture
def sample_sav_path(fixtures_dir: Path) -> str:
    """Path to sample .sav file (standard test data)."""
    return str(fixtures_dir / "sample_data.sav")


@pytest.fixture
def small_sav_path(fixtures_dir: Path) -> str:
    """Path to small .sav file (10 rows, for quick tests)."""
    return str(fixtures_dir / "small_data.sav")


@pytest.fixture
def large_sav_path(fixtures_dir: Path) -> str:
    """Path to large .sav file (500 rows, for performance tests)."""
    return str(fixtures_dir / "large_data.sav")


@pytest.fixture
def edge_case_sav_path(fixtures_dir: Path) -> str:
    """Path to edge case .sav file (missing values, outliers)."""
    return str(fixtures_dir / "edge_case_data.sav")


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for test runs."""
    temp_dir = tempfile.mkdtemp(prefix="pytest_output_")
    yield Path(temp_dir)
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_checkpoint_db():
    """Create temporary SQLite checkpoint database for testing."""
    import os
    fd, db_path = tempfile.mkstemp(suffix=".db", prefix="pytest_cp_")
    os.close(fd)
    yield db_path
    # Cleanup
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass


# =============================================================================
# Data File Fixtures
# =============================================================================

@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """
    Sample pandas DataFrame for testing.

    Creates a DataFrame with common survey variable types:
    - Numeric variables (age, satisfaction)
    - Categorical variables (gender, education)
    - Binary variable (employed)

    Returns:
        pandas DataFrame with 50 rows and 6 columns
    """
    import numpy as np
    np.random.seed(42)  # For reproducible tests

    data = {
        "age": np.random.randint(18, 80, 50),
        "gender": np.random.choice([1, 2, 3], 50),
        "education": np.random.choice([1, 2, 3, 4, 5], 50),
        "satisfaction": np.random.randint(1, 6, 50),
        "employed": np.random.choice([0, 1], 50),
        "income": np.random.randint(20000, 150000, 50),
    }

    return pd.DataFrame(data)


@pytest.fixture
def small_dataframe() -> pd.DataFrame:
    """
    Small DataFrame for quick tests.

    Returns:
        pandas DataFrame with 10 rows and 4 columns
    """
    import numpy as np
    np.random.seed(42)

    return pd.DataFrame({
        "age": np.random.randint(18, 65, 10),
        "gender": np.random.choice([1, 2], 10),
        "satisfaction": np.random.randint(1, 6, 10),
        "employed": np.random.choice([0, 1], 10),
    })


@pytest.fixture
def large_dataframe() -> pd.DataFrame:
    """
    Large DataFrame for performance tests.

    Returns:
        pandas DataFrame with 500 rows and 15 variables
    """
    import numpy as np
    np.random.seed(42)

    data = {}
    for i in range(1, 11):
        data[f"q{i}"] = np.random.randint(1, 6, 500)

    data.update({
        "age": np.random.randint(18, 80, 500),
        "gender": np.random.choice([1, 2, 3], 500),
        "education": np.random.choice([1, 2, 3, 4, 5], 500),
        "income": np.random.randint(20000, 200000, 500),
        "employed": np.random.choice([0, 1], 500),
    })

    return pd.DataFrame(data)


@pytest.fixture
def edge_case_dataframe() -> pd.DataFrame:
    """
    DataFrame with edge cases for testing.

    Includes:
    - Missing values (NaN, None)
    - Outliers (extreme values)
    - Mixed data types

    Returns:
        pandas DataFrame with edge cases
    """
    import numpy as np
    np.random.seed(42)

    return pd.DataFrame({
        "age": [18, 25, 35, 45, 55, 65, 75, 85, 120, None, 30, 40],
        "gender": [1, 2, 3, 1, 2, 3, 1, 2, None, 1, 2, 3],
        "income": [20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000,
                   180000, 200000, 999999, None],
        "satisfaction": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, None],
    })


# =============================================================================
# Metadata Fixtures
# =============================================================================

@pytest.fixture
def sample_metadata() -> Dict[str, Any]:
    """
    Sample SPSS metadata for testing.

    Simulates the metadata structure returned by pyreadstat after
    reading an SPSS file.

    Returns:
        Dictionary with SPSS metadata structure
    """
    return {
        "file_name": "sample_data.sav",
        "n_rows": 50,
        "n_columns": 6,
        "column_labels": {
            "age": "Respondent Age",
            "gender": "Gender",
            "education": "Education Level",
            "satisfaction": "Overall Satisfaction",
            "employed": "Employment Status",
            "income": "Annual Income",
        },
        "column_value_labels": {
            "gender": {1: "Male", 2: "Female", 3: "Other"},
            "education": {
                1: "Less than High School",
                2: "High School Graduate",
                3: "Some College",
                4: "College Degree",
                5: "Postgraduate Degree",
            },
            "satisfaction": {
                1: "Very Dissatisfied",
                2: "Dissatisfied",
                3: "Neutral",
                4: "Satisfied",
                5: "Very Satisfied",
            },
            "employed": {0: "Unemployed", 1: "Employed"},
        },
        "variable_types": {
            "age": "numeric",
            "gender": "numeric",
            "education": "numeric",
            "satisfaction": "numeric",
            "employed": "numeric",
            "income": "numeric",
        },
    }


@pytest.fixture
def variable_centered_metadata() -> Dict[str, Any]:
    """
    Sample variable-centered metadata for testing.

    Simulates the structure created by transform_metadata_node (Step 2).

    Returns:
        Dictionary with variable-centered metadata structure
    """
    return {
        "variables": {
            "age": {
                "name": "age",
                "label": "Respondent Age",
                "variable_type": "numeric",
                "min_value": 18,
                "max_value": 79,
                "value_labels": {},
                "distinct_count": 50,
            },
            "gender": {
                "name": "gender",
                "label": "Gender",
                "variable_type": "numeric",
                "min_value": 1,
                "max_value": 3,
                "value_labels": {1: "Male", 2: "Female", 3: "Other"},
                "distinct_count": 3,
            },
            "education": {
                "name": "education",
                "label": "Education Level",
                "variable_type": "numeric",
                "min_value": 1,
                "max_value": 5,
                "value_labels": {
                    1: "Less than High School",
                    2: "High School Graduate",
                    3: "Some College",
                    4: "College Degree",
                    5: "Postgraduate Degree",
                },
                "distinct_count": 5,
            },
            "satisfaction": {
                "name": "satisfaction",
                "label": "Overall Satisfaction",
                "variable_type": "numeric",
                "min_value": 1,
                "max_value": 5,
                "value_labels": {
                    1: "Very Dissatisfied",
                    2: "Dissatisfied",
                    3: "Neutral",
                    4: "Satisfied",
                    5: "Very Satisfied",
                },
                "distinct_count": 5,
            },
            "employed": {
                "name": "employed",
                "label": "Employment Status",
                "variable_type": "numeric",
                "min_value": 0,
                "max_value": 1,
                "value_labels": {0: "Unemployed", 1: "Employed"},
                "distinct_count": 2,
            },
            "income": {
                "name": "income",
                "label": "Annual Income",
                "variable_type": "numeric",
                "min_value": 20000,
                "max_value": 149000,
                "value_labels": {},
                "distinct_count": 50,
            },
        },
        "n_variables": 6,
        "n_numeric": 6,
        "n_string": 0,
        "n_date": 0,
        "total_records": 50,
    }


@pytest.fixture
def filtered_metadata() -> list:
    """
    Sample filtered metadata for testing.

    Simulates the filtered_metadata structure after filter_metadata_node (Step 3).
    Excludes binary variables (employed) and high cardinality variables (income).

    Returns:
        List of variable dicts requiring recoding
    """
    return [
        {
            "name": "gender",
            "label": "Gender",
            "variable_type": "numeric",
            "min_value": 1,
            "max_value": 3,
            "value_labels": {1: "Male", 2: "Female", 3: "Other"},
            "distinct_count": 3,
        },
        {
            "name": "education",
            "label": "Education Level",
            "variable_type": "numeric",
            "min_value": 1,
            "max_value": 5,
            "value_labels": {
                1: "Less than High School",
                2: "High School Graduate",
                3: "Some College",
                4: "College Degree",
                5: "Postgraduate Degree",
            },
            "distinct_count": 5,
        },
        {
            "name": "satisfaction",
            "label": "Overall Satisfaction",
            "variable_type": "numeric",
            "min_value": 1,
            "max_value": 5,
            "value_labels": {
                1: "Very Dissatisfied",
                2: "Dissatisfied",
                3: "Neutral",
                4: "Satisfied",
                5: "Very Satisfied",
            },
            "distinct_count": 5,
        },
    ]


@pytest.fixture
def new_metadata() -> Dict[str, Any]:
    """
    Sample new_metadata for testing (after Step 8).

    Simulates the metadata structure from new_data.sav after recoding.

    Returns:
        Dictionary with new_metadata structure
    """
    return {
        "variable_names": ["gender", "age_group", "education", "satisfaction", "employed"],
        "variable_labels": {
            "gender": "Gender",
            "age_group": "Age Group",
            "education": "Education Level",
            "satisfaction": "Overall Satisfaction",
            "employed": "Employment Status",
        },
        "value_labels": {
            "gender": {1: "Male", 2: "Female", 3: "Other"},
            "age_group": {1: "18-34", 2: "35-54", 3: "55+"},
            "education": {
                1: "Less than High School",
                2: "High School Graduate",
                3: "Some College",
                4: "College Degree",
                5: "Postgraduate Degree",
            },
            "satisfaction": {
                1: "Very Dissatisfied",
                2: "Dissatisfied",
                3: "Neutral",
                4: "Satisfied",
                5: "Very Satisfied",
            },
            "employed": {0: "Unemployed", 1: "Employed"},
        },
    }


# =============================================================================
# State Fixtures (Workflow Phases)
# =============================================================================

@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """
    Sample configuration for testing.

    Returns a minimal config with all required keys for testing.
    Override values in specific tests as needed.
    """
    from agent.config import DEFAULT_CONFIG
    config = DEFAULT_CONFIG.copy()
    # Override for faster testing
    config["max_self_correction_iterations"] = 2
    config["cardinality_threshold"] = 30
    config["enable_human_review"] = False  # Auto-approve for testing
    config["auto_approve_recoding"] = True
    config["auto_approve_indicators"] = True
    config["auto_approve_table_specs"] = True
    return config


@pytest.fixture
def minimal_config() -> Dict[str, Any]:
    """
    Minimal configuration for fast tests.

    Stripped down config with only essential settings.
    """
    from agent.config import DEFAULT_CONFIG
    config = DEFAULT_CONFIG.copy()
    config["max_self_correction_iterations"] = 1
    config["enable_human_review"] = False
    config["auto_approve_recoding"] = True
    config["auto_approve_indicators"] = True
    config["auto_approve_table_specs"] = True
    return config


@pytest.fixture
def human_review_config() -> Dict[str, Any]:
    """
    Configuration with human review enabled.

    For testing human-in-the-loop scenarios.
    """
    from agent.config import DEFAULT_CONFIG
    config = DEFAULT_CONFIG.copy()
    config["enable_human_review"] = True
    config["auto_approve_recoding"] = False
    config["auto_approve_indicators"] = False
    config["auto_approve_table_specs"] = False
    return config


@pytest.fixture
def sample_state(sample_config: Dict[str, Any]) -> WorkflowState:
    """
    Initial workflow state for testing (Step 0).

    Creates a fully initialized WorkflowState with default values.
    Modify specific fields in tests as needed.

    Args:
        sample_config: Configuration from sample_config fixture

    Returns:
        Initialized WorkflowState
    """
    state = create_initial_state("tests/fixtures/sample_data.sav", sample_config)
    return state


@pytest.fixture
def extraction_state(sample_state: WorkflowState, sample_dataframe: pd.DataFrame,
                     sample_metadata: Dict[str, Any]) -> WorkflowState:
    """
    Workflow state after Phase 1 (Steps 1-3: Extraction).

    Simulates state after Step 3 (filter_metadata_node) completes.
    """
    return {
        **sample_state,
        "current_step": 3,
        "raw_data": sample_dataframe,
        "original_metadata": sample_metadata,
        "variable_centered_metadata": None,  # Would be populated by actual transform
        "filtered_metadata": None,  # Would be populated by actual filter
        "filtered_out_variables": [],
    }


@pytest.fixture
def populated_state(sample_state: WorkflowState, sample_dataframe: pd.DataFrame,
                     sample_metadata: Dict[str, Any], variable_centered_metadata: Dict[str, Any],
                     filtered_metadata: list) -> WorkflowState:
    """
    Populated state for node tests.

    This fixture provides a state with raw data, metadata, and filtered_metadata loaded,
    suitable for testing individual nodes that require extracted and filtered data.

    Args:
        sample_state: Base state from sample_state fixture
        sample_dataframe: Sample data DataFrame
        sample_metadata: Sample SPSS metadata
        variable_centered_metadata: Variable-centered metadata
        filtered_metadata: Filtered metadata list

    Returns:
        WorkflowState with data, metadata, and filtered_metadata populated
    """
    return {
        **sample_state,
        "current_step": 3,
        "raw_data": sample_dataframe,
        "original_metadata": sample_metadata,
        "variable_centered_metadata": variable_centered_metadata,
        "filtered_metadata": filtered_metadata,
        "filtered_out_variables": [],
    }


@pytest.fixture
def recoding_state(extraction_state: WorkflowState) -> WorkflowState:
    """
    Workflow state after Phase 2 (Steps 4-8: Recoding).

    Simulates state after Step 8 completes with recoding done.
    """
    return {
        **extraction_state,
        "current_step": 8,
        "recoding_rules": {"recoding_rules": []},
        "recoding_iteration": 0,
        "recoding_approved": True,
        "new_data_path": "/tmp/new_data.sav",
        "new_metadata": {
            "variable_names": ["gender", "age_group", "education"],
            "variable_labels": {},
            "value_labels": {},
        },
    }


@pytest.fixture
def indicator_state(recoding_state: WorkflowState) -> WorkflowState:
    """
    Workflow state after Phase 3 (Steps 9-11: Indicators).

    Simulates state after Step 11 completes.
    """
    return {
        **recoding_state,
        "current_step": 11,
        "indicators": {
            "indicators": [
                {"name": "demographics", "variables": ["gender", "age_group"]},
                {"name": "satisfaction", "variables": ["education"]},
            ]
        },
        "indicators_iteration": 0,
        "indicators_approved": True,
    }


@pytest.fixture
def table_state(indicator_state: WorkflowState) -> WorkflowState:
    """
    Workflow state after Phase 4 (Steps 12-16: Tables).

    Simulates state after Step 16 completes.
    """
    return {
        **indicator_state,
        "current_step": 16,
        "table_specifications": {
            "tables": [
                {
                    "table_id": "gender_x_education",
                    "row_variable": "gender",
                    "column_variable": "education",
                    "statistics": ["count", "columnpct"],
                }
            ]
        },
        "table_specs_iteration": 0,
        "table_specs_approved": True,
        "cross_table_sav_path": "/tmp/cross_table.sav",
    }


@pytest.fixture
def statistics_state(table_state: WorkflowState) -> WorkflowState:
    """
    Workflow state after Phase 5 (Steps 17-18: Statistics).

    Simulates state after Step 18 completes.
    """
    return {
        **table_state,
        "current_step": 18,
        "statistical_summary": [
            {
                "table_name": "gender_x_education",
                "chi_square": 15.3,
                "p_value": 0.002,
                "degrees_of_freedom": 4,
                "cramers_v": 0.45,
                "interpretation": "small",
                "is_significant": True,
            }
        ],
    }


@pytest.fixture
def filtering_state(statistics_state: WorkflowState) -> WorkflowState:
    """
    Workflow state after Phase 6 (Steps 19-20: Filtering).

    Simulates state after Step 20 completes.
    """
    return {
        **statistics_state,
        "current_step": 20,
        "filter_list": [
            {"table_id": "gender_x_education", "include": True, "passes_significance": True}
        ],
        "significant_tables": [
            {
                "table_name": "gender_x_education",
                "chi_square": 15.3,
                "p_value": 0.002,
                "is_significant": True,
            }
        ],
    }


@pytest.fixture
def presentation_state(filtering_state: WorkflowState) -> WorkflowState:
    """
    Workflow state after Phases 7-8 (Steps 21-22: Presentation).

    Simulates state after Step 22 completes.
    """
    return {
        **filtering_state,
        "current_step": 22,
        "powerpoint_path": "/tmp/presentation.pptx",
        "html_dashboard_path": "/tmp/dashboard.html",
    }


@pytest.fixture
def state_with_errors(sample_state: WorkflowState) -> WorkflowState:
    """
    Workflow state with errors for testing error handling.

    Returns:
        State with accumulated errors
    """
    return {
        **sample_state,
        "errors": ["Error 1: File not found", "Error 2: Invalid format"],
        "warnings": ["Warning: Low data quality"],
    }


@pytest.fixture
def state_at_max_iterations(sample_state: WorkflowState) -> WorkflowState:
    """
    Workflow state at maximum self-correction iterations.

    For testing max iteration behavior.
    """
    return {
        **sample_state,
        "current_step": 4,
        "recoding_iteration": 3,
        "recoding_validation": ValidationResult(
            is_valid=False,
            errors=["Still invalid"],
            warnings=[],
            checks_performed=[],
        ),
    }


# =============================================================================
# Artifact Fixtures (Recoding Rules, Indicators, Table Specs)
# =============================================================================

@pytest.fixture
def valid_recoding_rules() -> Dict[str, Any]:
    """
    Valid recoding rules for testing.

    Includes proper range grouping for age and income.
    """
    return {
        "recoding_rules": [
            {
                "source_variable": "age",
                "target_variable": "age_group",
                "transformation_type": "range_grouping",
                "rules": [
                    {"source_min": 18, "source_max": 34, "target_value": 1, "target_label": "18-34"},
                    {"source_min": 35, "source_max": 54, "target_value": 2, "target_label": "35-54"},
                    {"source_min": 55, "source_max": 100, "target_value": 3, "target_label": "55+"},
                ],
                "description": "Group age into meaningful ranges",
            },
            {
                "source_variable": "income",
                "target_variable": "income_group",
                "transformation_type": "range_grouping",
                "rules": [
                    {"source_min": 0, "source_max": 40000, "target_value": 1, "target_label": "Low"},
                    {"source_min": 40001, "source_max": 80000, "target_value": 2, "target_label": "Medium"},
                    {"source_min": 80001, "source_max": 999999, "target_value": 3, "target_label": "High"},
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
                "source_variable": "nonexistent_var",  # Doesn't exist
                "target_variable": "target1",
                "transformation_type": "range_grouping",
                "rules": [
                    {"source_min": 30, "source_max": 20, "target_value": 1, "target_label": "Invalid"},  # min > max
                    {"source_min": 25, "source_max": 35, "target_value": 1, "target_label": "Dup"},  # Duplicate target
                ],
                "description": "Invalid rule example",
            },
        ]
    }


@pytest.fixture
def valid_indicators() -> Dict[str, Any]:
    """
    Valid indicators for testing.

    Includes properly structured indicators with multiple variables.
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
                "variables": ["gender", "age_group", "education"],
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

    Includes properly structured cross-table definitions.
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
def significant_tables_data() -> Dict[str, Any]:
    """
    Sample significant tables data for testing.

    Simulates the structure of significant_tables.json output.
    """
    return {
        "tables": [
            {
                "name": "gender_x_satisfaction",
                "rows": "gender",
                "columns": "satisfaction",
                "data": {
                    "row_labels": ["Male", "Female"],
                    "column_labels": ["Very Dissatisfied", "Neutral", "Very Satisfied"],
                    "counts": [[5, 10, 15], [8, 12, 10]],
                    "row_percentages": [[16.7, 33.3, 50.0], [26.7, 40.0, 33.3]],
                    "column_percentages": [[38.5, 45.5, 60.0], [61.5, 54.5, 40.0]],
                },
                "statistics": {
                    "chi_square": 2.45,
                    "p_value": 0.29,
                    "degrees_of_freedom": 2,
                    "cramers_v": 0.12,
                    "interpretation": "negligible",
                },
                "sample_size": 60,
            }
        ]
    }


@pytest.fixture
def statistical_summary_data() -> list:
    """
    Sample statistical summary data for testing.

    Simulates the structure of statistical_analysis_summary.json output.
    """
    return [
        {
            "table_name": "gender_x_satisfaction",
            "chi_square": 15.3,
            "p_value": 0.002,
            "degrees_of_freedom": 4,
            "cramers_v": 0.45,
            "interpretation": "medium",
            "sample_size": 150,
            "is_significant": True,
        },
        {
            "table_name": "age_x_education",
            "chi_square": 8.2,
            "p_value": 0.08,
            "degrees_of_freedom": 6,
            "cramers_v": 0.15,
            "interpretation": "small",
            "sample_size": 150,
            "is_significant": False,
        },
    ]


# =============================================================================
# LLM Response Fixtures
# =============================================================================

@pytest.fixture
def mock_llm_client() -> Mock:
    """
    Mock LLM client for testing LLM-dependent nodes.

    Provides a mock client that returns valid JSON responses.
    Override return_value in specific tests as needed.

    Returns:
        Mock object configured for LLM client usage
    """
    client = Mock()

    # Default: return a valid JSON response with empty recoding rules
    mock_response = Mock()
    mock_response.content = '{"recoding_rules": []}'
    client.invoke.return_value = mock_response

    return client


@pytest.fixture
def valid_recoding_llm_response() -> str:
    """
    Valid LLM response for recoding rules generation.

    Returns:
        JSON string with valid recoding rules
    """
    return '{"recoding_rules": [{"source_variable": "age", "target_variable": "age_group", "transformation_type": "range_grouping", "rules": [{"source_min": 18, "source_max": 34, "target_value": 1, "target_label": "18-34"}]}]}'


@pytest.fixture
def valid_indicators_llm_response() -> str:
    """
    Valid LLM response for indicators generation.

    Returns:
        JSON string with valid indicators
    """
    return '{"indicators": [{"indicator_name": "Demographics", "description": "Demographic profile", "variables": ["gender", "age_group"]}]}'


@pytest.fixture
def valid_table_specs_llm_response() -> str:
    """
    Valid LLM response for table specifications generation.

    Returns:
        JSON string with valid table specifications
    """
    return '{"tables": [{"table_id": "gender_x_satisfaction", "row_variable": "gender", "column_variable": "satisfaction", "statistics": ["count", "columnpct"]}]}'


@pytest.fixture
def invalid_json_llm_response() -> str:
    """
    Invalid JSON LLM response for testing error handling.

    Returns:
        Malformed JSON string
    """
    return 'This is not valid JSON at all'


@pytest.fixture
def empty_llm_response() -> str:
    """
    Empty LLM response for testing error handling.

    Returns:
        Empty string
    """
    return ''


@pytest.fixture
def error_llm_response() -> str:
    """
    Error LLM response for testing error handling.

    Returns:
        JSON with error message
    """
    return '{"error": "LLM API error occurred", "message": "Rate limit exceeded"}'


# =============================================================================
# PSPP Output Fixtures
# =============================================================================

@pytest.fixture
def mock_pspp_wrapper() -> Mock:
    """
    Mock PSPP wrapper for testing PSPP-dependent nodes.

    Provides a mock wrapper that simulates successful PSPP execution.
    Override in specific tests as needed.

    Returns:
        Mock object configured for PSPP wrapper usage
    """
    wrapper = Mock()

    # Default: simulate successful execution
    wrapper.run_pspp.return_value = {
        "exit_code": 0,
        "stdout": "PSPP executed successfully",
        "stderr": "",
        "output_file": "/tmp/output.sav",
    }

    return wrapper


@pytest.fixture
def sample_pspp_recoding_syntax() -> str:
    """
    Sample PSPP recoding syntax for testing.

    Returns:
        String with valid PSPP RECODE commands
    """
    return """* Recoding generated by AI Survey Analysis System.
* Generated at: 2024-01-01 12:00:00

RECODE age (18 THRU 34 = 1) (35 THRU 54 = 2) (55 THRU HI = 3) INTO age_group.
VARIABLE LABELS age_group 'Age Group'.
VALUE LABELS age_group 1 '18-34' 2 '35-54' 3 '55+'.

EXECUTE.
"""


@pytest.fixture
def sample_pspp_table_syntax() -> str:
    """
    Sample PSPP cross-table syntax for testing.

    Returns:
        String with valid PSPP CTABLES commands
    """
    return """* Cross-tables generated by AI Survey Analysis System.
* Generated at: 2024-01-01 12:00:00

CTABLES
  /TABLE gender BY satisfaction
  /STATISTICS CHISQ CRAMERSV.

EXECUTE.
"""


@pytest.fixture
def sample_pspp_output() -> Dict[str, Any]:
    """
    Sample PSPP execution output for testing.

    Returns:
        Dictionary with stdout, stderr, exit code
    """
    return {
        "exit_code": 0,
        "stdout": "PSPP execution successful\nOutput written to /tmp/output.sav",
        "stderr": "",
        "output_file": "/tmp/output.sav",
    }


@pytest.fixture
def sample_pspp_error() -> Dict[str, Any]:
    """
    Sample PSPP error output for testing.

    Returns:
        Dictionary with error information
    """
    return {
        "exit_code": 1,
        "stdout": "",
        "stderr": "error: syntax error at line 15",
        "output_file": None,
    }


# =============================================================================
# Validation Result Fixtures
# =============================================================================

@pytest.fixture
def valid_validation_result() -> ValidationResult:
    """
    Valid ValidationResult with no errors.

    Returns:
        ValidationResult with is_valid=True
    """
    return ValidationResult(
        is_valid=True,
        errors=[],
        warnings=["Minor warning about data quality"],
        checks_performed=["structure_check", "syntax_check", "logic_check"],
    )


@pytest.fixture
def invalid_validation_result() -> ValidationResult:
    """
    Invalid ValidationResult with errors.

    Returns:
        ValidationResult with is_valid=False
    """
    return ValidationResult(
        is_valid=False,
        errors=["Syntax error on line 15", "Undefined variable 'x'"],
        warnings=["Missing value labels for variable y"],
        checks_performed=["structure_check", "syntax_check", "logic_check"],
    )


@pytest.fixture
def validation_result_warnings_only() -> ValidationResult:
    """
    ValidationResult with warnings but valid.

    Returns:
        ValidationResult with is_valid=True but with warnings
    """
    return ValidationResult(
        is_valid=True,
        errors=[],
        warnings=[
            "Variable 'age' has high cardinality (50 distinct values)",
            "Some missing values detected",
        ],
        checks_performed=["structure_check", "syntax_check"],
    )


@pytest.fixture
def validation_result_at_max_iterations() -> ValidationResult:
    """
    ValidationResult at maximum self-correction iterations.

    For testing max iteration behavior.

    Returns:
        ValidationResult indicating max iterations reached
    """
    return ValidationResult(
        is_valid=False,
        errors=["Maximum self-correction iterations reached without resolving validation errors"],
        warnings=["Consider manual review"],
        checks_performed=["structure_check", "syntax_check"],
    )


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_read_spss_file(sample_dataframe: pd.DataFrame, sample_metadata: Dict[str, Any]) -> Mock:
    """
    Mock read_spss_file function for testing.

    Simulates successful SPSS file reading without requiring actual .sav files.

    Returns:
        Mock object that returns sample dataframe and metadata
    """
    mock_func = Mock()
    mock_metadata_obj = Mock()
    mock_metadata_obj.column_labels = sample_metadata.get("column_labels", {})
    mock_metadata_obj.variable_value_labels = sample_metadata.get("column_value_labels", {})
    mock_metadata_obj.variable_storage_types = sample_metadata.get("variable_types", {})
    mock_func.return_value = (sample_dataframe, mock_metadata_obj)

    return mock_func


@pytest.fixture
def mock_dependencies(sample_dataframe: pd.DataFrame, sample_metadata: Dict[str, Any]):
    """
    Mock all external dependencies for E2E testing.

    This context manager patches:
    - pyreadstat.read_sav (for SPSS file reading)

    Yields:
        Context manager for mocking dependencies
    """
    from unittest.mock import patch

    with patch('agent.utils.file_io.read_spss_file') as mock_read:
        mock_metadata_obj = Mock()
        mock_metadata_obj.column_labels = sample_metadata.get("column_labels", {})
        mock_metadata_obj.variable_value_labels = sample_metadata.get("column_value_labels", {})
        mock_metadata_obj.variable_storage_types = sample_metadata.get("variable_types", {})
        mock_read.return_value = (sample_dataframe, mock_metadata_obj)

        yield


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, may require external resources)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (take > 1 second)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end workflow tests"
    )
    config.addinivalue_line(
        "markers", "llm: Tests requiring LLM API"
    )
    config.addinivalue_line(
        "markers", "pspp: Tests requiring PSPP installation"
    )
    # Error recovery test markers
    config.addinivalue_line(
        "markers", "error_recovery: Tests for error handling and recovery scenarios"
    )
    config.addinivalue_line(
        "markers", "llm_errors: Tests for LLM API error handling"
    )
    config.addinivalue_line(
        "markers", "pspp_errors: Tests for PSPP execution error handling"
    )
    config.addinivalue_line(
        "markers", "validation_errors: Tests for validation loop error scenarios"
    )
    config.addinivalue_line(
        "markers", "fileio_errors: Tests for file I/O error handling"
    )
    config.addinivalue_line(
        "markers", "state_corruption: Tests for state corruption scenarios"
    )
    config.addinivalue_line(
        "markers", "partial_recovery: Tests for partial recovery and resumption"
    )
    config.addinivalue_line(
        "markers", "error_reporting: Tests for error reporting and logging"
    )
    config.addinivalue_line(
        "markers", "comprehensive: Comprehensive verification tests"
    )


# =============================================================================
# Additional State Fixtures for Edge Cases
# =============================================================================

@pytest.fixture
def state_with_iteration_error(sample_state: WorkflowState) -> WorkflowState:
    """
    Workflow state with iteration limit error for testing retry logic.

    Returns:
        State at maximum iterations with validation errors
    """
    return {
        **sample_state,
        "current_step": 4,
        "iteration_count": 3,
        "recoding_validation_result": ValidationResult(
            is_valid=False,
            errors=["Validation failed after 3 attempts"],
            warnings=[],
            checks_performed=["structure_check", "syntax_check"],
        ),
    }


@pytest.fixture
def state_at_step_4(sample_state: WorkflowState) -> WorkflowState:
    """
    Workflow state at Step 4 (Recoding Rules Generation).

    Returns:
        State ready for Step 4 execution
    """
    return {
        **sample_state,
        "current_step": 4,
        "raw_data": sample_dataframe(),
        "variable_centered_metadata": variable_centered_metadata(),
        "filtered_metadata": filtered_metadata(),
    }


@pytest.fixture
def state_at_step_9(sample_state: WorkflowState) -> WorkflowState:
    """
    Workflow state at Step 9 (Indicator Generation).

    Returns:
        State ready for Step 9 execution
    """
    return {
        **sample_state,
        "current_step": 9,
        "new_metadata": new_metadata(),
        "new_data_file": "/tmp/new_data.sav",
    }


@pytest.fixture
def state_at_step_12(sample_state: WorkflowState) -> WorkflowState:
    """
    Workflow state at Step 12 (Table Specifications).

    Returns:
        State ready for Step 12 execution
    """
    return {
        **sample_state,
        "current_step": 12,
        "indicators": valid_indicators(),
        "indicators_approved": True,
    }


# =============================================================================
# Complete Workflow State Fixtures
# =============================================================================

@pytest.fixture
def complete_workflow_state() -> WorkflowState:
    """
    Complete workflow state with all fields populated.

    Returns a state object with all sub-states fully populated,
    useful for testing state serialization and summary functions.
    """
    return WorkflowState(
        # InputState
        input_file_path="tests/fixtures/sample_data.sav",
        original_metadata=sample_metadata(),

        # ExtractionState
        raw_data=sample_dataframe(),
        variable_centered_metadata=variable_centered_metadata(),
        filtered_metadata=filtered_metadata(),
        filtered_out_variables=[],

        # RecodingState
        recoding_rules=valid_recoding_rules(),
        recoding_validation_result=valid_validation_result(),
        recoding_approved=True,
        recoding_feedback=None,
        new_metadata=new_metadata(),
        new_data_file="/tmp/new_data.sav",

        # IndicatorState
        indicators=valid_indicators(),
        indicator_validation_result=valid_validation_result(),
        indicators_approved=True,
        indicator_feedback=None,

        # CrossTableState
        table_specifications=valid_table_specs(),
        table_validation_result=valid_validation_result(),
        table_specs_approved=True,
        table_specs_feedback=None,
        table_syntax_file="/tmp/tables.sps",
        cross_table_file="/tmp/cross_tables.sav",

        # StatisticalAnalysisState
        statistics_script="/tmp/stats_script.py",
        statistical_summary=statistical_summary_data(),

        # FilteringState
        filter_list=significant_tables_data(),
        filtered_tables=significant_tables_data(),
        total_tables_evaluated=5,
        significant_tables_count=3,
        filtering_valid=True,

        # PresentationState
        powerpoint_file="/tmp/presentation.pptx",
        html_dashboard_file="/tmp/dashboard.html",

        # ApprovalState
        current_step=22,
        requires_human_review=False,
        iteration_count=0,

        # TrackingState
        errors=[],
        warnings=[],
    )


@pytest.fixture
def state_with_all_phases_populated() -> WorkflowState:
    """
    State with all phases populated but not completed.

    Useful for testing partial state scenarios.
    """
    return {
        "input_file_path": "tests/fixtures/sample_data.sav",
        "original_metadata": sample_metadata(),
        "raw_data": sample_dataframe(),
        "variable_centered_metadata": variable_centered_metadata(),
        "filtered_metadata": filtered_metadata(),
        "filtered_out_variables": [],
        "recoding_rules": valid_recoding_rules(),
        "recoding_validation_result": None,  # Not yet validated
        "recoding_approved": False,
        "recoding_feedback": None,
        "new_metadata": None,  # Not yet created
        "new_data_file": None,
        "indicators": None,  # Not yet generated
        "indicator_validation_result": None,
        "indicators_approved": False,
        "indicator_feedback": None,
        "table_specifications": None,  # Not yet generated
        "table_validation_result": None,
        "table_specs_approved": False,
        "table_specs_feedback": None,
        "table_syntax_file": None,
        "cross_table_file": None,
        "statistics_script": None,
        "statistical_summary": None,
        "filter_list": None,
        "filtered_tables": None,
        "total_tables_evaluated": 0,
        "significant_tables_count": 0,
        "filtering_valid": False,
        "powerpoint_file": None,
        "html_dashboard_file": None,
        "current_step": 5,
        "requires_human_review": False,
        "iteration_count": 1,
        "errors": [],
        "warnings": ["Validation pending"],
    }


# =============================================================================
# Helper function fixtures for creating test data
# =============================================================================

@pytest.fixture
def make_temp_file():
    """
    Factory fixture to create temporary files.

    Yields a function that creates temp files with given content.

    Example:
        def test_something(make_temp_file):
            temp_path = make_temp_file("test content", ".txt")
    """
    created_files = []

    def _make_temp_file(content: str, suffix: str = ".tmp") -> str:
        fd, path = tempfile.mkstemp(suffix=suffix, prefix="pytest_")
        os.close(fd)
        with open(path, 'w') as f:
            f.write(content)
        created_files.append(path)
        return path

    yield _make_temp_file

    # Cleanup
    for path in created_files:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass


@pytest.fixture
def make_temp_sav_file(temp_output_dir: Path):
    """
    Factory fixture to create temporary .sav files.

    Yields a function that creates minimal .sav files for testing.

    Example:
        def test_something(make_temp_sav_file):
            sav_path = make_temp_sav_file(dataframe)
    """
    def _make_temp_sav_file(df: pd.DataFrame, name: str = "test") -> str:
        path = str(temp_output_dir / f"{name}.sav")
        try:
            import pyreadstat
            pyreadstat.write_sav(df, path)
        except ImportError:
            # If pyreadstat not available, create a dummy file
            with open(path, 'wb') as f:
                f.write(b"dummy sav file")
        return path

    return _make_temp_sav_file


@pytest.fixture
def sample_state_transitions():
    """
    Sample state transitions for testing workflow progression.

    Returns a list of (step, state) tuples showing how state evolves.
    """
    return [
        (0, create_initial_state("tests/fixtures/sample_data.sav")),
        (3, {**create_initial_state("tests/fixtures/sample_data.sav"),
              "current_step": 3, "raw_data": sample_dataframe()}),
        (8, {**create_initial_state("tests/fixtures/sample_data.sav"),
              "current_step": 8, "new_data_file": "/tmp/new.sav"}),
        (11, {**create_initial_state("tests/fixtures/sample_data.sav"),
               "current_step": 11, "indicators": valid_indicators()}),
        (16, {**create_initial_state("tests/fixtures/sample_data.sav"),
               "current_step": 16, "cross_table_file": "/tmp/ct.sav"}),
        (22, {**create_initial_state("tests/fixtures/sample_data.sav"),
               "current_step": 22, "powerpoint_file": "/tmp/out.pptx"}),
    ]
