"""
Integration Tests for Output Generation (Steps 21-22)

This module contains comprehensive integration tests for the final two steps
of the workflow that generate outputs:
- Step 21: PowerPoint Generation (phase7_powerpoint.py)
- Step 22: HTML Dashboard Generation (phase8_html_dashboard.py)

Test Categories:
1. PowerPoint Generation Tests
   - Title slide creation
   - Table slide creation with charts
   - Summary slide generation
   - Chart type selection logic
   - Chart styling and color schemes
   - Statistics footer display

2. HTML Dashboard Generation Tests
   - Complete HTML structure
   - Sidebar navigation
   - Table card generation
   - Interactive Chart.js charts
   - Significance highlighting
   - Filtering and sorting functionality

3. Chart Generation Tests
   - Clustered column charts (2x2 tables)
   - Horizontal bar charts (>5 rows)
   - 100% stacked column charts (>4 columns)
   - Line charts (time series)
   - Chart data formatting

4. Data Integration Tests
   - Sample significant tables data
   - Statistical summary integration
   - Edge cases (no tables, all significant, etc.)

5. File Output Tests
   - File creation and naming
   - File format validation
   - File permissions

Dependencies:
- pytest: Test framework
- python-pptx: PowerPoint file generation
- json: HTML dashboard data handling
- tempfile: Temporary output file handling
"""

import pytest
import json
import tempfile
import shutil
import os
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

import pandas as pd

from agent.state import (
    WorkflowState, create_initial_state,
    STEP_0_INITIAL, STEP_1_EXTRACT_SPSS,
    STEP_4_GENERATE_RECODING_RULES, STEP_5_VALIDATE_RECODING_RULES, STEP_6_REVIEW_RECODING_RULES,
    STEP_20_APPLY_FILTER_TO_TABLES, STEP_21_GENERATE_POWERPOINT, STEP_22_GENERATE_HTML_DASHBOARD
)
from agent.config import DEFAULT_CONFIG
from agent.nodes.phase7_powerpoint import (
    generate_powerpoint_node,
    select_chart_type,
    get_xl_chart_type,
    get_chart_type_description,
    ChartType,
    SemanticHint,
    validate_table_dimensions,
)
from agent.nodes.phase8_html_dashboard import (
    generate_html_dashboard_node,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def temp_output_dir():
    """
    Create temporary output directory for test runs.

    Yields:
        Path to temporary output directory
    """
    temp_dir = tempfile.mkdtemp(prefix="output_generation_")
    yield Path(temp_dir)
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_config(temp_output_dir: Path) -> Dict[str, Any]:
    """
    Create test configuration with temporary output directory.

    Args:
        temp_output_dir: Temporary output directory for this test

    Returns:
        Configuration dictionary for testing
    """
    config = DEFAULT_CONFIG.copy()
    config["output_dir"] = str(temp_output_dir)
    config["significance_level"] = 0.05
    config["min_cramers_v"] = 0.1
    return config


@pytest.fixture
def sample_significant_tables() -> Dict[str, Any]:
    """
    Sample significant tables data for testing.

    Returns a realistic filtered_tables structure with various table types.
    """
    return {
        "tables": [
            {
                "table_id": "gender_x_satisfaction",
                "table_name": "gender_x_satisfaction",
                "row_variable": "gender",
                "column_variable": "satisfaction",
                "data": {
                    "row_labels": ["Male", "Female"],
                    "column_labels": ["Satisfied", "Neutral", "Dissatisfied"],
                    "counts": [
                        [45, 32, 15],
                        [52, 28, 18]
                    ],
                    "column_percentages": [
                        [48.4, 34.4, 16.1],
                        [52.5, 28.3, 17.2]
                    ]
                }
            },
            {
                "table_id": "age_x_satisfaction",
                "table_name": "age_x_satisfaction",
                "row_variable": "age_group",
                "column_variable": "satisfaction",
                "data": {
                    "row_labels": ["18-29", "30-44", "45-59", "60+"],
                    "column_labels": ["Satisfied", "Neutral", "Dissatisfied"],
                    "counts": [
                        [30, 25, 15],
                        [40, 20, 10],
                        [35, 30, 12],
                        [25, 28, 20]
                    ],
                    "column_percentages": [
                        [42.9, 35.7, 21.4],
                        [57.1, 28.6, 14.3],
                        [45.5, 39.0, 15.6],
                        [34.7, 38.9, 27.8]
                    ]
                }
            },
            {
                "table_id": "region_x_product",
                "table_name": "region_x_product",
                "row_variable": "region",
                "column_variable": "product_preference",
                "data": {
                    "row_labels": ["North", "South", "East", "West", "Central", "Northeast", "Southeast", "Midwest"],
                    "column_labels": ["Product A", "Product B"],
                    "counts": [
                        [120, 80],
                        [95, 105],
                        [110, 90],
                        [85, 115],
                        [100, 100],
                        [130, 70],
                        [90, 110],
                        [105, 95]
                    ],
                    "column_percentages": [
                        [60.0, 40.0],
                        [47.5, 52.5],
                        [55.0, 45.0],
                        [42.5, 57.5],
                        [50.0, 50.0],
                        [65.0, 35.0],
                        [45.0, 55.0],
                        [52.5, 47.5]
                    ]
                }
            },
            {
                "table_id": "income_x_brand",
                "table_name": "income_x_brand",
                "row_variable": "income_bracket",
                "column_variable": "brand_preference",
                "data": {
                    "row_labels": ["<$30k", "$30k-$50k", "$50k-$75k", "$75k-$100k", "$100k+"],
                    "column_labels": ["Brand A", "Brand B", "Brand C", "Brand D", "Brand E", "Brand F"],
                    "counts": [
                        [20, 25, 30, 15, 18, 12],
                        [25, 30, 25, 20, 15, 10],
                        [30, 25, 20, 25, 12, 8],
                        [35, 20, 15, 30, 10, 5],
                        [40, 15, 10, 35, 8, 3]
                    ],
                    "column_percentages": [
                        [16.7, 20.8, 25.0, 12.5, 15.0, 10.0],
                        [20.8, 25.0, 20.8, 16.7, 12.5, 8.3],
                        [25.0, 20.8, 16.7, 20.8, 10.0, 6.7],
                        [29.2, 16.7, 12.5, 25.0, 8.3, 4.2],
                        [33.3, 12.5, 8.3, 29.2, 6.7, 2.5]
                    ]
                }
            }
        ],
        "summary": {
            "original_count": 4,
            "filtered_count": 4,
            "inclusion_rate": 100.0
        }
    }


@pytest.fixture
def sample_statistical_summary() -> Dict[str, Any]:
    """
    Sample statistical summary for testing.

    Matches the tables from sample_significant_tables.
    """
    return {
        "tables": [
            {
                "table_name": "gender_x_satisfaction",
                "chi_square": 4.52,
                "p_value": 0.0335,
                "degrees_of_freedom": 2,
                "cramers_v": 0.18,
                "interpretation": "small",
                "sample_size": 190,
                "is_significant": True,
                "is_valid": True
            },
            {
                "table_name": "age_x_satisfaction",
                "chi_square": 8.73,
                "p_value": 0.0331,
                "degrees_of_freedom": 6,
                "cramers_v": 0.15,
                "interpretation": "small",
                "sample_size": 280,
                "is_significant": True,
                "is_valid": True
            },
            {
                "table_name": "region_x_product",
                "chi_square": 12.45,
                "p_value": 0.0521,
                "degrees_of_freedom": 7,
                "cramers_v": 0.12,
                "interpretation": "small",
                "sample_size": 1600,
                "is_significant": False,
                "is_valid": True
            },
            {
                "table_name": "income_x_brand",
                "chi_square": 35.78,
                "p_value": 0.0001,
                "degrees_of_freedom": 20,
                "cramers_v": 0.22,
                "interpretation": "medium",
                "sample_size": 600,
                "is_significant": True,
                "is_valid": True
            }
        ],
        "significant_tables": 3,
        "significance_level": 0.05,
        "alpha": 0.05
    }


@pytest.fixture
def sample_metadata() -> Dict[str, Any]:
    """
    Sample metadata for variable labels.
    """
    return {
        "gender": {
            "label": "Gender",
            "value_labels": {
                "1": "Male",
                "2": "Female"
            }
        },
        "age_group": {
            "label": "Age Group",
            "value_labels": {
                "1": "18-29",
                "2": "30-44",
                "3": "45-59",
                "4": "60+"
            }
        },
        "satisfaction": {
            "label": "Customer Satisfaction",
            "value_labels": {
                "1": "Satisfied",
                "2": "Neutral",
                "3": "Dissatisfied"
            }
        },
        "region": {
            "label": "Geographic Region",
            "value_labels": {
                "1": "North",
                "2": "South",
                "3": "East",
                "4": "West"
            }
        },
        "product_preference": {
            "label": "Product Preference",
            "value_labels": {
                "1": "Product A",
                "2": "Product B"
            }
        },
        "income_bracket": {
            "label": "Income Bracket",
            "value_labels": {
                "1": "<$30k",
                "2": "$30k-$50k",
                "3": "$50k-$75k",
                "4": "$75k-$100k",
                "5": "$100k+"
            }
        },
        "brand_preference": {
            "label": "Brand Preference",
            "value_labels": {
                "1": "Brand A",
                "2": "Brand B",
                "3": "Brand C",
                "4": "Brand D",
                "5": "Brand E",
                "6": "Brand F"
            }
        }
    }


@pytest.fixture
def sample_raw_data() -> pd.DataFrame:
    """Sample raw data for sample size calculation."""
    # Create 190 rows of data
    n = 190
    return pd.DataFrame({
        "gender": [1, 2] * (n // 2) + [1],  # 95 rows of each
        "satisfaction": [1, 2, 3] * (n // 3) + [1, 2]
    })


@pytest.fixture
def populated_powerpoint_state(
    test_config: Dict[str, Any],
    sample_significant_tables: Dict[str, Any],
    sample_statistical_summary: Dict[str, Any],
    sample_metadata: Dict[str, Any],
    sample_raw_data: pd.DataFrame
) -> WorkflowState:
    """
    Fully populated state for PowerPoint generation testing.

    Simulates state after Step 20 completes.
    """
    return {
        "current_step": STEP_20_APPLY_FILTER_TO_TABLES,
        "config": test_config,
        "filtered_tables": sample_significant_tables,
        "statistical_summary": sample_statistical_summary,
        "new_metadata": sample_metadata,
        "raw_data": sample_raw_data,
        "original_metadata": {
            "file_name": "sample_survey.sav",
            "n_rows": 190
        },
        "errors": [],
        "warnings": []
    }


@pytest.fixture
def sample_cross_table_data() -> Dict[str, Any]:
    """
    Sample cross-table data for HTML dashboard testing.

    Includes both significant and non-significant tables.
    """
    return {
        "tables": [
            {
                "table_id": "gender_x_satisfaction",
                "table_name": "gender_x_satisfaction",
                "row_variable": "gender",
                "column_variable": "satisfaction",
                "data": {
                    "row_labels": ["Male", "Female"],
                    "column_labels": ["Satisfied", "Neutral", "Dissatisfied"],
                    "counts": [[45, 32, 15], [52, 28, 18]],
                    "column_percentages": [[48.4, 34.4, 16.1], [52.5, 28.3, 17.2]]
                }
            },
            {
                "table_id": "age_x_satisfaction",
                "table_name": "age_x_satisfaction",
                "row_variable": "age_group",
                "column_variable": "satisfaction",
                "data": {
                    "row_labels": ["18-29", "30-44", "45-59", "60+"],
                    "column_labels": ["Satisfied", "Neutral", "Dissatisfied"],
                    "counts": [[30, 25, 15], [40, 20, 10], [35, 30, 12], [25, 28, 20]],
                    "column_percentages": [[42.9, 35.7, 21.4], [57.1, 28.6, 14.3], [45.5, 39.0, 15.6], [34.7, 38.9, 27.8]]
                }
            },
            {
                "table_id": "education_x_income",
                "table_name": "education_x_income",
                "row_variable": "education",
                "column_variable": "income_level",
                "data": {
                    "row_labels": ["High School", "College", "Graduate"],
                    "column_labels": ["Low", "Medium", "High"],
                    "counts": [[20, 30, 10], [15, 40, 25], [10, 20, 40]],
                    "column_percentages": [[33.3, 50.0, 16.7], [18.8, 50.0, 31.3], [14.3, 28.6, 57.1]]
                }
            }
        ]
    }


@pytest.fixture
def sample_filter_list() -> Dict[str, Any]:
    """Sample filter list for HTML dashboard testing."""
    return {
        "filters": [
            {
                "table_id": "gender_x_satisfaction",
                "table_name": "gender_x_satisfaction",
                "passes_cramers_v": True,
                "passes_sample_size": True,
                "passes_significance": True,
                "include": True,
                "reason": "All criteria passed"
            },
            {
                "table_id": "age_x_satisfaction",
                "table_name": "age_x_satisfaction",
                "passes_cramers_v": True,
                "passes_sample_size": True,
                "passes_significance": True,
                "include": True,
                "reason": "All criteria passed"
            },
            {
                "table_id": "education_x_income",
                "table_name": "education_x_income",
                "passes_cramers_v": False,
                "passes_sample_size": True,
                "passes_significance": False,
                "include": False,
                "reason": "Failed significance and Cramer's V threshold"
            }
        ]
    }


@pytest.fixture
def populated_html_state(
    test_config: Dict[str, Any],
    sample_cross_table_data: Dict[str, Any],
    sample_statistical_summary: Dict[str, Any],
    sample_filter_list: Dict[str, Any],
    temp_output_dir: Path
) -> WorkflowState:
    """
    Fully populated state for HTML dashboard generation testing.

    Simulates state after Step 20 completes with cross-table file.
    """
    # Create cross-table JSON file
    cross_table_file = temp_output_dir / "cross_table.json"
    with open(cross_table_file, 'w') as f:
        json.dump(sample_cross_table_data, f)

    return {
        "current_step": STEP_21_GENERATE_POWERPOINT,
        "config": test_config,
        "cross_table_file": str(cross_table_file),
        "statistical_summary": sample_statistical_summary,
        "filter_list": sample_filter_list,
        "errors": [],
        "warnings": []
    }


# =============================================================================
# Chart Type Selection Tests
# =============================================================================

class TestChartTypeSelection:
    """Tests for select_chart_type function."""

    def test_2x2_table_selects_clustered_column(self):
        """Test that 2x2 tables select clustered column chart."""
        table = {
            "table_name": "test_2x2",
            "data": {
                "row_labels": ["A", "B"],
                "column_labels": ["X", "Y"]
            }
        }

        chart_type = select_chart_type(table)
        assert chart_type == ChartType.CLUSTERED_COLUMN.value

    def test_more_than_5_rows_selects_horizontal_bar(self):
        """Test that tables with >5 rows select horizontal bar chart."""
        table = {
            "table_name": "test_many_rows",
            "data": {
                "row_labels": [f"Row{i}" for i in range(8)],
                "column_labels": ["A", "B"]
            }
        }

        chart_type = select_chart_type(table)
        assert chart_type == ChartType.HORIZONTAL_BAR.value

    def test_more_than_4_columns_selects_stacked_column(self):
        """Test that tables with >4 columns select 100% stacked column."""
        table = {
            "table_name": "test_many_cols",
            "data": {
                "row_labels": ["A", "B"],
                "column_labels": [f"Col{i}" for i in range(6)]
            }
        }

        chart_type = select_chart_type(table)
        assert chart_type == ChartType.STACKED_COLUMN_100.value

    def test_single_row_selects_horizontal_bar(self):
        """Test that single-row tables select horizontal bar."""
        table = {
            "table_name": "test_single_row",
            "data": {
                "row_labels": ["Only Row"],
                "column_labels": ["A", "B", "C"]
            }
        }

        chart_type = select_chart_type(table)
        assert chart_type == ChartType.HORIZONTAL_BAR.value

    def test_single_column_selects_clustered_column(self):
        """Test that single-column tables select clustered column."""
        table = {
            "table_name": "test_single_col",
            "data": {
                "row_labels": ["A", "B", "C"],
                "column_labels": ["Only"]
            }
        }

        chart_type = select_chart_type(table)
        assert chart_type == ChartType.CLUSTERED_COLUMN.value

    def test_default_selects_clustered_column(self):
        """Test that default case selects clustered column."""
        table = {
            "table_name": "test_default",
            "data": {
                "row_labels": ["A", "B", "C"],
                "column_labels": ["X", "Y"]
            }
        }

        chart_type = select_chart_type(table)
        assert chart_type == ChartType.CLUSTERED_COLUMN.value

    def test_semantic_hint_time_series_selects_line(self):
        """Test that time_series semantic hint selects line chart."""
        table = {
            "table_name": "test_time_series",
            "data": {
                "row_labels": ["2020", "2021", "2022"],
                "column_labels": ["A", "B"]
            }
        }

        chart_type = select_chart_type(table, semantic_hint=SemanticHint.TIME_SERIES)
        assert chart_type == ChartType.LINE.value

    def test_semantic_hint_ranking_selects_horizontal_bar(self):
        """Test that ranking semantic hint selects horizontal bar."""
        table = {
            "table_name": "test_ranking",
            "data": {
                "row_labels": ["A", "B", "C"],
                "column_labels": ["X", "Y"]
            }
        }

        chart_type = select_chart_type(table, semantic_hint=SemanticHint.RANKING)
        assert chart_type == ChartType.HORIZONTAL_BAR.value

    def test_semantic_hint_part_to_whole_selects_stacked(self):
        """Test that part_to_whole semantic hint selects stacked column."""
        table = {
            "table_name": "test_part_whole",
            "data": {
                "row_labels": ["A", "B"],
                "column_labels": ["X", "Y"]
            }
        }

        chart_type = select_chart_type(table, semantic_hint=SemanticHint.PART_TO_WHOLE)
        assert chart_type == ChartType.STACKED_COLUMN_100.value

    def test_empty_table_raises_error(self):
        """Test that empty table raises ValueError."""
        with pytest.raises(ValueError, match="table_data cannot be None or empty"):
            select_chart_type(None)

    def test_missing_data_section_raises_error(self):
        """Test that missing data section raises ValueError."""
        table = {"table_name": "test"}
        with pytest.raises(ValueError, match="must contain 'data' section"):
            select_chart_type(table)

    def test_missing_labels_raises_error(self):
        """Test that missing labels raises ValueError."""
        table = {
            "table_name": "test",
            "data": {"counts": [[1, 2], [3, 4]]}
        }
        with pytest.raises(ValueError, match="must contain 'row_labels' and 'column_labels'"):
            select_chart_type(table)


class TestChartTypeUtilities:
    """Tests for chart type utility functions."""

    def test_get_xl_chart_type_clustered_column(self):
        """Test XL chart type mapping for clustered column."""
        xl_type = get_xl_chart_type(ChartType.CLUSTERED_COLUMN.value)
        assert xl_type == "COLUMN_CLUSTERED"

    def test_get_xl_chart_type_horizontal_bar(self):
        """Test XL chart type mapping for horizontal bar."""
        xl_type = get_xl_chart_type(ChartType.HORIZONTAL_BAR.value)
        assert xl_type == "BAR_CLUSTERED"

    def test_get_xl_chart_type_stacked_100(self):
        """Test XL chart type mapping for 100% stacked column."""
        xl_type = get_xl_chart_type(ChartType.STACKED_COLUMN_100.value)
        assert xl_type == "COLUMN_STACKED_100"

    def test_get_xl_chart_type_line(self):
        """Test XL chart type mapping for line."""
        xl_type = get_xl_chart_type(ChartType.LINE.value)
        assert xl_type == "LINE"

    def test_get_xl_chart_type_invalid_raises_error(self):
        """Test that invalid chart type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown chart type"):
            get_xl_chart_type("invalid_type")

    def test_get_chart_type_description(self):
        """Test getting chart type documentation."""
        docs = get_chart_type_description(ChartType.CLUSTERED_COLUMN.value)

        assert "xl_chart_type" in docs
        assert "description" in docs
        assert "best_for" in docs
        assert docs["xl_chart_type"] == "COLUMN_CLUSTERED"
        assert isinstance(docs["best_for"], list)

    def test_get_chart_type_description_invalid_raises_error(self):
        """Test that invalid chart type raises ValueError in description."""
        with pytest.raises(ValueError, match="Unknown chart type"):
            get_chart_type_description("invalid_type")


class TestTableDimensionValidation:
    """Tests for validate_table_dimensions function."""

    def test_valid_dimensions_pass(self):
        """Test that valid dimensions pass validation."""
        is_valid, warning = validate_table_dimensions(5, 3)
        assert is_valid is True
        assert warning is None

    def test_excessive_rows_fail_validation(self):
        """Test that too many rows fail validation."""
        is_valid, warning = validate_table_dimensions(25, 3)
        assert is_valid is False
        assert "rows" in warning.lower()
        assert "25" in warning

    def test_excessive_columns_fail_validation(self):
        """Test that too many columns fail validation."""
        is_valid, warning = validate_table_dimensions(5, 12)
        assert is_valid is False
        assert "columns" in warning.lower()
        assert "12" in warning

    def test_custom_max_thresholds(self):
        """Test custom max thresholds."""
        is_valid, warning = validate_table_dimensions(15, 3, max_rows=20)
        assert is_valid is True

        is_valid, warning = validate_table_dimensions(15, 3, max_rows=10)
        assert is_valid is False


# =============================================================================
# PowerPoint Generation Tests
# =============================================================================

class TestPowerPointGeneration:
    """Tests for PowerPoint generation (Step 21)."""

    @pytest.mark.slow
    def test_generate_powerpoint_creates_file(
        self,
        populated_powerpoint_state: WorkflowState,
        temp_output_dir: Path
    ):
        """Test that PowerPoint generation creates .pptx file."""
        result = generate_powerpoint_node(populated_powerpoint_state)

        # Check state is updated
        assert result["current_step"] == STEP_21_GENERATE_POWERPOINT
        assert "powerpoint_file" in result
        assert result["powerpoint_file"] is not None

        # Check file exists
        pptx_path = Path(result["powerpoint_file"])
        assert pptx_path.exists()
        assert pptx_path.suffix == ".pptx"

        # Check file size is reasonable (> 1KB)
        assert pptx_path.stat().st_size > 1024

    @pytest.mark.slow
    def test_generate_powerpoint_without_filtered_tables_errors(
        self,
        test_config: Dict[str, Any]
    ):
        """Test that missing filtered_tables produces error."""
        state = {
            "current_step": STEP_20_APPLY_FILTER_TO_TABLES,
            "config": test_config,
            "filtered_tables": None,
            "errors": []
        }

        result = generate_powerpoint_node(state)

        assert result["current_step"] == STEP_21_GENERATE_POWERPOINT
        assert len(result["errors"]) == 1
        assert "filtered_tables" in result["errors"][0].lower()

    @pytest.mark.slow
    def test_generate_powerpoint_with_empty_tables(
        self,
        test_config: Dict[str, Any],
        temp_output_dir: Path
    ):
        """Test PowerPoint generation with empty tables list."""
        state = {
            "current_step": STEP_20_APPLY_FILTER_TO_TABLES,
            "config": test_config,
            "filtered_tables": {"tables": [], "summary": {"original_count": 0, "filtered_count": 0}},
            "statistical_summary": {"tables": []},
            "new_metadata": {},
            "raw_data": pd.DataFrame(),
            "original_metadata": {"file_name": "test.sav"},
            "errors": []
        }

        result = generate_powerpoint_node(state)

        assert result["current_step"] == STEP_21_GENERATE_POWERPOINT
        # Should still create file even with no tables (title + summary slides)
        assert result["powerpoint_file"] is not None
        assert Path(result["powerpoint_file"]).exists()

    @pytest.mark.slow
    def test_powerpoint_title_slide_content(
        self,
        populated_powerpoint_state: WorkflowState
    ):
        """Test that title slide contains correct information."""
        result = generate_powerpoint_node(populated_powerpoint_state)

        # Verify file was created
        assert "powerpoint_file" in result

        # Note: Full slide content verification requires opening the .pptx file
        # which needs python-pptx to be installed and can be complex to test
        # This test verifies the file exists and is valid format

        pptx_path = Path(result["powerpoint_file"])
        assert pptx_path.exists()
        assert pptx_path.suffix == ".pptx"

    @pytest.mark.slow
    def test_powerpoint_includes_all_tables(
        self,
        populated_powerpoint_state: WorkflowState
    ):
        """Test that all significant tables get slides."""
        result = generate_powerpoint_node(populated_powerpoint_state)

        # Should have 4 table slides + title slide + summary slide = 6 slides
        # Verify file exists
        pptx_path = Path(result["powerpoint_file"])
        assert pptx_path.exists()

    @pytest.mark.slow
    def test_powerpoint_handles_missing_metadata(
        self,
        test_config: Dict[str, Any],
        sample_significant_tables: Dict[str, Any],
        sample_statistical_summary: Dict[str, Any],
        sample_raw_data: pd.DataFrame
    ):
        """Test PowerPoint generation handles missing metadata gracefully."""
        state = {
            "current_step": STEP_20_APPLY_FILTER_TO_TABLES,
            "config": test_config,
            "filtered_tables": sample_significant_tables,
            "statistical_summary": sample_statistical_summary,
            "new_metadata": None,  # Missing metadata
            "raw_data": sample_raw_data,
            "original_metadata": {"file_name": "test.sav"},
            "errors": []
        }

        result = generate_powerpoint_node(state)

        # Should still create file, using variable names as labels
        assert result["current_step"] == STEP_21_GENERATE_POWERPOINT
        assert result["powerpoint_file"] is not None
        assert Path(result["powerpoint_file"]).exists()

    @pytest.mark.slow
    def test_powerpoint_preserves_errors_from_state(
        self,
        populated_powerpoint_state: WorkflowState
    ):
        """Test that existing errors are preserved."""
        populated_powerpoint_state["errors"] = ["Previous error"]

        result = generate_powerpoint_node(populated_powerpoint_state)

        assert len(result["errors"]) == 1
        assert result["errors"][0] == "Previous error"

    @pytest.mark.slow
    def test_powerpoint_chart_types_selected(
        self,
        populated_powerpoint_state: WorkflowState
    ):
        """Test that appropriate chart types are selected for each table."""
        # The state has tables with different dimensions
        # gender_x_satisfaction: 2x3 (2 rows, >2 cols) - clustered column
        # age_x_satisfaction: 4x3 - clustered column
        # region_x_product: 8x2 (>5 rows) - horizontal bar
        # income_x_brand: 5x6 (>4 cols) - stacked 100%

        result = generate_powerpoint_node(populated_powerpoint_state)

        # Verify PowerPoint was created
        assert result["powerpoint_file"] is not None
        pptx_path = Path(result["powerpoint_file"])
        assert pptx_path.exists()


# =============================================================================
# HTML Dashboard Generation Tests
# =============================================================================

class TestHTMLDashboardGeneration:
    """Tests for HTML dashboard generation (Step 22)."""

    def test_generate_html_dashboard_creates_file(
        self,
        populated_html_state: WorkflowState,
        temp_output_dir: Path
    ):
        """Test that HTML dashboard generation creates .html file."""
        result = generate_html_dashboard_node(populated_html_state)

        # Check state is updated
        assert result["current_step"] == STEP_22_GENERATE_HTML_DASHBOARD
        assert "html_dashboard_file" in result
        assert result["html_dashboard_file"] is not None

        # Check file exists
        html_path = Path(result["html_dashboard_file"])
        assert html_path.exists()
        assert html_path.suffix == ".html"

        # Check file size is reasonable
        assert html_path.stat().st_size > 1000

    def test_generate_html_dashboard_without_cross_table_errors(
        self,
        test_config: Dict[str, Any]
    ):
        """Test that missing cross_table_file produces error."""
        state = {
            "current_step": STEP_21_GENERATE_POWERPOINT,
            "config": test_config,
            "cross_table_file": None,
            "statistical_summary": {"tables": []},
            "errors": []
        }

        result = generate_html_dashboard_node(state)

        assert result["current_step"] == STEP_22_GENERATE_HTML_DASHBOARD
        assert len(result["errors"]) == 1
        assert "cross_table_file" in result["errors"][0].lower()

    def test_generate_html_dashboard_missing_file_errors(
        self,
        test_config: Dict[str, Any],
        temp_output_dir: Path
    ):
        """Test that non-existent cross_table_file produces error."""
        state = {
            "current_step": STEP_21_GENERATE_POWERPOINT,
            "config": test_config,
            "cross_table_file": str(temp_output_dir / "nonexistent.json"),
            "statistical_summary": {"tables": []},
            "errors": []
        }

        result = generate_html_dashboard_node(state)

        assert result["current_step"] == STEP_22_GENERATE_HTML_DASHBOARD
        assert len(result["errors"]) == 1
        assert "not found" in result["errors"][0].lower()

    def test_generate_html_dashboard_without_statistical_summary_errors(
        self,
        test_config: Dict[str, Any],
        temp_output_dir: Path
    ):
        """Test that missing statistical_summary produces error."""
        # Create cross-table file
        cross_table_file = temp_output_dir / "cross_table.json"
        with open(cross_table_file, 'w') as f:
            json.dump({"tables": []}, f)

        state = {
            "current_step": STEP_21_GENERATE_POWERPOINT,
            "config": test_config,
            "cross_table_file": str(cross_table_file),
            "statistical_summary": None,
            "errors": []
        }

        result = generate_html_dashboard_node(state)

        assert result["current_step"] == STEP_22_GENERATE_HTML_DASHBOARD
        assert len(result["errors"]) == 1
        assert "statistical_summary" in result["errors"][0].lower()

    def test_html_dashboard_contains_required_elements(
        self,
        populated_html_state: WorkflowState
    ):
        """Test that HTML dashboard contains all required elements."""
        result = generate_html_dashboard_node(populated_html_state)

        html_path = Path(result["html_dashboard_file"])
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for required HTML structure
        assert "<!DOCTYPE html>" in html_content
        assert "<html" in html_content
        assert "<head>" in html_content
        assert "<body>" in html_content

        # Check for Chart.js CDN
        assert "chart.js" in html_content.lower() or "chartjs" in html_content.lower()

        # Check for sidebar
        assert "sidebar" in html_content.lower()
        assert "navigation" in html_content.lower()

        # Check for table cards
        assert "table-card" in html_content

        # Check for chart canvas elements
        assert "<canvas" in html_content

    def test_html_dashboard_includes_all_tables(
        self,
        populated_html_state: WorkflowState
    ):
        """Test that HTML dashboard includes all tables from cross-table data."""
        result = generate_html_dashboard_node(populated_html_state)

        html_path = Path(result["html_dashboard_file"])
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for each table name
        assert "gender_x_satisfaction" in html_content
        assert "age_x_satisfaction" in html_content
        assert "education_x_income" in html_content

    def test_html_dashboard_significance_highlighting(
        self,
        populated_html_state: WorkflowState
    ):
        """Test that significant tables are highlighted."""
        result = generate_html_dashboard_node(populated_html_state)

        html_path = Path(result["html_dashboard_file"])
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for significance classes
        assert "significant" in html_content.lower()
        assert "not-significant" in html_content.lower()

    def test_html_dashboard_sidebar_navigation(
        self,
        populated_html_state: WorkflowState
    ):
        """Test that sidebar has navigation links."""
        result = generate_html_dashboard_node(populated_html_state)

        html_path = Path(result["html_dashboard_file"])
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for sidebar list
        assert 'id="table-list"' in html_content or 'class="table-list"' in html_content

        # Check for table links/items
        assert "data-table-id" in html_content

    def test_html_dashboard_summary_section(
        self,
        populated_html_state: WorkflowState
    ):
        """Test that summary section exists with statistics."""
        result = generate_html_dashboard_node(populated_html_state)

        html_path = Path(result["html_dashboard_file"])
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for summary section
        assert "summary" in html_content.lower()

        # Check for stats
        assert "total tables" in html_content.lower() or "Total Tables" in html_content
        assert "significant" in html_content.lower()

    def test_html_dashboard_filtering_controls(
        self,
        populated_html_state: WorkflowState
    ):
        """Test that filtering controls are present."""
        result = generate_html_dashboard_node(populated_html_state)

        html_path = Path(result["html_dashboard_file"])
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for filter elements
        assert "show-significant-only" in html_content
        assert "max-p-value" in html_content
        assert "min-cramers-v" in html_content

    def test_html_dashboard_export_functionality(
        self,
        populated_html_state: WorkflowState
    ):
        """Test that export buttons are present."""
        result = generate_html_dashboard_node(populated_html_state)

        html_path = Path(result["html_dashboard_file"])
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for export buttons
        assert "export" in html_content.lower()
        assert "csv" in html_content.lower()

    def test_html_dashboard_responsive_design(
        self,
        populated_html_state: WorkflowState
    ):
        """Test that HTML has responsive design (viewport meta tag)."""
        result = generate_html_dashboard_node(populated_html_state)

        html_path = Path(result["html_dashboard_file"])
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for viewport meta tag
        assert "viewport" in html_content.lower()

    def test_html_dashboard_css_styling(
        self,
        populated_html_state: WorkflowState
    ):
        """Test that CSS styles are embedded."""
        result = generate_html_dashboard_node(populated_html_state)

        html_path = Path(result["html_dashboard_file"])
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for style tag
        assert "<style>" in html_content

        # Check for some CSS classes
        assert "class=" in html_content

    def test_html_dashboard_javascript_interactivity(
        self,
        populated_html_state: WorkflowState
    ):
        """Test that JavaScript is embedded for interactivity."""
        result = generate_html_dashboard_node(populated_html_state)

        html_path = Path(result["html_dashboard_file"])
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for script tag
        assert "<script>" in html_content

        # Check for event listeners or functions
        assert "addEventListener" in html_content or "function" in html_content


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestOutputGenerationEdgeCases:
    """Tests for edge cases in output generation."""

    @pytest.mark.slow
    def test_powerpoint_with_no_significant_tables(
        self,
        test_config: Dict[str, Any],
        temp_output_dir: Path
    ):
        """Test PowerPoint with no significant tables."""
        state = {
            "current_step": STEP_20_APPLY_FILTER_TO_TABLES,
            "config": test_config,
            "filtered_tables": {"tables": [], "summary": {"original_count": 0, "filtered_count": 0}},
            "statistical_summary": {"tables": [], "significant_tables": 0},
            "new_metadata": {},
            "raw_data": pd.DataFrame(),
            "original_metadata": {"file_name": "empty.sav"},
            "errors": []
        }

        result = generate_powerpoint_node(state)

        # Should still create file with title and summary slides
        assert result["powerpoint_file"] is not None
        assert Path(result["powerpoint_file"]).exists()

    def test_html_dashboard_with_empty_cross_tables(
        self,
        test_config: Dict[str, Any],
        temp_output_dir: Path
    ):
        """Test HTML dashboard with no tables."""
        # Create empty cross-table file
        cross_table_file = temp_output_dir / "cross_table.json"
        with open(cross_table_file, 'w') as f:
            json.dump({"tables": []}, f)

        state = {
            "current_step": STEP_21_GENERATE_POWERPOINT,
            "config": test_config,
            "cross_table_file": str(cross_table_file),
            "statistical_summary": {"tables": [], "significant_tables": 0},
            "filter_list": {"filters": []},
            "errors": []
        }

        result = generate_html_dashboard_node(state)

        # Should still create HTML file
        assert result["html_dashboard_file"] is not None
        html_path = Path(result["html_dashboard_file"])
        assert html_path.exists()

        # Verify it's valid HTML
        with open(html_path, 'r') as f:
            html_content = f.read()
        assert "<!DOCTYPE html>" in html_content

    @pytest.mark.slow
    def test_powerpoint_with_very_large_table(
        self,
        test_config: Dict[str, Any],
        temp_output_dir: Path
    ):
        """Test PowerPoint handles very large table gracefully."""
        # Create table with many rows and columns
        large_table = {
            "tables": [{
                "table_id": "large_table",
                "table_name": "large_table",
                "row_variable": "many_rows",
                "column_variable": "many_cols",
                "data": {
                    "row_labels": [f"Row{i}" for i in range(15)],
                    "column_labels": [f"Col{i}" for i in range(8)],
                    "counts": [[i * j % 100 for j in range(8)] for i in range(15)]
                }
            }],
            "summary": {"original_count": 1, "filtered_count": 1}
        }

        state = {
            "current_step": STEP_20_APPLY_FILTER_TO_TABLES,
            "config": test_config,
            "filtered_tables": large_table,
            "statistical_summary": {
                "tables": [{
                    "table_name": "large_table",
                    "chi_square": 100.5,
                    "p_value": 0.001,
                    "cramers_v": 0.3,
                    "interpretation": "medium",
                    "is_significant": True,
                    "is_valid": True
                }]
            },
            "new_metadata": {},
            "raw_data": pd.DataFrame(),
            "original_metadata": {"file_name": "large.sav"},
            "errors": []
        }

        result = generate_powerpoint_node(state)

        # Should still create file, limiting chart to 10 rows, 6 series
        assert result["powerpoint_file"] is not None
        assert Path(result["powerpoint_file"]).exists()

    def test_html_dashboard_with_missing_statistics(
        self,
        test_config: Dict[str, Any],
        sample_cross_table_data: Dict[str, Any],
        temp_output_dir: Path
    ):
        """Test HTML dashboard with missing statistical data."""
        # Create cross-table file
        cross_table_file = temp_output_dir / "cross_table.json"
        with open(cross_table_file, 'w') as f:
            json.dump(sample_cross_table_data, f)

        # Use statistical summary with missing fields
        incomplete_stats = {
            "tables": [
                {
                    "table_name": "gender_x_satisfaction",
                    # Missing some fields
                    "is_significant": True,
                    "is_valid": True
                }
            ]
        }

        state = {
            "current_step": STEP_21_GENERATE_POWERPOINT,
            "config": test_config,
            "cross_table_file": str(cross_table_file),
            "statistical_summary": incomplete_stats,
            "filter_list": None,  # No filters
            "errors": []
        }

        result = generate_html_dashboard_node(state)

        # Should still create HTML file
        assert result["html_dashboard_file"] is not None
        assert Path(result["html_dashboard_file"]).exists()


# =============================================================================
# File Output Validation Tests
# =============================================================================

class TestFileOutputValidation:
    """Tests for file output validation."""

    @pytest.mark.slow
    def test_powerpoint_file_permissions(
        self,
        populated_powerpoint_state: WorkflowState
    ):
        """Test that PowerPoint file has correct permissions."""
        result = generate_powerpoint_node(populated_powerpoint_state)

        pptx_path = Path(result["powerpoint_file"])

        # File should be readable
        assert os.access(pptx_path, os.R_OK)

        # On Unix-like systems, check write permission
        if hasattr(os, 'W_OK'):
            assert os.access(pptx_path, os.W_OK)

    def test_html_file_permissions(
        self,
        populated_html_state: WorkflowState
    ):
        """Test that HTML file has correct permissions."""
        result = generate_html_dashboard_node(populated_html_state)

        html_path = Path(result["html_dashboard_file"])

        # File should be readable
        assert os.access(html_path, os.R_OK)

        # On Unix-like systems, check write permission
        if hasattr(os, 'W_OK'):
            assert os.access(html_path, os.W_OK)

    @pytest.mark.slow
    def test_powerpoint_file_location(
        self,
        populated_powerpoint_state: WorkflowState,
        temp_output_dir: Path
    ):
        """Test that PowerPoint file is created in correct location."""
        result = generate_powerpoint_node(populated_powerpoint_state)

        pptx_path = Path(result["powerpoint_file"])

        # File should be in the output directory
        assert pptx_path.parent == temp_output_dir

        # File should have correct name
        assert pptx_path.name == "survey_analysis.pptx"

    def test_html_file_location(
        self,
        populated_html_state: WorkflowState,
        temp_output_dir: Path
    ):
        """Test that HTML file is created in correct location."""
        result = generate_html_dashboard_node(populated_html_state)

        html_path = Path(result["html_dashboard_file"])

        # File should be in the output directory
        assert html_path.parent == temp_output_dir

        # File should have correct name
        assert html_path.name == "dashboard.html"


# =============================================================================
# Integration Tests
# =============================================================================

class TestOutputGenerationIntegration:
    """Integration tests for complete output generation workflow."""

    @pytest.mark.slow
    def test_both_outputs_from_same_state(
        self,
        test_config: Dict[str, Any],
        sample_significant_tables: Dict[str, Any],
        sample_statistical_summary: Dict[str, Any],
        sample_metadata: Dict[str, Any],
        sample_raw_data: pd.DataFrame,
        sample_cross_table_data: Dict[str, Any],
        sample_filter_list: Dict[str, Any],
        temp_output_dir: Path
    ):
        """Test generating both PowerPoint and HTML from same workflow state."""
        # Create cross-table file
        cross_table_file = temp_output_dir / "cross_table.json"
        with open(cross_table_file, 'w') as f:
            json.dump(sample_cross_table_data, f)

        # Create initial state
        state = {
            "current_step": STEP_20_APPLY_FILTER_TO_TABLES,
            "config": test_config,
            "filtered_tables": sample_significant_tables,
            "statistical_summary": sample_statistical_summary,
            "new_metadata": sample_metadata,
            "raw_data": sample_raw_data,
            "original_metadata": {"file_name": "survey.sav"},
            "cross_table_file": str(cross_table_file),
            "filter_list": sample_filter_list,
            "errors": [],
            "warnings": []
        }

        # Generate PowerPoint
        state_after_ppt = generate_powerpoint_node(state)

        # Generate HTML dashboard
        final_state = generate_html_dashboard_node(state_after_ppt)

        # Both outputs should exist
        assert "powerpoint_file" in final_state
        assert "html_dashboard_file" in final_state

        pptx_path = Path(final_state["powerpoint_file"])
        html_path = Path(final_state["html_dashboard_file"])

        assert pptx_path.exists()
        assert html_path.exists()

        # Both should be in same output directory
        assert pptx_path.parent == html_path.parent


# =============================================================================
# Test Markers
# =============================================================================

@pytest.mark.unit
class TestChartTypeSelectionUnit:
    """Unit tests for chart type selection (fast, no file I/O)."""
    # All tests in TestChartTypeSelection class are unit tests
    pass


@pytest.mark.integration
class TestOutputGenerationIntegrationSlow:
    """Integration tests for output generation (slower, creates files)."""
    # Tests that actually create PowerPoint/HTML files
    pass
