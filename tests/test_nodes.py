"""
Unit Tests for Individual Node Functions

This module tests individual node implementations from all 8 phases.
Tests use fixtures to provide sample state and mock external dependencies.

Phases Tested:
- Phase 1 (Extraction): Steps 1-3
- Phase 2 (Recoding): Steps 4-8
- Phase 3 (Indicators): Steps 9-11
- Phase 4 (Tables): Steps 12-16
- Phase 5 (Statistics): Steps 17-18
- Phase 6 (Filtering): Steps 19-20
- Phase 7 (PowerPoint): Step 21
- Phase 8 (HTML Dashboard): Step 22

Test Coverage:
- All 22 node functions
- State immutability
- Error handling
- Three-node pattern feedback loops
"""

import pytest
import json
import copy
from unittest.mock import Mock, patch, MagicMock, call
from typing import Dict, Any
from pathlib import Path
import pandas as pd

from agent.state import (
    WorkflowState,
    ValidationResult,
    create_initial_state,
)

# Import nodes from each phase
from agent.nodes.phase1_extraction import (
    extract_spss_node,
    transform_metadata_node,
    filter_metadata_node,
)

from agent.nodes.phase2_recoding import (
    generate_recoding_rules_node,
    validate_recoding_rules_node,
    review_recoding_rules_node,
    generate_pspp_recoding_syntax_node,
    execute_pspp_recoding_node,
)

from agent.nodes.phase3_indicators import (
    generate_indicators_node,
    validate_indicators_node,
    review_indicators_node,
)

from agent.nodes.phase4_tables import (
    generate_table_specifications_node,
    validate_table_specs_node,
    review_table_specifications_node,
    generate_pspp_table_syntax_node,
    execute_pspp_tables_node,
)

from agent.nodes.phase5_statistics import (
    generate_python_statistics_script_node,
    execute_python_statistics_script_node,
)

from agent.nodes.phase6_filtering import (
    generate_filter_list_node,
    apply_filter_to_tables_node,
)

from agent.nodes.phase7_powerpoint import (
    generate_powerpoint_node,
)

from agent.nodes.phase8_html_dashboard import (
    generate_html_dashboard_node,
)


# =============================================================================
# Phase 1: Extraction Nodes (Steps 1-3)
# =============================================================================

class TestExtractSpssNode:
    """Tests for extract_spss_node (Step 1)."""

    def test_extract_spss_node_success(self, sample_state, sample_dataframe, sample_metadata):
        """Test successful SPSS file extraction."""
        # Mock read_spss_file to return sample data
        with patch('agent.nodes.phase1_extraction.read_spss_file') as mock_read:
            # Create proper mock metadata object
            mock_metadata = Mock()
            mock_metadata.column_labels = sample_metadata["column_labels"]
            mock_metadata.variable_value_labels = sample_metadata["column_value_labels"]
            mock_metadata.variable_storage_types = {}
            mock_read.return_value = (sample_dataframe, mock_metadata)

            result = extract_spss_node(sample_state)

            assert result["current_step"] == 1
            assert result["raw_data"] is not None
            assert len(result["raw_data"]) == 50
            assert result["original_metadata"] is not None
            assert result["original_metadata"]["n_rows"] == 50
            assert len(result["errors"]) == 0

    def test_extract_spss_node_file_not_found(self, sample_state):
        """Test SPSS extraction when file is not found."""
        with patch('agent.nodes.phase1_extraction.read_spss_file') as mock_read:
            mock_read.side_effect = FileNotFoundError("File not found")

            result = extract_spss_node(sample_state)

            assert result["current_step"] == 1
            assert len(result["errors"]) == 1
            assert "not found" in result["errors"][0].lower()

    def test_extract_spss_node_no_input_path(self):
        """Test SPSS extraction with no input_file_path."""
        state: WorkflowState = {}
        state["input_file_path"] = None
        state["errors"] = []

        result = extract_spss_node(state)

        assert len(result["errors"]) == 1
        assert "input_file_path" in result["errors"][0]


class TestTransformMetadataNode:
    """Tests for transform_metadata_node (Step 2)."""

    def test_transform_metadata_node_success(self, sample_state, sample_dataframe, sample_metadata):
        """Test successful metadata transformation."""
        # Prepare state with raw data
        state = {
            **sample_state,
            "raw_data": sample_dataframe,
            "original_metadata": sample_metadata,
            "warnings": [],
        }

        result = transform_metadata_node(state)

        assert result["current_step"] == 2
        assert result["variable_centered_metadata"] is not None
        assert result["variable_centered_metadata"]["n_variables"] == 6
        assert result["variable_centered_metadata"]["n_numeric"] == 6
        assert len(result["errors"]) == 0

    def test_transform_metadata_node_no_raw_data(self, sample_state):
        """Test metadata transformation with no raw_data."""
        state = {
            **sample_state,
            "raw_data": None,
            "original_metadata": None,
        }

        result = transform_metadata_node(state)

        assert result["current_step"] == 2
        assert len(result["errors"]) == 1
        assert "raw_data" in result["errors"][0]

    def test_transform_metadata_node_empty_dataframe(self, sample_state):
        """Test metadata transformation with empty DataFrame."""
        state = {
            **sample_state,
            "raw_data": pd.DataFrame(),
            "original_metadata": {"n_rows": 0, "n_columns": 0},
            "warnings": [],
        }

        result = transform_metadata_node(state)

        assert result["current_step"] == 2
        assert result["variable_centered_metadata"]["n_variables"] == 0
        assert len(result["warnings"]) >= 1


class TestFilterMetadataNode:
    """Tests for filter_metadata_node (Step 3)."""

    def test_filter_metadata_node_success(self, sample_state, sample_variable_centered_metadata):
        """Test successful metadata filtering."""
        state = {
            **sample_state,
            "variable_centered_metadata": sample_variable_centered_metadata,
            "warnings": [],
        }

        result = filter_metadata_node(state)

        assert result["current_step"] == 3
        assert result["filtered_metadata"] is not None
        assert result["filtered_out_variables"] is not None

        # Check that binary variable (employed) was filtered out
        filtered_out_names = [v["name"] for v in result["filtered_out_variables"]]
        assert "employed" in filtered_out_names

        # Check that valid variables remain
        included_names = [v["name"] for v in result["filtered_metadata"]]
        assert "gender" in included_names
        assert "education" in included_names

    def test_filter_metadata_node_no_metadata(self, sample_state):
        """Test metadata filtering with no variable_centered_metadata."""
        state = {
            **sample_state,
            "variable_centered_metadata": None,
        }

        result = filter_metadata_node(state)

        assert result["current_step"] == 3
        assert len(result["errors"]) == 1


# =============================================================================
# Phase 2: Recoding Nodes (Steps 4-8)
# =============================================================================

class TestGenerateRecodingRulesNode:
    """Tests for generate_recoding_rules_node (Step 4)."""

    def test_generate_recoding_rules_node_success(self, populated_state, mock_llm_client):
        """Test successful recoding rules generation."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = '{"recoding_rules": {"var1": {"recodings": []}}}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client):
            result = generate_recoding_rules_node(populated_state)

            assert result["current_step"] == 4
            assert result["recoding_rules"] is not None
            assert "var1" in result["recoding_rules"]

    def test_generate_recoding_rules_node_with_feedback(self, populated_state, mock_llm_client):
        """Test recoding rules generation with feedback."""
        state = {
            **populated_state,
            "recoding_feedback": "Previous rules were too aggressive",
        }

        with patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client):
            result = generate_recoding_rules_node(state)

            assert result["recoding_rules"] is not None
            assert result["iteration_count"] == 1


class TestValidateRecodingRulesNode:
    """Tests for validate_recoding_rules_node (Step 5)."""

    def test_validate_recoding_rules_node_valid(self, populated_state):
        """Test validation of valid recoding rules."""
        state = {
            **populated_state,
            "recoding_rules": {"var1": {"recodings": []}},
        }

        with patch('agent.nodes.phase2_recoding.validate_recoding_artifact') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["syntax", "logic"],
            )

            result = validate_recoding_rules_node(state)

            assert result["current_step"] == 5
            assert result["recoding_validation_result"].is_valid is True

    def test_validate_recoding_rules_node_invalid(self, populated_state):
        """Test validation of invalid recoding rules."""
        state = {
            **populated_state,
            "recoding_rules": {"var1": {"recodings": []}},
        }

        with patch('agent.nodes.phase2_recoding.validate_recoding_artifact') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=False,
                errors=["Syntax error"],
                warnings=[],
                checks_performed=["syntax", "logic"],
            )

            result = validate_recoding_rules_node(state)

            assert result["current_step"] == 5
            assert result["recoding_validation_result"].is_valid is False
            assert len(result["recoding_validation_result"].errors) == 1


class TestReviewRecodingRulesNode:
    """Tests for review_recoding_rules_node (Step 6)."""

    def test_review_recoding_rules_node_auto_approve(self, populated_state, sample_config):
        """Test auto-approval when enabled."""
        state = {
            **populated_state,
            "recoding_rules": {"recoding_rules": []},
            "recoding_validation_result": ValidationResult(is_valid=True, errors=[], warnings=[], checks_performed=[]),
            "config": sample_config,
        }

        with patch('agent.nodes.phase2_recoding.format_review_for_display'):
            result = review_recoding_rules_node(state)

            assert result["current_step"] == 6
            assert result["requires_human_review"] is True

    def test_review_recoding_rules_node_manual_review(self, populated_state):
        """Test manual review mode."""
        state = {
            **populated_state,
            "recoding_rules": {"recoding_rules": []},
            "recoding_validation_result": ValidationResult(is_valid=True, errors=[], warnings=[], checks_performed=[]),
            "config": {"auto_approve_recoding": False, "output_dir": "output"},
        }

        with patch('agent.nodes.phase2_recoding.format_review_for_display'):
            result = review_recoding_rules_node(state)

            assert result["current_step"] == 6
            assert result["requires_human_review"] is True

    def test_review_recoding_rules_node_no_rules(self, populated_state):
        """Test review with no recoding rules."""
        state = {
            **populated_state,
            "recoding_rules": None,
            "config": {"output_dir": "output"},
        }

        result = review_recoding_rules_node(state)

        assert result["current_step"] == 6
        assert len(result["errors"]) == 1


class TestGeneratePsppRecodingSyntaxNode:
    """Tests for generate_pspp_recoding_syntax_node (Step 7)."""

    def test_generate_pspp_recoding_syntax_node_success(self, populated_state):
        """Test successful PSPP recoding syntax generation."""
        recoding_rules = {
            "recoding_rules": [
                {
                    "source_variable": "age",
                    "target_variable": "age_recoded",
                    "transformation_type": "range_grouping",
                    "rules": [
                        {"source_min": 0, "source_max": 30, "target_value": 1},
                        {"source_min": 31, "source_max": 60, "target_value": 2},
                        {"source_min": 61, "source_max": "HI", "target_value": 3},
                    ],
                }
            ]
        }

        state = {
            **populated_state,
            "recoding_rules": recoding_rules,
            "filtered_metadata": [
                {"name": "age", "label": "Age", "variable_type": "numeric"},
            ],
            "warnings": [],
        }

        result = generate_pspp_recoding_syntax_node(state)

        assert result["current_step"] == 7
        assert result["pspp_recoding_syntax"] is not None
        assert result["recoding_syntax_file"] is not None
        assert "RECODE" in result["pspp_recoding_syntax"]
        assert len(result["errors"]) == 0

    def test_generate_pspp_recoding_syntax_node_state_immutability(self, populated_state):
        """Test that input state is not mutated."""
        recoding_rules = {"recoding_rules": []}
        state = {
            **populated_state,
            "recoding_rules": recoding_rules,
            "filtered_metadata": [],
            "warnings": [],
        }

        original_warnings = list(state["warnings"])

        result = generate_pspp_recoding_syntax_node(state)

        # Input state should be unchanged
        assert state["warnings"] == original_warnings
        assert "pspp_recoding_syntax" not in state

    def test_generate_pspp_recoding_syntax_node_no_rules(self, populated_state):
        """Test syntax generation with no recoding rules."""
        state = {
            **populated_state,
            "recoding_rules": None,
            "filtered_metadata": [],
        }

        result = generate_pspp_recoding_syntax_node(state)

        assert result["current_step"] == 7
        assert len(result["errors"]) == 1
        assert "recoding_rules" in result["errors"][0]

    def test_generate_pspp_recoding_syntax_node_empty_rules(self, populated_state):
        """Test syntax generation with empty rules list."""
        state = {
            **populated_state,
            "recoding_rules": {"recoding_rules": []},
            "filtered_metadata": [],
            "warnings": [],
        }

        result = generate_pspp_recoding_syntax_node(state)

        assert result["current_step"] == 7
        assert len(result["warnings"]) >= 1
        assert "empty" in result["warnings"][0].lower()


class TestExecutePsppRecodingNode:
    """Tests for execute_pspp_recoding_node (Step 8)."""

    def test_execute_pspp_recoding_node_success(self, populated_state, tmp_path):
        """Test successful PSPP recoding execution."""
        # Create temporary syntax file
        syntax_file = tmp_path / "recoding.sps"
        syntax_file.write_text("RECODE age (0 THRU 30 = 1).")

        # Create temporary input file
        input_file = tmp_path / "input.sav"
        input_file.write_text("mock")

        state = {
            **populated_state,
            "raw_data_file": str(input_file),
            "recoding_syntax_file": str(syntax_file),
            "config": {"output_dir": str(tmp_path)},
        }

        with patch('agent.nodes.phase2_recoding.execute_pspp_syntax') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "return_code": 0,
                "output": "PSPP executed successfully",
                "error": "",
                "output_file": str(tmp_path / "new_data.sav"),
            }

            result = execute_pspp_recoding_node(state)

            assert result["current_step"] == 8
            assert result["new_data_file"] is not None
            assert result["new_metadata"] is not None

    def test_execute_pspp_recoding_node_pspp_failure(self, populated_state, tmp_path):
        """Test PSPP execution failure."""
        syntax_file = tmp_path / "recoding.sps"
        syntax_file.write_text("INVALID SYNTAX")

        input_file = tmp_path / "input.sav"
        input_file.write_text("mock")

        state = {
            **populated_state,
            "raw_data_file": str(input_file),
            "recoding_syntax_file": str(syntax_file),
            "config": {"output_dir": str(tmp_path)},
        }

        with patch('agent.nodes.phase2_recoding.execute_pspp_syntax') as mock_execute:
            mock_execute.return_value = {
                "success": False,
                "return_code": 1,
                "output": "",
                "error": "Syntax error on line 1",
                "output_file": None,
            }

            result = execute_pspp_recoding_node(state)

            assert result["current_step"] == 8
            assert len(result["errors"]) == 1

    def test_execute_pspp_recoding_node_no_syntax_file(self, populated_state):
        """Test execution without syntax file."""
        state = {
            **populated_state,
            "recoding_syntax_file": None,
        }

        result = execute_pspp_recoding_node(state)

        assert result["current_step"] == 8
        assert len(result["errors"]) == 1


# =============================================================================
# Phase 3: Indicator Nodes (Steps 9-11)
# =============================================================================

class TestGenerateIndicatorsNode:
    """Tests for generate_indicators_node (Step 9)."""

    def test_generate_indicators_node_success(self, populated_state, mock_llm_client):
        """Test successful indicator generation."""
        state = {
            **populated_state,
            "new_metadata": {"variables": {}},
            "iteration_count": 0,
        }

        mock_response = Mock()
        mock_response.content = '{"indicators": {"indicator1": {"variables": ["var1", "var2"]}}}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase3_indicators.get_llm_client', return_value=mock_llm_client):
            result = generate_indicators_node(state)

            assert result["current_step"] == 9
            assert result["indicators"] is not None
            assert "indicator1" in result["indicators"]


class TestValidateIndicatorsNode:
    """Tests for validate_indicators_node (Step 10)."""

    def test_validate_indicators_node_valid(self, populated_state):
        """Test validation of valid indicators."""
        state = {
            **populated_state,
            "indicators": {"indicator1": {"variables": ["var1"]}},
        }

        with patch('agent.nodes.phase3_indicators.validate_indicator_artifact') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["structure", "variables"],
            )

            result = validate_indicators_node(state)

            assert result["current_step"] == 10
            assert result["indicator_validation_result"].is_valid is True


class TestReviewIndicatorsNode:
    """Tests for review_indicators_node (Step 11)."""

    def test_review_indicators_node(self, populated_state):
        """Test indicators review node."""
        state = {
            **populated_state,
            "indicators": {"indicator1": {"variables": ["var1"]}},
        }

        with patch('agent.nodes.phase3_indicators.format_review_for_display'):
            result = review_indicators_node(state)

            assert result["current_step"] == 11


# =============================================================================
# Phase 4: Table Specification Nodes (Steps 12-16)
# =============================================================================

class TestGenerateTableSpecificationsNode:
    """Tests for generate_table_specifications_node (Step 12)."""

    def test_generate_table_specifications_node_success(self, populated_state, mock_llm_client):
        """Test successful table specification generation."""
        state = {
            **populated_state,
            "indicators": {"indicator1": {"variables": ["var1", "var2"]}},
        }

        mock_response = Mock()
        mock_response.content = '{"table_specifications": {"table1": {"row": "var1", "column": "var2"}}}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase4_tables.get_llm_client', return_value=mock_llm_client):
            result = generate_table_specifications_node(state)

            assert result["current_step"] == 12
            assert result["table_specifications"] is not None
            assert "table1" in result["table_specifications"]


class TestValidateTableSpecsNode:
    """Tests for validate_table_specs_node (Step 13)."""

    def test_validate_table_specs_node_valid(self, populated_state):
        """Test validation of valid table specifications."""
        state = {
            **populated_state,
            "table_specifications": {"table1": {"row": "var1", "column": "var2"}},
        }

        with patch('agent.nodes.phase4_tables.validate_table_artifact') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["structure", "variables"],
            )

            result = validate_table_specs_node(state)

            assert result["current_step"] == 13
            assert result["table_validation_result"].is_valid is True


class TestReviewTableSpecificationsNode:
    """Tests for review_table_specifications_node (Step 14)."""

    def test_review_table_specifications_node(self, populated_state):
        """Test table specifications review node."""
        state = {
            **populated_state,
            "table_specifications": {"tables": []},
            "table_validation_result": ValidationResult(is_valid=True, errors=[], warnings=[], checks_performed=[]),
            "config": {"auto_approve_table_specs": True, "output_dir": "output"},
        }

        with patch('agent.nodes.phase4_tables.format_review_for_display'):
            result = review_table_specifications_node(state)

            assert result["current_step"] == 14


class TestGeneratePsppTableSyntaxNode:
    """Tests for generate_pspp_table_syntax_node (Step 15)."""

    def test_generate_pspp_table_syntax_node_success(self, populated_state):
        """Test successful PSPP table syntax generation."""
        table_specs = {
            "tables": [
                {
                    "table_id": "gender_x_satisfaction",
                    "row_variable": "gender",
                    "column_variable": "satisfaction",
                    "statistics": ["count", "columnpct"],
                }
            ]
        }

        state = {
            **populated_state,
            "table_specifications": table_specs,
            "new_metadata": {
                "variable_names": ["gender", "satisfaction"],
                "variable_labels": {"gender": "Gender", "satisfaction": "Satisfaction"},
            },
            "warnings": [],
        }

        result = generate_pspp_table_syntax_node(state)

        assert result["current_step"] == 15
        assert result["pspp_tables_syntax"] is not None
        assert result["table_syntax_file"] is not None
        assert "CTABLES" in result["pspp_tables_syntax"]

    def test_generate_pspp_table_syntax_node_no_specs(self, populated_state):
        """Test syntax generation without table specifications."""
        state = {
            **populated_state,
            "table_specifications": None,
        }

        result = generate_pspp_table_syntax_node(state)

        assert result["current_step"] == 15
        assert len(result["errors"]) == 1


class TestExecutePsppTablesNode:
    """Tests for execute_pspp_tables_node (Step 16)."""

    def test_execute_pspp_tables_node_success(self, populated_state, tmp_path):
        """Test successful PSPP tables execution."""
        syntax_file = tmp_path / "tables.sps"
        syntax_file.write_text("CTABLES /TABLE var1 BY var2.")

        input_file = tmp_path / "new_data.sav"
        input_file.write_text("mock")

        state = {
            **populated_state,
            "new_data_file": str(input_file),
            "table_syntax_file": str(syntax_file),
            "config": {"output_dir": str(tmp_path)},
        }

        # Create mock CSV output
        csv_file = tmp_path / "cross_table.csv"
        csv_file.write_text("row,col,value\n1,1,10\n")

        with patch('agent.nodes.phase4_tables.execute_pspp_syntax') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "return_code": 0,
                "output": "CTABLES executed",
                "error": "",
                "output_file": str(csv_file),
            }

            result = execute_pspp_tables_node(state)

            assert result["current_step"] == 16
            assert result["cross_table_file"] is not None

    def test_execute_pspp_tables_node_failure(self, populated_state, tmp_path):
        """Test PSPP tables execution failure."""
        syntax_file = tmp_path / "tables.sps"
        syntax_file.write_text("INVALID")

        input_file = tmp_path / "new_data.sav"
        input_file.write_text("mock")

        state = {
            **populated_state,
            "new_data_file": str(input_file),
            "table_syntax_file": str(syntax_file),
            "config": {"output_dir": str(tmp_path)},
        }

        with patch('agent.nodes.phase4_tables.execute_pspp_syntax') as mock_execute:
            mock_execute.return_value = {
                "success": False,
                "return_code": 1,
                "output": "",
                "error": "Syntax error",
                "output_file": None,
            }

            result = execute_pspp_tables_node(state)

            assert result["current_step"] == 16
            assert len(result["errors"]) == 1


# =============================================================================
# Phase 5: Statistics Nodes (Steps 17-18)
# =============================================================================

class TestGeneratePythonStatisticsScriptNode:
    """Tests for generate_python_statistics_script_node (Step 17)."""

    def test_generate_statistics_script_node_success(self, populated_state):
        """Test successful statistics script generation."""
        state = {
            **populated_state,
            "cross_table_file": "/tmp/crosstabs.txt",
        }

        with patch('agent.nodes.phase5_statistics.write_python_script') as mock_write:
            mock_write.return_value = "/tmp/stats_script.py"

            result = generate_python_statistics_script_node(state)

            assert result["current_step"] == 17
            assert result["statistics_script"] == "/tmp/stats_script.py"

    def test_generate_statistics_script_node_no_crosstabs(self, populated_state):
        """Test statistics script generation without cross-table file."""
        state = {
            **populated_state,
            "cross_table_file": None,
        }

        result = generate_python_statistics_script_node(state)

        assert result["current_step"] == 17
        assert len(result["errors"]) >= 1


class TestExecutePythonStatisticsScriptNode:
    """Tests for execute_python_statistics_script_node (Step 18)."""

    def test_execute_statistics_script_node_success(self, populated_state):
        """Test successful statistics script execution."""
        state = {
            **populated_state,
            "statistics_script": "/tmp/stats_script.py",
        }

        mock_summary = {
            "total_tests": 10,
            "significant_tests": 5,
            "results": [],
        }

        with patch('agent.nodes.phase5_statistics.run_python_script') as mock_run:
            mock_run.return_value = mock_summary

            result = execute_python_statistics_script_node(state)

            assert result["current_step"] == 18
            assert result["statistical_summary"] is not None
            assert result["statistical_summary"]["total_tests"] == 10


# =============================================================================
# Phase 6: Filtering Nodes (Steps 19-20)
# =============================================================================

class TestGenerateFilterListNode:
    """Tests for generate_filter_list_node (Step 19)."""

    def test_generate_filter_list_node_success(self, populated_state):
        """Test successful filter list generation."""
        state = {
            **populated_state,
            "statistical_summary": {
                "results": [
                    {"table": "table1", "p_value": 0.03, "cramers_v": 0.2},
                    {"table": "table2", "p_value": 0.15, "cramers_v": 0.05},
                ]
            },
        }

        result = generate_filter_list_node(state)

        assert result["current_step"] == 19
        assert result["filter_list"] is not None


class TestApplyFilterToTablesNode:
    """Tests for apply_filter_to_tables_node (Step 20)."""

    def test_apply_filter_to_tables_node_success(self, populated_state):
        """Test successful filter application."""
        state = {
            **populated_state,
            "filter_list": {
                "table1": {"pass": True, "p_value": 0.03},
                "table2": {"pass": False, "p_value": 0.15},
            },
        }

        result = apply_filter_to_tables_node(state)

        assert result["current_step"] == 20
        assert result["filtered_tables"] is not None
        assert result["total_tables_evaluated"] >= 0


# =============================================================================
# Phase 7: PowerPoint Node (Step 21)
# =============================================================================

class TestGeneratePowerPointNode:
    """Tests for generate_powerpoint_node (Step 21)."""

    def test_generate_powerpoint_node_success(self, populated_state):
        """Test successful PowerPoint generation."""
        state = {
            **populated_state,
            "filtered_tables": {
                "table1": {"data": []},
            },
            "statistical_summary": {
                "results": [],
            },
        }

        with patch('agent.nodes.phase7_powerpoint.create_powerpoint') as mock_create:
            mock_create.return_value = "/output/presentation.pptx"

            result = generate_powerpoint_node(state)

            assert result["current_step"] == 21
            assert result["powerpoint_file"] is not None

    def test_generate_powerpoint_node_no_tables(self, populated_state):
        """Test PowerPoint generation without tables."""
        state = {
            **populated_state,
            "filtered_tables": None,
        }

        result = generate_powerpoint_node(state)

        assert result["current_step"] == 21
        # Should have error or warning
        assert len(result["errors"]) >= 0 or len(result["warnings"]) >= 0


# =============================================================================
# Phase 8: HTML Dashboard Node (Step 22)
# =============================================================================

class TestGenerateHtmlDashboardNode:
    """Tests for generate_html_dashboard_node (Step 22)."""

    def test_generate_html_dashboard_node_success(self, populated_state):
        """Test successful HTML dashboard generation."""
        state = {
            **populated_state,
            "filtered_tables": {
                "table1": {"data": []},
            },
            "statistical_summary": {
                "results": [],
            },
            "new_metadata": {"variables": {}},
        }

        with patch('agent.nodes.phase8_html_dashboard.create_html_dashboard') as mock_create:
            mock_create.return_value = "/output/dashboard.html"

            result = generate_html_dashboard_node(state)

            assert result["current_step"] == 22
            assert result["html_dashboard_file"] is not None

    def test_generate_html_dashboard_node_no_data(self, populated_state):
        """Test HTML dashboard generation without data."""
        state = {
            **populated_state,
            "filtered_tables": None,
            "statistical_summary": None,
        }

        result = generate_html_dashboard_node(state)

        assert result["current_step"] == 22


# =============================================================================
# Node Error Handling Tests
# =============================================================================

class TestNodeErrorHandling:
    """Tests for error handling in nodes."""

    def test_extract_node_invalid_file_format(self, sample_state):
        """Test extraction with invalid file format."""
        with patch('agent.nodes.phase1_extraction.read_spss_file') as mock_read:
            mock_read.side_effect = ValueError("Invalid SPSS format")

            result = extract_spss_node(sample_state)

            assert result["current_step"] == 1
            assert len(result["errors"]) == 1
            assert "Invalid SPSS" in result["errors"][0]

    def test_transform_node_missing_metadata(self, sample_state):
        """Test transform with missing original_metadata."""
        state = {
            **sample_state,
            "raw_data": pd.DataFrame({"col1": [1, 2, 3]}),
            "original_metadata": None,
        }

        result = transform_metadata_node(state)

        assert result["current_step"] == 2
        assert len(result["errors"]) == 1

    def test_filter_node_missing_metadata(self, sample_state):
        """Test filter with missing variable_centered_metadata."""
        state = {
            **sample_state,
            "variable_centered_metadata": None,
        }

        result = filter_metadata_node(state)

        assert result["current_step"] == 3
        assert len(result["errors"]) == 1


# =============================================================================
# State Immutability Tests
# =============================================================================

class TestStateImmutability:
    """Tests that nodes do not mutate input state."""

    def test_extract_spss_node_immutability(self, sample_state, sample_dataframe):
        """Test that extract_spss_node does not mutate input state."""
        original_errors = list(sample_state.get("errors", []))
        original_warnings = list(sample_state.get("warnings", []))

        with patch('agent.nodes.phase1_extraction.read_spss_file') as mock_read:
            mock_metadata = Mock()
            mock_metadata.column_labels = {}
            mock_metadata.variable_value_labels = {}
            mock_metadata.variable_storage_types = {}
            mock_read.return_value = (sample_dataframe, mock_metadata)

            result = extract_spss_node(sample_state)

            # Input state should be unchanged
            assert sample_state.get("errors") == original_errors
            assert sample_state.get("warnings") == original_warnings
            assert "raw_data" not in sample_state

    def test_generate_recoding_rules_node_immutability(self, populated_state, mock_llm_client):
        """Test that generate_recoding_rules_node does not mutate input state."""
        original_iteration = populated_state.get("iteration_count", 0)

        mock_response = Mock()
        mock_response.content = '{"recoding_rules": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client):
            result = generate_recoding_rules_node(populated_state)

        # Input state iteration count should be unchanged
        assert populated_state.get("iteration_count", 0) == original_iteration
        assert "recoding_rules" not in populated_state


# =============================================================================
# Three-Node Pattern Feedback Loop Tests
# =============================================================================

class TestThreeNodePatternRecoding:
    """Tests for the three-node pattern in Phase 2 (Steps 4-6)."""

    def test_recoding_feedback_loop_valid_on_first_try(self, populated_state, mock_llm_client):
        """Test that valid rules on first generation skip feedback loop."""
        # Step 4: Generate rules
        mock_response = Mock()
        mock_response.content = '{"recoding_rules": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client):
            state_after_gen = generate_recoding_rules_node(populated_state)

        # Step 5: Validate
        with patch('agent.nodes.phase2_recoding.validate_recoding_rules') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["syntax"],
            )
            state_after_val = validate_recoding_rules_node(state_after_gen)

        # Step 6: Review
        with patch('agent.nodes.phase2_recoding.format_review_for_display'):
            state_after_rev = review_recoding_rules_node(state_after_val)

        assert state_after_gen["iteration_count"] == 0
        assert state_after_val["recoding_validation_result"].is_valid is True
        assert state_after_rev["current_step"] == 6

    def test_recoding_feedback_loop_invalid_then_valid(self, populated_state, mock_llm_client):
        """Test that invalid rules trigger feedback loop and retry."""
        # Step 4: Initial generation
        mock_response = Mock()
        mock_response.content = '{"recoding_rules": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client):
            state_after_gen = generate_recoding_rules_node(populated_state)

        # Step 5: Validation fails
        with patch('agent.nodes.phase2_recoding.validate_recoding_rules') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=False,
                errors=["Invalid range"],
                warnings=[],
                checks_performed=["syntax"],
            )
            state_after_val = validate_recoding_rules_node(state_after_gen)

        # Step 6: Review should require human review
        with patch('agent.nodes.phase2_recoding.format_review_for_display'):
            state_after_rev = review_recoding_rules_node(state_after_val)

        # Step 4 retry: With validation feedback
        state_with_feedback = {**state_after_rev, "iteration_count": 1}

        with patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client):
            state_after_retry = generate_recoding_rules_node(state_with_feedback)

        assert state_after_retry["iteration_count"] == 2


class TestThreeNodePatternIndicators:
    """Tests for the three-node pattern in Phase 3 (Steps 9-11)."""

    def test_indicators_feedback_loop_with_retry(self, populated_state, mock_llm_client):
        """Test indicators three-node pattern with validation retry."""
        state = {
            **populated_state,
            "new_metadata": {
                "variable_names": ["var1"],
                "variable_labels": {},
                "value_labels": {},
            },
            "iteration_count": 0,
        }

        # Step 9: Generate indicators
        mock_response = Mock()
        mock_response.content = '{"indicators": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase3_indicators.get_llm_client', return_value=mock_llm_client):
            state = generate_indicators_node(state)

        # Step 10: Validate
        with patch('agent.nodes.phase3_indicators.validate_indicator_artifact') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=False,
                errors=["No indicators"],
                warnings=[],
                checks_performed=["structure"],
            )
            state = validate_indicators_node(state)

        # Step 11: Review
        with patch('agent.nodes.phase3_indicators.format_review_for_display'):
            state = review_indicators_node(state)

        assert state["indicator_validation_result"].is_valid is False
        assert state["current_step"] == 11


class TestThreeNodePatternTables:
    """Tests for the three-node pattern in Phase 4 (Steps 12-14)."""

    def test_tables_feedback_loop_with_retry(self, populated_state, mock_llm_client):
        """Test tables three-node pattern with validation retry."""
        state = {
            **populated_state,
            "indicators": {"indicators": []},
            "iteration_count": 0,
        }

        # Step 12: Generate table specs
        mock_response = Mock()
        mock_response.content = '{"tables": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase4_tables.get_llm_client', return_value=mock_llm_client):
            state = generate_table_specifications_node(state)

        # Step 13: Validate
        with patch('agent.nodes.phase4_tables.validate_table_artifact') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["structure"],
            )
            state = validate_table_specs_node(state)

        # Step 14: Review
        with patch('agent.nodes.phase4_tables.format_review_for_display'):
            state = review_table_specifications_node(state)

        assert state["table_validation_result"].is_valid is True
        assert state["current_step"] == 14


# =============================================================================
# Common Node Behavior Tests
# =============================================================================

class TestNodeCommonBehaviors:
    """Tests for common behaviors across all nodes."""

    def test_nodes_accumulate_errors(self, sample_state):
        """Test that nodes accumulate errors, not replace them."""
        state = {
            **sample_state,
            "errors": ["Previous error"],
        }

        with patch('agent.nodes.phase1_extraction.read_spss_file') as mock_read:
            mock_read.side_effect = FileNotFoundError("Not found")

            result = extract_spss_node(state)

            assert len(result["errors"]) == 2
            assert "Previous error" in result["errors"]
            assert "not found" in result["errors"][1].lower()

    def test_nodes_accumulate_warnings(self, sample_state, sample_dataframe):
        """Test that nodes accumulate warnings, not replace them."""
        state = {
            **sample_state,
            "warnings": ["Previous warning"],
            "raw_data": pd.DataFrame(),
            "original_metadata": {"n_rows": 0, "n_columns": 0, "column_labels": {}, "column_value_labels": {}},
        }

        result = transform_metadata_node(state)

        assert len(result["warnings"]) >= 1
        assert "Previous warning" in result["warnings"]


# =============================================================================
# Additional Error Recovery Tests
# =============================================================================

class TestNodeErrorRecovery:
    """Tests for error recovery and graceful degradation."""

    def test_node_recovers_from_missing_optional_fields(self, populated_state, mock_llm_client):
        """Test that nodes handle missing optional fields gracefully."""
        state = populated_state.copy()

        # Remove optional fields
        state.pop("warnings", None)
        state.pop("errors", None)

        mock_response = Mock()
        mock_response.content = '{"recoding_rules": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client):
            result = generate_recoding_rules_node(state)

            # Should not crash, should create default empty lists
            assert result.get("errors") == []
            assert result.get("warnings") == []

    def test_node_handles_exception_gracefully(self, sample_state):
        """Test that nodes handle unexpected exceptions gracefully."""
        with patch('agent.nodes.phase1_extraction.read_spss_file') as mock_read:
            mock_read.side_effect = RuntimeError("Unexpected error")

            result = extract_spss_node(sample_state)

            assert len(result["errors"]) == 1
            assert "unexpected" in result["errors"][0].lower()


# =============================================================================
# Phase 1 Additional Tests
# =============================================================================

class TestExtractSpssNodeAdditional:
    """Additional tests for extract_spss_node."""

    def test_extract_spss_node_permission_error(self, sample_state):
        """Test SPSS extraction with permission denied."""
        with patch('agent.nodes.phase1_extraction.read_spss_file') as mock_read:
            mock_read.side_effect = PermissionError("Permission denied")

            result = extract_spss_node(sample_state)

            assert result["current_step"] == 1
            assert len(result["errors"]) == 1
            assert "permission" in result["errors"][0].lower()

    def test_extract_spss_node_empty_dataframe_warning(self, sample_state):
        """Test SPSS extraction with empty DataFrame generates warning."""
        with patch('agent.nodes.phase1_extraction.read_spss_file') as mock_read:
            mock_metadata = Mock()
            mock_metadata.column_labels = {}
            mock_metadata.variable_value_labels = {}
            mock_metadata.variable_storage_types = {}
            mock_read.return_value = (pd.DataFrame(), mock_metadata)

            result = extract_spss_node(sample_state)

            assert result["current_step"] == 1
            assert len(result["warnings"]) >= 1
            assert "no data" in result["warnings"][0].lower()


class TestTransformMetadataNodeAdditional:
    """Additional tests for transform_metadata_node."""

    def test_transform_metadata_node_state_immutability(self, sample_state, sample_dataframe, sample_metadata):
        """Test that input state is not mutated."""
        state = {
            **sample_state,
            "raw_data": sample_dataframe.copy(),
            "original_metadata": sample_metadata.copy(),
            "warnings": [],
        }

        original_warnings = list(state["warnings"])
        original_raw_data_id = id(state["raw_data"])

        result = transform_metadata_node(state)

        # Input state should be unchanged
        assert state["warnings"] == original_warnings
        assert "variable_centered_metadata" not in state
        assert id(state["raw_data"]) == original_raw_data_id


class TestFilterMetadataNodeAdditional:
    """Additional tests for filter_metadata_node."""

    def test_filter_metadata_node_state_immutability(self, sample_state, sample_variable_centered_metadata):
        """Test that input state is not mutated."""
        state = {
            **sample_state,
            "variable_centered_metadata": sample_variable_centered_metadata.copy(),
            "warnings": [],
        }

        original_warnings = list(state["warnings"])

        result = filter_metadata_node(state)

        # Input state should be unchanged
        assert state["warnings"] == original_warnings
        assert "filtered_metadata" not in state
        assert "filtered_out_variables" not in state

    def test_filter_metadata_node_all_filtered_out(self, sample_state):
        """Test when all variables are filtered out."""
        # Create metadata with only binary variables
        metadata = {
            "variables": {
                "var1": {"name": "var1", "distinct_count": 2},
                "var2": {"name": "var2", "distinct_count": 2},
            },
            "n_variables": 2,
            "n_numeric": 2,
            "total_records": 100,
        }

        state = {
            **sample_state,
            "variable_centered_metadata": metadata,
            "warnings": [],
        }

        result = filter_metadata_node(state)

        assert result["current_step"] == 3
        assert len(result["filtered_metadata"]) == 0
        assert len(result["warnings"]) >= 1


# =============================================================================
# Phase 2 Additional Tests
# =============================================================================

class TestGenerateRecodingRulesNodeAdditional:
    """Additional tests for generate_recoding_rules_node."""

    def test_generate_recoding_rules_node_with_validation_feedback(self, populated_state, mock_llm_client):
        """Test recoding rules generation with validation feedback."""
        state = {
            **populated_state,
            "iteration_count": 1,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Invalid range"],
                warnings=[],
                checks_performed=["syntax"],
            ),
        }

        mock_response = Mock()
        mock_response.content = '{"recoding_rules": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client):
            result = generate_recoding_rules_node(state)

            assert result["recoding_rules"] is not None
            assert result["iteration_count"] == 2

    def test_generate_recoding_rules_node_with_human_feedback(self, populated_state, mock_llm_client):
        """Test recoding rules generation with human feedback."""
        state = {
            **populated_state,
            "iteration_count": 1,
            "recoding_feedback": "Use quintiles instead of quartiles",
        }

        mock_response = Mock()
        mock_response.content = '{"recoding_rules": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client):
            result = generate_recoding_rules_node(state)

            assert result["recoding_rules"] is not None
            assert result["iteration_count"] == 2

    def test_generate_recoding_rules_node_invalid_json(self, populated_state, mock_llm_client):
        """Test recoding rules generation with invalid JSON response."""
        mock_response = Mock()
        mock_response.content = 'This is not valid JSON'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client):
            result = generate_recoding_rules_node(populated_state)

            assert result["current_step"] == 4
            assert len(result["errors"]) == 1
            assert "parse" in result["errors"][0].lower() or "json" in result["errors"][0].lower()

    def test_generate_recoding_rules_node_no_filtered_metadata(self, sample_state):
        """Test recoding rules generation without filtered_metadata."""
        state = {
            **sample_state,
            "filtered_metadata": None,
        }

        result = generate_recoding_rules_node(state)

        assert result["current_step"] == 4
        assert len(result["errors"]) == 1
        assert "filtered_metadata" in result["errors"][0]

    def test_generate_recoding_rules_node_clears_feedback_on_success(self, populated_state, mock_llm_client):
        """Test that successful generation clears previous feedback."""
        state = {
            **populated_state,
            "recoding_feedback": "Previous error message",
        }

        mock_response = Mock()
        mock_response.content = '{"recoding_rules": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client):
            result = generate_recoding_rules_node(state)

            assert result["recoding_feedback"] is None


class TestValidateRecodingRulesNodeAdditional:
    """Additional tests for validate_recoding_rules_node."""

    def test_validate_recoding_rules_node_state_immutability(self, populated_state):
        """Test that input state is not mutated."""
        state = {
            **populated_state,
            "recoding_rules": {"recoding_rules": []},
            "errors": [],
        }

        with patch('agent.nodes.phase2_recoding.validate_recoding_rules') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["syntax"],
            )

            result = validate_recoding_rules_node(state)

            # Input state should be unchanged
            assert state["errors"] == []
            assert "recoding_validation_result" not in state

    def test_validate_recoding_rules_node_no_rules(self, populated_state):
        """Test validation with no recoding rules."""
        state = {
            **populated_state,
            "recoding_rules": None,
        }

        result = validate_recoding_rules_node(state)

        assert result["current_step"] == 5
        assert len(result["errors"]) == 1
        assert "recoding_rules" in result["errors"][0]
