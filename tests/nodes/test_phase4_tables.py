"""
Unit Tests for Phase4 Tables Nodes

This module tests node implementations from Phase 4 (Tables).

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

from agent.state import ValidationResult, STEP_0_INITIAL, STEP_1_EXTRACT_SPSS, STEP_4_GENERATE_RECODING_RULES, STEP_5_VALIDATE_RECODING_RULES, STEP_6_REVIEW_RECODING_RULES
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


# =============================================================================
# Phase 4: Tables Nodes
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
        assert state["current_step"] == STEP_14_REVIEW_TABLE_SPECIFICATIONS


# =============================================================================
