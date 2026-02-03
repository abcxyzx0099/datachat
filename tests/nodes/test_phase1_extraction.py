"""
Unit Tests for Phase1 Extraction Nodes

This module tests node implementations from Phase 1 (Extraction).

Test Coverage:
- Node functions
- State immutability
- Error handling
"""
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

from agent.nodes.phase1_extraction import (
    extract_spss_node,
    transform_metadata_node,
    filter_metadata_node,
)


# =============================================================================
# Phase 1: Extraction Nodes
# =============================================================================
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
            # Note: raw_data is NOT stored to avoid LangGraph serialization issues
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

    def test_transform_metadata_node_success(self, sample_state, sample_metadata, sample_dataframe):
        """Test successful metadata transformation."""
        # Prepare state with original_metadata
        state = {
            **sample_state,
            "input_file_path": "test_data.sav",
            "original_metadata": sample_metadata,
            "warnings": [],
        }

        # Mock the file read since transform_metadata_node reads the file to compute stats
        with patch('pyreadstat.read_sav') as mock_read:
            mock_metadata = Mock()
            mock_metadata.column_labels = sample_metadata["column_labels"]
            mock_metadata.variable_value_labels = sample_metadata["column_value_labels"]
            mock_metadata.variable_storage_types = {}
            mock_read.return_value = (sample_dataframe, mock_metadata)

            result = transform_metadata_node(state)

            assert result["current_step"] == 2
            assert result["variable_centered_metadata"] is not None
            assert result["variable_centered_metadata"]["n_variables"] == 6
            assert result["variable_centered_metadata"]["n_numeric"] == 6
            assert len(result["errors"]) == 0

    def test_transform_metadata_node_no_metadata(self, sample_state):
        """Test metadata transformation with no original_metadata."""
        state = {
            **sample_state,
            "original_metadata": None,
        }

        result = transform_metadata_node(state)

        assert result["current_step"] == 2
        assert len(result["errors"]) == 1
        assert "original_metadata" in result["errors"][0]

    def test_transform_metadata_node_empty_metadata(self, sample_state):
        """Test metadata transformation with empty metadata."""
        state = {
            **sample_state,
            "input_file_path": "test_data.sav",
            "original_metadata": {"n_rows": 0, "n_columns": 0, "column_labels": {}, "column_value_labels": {}},
            "warnings": [],
        }

        # Mock the file read to return empty dataframe
        with patch('pyreadstat.read_sav') as mock_read:
            import pandas as pd
            mock_metadata = Mock()
            mock_metadata.column_labels = []
            mock_metadata.variable_value_labels = {}
            mock_metadata.variable_storage_types = {}
            mock_read.return_value = (pd.DataFrame(), mock_metadata)

            result = transform_metadata_node(state)

            assert result["current_step"] == 2
            assert result["variable_centered_metadata"] is not None
            assert result["variable_centered_metadata"]["n_variables"] == 0
            assert len(result["warnings"]) >= 1


class TestFilterMetadataNode:
    """Tests for filter_metadata_node (Step 3)."""

    def test_filter_metadata_node_success(self, sample_state, variable_centered_metadata):
        """Test successful metadata filtering."""
        state = {
            **sample_state,
            "variable_centered_metadata": variable_centered_metadata,
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
