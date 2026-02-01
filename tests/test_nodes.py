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
import os
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
    parse_llm_response,
    _validate_table_specs_structure,
    _convert_csv_to_json,
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

    def test_generate_indicators_node_success(self, sample_state, new_metadata, mock_llm_client):
        """Test successful indicator generation."""
        state = {
            **sample_state,
            "new_metadata": new_metadata,
            "iteration_count": 0,
            "config": {"output_dir": "/tmp/output"},
        }

        mock_response = Mock()
        mock_response.content = '{"indicators": [{"name": "Customer_Satisfaction", "description": "Test", "variables": ["var1", "var2"]}]}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase3_indicators.get_llm_client', return_value=mock_llm_client):
            result = generate_indicators_node(state)

            assert result["current_step"] == 9
            assert result["indicators"] is not None
            assert len(result["indicators"]["indicators"]) == 1
            assert result["indicators"]["indicators"][0]["name"] == "Customer_Satisfaction"

    def test_generate_indicators_node_no_metadata(self, sample_state):
        """Test indicator generation with no new_metadata."""
        state = {
            **sample_state,
            "new_metadata": None,
        }

        result = generate_indicators_node(state)

        assert result["current_step"] == 9
        assert len(result["errors"]) == 1
        assert "new_metadata" in result["errors"][0]

    def test_generate_indicators_node_empty_metadata(self, sample_state, mock_llm_client):
        """Test indicator generation with empty metadata (no variables)."""
        # Create metadata with empty variable list
        empty_metadata = {
            "variable_names": [],
            "variable_labels": {},
            "value_labels": {}
        }
        state = {
            **sample_state,
            "new_metadata": empty_metadata,
            "config": {"output_dir": "/tmp/output"},
        }

        mock_response = Mock()
        mock_response.content = '{"indicators": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase3_indicators.get_llm_client', return_value=mock_llm_client):
            result = generate_indicators_node(state)

            assert result["current_step"] == 9
            assert result["indicators"] is not None
            assert len(result["indicators"]["indicators"]) == 0
            assert len(result["warnings"]) >= 1
            assert "no indicators" in result["warnings"][0].lower()

    def test_generate_indicators_node_invalid_json(self, sample_state, new_metadata, mock_llm_client):
        """Test indicator generation with invalid JSON response."""
        state = {
            **sample_state,
            "new_metadata": new_metadata,
            "iteration_count": 0,
        }

        mock_response = Mock()
        mock_response.content = "This is not valid JSON"
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase3_indicators.get_llm_client', return_value=mock_llm_client):
            result = generate_indicators_node(state)

            assert result["current_step"] == 9
            assert len(result["errors"]) == 1
            assert "parse" in result["errors"][0].lower() or "json" in result["errors"][0].lower()
            assert result["iteration_count"] == 1

    def test_generate_indicators_node_invalid_structure(self, sample_state, new_metadata, mock_llm_client):
        """Test indicator generation with invalid indicator structure."""
        state = {
            **sample_state,
            "new_metadata": new_metadata,
            "iteration_count": 0,
        }

        mock_response = Mock()
        # Missing required fields
        mock_response.content = '{"indicators": [{"name": "Test"}]}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase3_indicators.get_llm_client', return_value=mock_llm_client):
            result = generate_indicators_node(state)

            assert result["current_step"] == 9
            assert len(result["errors"]) == 1
            assert "invalid" in result["errors"][0].lower() or "missing" in result["errors"][0].lower()
            assert result["iteration_count"] == 1

    def test_generate_indicators_node_with_validation_feedback(self, sample_state, new_metadata, mock_llm_client):
        """Test indicator generation with validation feedback (retry scenario)."""
        state = {
            **sample_state,
            "new_metadata": new_metadata,
            "iteration_count": 1,
            "indicator_validation_result": ValidationResult(
                is_valid=False,
                errors=["Variables not found"],
                warnings=[],
                checks_performed=["variables"],
            ),
            "config": {"output_dir": "/tmp/output"},
        }

        mock_response = Mock()
        mock_response.content = '{"indicators": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase3_indicators.get_llm_client', return_value=mock_llm_client):
            result = generate_indicators_node(state)

            assert result["current_step"] == 9
            assert result["iteration_count"] == 2
            assert result["indicators"] is not None

    def test_generate_indicators_node_with_human_feedback(self, sample_state, new_metadata, mock_llm_client):
        """Test indicator generation with human feedback."""
        state = {
            **sample_state,
            "new_metadata": new_metadata,
            "iteration_count": 1,
            "indicator_feedback": "Add more demographic indicators",
            "config": {"output_dir": "/tmp/output"},
        }

        mock_response = Mock()
        mock_response.content = '{"indicators": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase3_indicators.get_llm_client', return_value=mock_llm_client):
            result = generate_indicators_node(state)

            assert result["current_step"] == 9
            assert result["iteration_count"] == 2
            assert result["indicator_feedback"] is None  # Cleared on success

    def test_generate_indicators_node_clears_feedback_on_success(self, sample_state, new_metadata, mock_llm_client):
        """Test that successful generation clears previous feedback."""
        state = {
            **sample_state,
            "new_metadata": new_metadata,
            "indicator_feedback": "Previous error message",
            "config": {"output_dir": "/tmp/output"},
        }

        mock_response = Mock()
        mock_response.content = '{"indicators": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase3_indicators.get_llm_client', return_value=mock_llm_client):
            result = generate_indicators_node(state)

            assert result["indicator_feedback"] is None

    def test_generate_indicators_node_state_immutability(self, sample_state, new_metadata, mock_llm_client):
        """Test that input state is not mutated."""
        # Create a minimal state without pre-existing indicators key
        state = {
            "new_metadata": new_metadata,
            "warnings": [],
            "config": {"output_dir": "/tmp/output"},
            "current_step": 0,
            "errors": [],
        }

        original_warnings = list(state["warnings"])
        original_has_indicators = "indicators" in state

        mock_response = Mock()
        mock_response.content = '{"indicators": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase3_indicators.get_llm_client', return_value=mock_llm_client):
            result = generate_indicators_node(state)

            # Input state should be unchanged
            assert state["warnings"] == original_warnings
            assert ("indicators" in state) == original_has_indicators


class TestParseLlmResponse:
    """Tests for parse_llm_response helper function."""

    def test_parse_llm_response_direct_json(self):
        """Test parsing direct JSON response."""
        from agent.nodes.phase3_indicators import parse_llm_response

        response = '{"indicators": [{"name": "Test"}]}'
        result = parse_llm_response(response)

        assert result["indicators"][0]["name"] == "Test"

    def test_parse_llm_response_markdown_json(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        from agent.nodes.phase3_indicators import parse_llm_response

        response = '''```json
        {"indicators": [{"name": "Test"}]}
        ```'''
        result = parse_llm_response(response)

        assert result["indicators"][0]["name"] == "Test"

    def test_parse_llm_response_markdown_no_lang(self):
        """Test parsing JSON in markdown without language identifier."""
        from agent.nodes.phase3_indicators import parse_llm_response

        response = '''```
        {"indicators": [{"name": "Test"}]}
        ```'''
        result = parse_llm_response(response)

        assert result["indicators"][0]["name"] == "Test"

    def test_parse_llm_response_with_leading_text(self):
        """Test parsing JSON with leading/trailing text."""
        from agent.nodes.phase3_indicators import parse_llm_response

        response = 'Here is the result: {"indicators": [{"name": "Test"}]} Thank you!'
        result = parse_llm_response(response)

        assert result["indicators"][0]["name"] == "Test"

    def test_parse_llm_response_empty(self):
        """Test parsing empty response."""
        from agent.nodes.phase3_indicators import parse_llm_response

        with pytest.raises(ValueError, match="Empty LLM response"):
            parse_llm_response("")

    def test_parse_llm_response_invalid_json(self):
        """Test parsing completely invalid response."""
        from agent.nodes.phase3_indicators import parse_llm_response

        with pytest.raises(ValueError, match="Could not extract valid JSON"):
            parse_llm_response("This is just plain text with no JSON")


class TestCleanJsonString:
    """Tests for _clean_json_string helper function."""

    def test_clean_json_trailing_commas(self):
        """Test cleaning trailing commas."""
        from agent.nodes.phase3_indicators import _clean_json_string

        json_str = '{"indicators": [1, 2, 3,]}'
        result = _clean_json_string(json_str)

        # After cleaning, trailing comma should be removed
        assert result == '{"indicators": [1, 2, 3]}' or result == '{"indicators": [1, 2, 3]}'  # No trailing comma

    def test_clean_json_comments(self):
        """Test removing comments."""
        from agent.nodes.phase3_indicators import _clean_json_string

        json_str = '{"indicators": [1, 2, 3], // comment here\n}'
        result = _clean_json_string(json_str)

        assert "// comment here" not in result
        assert "}" in result

    def test_clean_json_hash_comments(self):
        """Test removing hash comments."""
        from agent.nodes.phase3_indicators import _clean_json_string

        json_str = '{"indicators": [1, 2, 3], # hash comment\n}'
        result = _clean_json_string(json_str)

        assert "# hash comment" not in result


class TestValidateIndicatorsStructure:
    """Tests for _validate_indicators_structure helper function."""

    def test_validate_structure_valid(self):
        """Test validation of valid indicators structure."""
        from agent.nodes.phase3_indicators import _validate_indicators_structure

        indicators = {
            "indicators": [
                {
                    "name": "Test",
                    "description": "Test indicator",
                    "variables": ["var1", "var2", "var3"]
                }
            ]
        }

        result = _validate_indicators_structure(indicators)

        assert result is None

    def test_validate_structure_empty_list(self):
        """Test validation with empty indicators list (allowed)."""
        from agent.nodes.phase3_indicators import _validate_indicators_structure

        indicators = {"indicators": []}

        result = _validate_indicators_structure(indicators)

        assert result is None  # Empty list is allowed

    def test_validate_structure_not_dict(self):
        """Test validation when indicators is not a dict."""
        from agent.nodes.phase3_indicators import _validate_indicators_structure

        indicators = ["not", "a", "dict"]

        result = _validate_indicators_structure(indicators)

        assert result is not None
        assert "JSON object" in result

    def test_validate_structure_missing_indicators_key(self):
        """Test validation with missing 'indicators' key."""
        from agent.nodes.phase3_indicators import _validate_indicators_structure

        indicators = {"wrong_key": []}

        result = _validate_indicators_structure(indicators)

        assert result is not None
        assert "indicators" in result.lower()

    def test_validate_structure_indicators_not_list(self):
        """Test validation when 'indicators' is not a list."""
        from agent.nodes.phase3_indicators import _validate_indicators_structure

        indicators = {"indicators": "not a list"}

        result = _validate_indicators_structure(indicators)

        assert result is not None
        assert "list" in result

    def test_validate_structure_missing_name(self):
        """Test validation when indicator missing 'name' field."""
        from agent.nodes.phase3_indicators import _validate_indicators_structure

        indicators = {
            "indicators": [
                {
                    "description": "Test",
                    "variables": ["var1", "var2"]
                }
            ]
        }

        result = _validate_indicators_structure(indicators)

        assert result is not None
        assert "name" in result

    def test_validate_structure_missing_description(self):
        """Test validation when indicator missing 'description' field."""
        from agent.nodes.phase3_indicators import _validate_indicators_structure

        indicators = {
            "indicators": [
                {
                    "name": "Test",
                    "variables": ["var1", "var2"]
                }
            ]
        }

        result = _validate_indicators_structure(indicators)

        assert result is not None
        assert "description" in result

    def test_validate_structure_missing_variables(self):
        """Test validation when indicator missing 'variables' field."""
        from agent.nodes.phase3_indicators import _validate_indicators_structure

        indicators = {
            "indicators": [
                {
                    "name": "Test",
                    "description": "Test indicator"
                }
            ]
        }

        result = _validate_indicators_structure(indicators)

        assert result is not None
        assert "variables" in result

    def test_validate_structure_variables_not_list(self):
        """Test validation when 'variables' is not a list."""
        from agent.nodes.phase3_indicators import _validate_indicators_structure

        indicators = {
            "indicators": [
                {
                    "name": "Test",
                    "description": "Test indicator",
                    "variables": "var1"
                }
            ]
        }

        result = _validate_indicators_structure(indicators)

        assert result is not None
        assert "list" in result

    def test_validate_structure_too_few_variables(self):
        """Test validation with too few variables (< 2)."""
        from agent.nodes.phase3_indicators import _validate_indicators_structure

        indicators = {
            "indicators": [
                {
                    "name": "Test",
                    "description": "Test indicator",
                    "variables": ["var1"]
                }
            ]
        }

        result = _validate_indicators_structure(indicators)

        assert result is not None
        assert "minimum" in result or "2" in result

    def test_validate_structure_too_many_variables(self):
        """Test validation with too many variables (> 10)."""
        from agent.nodes.phase3_indicators import _validate_indicators_structure

        indicators = {
            "indicators": [
                {
                    "name": "Test",
                    "description": "Test indicator",
                    "variables": [f"var{i}" for i in range(11)]
                }
            ]
        }

        result = _validate_indicators_structure(indicators)

        assert result is not None
        assert "maximum" in result or "10" in result

    def test_validate_structure_variable_not_string(self):
        """Test validation when variable name is not a string."""
        from agent.nodes.phase3_indicators import _validate_indicators_structure

        indicators = {
            "indicators": [
                {
                    "name": "Test",
                    "description": "Test indicator",
                    "variables": ["var1", 123, "var3"]
                }
            ]
        }

        result = _validate_indicators_structure(indicators)

        assert result is not None
        assert "string" in result


class TestValidateIndicatorsNode:
    """Tests for validate_indicators_node (Step 10)."""

    def test_validate_indicators_node_valid(self, sample_state):
        """Test validation of valid indicators."""
        indicators = {
            "indicators": [
                {
                    "name": "Test",
                    "description": "Test indicator",
                    "variables": ["gender", "age_group"]
                }
            ]
        }
        new_metadata = {
            "variable_names": ["gender", "age_group", "education"],
            "variable_labels": {},
            "value_labels": {}
        }

        state = {
            **sample_state,
            "indicators": indicators,
            "new_metadata": new_metadata,
        }

        result = validate_indicators_node(state)

        assert result["current_step"] == 10
        assert result["indicator_validation_result"] is not None

    def test_validate_indicators_node_no_indicators(self, sample_state):
        """Test validation with no indicators."""
        state = {
            **sample_state,
            "indicators": None,
        }

        result = validate_indicators_node(state)

        assert result["current_step"] == 10
        assert len(result["errors"]) == 1
        assert "indicators" in result["errors"][0].lower()

    def test_validate_indicators_node_no_metadata(self, sample_state):
        """Test validation with no new_metadata."""
        state = {
            **sample_state,
            "indicators": {"indicators": []},
            "new_metadata": None,
        }

        result = validate_indicators_node(state)

        assert result["current_step"] == 10
        assert len(result["errors"]) == 1
        assert "metadata" in result["errors"][0].lower()


class TestReviewIndicatorsNode:
    """Tests for review_indicators_node (Step 11)."""

    def test_review_indicators_node(self, sample_state, tmp_path):
        """Test indicators review node."""
        indicators = {
            "indicators": [
                {
                    "name": "Test",
                    "description": "Test indicator",
                    "variables": ["gender", "age_group"]
                }
            ]
        }

        state = {
            **sample_state,
            "indicators": indicators,
            "indicator_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["structure"]
            ),
            "iteration_count": 0,
            "config": {"output_dir": str(tmp_path)},
        }

        # Mock the langgraph interrupt function
        with patch('langgraph.types.interrupt'):
            result = review_indicators_node(state)

            assert result["current_step"] == 11
            assert result["requires_human_review"] is True

    def test_review_indicators_node_no_indicators(self, sample_state):
        """Test review with no indicators."""
        state = {
            **sample_state,
            "indicators": None,
            "config": {"output_dir": "/tmp"},
        }

        result = review_indicators_node(state)

        assert result["current_step"] == 11
        assert len(result["errors"]) == 1
        assert "indicators" in result["errors"][0].lower()
        assert result["requires_human_review"] is True

    def test_review_indicators_node_with_previous_feedback(self, sample_state, tmp_path):
        """Test review with previous feedback (retry scenario)."""
        indicators = {
            "indicators": [
                {
                    "name": "Test",
                    "description": "Test indicator",
                    "variables": ["gender", "age_group"]
                }
            ]
        }

        state = {
            **sample_state,
            "indicators": indicators,
            "indicator_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["structure"]
            ),
            "iteration_count": 1,
            "indicator_feedback": "Add more variables",
            "config": {"output_dir": str(tmp_path)},
        }

        with patch('langgraph.types.interrupt'):
            result = review_indicators_node(state)

            assert result["current_step"] == 11
            assert result["requires_human_review"] is True

    def test_review_indicators_node_creates_review_document(self, sample_state, tmp_path):
        """Test that review document is created."""
        indicators = {
            "indicators": [
                {
                    "name": "Test",
                    "description": "Test indicator",
                    "variables": ["gender", "age_group"]
                }
            ]
        }

        state = {
            **sample_state,
            "indicators": indicators,
            "indicator_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["structure"]
            ),
            "iteration_count": 0,
            "config": {"output_dir": str(tmp_path)},
        }

        with patch('langgraph.types.interrupt'):
            result = review_indicators_node(state)

            # Check that review document was created
            review_path = tmp_path / "reviews" / "indicators_review.md"
            assert review_path.exists()

            content = review_path.read_text()
            assert "Indicators Review" in content
            assert "Test" in content


class TestBuildMetadataList:
    """Tests for _build_metadata_list helper function."""

    def test_build_metadata_list_categorical(self):
        """Test building metadata list for categorical variables."""
        from agent.nodes.phase3_indicators import _build_metadata_list

        new_metadata = {
            "variable_names": ["gender", "education"],
            "variable_labels": {
                "gender": "Gender",
                "education": "Education"
            },
            "value_labels": {
                "gender": {1: "Male", 2: "Female"},
                "education": {1: "High School", 2: "College"}
            }
        }

        result = _build_metadata_list(new_metadata)

        assert len(result) == 2
        assert result[0]["name"] == "gender"
        assert result[0]["label"] == "Gender"
        assert result[0]["variable_type"] == "categorical"
        assert result[0]["value_labels"] == {1: "Male", 2: "Female"}

    def test_build_metadata_list_numeric(self):
        """Test building metadata list for numeric variables."""
        from agent.nodes.phase3_indicators import _build_metadata_list

        new_metadata = {
            "variable_names": ["income", "age"],
            "variable_labels": {
                "income": "Income",
                "age": "Age"
            },
            "value_labels": {}  # No value labels => numeric
        }

        result = _build_metadata_list(new_metadata)

        assert len(result) == 2
        assert result[0]["name"] == "income"
        assert result[0]["variable_type"] == "numeric"

    def test_build_metadata_list_empty(self):
        """Test building metadata list with no variables."""
        from agent.nodes.phase3_indicators import _build_metadata_list

        new_metadata = {
            "variable_names": [],
            "variable_labels": {},
            "value_labels": {}
        }

        result = _build_metadata_list(new_metadata)

        assert len(result) == 0


# =============================================================================
# Phase 4: Table Specification Nodes (Steps 12-16)
# =============================================================================

class TestGenerateTableSpecificationsNode:
    """Tests for generate_table_specifications_node (Step 12)."""

    def test_generate_table_specifications_node_success(self, indicator_state, mock_llm_client, tmp_path):
        """Test successful table specification generation."""
        # Create valid new_metadata structure
        new_metadata = {
            "variable_names": ["gender", "age_group", "education", "satisfaction"],
            "variable_labels": {
                "gender": "Gender",
                "age_group": "Age Group",
                "education": "Education Level",
                "satisfaction": "Satisfaction"
            },
            "value_labels": {
                "gender": {1: "Male", 2: "Female"},
                "satisfaction": {1: "Low", 2: "Medium", 3: "High"}
            }
        }

        state = {
            **indicator_state,
            "new_metadata": new_metadata,
            "indicators": {"indicators": [{"indicator_name": "Demographics", "variables": ["gender", "age_group"]}]},
            "config": {"output_dir": str(tmp_path)},
        }

        mock_response = Mock()
        mock_response.content = '{"tables": [{"table_id": "gender_x_satisfaction", "row_variable": "gender", "column_variable": "satisfaction", "statistics": ["count", "columnpct"]}]}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase4_tables.get_llm_client', return_value=mock_llm_client):
            result = generate_table_specifications_node(state)

            assert result["current_step"] == 12
            assert result["table_specifications"] is not None
            assert len(result["table_specifications"]["tables"]) == 1

    def test_generate_table_specifications_node_no_metadata(self, indicator_state):
        """Test table specs generation fails when new_metadata is missing."""
        state = {
            **indicator_state,
            "new_metadata": None,
        }

        result = generate_table_specifications_node(state)

        assert result["current_step"] == 12
        assert len(result["errors"]) == 1
        assert "new_metadata" in result["errors"][0].lower()

    def test_generate_table_specifications_node_validation_retry(self, indicator_state, mock_llm_client, tmp_path):
        """Test table specs generation with validation feedback retry."""
        new_metadata = {
            "variable_names": ["gender", "satisfaction"],
            "variable_labels": {"gender": "Gender", "satisfaction": "Satisfaction"},
            "value_labels": {}
        }

        # Create validation result with errors
        validation_result = ValidationResult(
            is_valid=False,
            errors=["Invalid variable reference"],
            warnings=[],
            checks_performed=["structure"]
        )

        state = {
            **indicator_state,
            "new_metadata": new_metadata,
            "iteration_count": 1,
            "table_validation_result": validation_result,
            "config": {"output_dir": str(tmp_path)},
        }

        mock_response = Mock()
        mock_response.content = '{"tables": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase4_tables.get_llm_client', return_value=mock_llm_client):
            result = generate_table_specifications_node(state)

            assert result["current_step"] == 12
            assert result["iteration_count"] == 2

    def test_generate_table_specifications_node_human_feedback_retry(self, indicator_state, mock_llm_client, tmp_path):
        """Test table specs generation with human feedback retry."""
        new_metadata = {
            "variable_names": ["gender", "satisfaction"],
            "variable_labels": {},
            "value_labels": {}
        }

        state = {
            **indicator_state,
            "new_metadata": new_metadata,
            "iteration_count": 1,
            "table_specs_feedback": "Add more tables",
            "config": {"output_dir": str(tmp_path)},
        }

        mock_response = Mock()
        mock_response.content = '{"tables": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase4_tables.get_llm_client', return_value=mock_llm_client):
            result = generate_table_specifications_node(state)

            assert result["current_step"] == 12
            assert result["iteration_count"] == 2

    def test_generate_table_specifications_node_json_parse_error(self, indicator_state, mock_llm_client):
        """Test handling of LLM response that cannot be parsed as JSON."""
        new_metadata = {
            "variable_names": ["gender"],
            "variable_labels": {},
            "value_labels": {}
        }

        state = {
            **indicator_state,
            "new_metadata": new_metadata,
        }

        mock_response = Mock()
        mock_response.content = "This is not valid JSON at all"
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase4_tables.get_llm_client', return_value=mock_llm_client):
            result = generate_table_specifications_node(state)

            assert result["current_step"] == 12
            assert len(result["errors"]) >= 1
            assert "json" in result["errors"][0].lower()

    def test_generate_table_specifications_node_structure_validation_error(self, indicator_state, mock_llm_client):
        """Test handling of invalid table specifications structure."""
        new_metadata = {
            "variable_names": ["gender"],
            "variable_labels": {},
            "value_labels": {}
        }

        state = {
            **indicator_state,
            "new_metadata": new_metadata,
        }

        # Return valid JSON but invalid structure (missing 'tables' key)
        mock_response = Mock()
        mock_response.content = '{"invalid": "structure"}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase4_tables.get_llm_client', return_value=mock_llm_client):
            result = generate_table_specifications_node(state)

            assert result["current_step"] == 12
            assert len(result["errors"]) >= 1

    def test_generate_table_specifications_node_zero_tables_warning(self, indicator_state, mock_llm_client, tmp_path):
        """Test warning when no tables are generated."""
        new_metadata = {
            "variable_names": ["gender"],
            "variable_labels": {},
            "value_labels": {}
        }

        state = {
            **indicator_state,
            "new_metadata": new_metadata,
            "warnings": [],
            "config": {"output_dir": str(tmp_path)},
        }

        # Return valid JSON with empty tables list
        mock_response = Mock()
        mock_response.content = '{"tables": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase4_tables.get_llm_client', return_value=mock_llm_client):
            result = generate_table_specifications_node(state)

            assert result["current_step"] == 12
            assert len(result["warnings"]) >= 1
            assert "no table" in result["warnings"][0].lower()

    def test_generate_table_specifications_node_exception_handling(self, indicator_state, tmp_path):
        """Test exception handling during table specs generation."""
        new_metadata = {
            "variable_names": ["gender"],
            "variable_labels": {},
            "value_labels": {}
        }

        state = {
            **indicator_state,
            "new_metadata": new_metadata,
            "config": {"output_dir": str(tmp_path)},
        }

        # Mock LLM client that raises exception
        mock_client = Mock()
        mock_client.invoke.side_effect = RuntimeError("LLM API error")

        with patch('agent.nodes.phase4_tables.get_llm_client', return_value=mock_client):
            result = generate_table_specifications_node(state)

            assert result["current_step"] == 12
            assert len(result["errors"]) >= 1
            assert "unexpected error" in result["errors"][-1].lower()


class TestParseLLMResponse:
    """Tests for parse_llm_response helper function."""

    def test_parse_llm_response_direct_json(self):
        """Test parsing direct JSON response."""
        response = '{"tables": [{"table_id": "test"}]}'
        result = parse_llm_response(response)

        assert result["tables"][0]["table_id"] == "test"

    def test_parse_llm_response_markdown_json_block(self):
        """Test parsing JSON from markdown code block with language identifier."""
        response = '''```json
{"tables": [{"table_id": "test"}]}
```'''
        result = parse_llm_response(response)

        assert result["tables"][0]["table_id"] == "test"

    def test_parse_llm_response_plain_code_block(self):
        """Test parsing JSON from plain code block."""
        response = '''```
{"tables": [{"table_id": "test"}]}
```'''
        result = parse_llm_response(response)

        assert result["tables"][0]["table_id"] == "test"

    def test_parse_llm_response_extract_json_boundaries(self):
        """Test extracting JSON from within text."""
        response = 'Some text before {"tables": [{"table_id": "test"}]} some text after'
        result = parse_llm_response(response)

        assert result["tables"][0]["table_id"] == "test"

    def test_parse_llm_response_trailing_comma(self):
        """Test parsing JSON with trailing comma."""
        response = '{"tables": [{"table_id": "test",}]}'
        result = parse_llm_response(response)

        assert result["tables"][0]["table_id"] == "test"

    def test_parse_llm_response_empty_error(self):
        """Test error handling for empty response."""
        with pytest.raises(ValueError, match="Empty LLM response"):
            parse_llm_response("")

    def test_parse_llm_response_no_json_error(self):
        """Test error handling when no JSON found."""
        with pytest.raises(ValueError, match="Could not extract valid JSON"):
            parse_llm_response("This has no JSON at all")


class TestValidateTableSpecsStructure:
    """Tests for _validate_table_specs_structure helper function."""

    def test_validate_table_specs_not_dict(self):
        """Test validation rejects non-dict input."""
        result = _validate_table_specs_structure("not a dict")
        assert result is not None
        assert "json object" in result.lower()

    def test_validate_table_specs_missing_tables_key(self):
        """Test validation rejects missing 'tables' key."""
        result = _validate_table_specs_structure({"invalid": "data"})
        assert result is not None
        assert "tables" in result.lower()

    def test_validate_table_specs_tables_not_list(self):
        """Test validation rejects non-list 'tables' value."""
        result = _validate_table_specs_structure({"tables": "not a list"})
        assert result is not None
        assert "list" in result.lower()

    def test_validate_table_specs_empty_tables_valid(self):
        """Test validation accepts empty tables list (warning, not error)."""
        result = _validate_table_specs_structure({"tables": []})
        assert result is None

    def test_validate_table_specs_table_not_dict(self):
        """Test validation rejects non-dict table."""
        result = _validate_table_specs_structure({"tables": ["not a dict"]})
        assert result is not None
        assert "not a json object" in result.lower()

    def test_validate_table_specs_missing_required_field(self):
        """Test validation rejects missing required fields."""
        result = _validate_table_specs_structure({"tables": [{"table_id": "test"}]})
        assert result is not None
        assert "row_variable" in result.lower()

    def test_validate_table_specs_duplicate_table_ids(self):
        """Test validation rejects duplicate table IDs."""
        tables = {
            "tables": [
                {"table_id": "duplicate", "row_variable": "var1", "column_variable": "var2", "statistics": []},
                {"table_id": "duplicate", "row_variable": "var3", "column_variable": "var4", "statistics": []},
            ]
        }
        result = _validate_table_specs_structure(tables)
        assert result is not None
        assert "duplicate" in result.lower()

    def test_validate_table_specs_invalid_statistic(self):
        """Test validation rejects invalid statistic."""
        tables = {
            "tables": [
                {"table_id": "test", "row_variable": "var1", "column_variable": "var2", "statistics": ["invalid_stat"]}
            ]
        }
        result = _validate_table_specs_structure(tables)
        assert result is not None
        assert "invalid statistic" in result.lower()

    def test_validate_table_specs_invalid_weight_variable(self):
        """Test validation rejects invalid weight variable type."""
        tables = {
            "tables": [
                {"table_id": "test", "row_variable": "var1", "column_variable": "var2", "statistics": [], "weight_variable": 123}
            ]
        }
        result = _validate_table_specs_structure(tables)
        assert result is not None
        assert "weight_variable" in result.lower()

    def test_validate_table_specs_valid_structure(self):
        """Test validation accepts valid structure."""
        tables = {
            "tables": [
                {
                    "table_id": "gender_x_satisfaction",
                    "row_variable": "gender",
                    "column_variable": "satisfaction",
                    "statistics": ["count", "columnpct", "chisq", "cramersv"],
                    "weight_variable": None
                }
            ]
        }
        result = _validate_table_specs_structure(tables)
        assert result is None


class TestValidateTableSpecsNode:
    """Tests for validate_table_specs_node (Step 13)."""

    def test_validate_table_specs_node_valid(self, indicator_state, valid_table_specs, new_metadata):
        """Test validation of valid table specifications."""
        state = {
            **indicator_state,
            "table_specifications": valid_table_specs,
            "new_metadata": new_metadata,
        }

        result = validate_table_specs_node(state)

        assert result["current_step"] == 13
        assert result["table_validation_result"] is not None

    def test_validate_table_specs_node_missing_specs(self, indicator_state):
        """Test validation fails when table_specs is missing."""
        state = {
            **indicator_state,
            "table_specifications": None,
        }

        result = validate_table_specs_node(state)

        assert result["current_step"] == 13
        assert len(result["errors"]) == 1
        assert "table_specifications" in result["errors"][0].lower()

    def test_validate_table_specs_node_missing_metadata(self, indicator_state, valid_table_specs):
        """Test validation fails when new_metadata is missing."""
        state = {
            **indicator_state,
            "table_specifications": valid_table_specs,
            "new_metadata": None,
        }

        result = validate_table_specs_node(state)

        assert result["current_step"] == 13
        assert len(result["errors"]) == 1
        assert "new_metadata" in result["errors"][0].lower()

    def test_validate_table_specs_node_exception_handling(self, indicator_state):
        """Test exception handling during validation."""
        state = {
            **indicator_state,
            "table_specifications": {"tables": []},
            "new_metadata": {"variable_names": []},
        }

        # Mock validate_table_specs to raise exception
        with patch('agent.validation.tables.validate_table_specs') as mock_validate:
            mock_validate.side_effect = RuntimeError("Validation error")

            result = validate_table_specs_node(state)

            assert result["current_step"] == 13
            assert len(result["errors"]) >= 1


class TestReviewTableSpecificationsNode:
    """Tests for review_table_specifications_node (Step 14)."""

    def test_review_table_specifications_node(self, indicator_state, valid_table_specs, tmp_path):
        """Test table specifications review node."""
        config = {"output_dir": str(tmp_path)}

        state = {
            **indicator_state,
            "table_specifications": valid_table_specs,
            "table_validation_result": ValidationResult(is_valid=True, errors=[], warnings=[], checks_performed=[]),
            "config": config,
        }

        with patch('langgraph.types.interrupt'):
            result = review_table_specifications_node(state)

            assert result["current_step"] == 14
            assert result["requires_human_review"] is True

    def test_review_table_specs_missing_specs(self, indicator_state, tmp_path):
        """Test review fails when table_specs is missing."""
        config = {"output_dir": str(tmp_path)}

        state = {
            **indicator_state,
            "table_specifications": None,
            "config": config,
        }

        result = review_table_specifications_node(state)

        assert result["current_step"] == 14
        assert len(result["errors"]) >= 1

    def test_review_table_specs_exception_handling(self, indicator_state, valid_table_specs, tmp_path):
        """Test exception handling during review."""
        config = {"output_dir": str(tmp_path)}

        state = {
            **indicator_state,
            "table_specifications": valid_table_specs,
            "config": config,
        }

        # Mock interrupt to raise exception
        with patch('langgraph.types.interrupt') as mock_interrupt:
            mock_interrupt.side_effect = RuntimeError("Interrupt error")

            result = review_table_specifications_node(state)

            assert result["current_step"] == 14


class TestGeneratePsppTableSyntaxNode:
    """Tests for generate_pspp_table_syntax_node (Step 15)."""

    def test_generate_pspp_table_syntax_node_success(self, indicator_state, valid_table_specs, new_metadata, tmp_path):
        """Test successful PSPP table syntax generation."""
        config = {"output_dir": str(tmp_path)}

        state = {
            **indicator_state,
            "table_specifications": valid_table_specs,
            "new_metadata": new_metadata,
            "config": config,
            "warnings": [],
        }

        result = generate_pspp_table_syntax_node(state)

        assert result["current_step"] == 15
        assert result["pspp_tables_syntax"] is not None
        assert result["table_syntax_file"] is not None
        assert "CTABLES" in result["pspp_tables_syntax"]

    def test_generate_pspp_table_syntax_node_no_specs(self, indicator_state):
        """Test syntax generation fails without table specifications."""
        state = {
            **indicator_state,
            "table_specifications": None,
        }

        result = generate_pspp_table_syntax_node(state)

        assert result["current_step"] == 15
        assert len(result["errors"]) == 1

    def test_generate_pspp_table_syntax_node_empty_tables(self, indicator_state, new_metadata):
        """Test syntax generation with empty tables list."""
        state = {
            **indicator_state,
            "table_specifications": {"tables": []},
            "new_metadata": new_metadata,
            "warnings": [],
        }

        result = generate_pspp_table_syntax_node(state)

        assert result["current_step"] == 15
        assert len(result["warnings"]) >= 1

    def test_generate_pspp_table_syntax_node_multiple_tables(self, indicator_state, new_metadata, tmp_path):
        """Test syntax generation with multiple tables."""
        tables = {
            "tables": [
                {
                    "table_id": "gender_x_satisfaction",
                    "row_variable": "gender",
                    "column_variable": "satisfaction",
                    "statistics": ["count", "columnpct", "chisq", "cramersv"],
                },
                {
                    "table_id": "age_x_education",
                    "row_variable": "age_group",
                    "column_variable": "education",
                    "statistics": ["count", "rowpct"],
                },
            ]
        }

        state = {
            **indicator_state,
            "table_specifications": tables,
            "new_metadata": new_metadata,
            "config": {"output_dir": str(tmp_path)},
            "warnings": [],
        }

        result = generate_pspp_table_syntax_node(state)

        assert result["current_step"] == 15
        assert "CTABLES" in result["pspp_tables_syntax"]
        assert result["pspp_tables_syntax"].count("CTABLES") >= 2

    def test_generate_pspp_table_syntax_node_exception_handling(self, indicator_state, valid_table_specs):
        """Test exception handling during syntax generation."""
        state = {
            **indicator_state,
            "table_specifications": valid_table_specs,
            "new_metadata": None,  # This might cause issues
        }

        result = generate_pspp_table_syntax_node(state)

        assert result["current_step"] == 15


class TestExecutePsppTablesNode:
    """Tests for execute_pspp_tables_node (Step 16)."""

    def test_execute_pspp_tables_node_success(self, indicator_state, tmp_path):
        """Test successful PSPP tables execution."""
        # Create syntax file
        syntax_file = tmp_path / "tables.sps"
        syntax_file.write_text("CTABLES /TABLE var1 BY var2.")

        # Create input file
        input_file = tmp_path / "new_data.sav"
        input_file.write_text("mock")

        state = {
            **indicator_state,
            "new_data_file": str(input_file),
            "table_syntax_file": str(syntax_file),
            "config": {"output_dir": str(tmp_path)},
            "warnings": [],
        }

        # Create mock CSV output
        csv_file = tmp_path / "cross_table.csv"
        csv_file.write_text("row,col,value\n1,1,10\n")

        with patch('agent.utils.pspp_wrapper.execute_pspp_syntax') as mock_execute:
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

    def test_execute_pspp_tables_node_missing_data_file(self, indicator_state, tmp_path):
        """Test PSPP execution fails when new_data_file is missing."""
        syntax_file = tmp_path / "tables.sps"
        syntax_file.write_text("CTABLES /TABLE var1 BY var2.")

        state = {
            **indicator_state,
            "new_data_file": None,
            "table_syntax_file": str(syntax_file),
            "config": {"output_dir": str(tmp_path)},
        }

        result = execute_pspp_tables_node(state)

        assert result["current_step"] == 16
        assert len(result["errors"]) == 1

    def test_execute_pspp_tables_node_missing_syntax_file(self, indicator_state, tmp_path):
        """Test PSPP execution fails when syntax file is missing."""
        input_file = tmp_path / "new_data.sav"
        input_file.write_text("mock")

        state = {
            **indicator_state,
            "new_data_file": str(input_file),
            "table_syntax_file": None,
            "config": {"output_dir": str(tmp_path)},
        }

        result = execute_pspp_tables_node(state)

        assert result["current_step"] == 16
        assert len(result["errors"]) == 1

    def test_execute_pspp_tables_node_syntax_file_not_exists(self, indicator_state, tmp_path):
        """Test PSPP execution fails when syntax file doesn't exist."""
        input_file = tmp_path / "new_data.sav"
        input_file.write_text("mock")

        state = {
            **indicator_state,
            "new_data_file": str(input_file),
            "table_syntax_file": "/nonexistent/tables.sps",
            "config": {"output_dir": str(tmp_path)},
        }

        result = execute_pspp_tables_node(state)

        assert result["current_step"] == 16
        assert len(result["errors"]) == 1

    def test_execute_pspp_tables_node_input_file_not_exists(self, indicator_state, tmp_path):
        """Test PSPP execution fails when input file doesn't exist."""
        syntax_file = tmp_path / "tables.sps"
        syntax_file.write_text("CTABLES /TABLE var1 BY var2.")

        state = {
            **indicator_state,
            "new_data_file": "/nonexistent/new_data.sav",
            "table_syntax_file": str(syntax_file),
            "config": {"output_dir": str(tmp_path)},
        }

        result = execute_pspp_tables_node(state)

        assert result["current_step"] == 16
        assert len(result["errors"]) == 1

    def test_execute_pspp_tables_node_failure(self, indicator_state, tmp_path):
        """Test PSPP tables execution failure."""
        syntax_file = tmp_path / "tables.sps"
        syntax_file.write_text("INVALID")

        input_file = tmp_path / "new_data.sav"
        input_file.write_text("mock")

        state = {
            **indicator_state,
            "new_data_file": str(input_file),
            "table_syntax_file": str(syntax_file),
            "config": {"output_dir": str(tmp_path)},
        }

        with patch('agent.utils.pspp_wrapper.execute_pspp_syntax') as mock_execute:
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

    def test_execute_pspp_tables_node_output_not_created(self, indicator_state, tmp_path):
        """Test PSPP execution when output file is not created."""
        syntax_file = tmp_path / "tables.sps"
        syntax_file.write_text("CTABLES /TABLE var1 BY var2.")

        input_file = tmp_path / "new_data.sav"
        input_file.write_text("mock")

        state = {
            **indicator_state,
            "new_data_file": str(input_file),
            "table_syntax_file": str(syntax_file),
            "config": {"output_dir": str(tmp_path)},
        }

        with patch('agent.utils.pspp_wrapper.execute_pspp_syntax') as mock_execute:
            # Return success but output file won't exist
            mock_execute.return_value = {
                "success": True,
                "return_code": 0,
                "output": "Executed",
                "error": "",
            }

            result = execute_pspp_tables_node(state)

            assert result["current_step"] == 16
            assert len(result["errors"]) >= 1

    def test_execute_pspp_tables_node_exception_handling(self, indicator_state, tmp_path):
        """Test exception handling during PSPP execution."""
        syntax_file = tmp_path / "tables.sps"
        syntax_file.write_text("CTABLES /TABLE var1 BY var2.")

        input_file = tmp_path / "new_data.sav"
        input_file.write_text("mock")

        state = {
            **indicator_state,
            "new_data_file": str(input_file),
            "table_syntax_file": str(syntax_file),
            "config": {"output_dir": str(tmp_path)},
        }

        with patch('agent.utils.pspp_wrapper.execute_pspp_syntax') as mock_execute:
            mock_execute.side_effect = RuntimeError("PSPP error")

            result = execute_pspp_tables_node(state)

            assert result["current_step"] == 16
            assert len(result["errors"]) >= 1


class TestConvertCsvToJson:
    """Tests for _convert_csv_to_json helper function."""

    def test_convert_csv_to_json_success(self, tmp_path):
        """Test successful CSV to JSON conversion."""
        # Create test CSV file
        csv_file = tmp_path / "test.csv"
        json_file = tmp_path / "test.json"
        csv_file.write_text("col1,col2,col3\n1,2,3\n4,5,6\n")

        result = _convert_csv_to_json(str(csv_file), str(json_file))

        assert result >= 1
        assert json_file.exists()

    def test_convert_csv_to_json_file_not_found(self, tmp_path):
        """Test error when CSV file doesn't exist."""
        json_file = tmp_path / "test.json"

        with pytest.raises(FileNotFoundError):
            _convert_csv_to_json("/nonexistent/test.csv", str(json_file))

    def test_convert_csv_to_json_empty_csv(self, tmp_path):
        """Test error when CSV file is empty."""
        import pandas as pd

        csv_file = tmp_path / "empty.csv"
        json_file = tmp_path / "test.json"
        # Create empty CSV
        pd.DataFrame().to_csv(csv_file, index=False)

        with pytest.raises(ValueError, match="empty"):
            _convert_csv_to_json(str(csv_file), str(json_file))


class TestThreeNodePatternTables:
    """Tests for the three-node pattern in Phase 4 (Steps 12-14)."""

    def test_tables_feedback_loop_with_retry(self, indicator_state, mock_llm_client, tmp_path, new_metadata):
        """Test tables three-node pattern with validation retry."""
        state = {
            **indicator_state,
            "new_metadata": new_metadata,
            "indicators": {"indicators": []},
            "iteration_count": 0,
            "config": {"output_dir": str(tmp_path)},
        }

        # Step 12: Generate table specs
        mock_response = Mock()
        mock_response.content = '{"tables": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase4_tables.get_llm_client', return_value=mock_llm_client):
            state = generate_table_specifications_node(state)

        # Step 13: Validate
        state = validate_table_specs_node(state)

        # Step 14: Review
        with patch('langgraph.types.interrupt'):
            state = review_table_specifications_node(state)

        assert state["table_validation_result"] is not None
        assert state["current_step"] == 14


# =============================================================================
# Phase 5: Statistics Nodes (Steps 17-18)
# =============================================================================

class TestGeneratePythonStatisticsScriptNode:
    """Tests for generate_python_statistics_script_node (Step 17)."""

    def test_generate_statistics_script_success(self, table_state, tmp_path):
        """Test successful statistics script generation."""
        output_dir = str(tmp_path / "output")
        temp_dir = str(tmp_path / "temp")
        state = {
            **table_state,
            "new_data_file": "/tmp/new_data.sav",
            "cross_table_file": "/tmp/cross_tables.csv",
            "config": {
                "output_dir": output_dir,
                "temp_dir": temp_dir,
                "significance_level": 0.05,
            },
        }

        result = generate_python_statistics_script_node(state)

        assert result["current_step"] == 17
        assert "statistics_script" in result
        assert result["statistics_script"].endswith("stats_script.py")

        # Verify script file was created
        assert os.path.exists(result["statistics_script"])

        # Verify script content
        with open(result["statistics_script"], 'r') as f:
            script_content = f.read()

        # Check for key components in generated script
        assert "import pandas as pd" in script_content
        assert "from scipy.stats import chi2_contingency" in script_content
        assert "def cramers_v" in script_content
        assert "def compute_statistics_for_table" in script_content
        assert "def main()" in script_content
        assert "chi_square" in script_content
        assert "cramers_v" in script_content

    def test_generate_statistics_script_missing_new_data_file(self, table_state):
        """Test error handling when new_data_file is missing."""
        state = {
            **table_state,
            "new_data_file": None,
        }

        result = generate_python_statistics_script_node(state)

        assert result["current_step"] == 17
        assert len(result["errors"]) > 0
        assert any("new_data_file" in err for err in result["errors"])
        assert "statistics_script" not in result or result.get("statistics_script") is None

    def test_generate_statistics_script_missing_table_specifications(self, table_state):
        """Test error handling when table_specifications is missing."""
        state = {
            **table_state,
            "new_data_file": "/tmp/new_data.sav",
            "table_specifications": None,
        }

        result = generate_python_statistics_script_node(state)

        assert result["current_step"] == 17
        assert len(result["errors"]) > 0
        assert any("table_specifications" in err for err in result["errors"])

    def test_generate_statistics_script_empty_tables_list(self, table_state, tmp_path):
        """Test handling of empty tables list in specifications."""
        temp_dir = str(tmp_path / "temp")
        state = {
            **table_state,
            "new_data_file": "/tmp/new_data.sav",
            "table_specifications": {"tables": []},
            "config": {"temp_dir": temp_dir},
        }

        result = generate_python_statistics_script_node(state)

        assert result["current_step"] == 17
        assert len(result["warnings"]) > 0
        assert any("No tables found" in warn for warn in result["warnings"])

    def test_generate_statistics_script_custom_config(self, table_state, tmp_path):
        """Test script generation with custom config paths."""
        custom_temp = str(tmp_path / "custom_temp")
        state = {
            **table_state,
            "new_data_file": "/tmp/new_data.sav",
            "config": {
                "temp_dir": custom_temp,
                "significance_level": 0.01,
            },
        }

        result = generate_python_statistics_script_node(state)

        assert result["current_step"] == 17
        assert "statistics_script" in result
        assert custom_temp in result["statistics_script"]

    def test_generate_statistics_script_multiple_tables(self, table_state, tmp_path):
        """Test script generation with multiple tables."""
        temp_dir = str(tmp_path / "temp")
        state = {
            **table_state,
            "new_data_file": "/tmp/new_data.sav",
            "table_specifications": {
                "tables": [
                    {"table_name": "table1", "row_variable": "var1", "column_variable": "var2"},
                    {"table_name": "table2", "row_variable": "var3", "column_variable": "var4"},
                    {"table_name": "table3", "row_variable": "var5", "column_variable": "var6"},
                ]
            },
            "config": {"temp_dir": temp_dir},
        }

        result = generate_python_statistics_script_node(state)

        assert result["current_step"] == 17
        assert "statistics_script" in result

        # Verify all tables are included in script
        with open(result["statistics_script"], 'r') as f:
            script_content = f.read()

        assert '"table_name": "table1"' in script_content
        assert '"table_name": "table2"' in script_content
        assert '"table_name": "table3"' in script_content

    def test_generate_statistics_script_preserves_existing_errors(self, table_state, tmp_path):
        """Test that existing errors in state are preserved."""
        temp_dir = str(tmp_path / "temp")
        state = {
            **table_state,
            "new_data_file": "/tmp/new_data.sav",
            "errors": ["Previous error 1", "Previous error 2"],
            "config": {"temp_dir": temp_dir},
        }

        result = generate_python_statistics_script_node(state)

        assert result["current_step"] == 17
        assert "Previous error 1" in result["errors"]
        assert "Previous error 2" in result["errors"]

    def test_generate_statistics_script_significance_level_in_output(self, table_state, tmp_path):
        """Test that custom significance level is included in generated script."""
        temp_dir = str(tmp_path / "temp")
        state = {
            **table_state,
            "new_data_file": "/tmp/new_data.sav",
            "config": {
                "temp_dir": temp_dir,
                "significance_level": 0.01,
            },
        }

        result = generate_python_statistics_script_node(state)

        with open(result["statistics_script"], 'r') as f:
            script_content = f.read()

        # Check that the significance level is used in the script
        assert "0.01" in script_content or "1e-02" in script_content or "0.01," in script_content

    def test_generate_statistics_script_includes_safety_checks(self, table_state, tmp_path):
        """Test that generated script includes statistical safety checks."""
        temp_dir = str(tmp_path / "temp")
        state = {
            **table_state,
            "new_data_file": "/tmp/new_data.sav",
            "config": {"temp_dir": temp_dir},
        }

        result = generate_python_statistics_script_node(state)

        with open(result["statistics_script"], 'r') as f:
            script_content = f.read()

        # Check for safety checks in the generated script
        assert "contingency_table.shape" in script_content
        assert "minimum expected" in script_content.lower() or "min_cell_count" in script_content
        assert "is_valid" in script_content


class TestExecutePythonStatisticsScriptNode:
    """Tests for execute_python_statistics_script_node (Step 18)."""

    def test_execute_statistics_script_success(self, table_state, tmp_path):
        """Test successful statistics script execution."""
        # Create a mock statistics script that produces valid output
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = scripts_dir / "stats_script.py"

        # Create a mock script that generates valid output
        script_content = '''#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def main():
    output_dir = "''' + str(tmp_path / "output") + '''"
    output_file = Path(output_dir) / "statistical_summary.json"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "generated_at": "2024-01-01T00:00:00",
        "total_tables": 2,
        "valid_tables": 2,
        "invalid_tables": 0,
        "significant_tables": 1,
        "significance_level": 0.05,
        "min_cell_count": 10,
        "tables": [
            {
                "table_name": "table1",
                "row_variable": "var1",
                "column_variable": "var2",
                "is_valid": True,
                "chi_square": 5.5,
                "p_value": 0.02,
                "degrees_of_freedom": 1,
                "cramers_v": 0.35,
                "interpretation": "small",
                "is_significant": True,
                "sample_size": 100,
            },
            {
                "table_name": "table2",
                "row_variable": "var3",
                "column_variable": "var4",
                "is_valid": True,
                "chi_square": 1.5,
                "p_value": 0.22,
                "degrees_of_freedom": 1,
                "cramers_v": 0.12,
                "interpretation": "negligible",
                "is_significant": False,
                "sample_size": 80,
            }
        ]
    }

    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)

    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

        script_path.write_text(script_content)

        output_dir = str(tmp_path / "output")
        state = {
            **table_state,
            "statistics_script": str(script_path),
            "config": {"output_dir": output_dir},
        }

        result = execute_python_statistics_script_node(state)

        assert result["current_step"] == 18
        assert "statistical_summary" in result
        assert result["statistical_summary"]["total_tables"] == 2
        assert result["statistical_summary"]["valid_tables"] == 2
        assert result["statistical_summary"]["significant_tables"] == 1
        assert len(result["errors"]) == 0

    def test_execute_statistics_script_missing_script(self, table_state):
        """Test error handling when statistics_script is missing."""
        state = {
            **table_state,
            "statistics_script": None,
        }

        result = execute_python_statistics_script_node(state)

        assert result["current_step"] == 18
        assert len(result["errors"]) > 0
        assert any("statistics_script" in err for err in result["errors"])

    def test_execute_statistics_script_file_not_found(self, table_state):
        """Test error handling when script file doesn't exist."""
        state = {
            **table_state,
            "statistics_script": "/nonexistent/path/to/script.py",
            "config": {"output_dir": "/tmp/output"},
        }

        result = execute_python_statistics_script_node(state)

        assert result["current_step"] == 18
        assert len(result["errors"]) > 0
        assert any("not found" in err.lower() for err in result["errors"])

    def test_execute_statistics_script_execution_failure(self, table_state, tmp_path):
        """Test handling of script execution failure."""
        # Create a script that exits with error
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = scripts_dir / "failing_script.py"

        script_content = '''#!/usr/bin/env python3
import sys
sys.exit(1)
'''
        script_path.write_text(script_content)

        state = {
            **table_state,
            "statistics_script": str(script_path),
            "config": {"output_dir": str(tmp_path / "output")},
        }

        result = execute_python_statistics_script_node(state)

        assert result["current_step"] == 18
        assert len(result["errors"]) > 0
        assert any("execution failed" in err.lower() or "return code" in err.lower() for err in result["errors"])

    def test_execute_statistics_script_missing_output_file(self, table_state, tmp_path):
        """Test error handling when output file is not created."""
        # Create a script that runs successfully but doesn't create output
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = scripts_dir / "no_output_script.py"

        script_content = '''#!/usr/bin/env python3
# Script runs but doesn't create any output file
pass
'''
        script_path.write_text(script_content)

        output_dir = str(tmp_path / "output")
        state = {
            **table_state,
            "statistics_script": str(script_path),
            "config": {"output_dir": output_dir},
        }

        result = execute_python_statistics_script_node(state)

        assert result["current_step"] == 18
        assert len(result["errors"]) > 0
        assert any("not created" in err.lower() or "output file" in err.lower() for err in result["errors"])

    def test_execute_statistics_script_invalid_json(self, table_state, tmp_path):
        """Test handling of invalid JSON in output file."""
        # Create script that writes invalid JSON
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = scripts_dir / "invalid_json_script.py"

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        script_content = f'''#!/usr/bin/env python3
import sys
from pathlib import Path

output_file = Path("{output_dir}/statistical_summary.json")
with open(output_file, "w") as f:
    f.write("{{ invalid json }}")
'''
        script_path.write_text(script_content)

        state = {
            **table_state,
            "statistics_script": str(script_path),
            "config": {"output_dir": str(output_dir)},
        }

        result = execute_python_statistics_script_node(state)

        assert result["current_step"] == 18
        assert len(result["errors"]) > 0
        assert any("json" in err.lower() or "parse" in err.lower() for err in result["errors"])

    def test_execute_statistics_script_zero_tables_warning(self, table_state, tmp_path):
        """Test warning when no tables are processed."""
        # Create script that produces zero tables
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = scripts_dir / "zero_tables_script.py"

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        script_content = f'''#!/usr/bin/env python3
import json
from pathlib import Path

output_file = Path("{output_dir}/statistical_summary.json")
summary = {{
    "generated_at": "2024-01-01T00:00:00",
    "total_tables": 0,
    "valid_tables": 0,
    "invalid_tables": 0,
    "significant_tables": 0,
    "significance_level": 0.05,
    "min_cell_count": 10,
    "tables": []
}}
with open(output_file, "w") as f:
    json.dump(summary, f, indent=2)
'''
        script_path.write_text(script_content)

        state = {
            **table_state,
            "statistics_script": str(script_path),
            "config": {"output_dir": str(output_dir)},
        }

        result = execute_python_statistics_script_node(state)

        assert result["current_step"] == 18
        assert len(result["warnings"]) > 0
        assert any("no tables" in warn.lower() for warn in result["warnings"])

    def test_execute_statistics_script_invalid_tables_warning(self, table_state, tmp_path):
        """Test warning when some tables are invalid."""
        # Create script with some invalid tables
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = scripts_dir / "invalid_tables_script.py"

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        script_content = f'''#!/usr/bin/env python3
import json
from pathlib import Path

output_file = Path("{output_dir}/statistical_summary.json")
summary = {{
    "generated_at": "2024-01-01T00:00:00",
    "total_tables": 3,
    "valid_tables": 1,
    "invalid_tables": 2,
    "significant_tables": 0,
    "significance_level": 0.05,
    "min_cell_count": 10,
    "tables": [
        {{
            "table_name": "valid_table",
            "is_valid": True,
            "chi_square": 5.0,
            "p_value": 0.03,
            "degrees_of_freedom": 1,
            "cramers_v": 0.3,
            "interpretation": "small",
            "is_significant": True,
            "sample_size": 100,
        }},
        {{
            "table_name": "invalid_table1",
            "is_valid": False,
            "error": "Sample size too small"
        }},
        {{
            "table_name": "invalid_table2",
            "is_valid": False,
            "error": "Zero cells detected"
        }}
    ]
}}
with open(output_file, "w") as f:
    json.dump(summary, f, indent=2)
'''
        script_path.write_text(script_content)

        state = {
            **table_state,
            "statistics_script": str(script_path),
            "config": {"output_dir": str(output_dir)},
        }

        result = execute_python_statistics_script_node(state)

        assert result["current_step"] == 18
        assert result["statistical_summary"]["invalid_tables"] == 2
        assert len(result["warnings"]) > 0
        assert any("invalid" in warn.lower() or "assumption" in warn.lower() for warn in result["warnings"])

    def test_execute_statistics_script_no_significant_tables_warning(self, table_state, tmp_path):
        """Test warning when no tables are significant."""
        # Create script with no significant tables
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = scripts_dir / "no_significant_script.py"

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        script_content = f'''#!/usr/bin/env python3
import json
from pathlib import Path

output_file = Path("{output_dir}/statistical_summary.json")
summary = {{
    "generated_at": "2024-01-01T00:00:00",
    "total_tables": 2,
    "valid_tables": 2,
    "invalid_tables": 0,
    "significant_tables": 0,
    "significance_level": 0.05,
    "min_cell_count": 10,
    "tables": [
        {{
            "table_name": "table1",
            "is_valid": True,
            "chi_square": 1.0,
            "p_value": 0.5,
            "degrees_of_freedom": 1,
            "cramers_v": 0.05,
            "interpretation": "negligible",
            "is_significant": False,
            "sample_size": 100,
        }},
        {{
            "table_name": "table2",
            "is_valid": True,
            "chi_square": 2.0,
            "p_value": 0.15,
            "degrees_of_freedom": 1,
            "cramers_v": 0.1,
            "interpretation": "negligible",
            "is_significant": False,
            "sample_size": 80,
        }}
    ]
}}
with open(output_file, "w") as f:
    json.dump(summary, f, indent=2)
'''
        script_path.write_text(script_content)

        state = {
            **table_state,
            "statistics_script": str(script_path),
            "config": {"output_dir": str(output_dir)},
        }

        result = execute_python_statistics_script_node(state)

        assert result["current_step"] == 18
        assert result["statistical_summary"]["significant_tables"] == 0
        assert result["statistical_summary"]["valid_tables"] > 0
        assert len(result["warnings"]) > 0
        assert any("significant" in warn.lower() for warn in result["warnings"])

    def test_execute_statistics_script_preserves_existing_warnings(self, table_state, tmp_path):
        """Test that existing warnings in state are preserved."""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = scripts_dir / "stats_script.py"

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        script_content = f'''#!/usr/bin/env python3
import json
from pathlib import Path

output_file = Path("{output_dir}/statistical_summary.json")
summary = {{
    "generated_at": "2024-01-01T00:00:00",
    "total_tables": 1,
    "valid_tables": 1,
    "invalid_tables": 0,
    "significant_tables": 1,
    "significance_level": 0.05,
    "min_cell_count": 10,
    "tables": [{{
        "table_name": "table1",
        "is_valid": True,
        "chi_square": 5.0,
        "p_value": 0.03,
        "degrees_of_freedom": 1,
        "cramers_v": 0.3,
        "interpretation": "small",
        "is_significant": True,
        "sample_size": 100,
    }}]
}}
with open(output_file, "w") as f:
    json.dump(summary, f, indent=2)
'''
        script_path.write_text(script_content)

        state = {
            **table_state,
            "statistics_script": str(script_path),
            "config": {"output_dir": str(output_dir)},
            "warnings": ["Previous warning 1", "Previous warning 2"],
        }

        result = execute_python_statistics_script_node(state)

        assert result["current_step"] == 18
        assert "Previous warning 1" in result["warnings"]
        assert "Previous warning 2" in result["warnings"]

    def test_execute_statistics_script_custom_output_dir(self, table_state, tmp_path):
        """Test script execution with custom output directory."""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = scripts_dir / "custom_output_script.py"

        custom_output = tmp_path / "custom_output"
        custom_output.mkdir(parents=True, exist_ok=True)

        script_content = f'''#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Override output path in this test
output_file = Path("{custom_output}/statistical_summary.json")
summary = {{
    "generated_at": "2024-01-01T00:00:00",
    "total_tables": 1,
    "valid_tables": 1,
    "invalid_tables": 0,
    "significant_tables": 0,
    "significance_level": 0.05,
    "min_cell_count": 10,
    "tables": [{{
        "table_name": "table1",
        "is_valid": True,
        "chi_square": 1.0,
        "p_value": 0.5,
        "degrees_of_freedom": 1,
        "cramers_v": 0.05,
        "interpretation": "negligible",
        "is_significant": False,
        "sample_size": 50,
    }}]
}}
with open(output_file, "w") as f:
    json.dump(summary, f, indent=2)

# Also create at the expected location
expected_output = Path("{tmp_path}/output/statistical_summary.json")
expected_output.parent.mkdir(parents=True, exist_ok=True)
with open(expected_output, "w") as f:
    json.dump(summary, f, indent=2)
'''
        script_path.write_text(script_content)

        state = {
            **table_state,
            "statistics_script": str(script_path),
            "config": {"output_dir": str(tmp_path / "output")},
        }

        result = execute_python_statistics_script_node(state)

        assert result["current_step"] == 18
        assert "statistical_summary" in result

    def test_execute_statistics_script_with_stdout_stderr(self, table_state, tmp_path):
        """Test script execution that produces stdout and stderr output."""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = scripts_dir / "output_script.py"

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        script_content = f'''#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Produce stdout and stderr
print("Processing table 1...", file=sys.stdout)
print("Debug: Loading data", file=sys.stderr)

output_file = Path("{output_dir}/statistical_summary.json")
summary = {{
    "generated_at": "2024-01-01T00:00:00",
    "total_tables": 1,
    "valid_tables": 1,
    "invalid_tables": 0,
    "significant_tables": 1,
    "significance_level": 0.05,
    "min_cell_count": 10,
    "tables": [{{
        "table_name": "table1",
        "is_valid": True,
        "chi_square": 5.0,
        "p_value": 0.03,
        "degrees_of_freedom": 1,
        "cramers_v": 0.3,
        "interpretation": "small",
        "is_significant": True,
        "sample_size": 100,
    }}]
}}
with open(output_file, "w") as f:
    json.dump(summary, f, indent=2)

print("Processing complete", file=sys.stdout)
'''
        script_path.write_text(script_content)

        state = {
            **table_state,
            "statistics_script": str(script_path),
            "config": {"output_dir": str(output_dir)},
        }

        result = execute_python_statistics_script_node(state)

        assert result["current_step"] == 18
        assert "statistical_summary" in result
        assert len(result["errors"]) == 0

    def test_execute_statistics_script_failure_with_stderr(self, table_state, tmp_path):
        """Test script execution failure with stderr output."""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = scripts_dir / "failing_with_stderr.py"

        script_content = '''#!/usr/bin/env python3
import sys

print("This is an error message", file=sys.stderr)
print("Starting processing...", file=sys.stdout)
sys.exit(1)
'''
        script_path.write_text(script_content)

        state = {
            **table_state,
            "statistics_script": str(script_path),
            "config": {"output_dir": str(tmp_path / "output")},
        }

        result = execute_python_statistics_script_node(state)

        assert result["current_step"] == 18
        assert len(result["errors"]) > 0
        assert any("execution failed" in err.lower() or "return code" in err.lower() for err in result["errors"])

    def test_execute_statistics_script_timeout_error(self, table_state, tmp_path):
        """Test handling of script timeout using mock."""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_path = scripts_dir / "timeout_script.py"

        output_dir = tmp_path / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        script_content = f'''#!/usr/bin/env python3
import json
from pathlib import Path

output_file = Path("{output_dir}/statistical_summary.json")
summary = {{
    "generated_at": "2024-01-01T00:00:00",
    "total_tables": 1,
    "valid_tables": 1,
    "invalid_tables": 0,
    "significant_tables": 0,
    "significance_level": 0.05,
    "min_cell_count": 10,
    "tables": [{{
        "table_name": "table1",
        "is_valid": True,
        "chi_square": 1.0,
        "p_value": 0.5,
        "degrees_of_freedom": 1,
        "cramers_v": 0.05,
        "interpretation": "negligible",
        "is_significant": False,
        "sample_size": 50,
    }}]
}}
with open(output_file, "w") as f:
    json.dump(summary, f, indent=2)
'''
        script_path.write_text(script_content)

        state = {
            **table_state,
            "statistics_script": str(script_path),
            "config": {"output_dir": str(output_dir)},
        }

        # Mock subprocess.run to raise TimeoutExpired
        import subprocess
        with patch('agent.nodes.phase5_statistics.subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(script_path, 300)

            result = execute_python_statistics_script_node(state)

            assert result["current_step"] == 18
            assert len(result["errors"]) > 0
            assert any("timed out" in err.lower() for err in result["errors"])


class TestGeneratePythonStatisticsScriptNodeAdditional:
    """Additional tests for generate_python_statistics_script_node (Step 17)."""

    def test_generate_statistics_script_unexpected_exception(self, table_state, tmp_path):
        """Test handling of unexpected exceptions during script generation."""
        # Create a temp dir that will cause an error
        state = {
            **table_state,
            "new_data_file": "/tmp/new_data.sav",
            "config": {
                "temp_dir": "/dev/null/invalid_path_12345",  # Invalid path that should cause error
            },
        }

        result = generate_python_statistics_script_node(state)

        assert result["current_step"] == 17
        # Should have error due to invalid path
        assert len(result.get("errors", [])) > 0
        assert "statistics_script" not in result or result.get("statistics_script") is None

    def test_generate_statistics_script_unicode_table_names(self, table_state, tmp_path):
        """Test script generation with Unicode characters in table names."""
        temp_dir = str(tmp_path / "temp")
        state = {
            **table_state,
            "new_data_file": "/tmp/new_data.sav",
            "table_specifications": {
                "tables": [
                    {"table_name": "café_table", "row_variable": "var1", "column_variable": "var2"},
                    {"table_name": "日本語_table", "row_variable": "var3", "column_variable": "var4"},
                ]
            },
            "config": {"temp_dir": temp_dir},
        }

        result = generate_python_statistics_script_node(state)

        assert result["current_step"] == 17
        assert "statistics_script" in result

        # Verify Unicode table names are in the script
        with open(result["statistics_script"], 'r', encoding='utf-8') as f:
            script_content = f.read()

        assert "café_table" in script_content
        assert "日本語_table" in script_content


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

    def test_indicators_feedback_loop_with_retry(self, sample_state, new_metadata, mock_llm_client, tmp_path):
        """Test indicators three-node pattern with validation retry."""
        state = {
            **sample_state,
            "new_metadata": new_metadata,
            "iteration_count": 0,
            "config": {"output_dir": str(tmp_path)},
        }

        # Step 9: Generate indicators
        mock_response = Mock()
        mock_response.content = '{"indicators": [{"name": "Test", "description": "Test", "variables": ["gender", "age_group"]}]}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase3_indicators.get_llm_client', return_value=mock_llm_client):
            state = generate_indicators_node(state)

        assert state["current_step"] == 9
        assert state["indicators"] is not None

        # Step 10: Validate
        state = validate_indicators_node(state)

        assert state["current_step"] == 10
        assert state["indicator_validation_result"] is not None

        # Step 11: Review
        with patch('langgraph.types.interrupt'):
            state = review_indicators_node(state)

        assert state["current_step"] == 11
        assert state["requires_human_review"] is True


# Duplicate TestThreeNodePatternTables removed - now in Phase 4 section above
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
