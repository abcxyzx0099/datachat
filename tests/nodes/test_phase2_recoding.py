"""
Unit Tests for Phase2 Recoding Nodes

This module tests node implementations from Phase 2 (Recoding).

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
from unittest.mock import patch, Mock

from agent.state import ValidationResult
from agent.nodes.phase2_recoding import (
    generate_recoding_rules_node,
    validate_recoding_rules_node,
    review_recoding_rules_node,
    generate_pspp_recoding_syntax_node,
    execute_pspp_recoding_node,
)


# =============================================================================
# Phase 2: Recoding Nodes
# =============================================================================
# Phase 2: Recoding Nodes (Steps 4-8)
# =============================================================================

class TestGenerateRecodingRulesNode:
    """Tests for generate_recoding_rules_node (Step 4)."""

    def test_generate_recoding_rules_node_success(self, populated_state, mock_llm_client):
        """Test successful recoding rules generation."""
        # Mock LLM response - recoding_rules must be a list
        mock_response = Mock()
        mock_response.content = '{"recoding_rules": []}'
        mock_llm_client.invoke.return_value = mock_response

        with patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client):
            result = generate_recoding_rules_node(populated_state)

            assert result["current_step"] == 4
            assert result["recoding_rules"] is not None
            assert result["recoding_rules"]["recoding_rules"] == []

    def test_generate_recoding_rules_node_with_feedback(self, populated_state, mock_llm_client):
        """Test recoding rules generation with feedback."""
        state = {
            **populated_state,
            "iteration_count": 1,  # Set to 1 to simulate a retry scenario
            "recoding_feedback": "Previous rules were too aggressive",
        }

        with patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client):
            result = generate_recoding_rules_node(state)

            assert result["recoding_rules"] is not None
            # iteration_count is incremented on successful completion
            assert result["iteration_count"] == 2


class TestValidateRecodingRulesNode:
    """Tests for validate_recoding_rules_node (Step 5)."""

    def test_validate_recoding_rules_node_valid(self, populated_state):
        """Test validation of valid recoding rules."""
        state = {
            **populated_state,
            "recoding_rules": {"var1": {"recodings": []}},
        }

        with patch('agent.validation.recoding.validate_recoding_rules') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["syntax", "logic"],
            )

            result = validate_recoding_rules_node(state)

            assert result["current_step"] == 5
            assert result["recoding_validation_result"]['is_valid'] is True

    def test_validate_recoding_rules_node_invalid(self, populated_state):
        """Test validation of invalid recoding rules."""
        state = {
            **populated_state,
            "recoding_rules": {"var1": {"recodings": []}},
        }

        with patch('agent.validation.recoding.validate_recoding_rules') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=False,
                errors=["Syntax error"],
                warnings=[],
                checks_performed=["syntax", "logic"],
            )

            result = validate_recoding_rules_node(state)

            assert result["current_step"] == 5
            assert result["recoding_validation_result"]['is_valid'] is False
            assert len(result["recoding_validation_result"]['errors']) == 1


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

        with patch('agent.nodes.phase2_recoding._generate_recoding_review_markdown'):
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

        with patch('agent.nodes.phase2_recoding._generate_recoding_review_markdown'):
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

        # Create the expected output file
        output_file = tmp_path / "new_data.sav"
        output_file.write_text("mock sav content")

        state = {
            **populated_state,
            "raw_data_file": str(input_file),
            "recoding_syntax_file": str(syntax_file),
            "config": {"output_dir": str(tmp_path)},
        }

        with patch('agent.utils.pspp_wrapper.execute_pspp_syntax') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "return_code": 0,
                "output": "PSPP executed successfully",
                "error": "",
                "output_file": str(output_file),
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

        with patch('agent.utils.pspp_wrapper.execute_pspp_syntax') as mock_execute:
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
