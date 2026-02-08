"""
Unit Tests for Phase3 Indicators Nodes

This module tests node implementations from Phase 3 (Indicators).

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

from agent.state import (
    ValidationResult,
    STEP_0_INITIAL, STEP_1_EXTRACT_SPSS,
    STEP_4_GENERATE_RECODING_RULES, STEP_5_VALIDATE_RECODING_RULES, STEP_6_REVIEW_RECODING_RULES,
    STEP_8_EXECUTE_PSPP_RECODING, STEP_9_GENERATE_INDICATORS, STEP_10_VALIDATE_INDICATORS, STEP_11_REVIEW_INDICATORS
)
from agent.nodes.phase3_indicators import (
    generate_indicators_node,
    validate_indicators_node,
    review_indicators_node,
)


# =============================================================================
# Phase 3: Indicators Nodes
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

            assert result["current_step"] == STEP_9_GENERATE_INDICATORS
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

        assert result["current_step"] == STEP_9_GENERATE_INDICATORS
        assert len(result.get("errors", [])) == 1
        assert "new_metadata" in result.get("errors", [])[0]

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

            assert result["current_step"] == STEP_9_GENERATE_INDICATORS
            assert result["indicators"] is not None
            assert len(result["indicators"]["indicators"]) == 0
            assert len(result.get("warnings", [])) >= 1
            assert "no indicators" in result.get("warnings", [])[0].lower()

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

            assert result["current_step"] == STEP_9_GENERATE_INDICATORS
            assert len(result.get("errors", [])) == 1
            assert "parse" in result.get("errors", [])[0].lower() or "json" in result.get("errors", [])[0].lower()
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

            assert result["current_step"] == STEP_9_GENERATE_INDICATORS
            assert len(result.get("errors", [])) == 1
            assert "invalid" in result.get("errors", [])[0].lower() or "missing" in result.get("errors", [])[0].lower()
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

            assert result["current_step"] == STEP_9_GENERATE_INDICATORS
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

            assert result["current_step"] == STEP_9_GENERATE_INDICATORS
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
            "current_step": STEP_0_INITIAL,
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

        assert result["current_step"] == STEP_10_VALIDATE_INDICATORS
        assert result["indicator_validation_result"] is not None

    def test_validate_indicators_node_no_indicators(self, sample_state):
        """Test validation with no indicators."""
        state = {
            **sample_state,
            "indicators": None,
        }

        result = validate_indicators_node(state)

        assert result["current_step"] == STEP_10_VALIDATE_INDICATORS
        assert len(result.get("errors", [])) == 1
        assert "indicators" in result.get("errors", [])[0].lower()

    def test_validate_indicators_node_no_metadata(self, sample_state):
        """Test validation with no new_metadata."""
        state = {
            **sample_state,
            "indicators": {"indicators": []},
            "new_metadata": None,
        }

        result = validate_indicators_node(state)

        assert result["current_step"] == STEP_10_VALIDATE_INDICATORS
        assert len(result.get("errors", [])) == 1
        assert "metadata" in result.get("errors", [])[0].lower()


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

            assert result["current_step"] == STEP_11_REVIEW_INDICATORS
            assert result["requires_human_review"] is True

    def test_review_indicators_node_no_indicators(self, sample_state):
        """Test review with no indicators."""
        state = {
            **sample_state,
            "indicators": None,
            "config": {"output_dir": "/tmp"},
        }

        result = review_indicators_node(state)

        assert result["current_step"] == STEP_11_REVIEW_INDICATORS
        assert len(result.get("errors", [])) == 1
        assert "indicators" in result.get("errors", [])[0].lower()
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

            assert result["current_step"] == STEP_11_REVIEW_INDICATORS
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
