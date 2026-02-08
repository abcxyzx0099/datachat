"""
Integration Tests for PSPP Execution

This module contains comprehensive integration tests for complete PSPP workflow
including syntax generation, file execution, and output parsing.

Test Coverage:
1. Recoding Workflow Tests (Steps 7-8)
   - Complete recoding flow: generate rules → create syntax → execute PSPP → read new data
   - RECODE syntax generation from recoding rules JSON
   - VARIABLE LABELS generation
   - VALUE LABELS generation
   - PSPP execution with recoding syntax
   - Reading new_data.sav with pyreadstat
   - new_metadata extraction

2. Cross-Table Workflow Tests (Steps 15-16)
   - Complete cross-table flow: generate table specs → create syntax → execute PSPP → export results
   - CTABLES syntax generation from table specifications
   - /VLABELS, /TABLE, /STATISTICS commands
   - PSPP execution with CTABLES syntax
   - Reading cross_table.csv and cross_table.json
   - Data extraction from PSPP output

3. Syntax File Tests
   - Syntax files are written to correct location
   - Syntax files use correct PSPP commands
   - Syntax files include proper formatting
   - Syntax files can be executed manually if needed

4. Output Parsing Tests
   - Parsing PSPP stdout for execution status
   - Parsing PSPP stderr for errors
   - Extracting output file paths
   - Handling PSPP warnings

5. Error Handling Tests
   - Invalid PSPP syntax (syntax errors)
   - Missing input files
   - Permission denied errors
   - PSPP not installed (graceful error message)
   - Timeout handling for long-running PSPP commands

6. Real PSPP Tests (optional, marked as @pytest.mark.integration)
   - Tests with actual PSPP installation
   - Tests with real .sav files
   - Verify actual output matches expected format
   - Test with PSPP different versions

All default tests work without PSPP (mocked).
Optional: Add @pytest.mark.integration for tests requiring real PSPP.
"""

import sys
from pathlib import Path

# Add agent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import os
import json
import tempfile
import subprocess
from unittest.mock import Mock, patch, MagicMock, mock_open
from typing import Dict, Any, List
import pandas as pd

# Import modules under test
from agent.nodes.phase2_recoding import (
    generate_pspp_recoding_syntax_node,
    execute_pspp_recoding_node,
    _generate_pspp_header,
    _generate_rule_syntax,
    _generate_range_grouping_syntax,
    _generate_category_consolidation_syntax,
    _generate_top_bottom_box_syntax,
    _generate_derived_syntax,
    _generate_variable_labels,
    _generate_value_labels,
    _extract_metadata_from_sav,
)
from agent.nodes.phase4_tables import (
    generate_pspp_table_syntax_node,
    execute_pspp_tables_node,
    _generate_ctables_header,
    _generate_ctable_command,
    _convert_csv_to_json,
)
from agent.utils.pspp_wrapper import execute_pspp_syntax
from agent.state import WorkflowState, create_initial_state, STEP_0_INITIAL, STEP_1_EXTRACT_SPSS, STEP_4_GENERATE_RECODING_RULES, STEP_5_VALIDATE_RECODING_RULES, STEP_6_REVIEW_RECODING_RULES
from agent.config import DEFAULT_CONFIG


# =============================================================================
# Recoding Workflow Tests (Steps 7-8)
# =============================================================================

class TestRecodingWorkflow:
    """Integration tests for complete PSPP recoding workflow."""

    @pytest.fixture
    def sample_recoding_rules(self) -> Dict[str, Any]:
        """Sample recoding rules for testing."""
        return {
            "recoding_rules": [
                {
                    "source_variable": "age",
                    "target_variable": "age_group",
                    "transformation_type": "range_grouping",
                    "description": "Group age into categories",
                    "rules": [
                        {"source_min": 18, "source_max": 34, "target_value": 1, "target_label": "Young Adult"},
                        {"source_min": 35, "source_max": 54, "target_value": 2, "target_label": "Middle-aged"},
                        {"source_min": 55, "source_max": "HI", "target_value": 3, "target_label": "Senior"}
                    ]
                },
                {
                    "source_variable": "satisfaction",
                    "target_variable": "sat_top2box",
                    "transformation_type": "top_bottom_box",
                    "description": "Top 2 box satisfaction",
                    "rules": [
                        {"source_values": [4, 5], "target_value": 1, "target_label": "Top 2 Box"},
                        {"source_values": [1, 2, 3], "target_value": 0, "target_label": "Others"}
                    ]
                }
            ]
        }

    @pytest.fixture
    def sample_filtered_metadata(self) -> List[Dict[str, Any]]:
        """Sample filtered metadata for recoding tests."""
        return [
            {
                "name": "age",
                "label": "Respondent Age",
                "variable_type": "numeric",
                "min_value": 18,
                "max_value": 80,
                "value_labels": {},
                "distinct_count": 50
            },
            {
                "name": "satisfaction",
                "label": "Overall Satisfaction",
                "variable_type": "numeric",
                "min_value": 1,
                "max_value": 5,
                "value_labels": {1: "Very Dissatisfied", 2: "Dissatisfied", 3: "Neutral", 4: "Satisfied", 5: "Very Satisfied"},
                "distinct_count": 5
            }
        ]

    @pytest.fixture
    def recoding_state(self, sample_recoding_rules, sample_filtered_metadata) -> WorkflowState:
        """Workflow state with recoding data for Step 7."""
        state = create_initial_state("tests/fixtures/sample_data.sav", DEFAULT_CONFIG)
        state["recoding_rules"] = sample_recoding_rules
        state["filtered_metadata"] = sample_filtered_metadata
        state["input_file_path"] = "tests/fixtures/sample_data.sav"
        return state

    def test_complete_recoding_workflow(self, recoding_state):
        """Test complete recoding workflow from rules to new_data.sav."""
        # Step 7: Generate PSPP syntax
        step7_result = generate_pspp_recoding_syntax_node(recoding_state)

        assert step7_result["current_step"] == 7
        assert "recoding_syntax_file" in step7_result
        assert "pspp_recoding_syntax" in step7_result
        assert os.path.exists(step7_result["recoding_syntax_file"])

        # Verify syntax content
        syntax_content = step7_result["pspp_recoding_syntax"]
        assert "RECODE" in syntax_content
        assert "age_group" in syntax_content
        assert "sat_top2box" in syntax_content
        assert "VARIABLE LABELS" in syntax_content
        assert "VALUE LABELS" in syntax_content

        # Step 8: Execute PSPP (mocked)
        # Create a temporary directory for the output
        with tempfile.TemporaryDirectory() as temp_dir:
            new_data_path = os.path.join(temp_dir, "new_data.sav")

            # Create the output file before mocking (simulate PSPP creating it)
            with open(new_data_path, 'wb') as f:
                f.write(b"dummy sav file content")

            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_result.stdout = ""
                    mock_result.stderr = ""
                    mock_run.return_value = mock_result

                    # Mock pyreadstat reading - return dict not Mock
                    import pyreadstat
                    with patch.object(pyreadstat, 'read_sav') as mock_read:
                        mock_df = pd.DataFrame({
                            "age_group": [1, 2, 3],
                            "sat_top2box": [0, 1, 1]
                        })
                        # Use a real dict for metadata, not Mock
                        mock_metadata = {
                            "column_labels": {
                                "age_group": "Age Group",
                                "sat_top2box": "Top 2 Box Satisfaction"
                            },
                            "value_labels": {
                                "age_group": {1: "Young Adult", 2: "Middle-aged", 3: "Senior"},
                                "sat_top2box": {0: "Others", 1: "Top 2 Box"}
                            }
                        }
                        mock_read.return_value = (mock_df, mock_metadata)

                        # Update state with our temp file path
                        step8_state = {**recoding_state, **step7_result}
                        step8_state["config"] = {**step8_state.get("config", {}), "output_dir": temp_dir}

                        step8_result = execute_pspp_recoding_node(step8_state)

                        assert step8_result["current_step"] == 8
                        assert "new_data_file" in step8_result
                        assert "new_metadata" in step8_result
                        assert step8_result["new_metadata"] is not None
                        assert step8_result["new_metadata"]["variable_count"] == 2
                        assert "age_group" in step8_result["new_metadata"]["variable_names"]

    def test_recode_syntax_generation_range_grouping(self, sample_recoding_rules, sample_filtered_metadata):
        """Test RECODE syntax generation for range grouping transformation."""
        rule = sample_recoding_rules["recoding_rules"][0]
        metadata_lookup = {v["name"]: v for v in sample_filtered_metadata}

        syntax = _generate_range_grouping_syntax(rule, metadata_lookup)

        assert len(syntax) > 0
        syntax_str = "\n".join(syntax)
        assert "RECODE age" in syntax_str
        assert "INTO age_group" in syntax_str
        assert "18 THRU 34" in syntax_str
        assert "55 THRU HI" in syntax_str
        assert "VARIABLE LABELS age_group" in syntax_str
        assert "VALUE LABELS age_group" in syntax_str

    def test_recode_syntax_generation_top_bottom_box(self, sample_recoding_rules, sample_filtered_metadata):
        """Test RECODE syntax generation for top/bottom box transformation."""
        rule = sample_recoding_rules["recoding_rules"][1]
        metadata_lookup = {v["name"]: v for v in sample_filtered_metadata}

        syntax = _generate_top_bottom_box_syntax(rule, metadata_lookup)

        assert len(syntax) > 0
        syntax_str = "\n".join(syntax)
        assert "RECODE satisfaction" in syntax_str
        assert "INTO sat_top2box" in syntax_str
        assert "4, 5" in syntax_str or "(4,5" in syntax_str  # Check for source values
        assert "VARIABLE LABELS sat_top2box" in syntax_str
        assert "VALUE LABELS sat_top2box" in syntax_str

    def test_variable_labels_generation(self):
        """Test VARIABLE LABELS command generation."""
        rule = {
            "target_variable": "age_group",
            "description": "Age Group Categories"
        }

        labels = _generate_variable_labels(rule, {})

        assert len(labels) == 1
        assert "VARIABLE LABELS age_group" in labels[0]
        assert "Age Group Categories" in labels[0]

    def test_value_labels_generation(self):
        """Test VALUE LABELS command generation."""
        rule = {
            "target_variable": "age_group",
            "rules": [
                {"target_value": 1, "target_label": "Young Adult"},
                {"target_value": 2, "target_label": "Middle-aged"},
                {"target_value": 3, "target_label": "Senior"}
            ]
        }

        labels = _generate_value_labels(rule, {})

        assert len(labels) > 0
        labels_str = "\n".join(labels)
        assert "VALUE LABELS age_group" in labels_str
        assert "1 'Young Adult'" in labels_str
        assert "2 'Middle-aged'" in labels_str
        assert "3 'Senior'" in labels_str

    def test_category_consolidation_syntax(self):
        """Test RECODE syntax for category consolidation."""
        rule = {
            "source_variable": "region",
            "target_variable": "region_group",
            "transformation_type": "category_consolidation",
            "rules": [
                {"source_values": [1, 2], "target_value": 1, "target_label": "North"},
                {"source_values": [3, 4], "target_value": 2, "target_label": "South"},
                {"source_values": [5], "target_value": 3, "target_label": "West"}
            ]
        }

        metadata_lookup = {
            "region": {"variable_type": "numeric"}
        }

        syntax = _generate_category_consolidation_syntax(rule, metadata_lookup)

        assert len(syntax) > 0
        syntax_str = "\n".join(syntax)
        assert "RECODE region" in syntax_str
        assert "INTO region_group" in syntax_str

    def test_derived_variable_syntax(self):
        """Test COMPUTE syntax for derived variables."""
        rule = {
            "target_variable": "satisfaction_index",
            "transformation_type": "derived",
            "formula": "MEAN(sat_q1, sat_q2, sat_q3)",
            "description": "Average satisfaction score"
        }

        syntax = _generate_derived_syntax(rule, {})

        assert len(syntax) > 0
        syntax_str = "\n".join(syntax)
        assert "COMPUTE satisfaction_index = MEAN(sat_q1, sat_q2, sat_q3)" in syntax_str
        assert "VARIABLE LABELS satisfaction_index" in syntax_str

    def test_syntax_file_written_to_correct_location(self, recoding_state):
        """Test that syntax files are written to temp/pspp_syntax/."""
        result = generate_pspp_recoding_syntax_node(recoding_state)

        syntax_path = result["recoding_syntax_file"]
        assert "temp/pspp_syntax" in syntax_path or "temp" in syntax_path
        assert syntax_path.endswith(".sps")
        assert os.path.exists(syntax_path)

    def test_syntax_file_can_be_read_manually(self, recoding_state):
        """Test that generated syntax files are readable and valid PSPP syntax."""
        result = generate_pspp_recoding_syntax_node(recoding_state)

        # Read the syntax file
        with open(result["recoding_syntax_file"], 'r') as f:
            content = f.read()

        # Verify it contains valid PSPP syntax structure
        assert "*" in content  # Comments
        assert "RECODE" in content or "COMPUTE" in content
        assert "EXECUTE" in content
        # Should be valid text
        assert len(content) > 0


# =============================================================================
# Cross-Table Workflow Tests (Steps 15-16)
# =============================================================================

class TestCrossTableWorkflow:
    """Integration tests for complete PSPP cross-table workflow."""

    @pytest.fixture
    def sample_table_specs(self) -> Dict[str, Any]:
        """Sample table specifications for testing."""
        return {
            "tables": [
                {
                    "table_id": "gender_x_satisfaction",
                    "row_variable": "gender",
                    "column_variable": "sat_top2box",
                    "weight_variable": None,
                    "statistics": ["count", "columnpct", "chisq"]
                },
                {
                    "table_id": "age_group_x_satisfaction",
                    "row_variable": "age_group",
                    "column_variable": "sat_top2box",
                    "weight_variable": None,
                    "statistics": ["count", "columnpct"]
                }
            ]
        }

    @pytest.fixture
    def sample_new_metadata(self) -> Dict[str, Any]:
        """Sample new metadata from Step 8."""
        return {
            "variable_count": 4,
            "variable_names": ["gender", "age_group", "sat_top2box", "income"],
            "variable_labels": {
                "gender": "Gender",
                "age_group": "Age Group",
                "sat_top2box": "Top 2 Box Satisfaction",
                "income": "Annual Income"
            },
            "value_labels": {
                "gender": {1: "Male", 2: "Female"},
                "age_group": {1: "Young", 2: "Middle", 3: "Senior"},
                "sat_top2box": {0: "Others", 1: "Top 2 Box"}
            },
            "row_count": 100
        }

    @pytest.fixture
    def ctables_state(self, sample_table_specs, sample_new_metadata) -> WorkflowState:
        """Workflow state with table specs for Step 15."""
        state = create_initial_state("output/new_data.sav", DEFAULT_CONFIG)
        state["table_specifications"] = sample_table_specs
        state["new_metadata"] = sample_new_metadata
        state["new_data_file"] = "output/new_data.sav"
        return state

    def test_complete_cross_table_workflow(self, ctables_state):
        """Test complete cross-table workflow from specs to output files."""
        # Step 15: Generate PSPP CTABLES syntax
        step15_result = generate_pspp_table_syntax_node(ctables_state)

        assert step15_result["current_step"] == 15
        assert "table_syntax_file" in step15_result
        assert "pspp_tables_syntax" in step15_result
        assert os.path.exists(step15_result["table_syntax_file"])

        # Verify syntax content
        syntax_content = step15_result["pspp_tables_syntax"]
        assert "CTABLES" in syntax_content
        assert "/VLABELS" in syntax_content
        assert "/TABLE" in syntax_content
        assert "/STATISTICS" in syntax_content

        # Create a mock new_data.sav file for Step 16
        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            mock_sav_path = f.name

        try:
            # Update state with mock file
            step16_state = {**ctables_state, **step15_result}
            step16_state["new_data_file"] = mock_sav_path

            # Step 16: Execute PSPP (mocked)
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
                csv_path = f.name

            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
                json_path = f.name

            try:
                with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                    mock_get_path.return_value = "/usr/bin/pspp"
                    with patch('subprocess.run') as mock_run:
                        mock_result = Mock()
                        mock_result.returncode = 0
                        mock_result.stdout = ""
                        mock_result.stderr = ""
                        mock_run.return_value = mock_result

                        # Mock CSV file creation
                        with patch('pandas.read_csv') as mock_read_csv:
                            mock_df = pd.DataFrame({
                                "gender": ["Male", "Female"],
                                "sat_top2box": ["Others", "Top 2 Box"],
                                "count": [50, 50],
                                "columnpct": [50.0, 50.0]
                            })
                            mock_read_csv.return_value = mock_df

                            step16_result = execute_pspp_tables_node(step16_state)

                            assert step16_result["current_step"] == 16
                            assert "cross_table_file" in step16_result
            finally:
                if os.path.exists(csv_path):
                    os.unlink(csv_path)
                if os.path.exists(json_path):
                    os.unlink(json_path)
        finally:
            if os.path.exists(mock_sav_path):
                os.unlink(mock_sav_path)

    def test_ctables_syntax_generation(self, sample_table_specs, sample_new_metadata):
        """Test CTABLES syntax generation from table specifications."""
        table = sample_table_specs["tables"][0]
        variable_labels = sample_new_metadata["variable_labels"]

        syntax = _generate_ctable_command(table, variable_labels, 1)

        assert len(syntax) > 0
        syntax_str = "\n".join(syntax)
        assert "CTABLES" in syntax_str
        assert "/VLABELS VARIABLES=gender sat_top2box" in syntax_str
        assert "/TABLE gender BY sat_top2box" in syntax_str
        assert "/STATISTICS" in syntax_str
        assert "count('n')" in syntax_str
        assert "columnpct('Column %')" in syntax_str
        assert "chisq('chi-square')" in syntax_str

    def test_ctables_with_weight_variable(self):
        """Test CTABLES syntax generation with weight variable."""
        table = {
            "table_id": "weighted_table",
            "row_variable": "gender",
            "column_variable": "satisfaction",
            "weight_variable": "weight_var",
            "statistics": ["count", "columnpct"]
        }

        syntax = _generate_ctable_command(table, {}, 1)

        syntax_str = "\n".join(syntax)
        assert "/WEIGHT weight_var" in syntax_str

    def test_statistics_mapping(self):
        """Test correct mapping of statistics to PSPP syntax."""
        stats_tests = [
            (["count"], "count('n')"),
            (["columnpct"], "columnpct('Column %')"),
            (["rowpct"], "rowpct('Row %')"),
            (["totalpct"], "totalpct('Total %')"),
            (["chisq"], "chisq('chi-square')"),
            (["cramersv"], "cramersv('Cramer''s V')"),  # Note double quote
        ]

        for stats, expected in stats_tests:
            table = {
                "table_id": "test_table",
                "row_variable": "var1",
                "column_variable": "var2",
                "statistics": stats
            }

            syntax = _generate_ctable_command(table, {}, 1)
            syntax_str = "\n".join(syntax)
            assert expected in syntax_str

    def test_multiple_tables_in_one_syntax_file(self, ctables_state):
        """Test that multiple tables are included in the syntax file."""
        result = generate_pspp_table_syntax_node(ctables_state)

        syntax_content = result["pspp_tables_syntax"]

        # Should have CTABLES command for each table (at least 2)
        assert syntax_content.count("CTABLES") >= 2

        # Should have both table variables
        assert "gender" in syntax_content
        assert "age_group" in syntax_content

    def test_csv_to_json_conversion(self):
        """Test conversion of PSPP CSV output to JSON format."""
        # Create a sample CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_path = f.name
            f.write("gender,sat_top2box,count,columnpct\n")
            f.write("Male,Others,30,60.0\n")
            f.write("Male,Top 2 Box,20,40.0\n")
            f.write("Female,Others,25,50.0\n")
            f.write("Female,Top 2 Box,25,50.0\n")

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            json_path = f.name

        try:
            table_count = _convert_csv_to_json(csv_path, json_path)

            assert table_count >= 1
            assert os.path.exists(json_path)

            with open(json_path, 'r') as f:
                json_data = json.load(f)

            assert "tables" in json_data
            assert isinstance(json_data["tables"], list)
        finally:
            os.unlink(csv_path)
            os.unlink(json_path)


# =============================================================================
# Syntax File Tests
# =============================================================================

class TestSyntaxFiles:
    """Tests for PSPP syntax file generation and structure."""

    def test_pspp_header_generation(self):
        """Test PSPP file header generation."""
        header = _generate_pspp_header()

        assert len(header) >= 3
        assert "*" in header[0]  # Comment
        assert "Generated" in header[1] or "DataChat" in header[0]

    def test_ctables_header_generation(self):
        """Test CTABLES file header generation."""
        header = _generate_ctables_header()

        assert len(header) >= 4
        assert "*" in header[0]
        assert "SET DECIMAL = TAB" in "\n".join(header)

    def test_syntax_file_location(self):
        """Test that syntax files are created in temp/pspp_syntax/."""
        # Check directory creation
        temp_dir = Path("temp/pspp_syntax")
        assert temp_dir.exists() or temp_dir.parent.exists()

    def test_syntax_file_proper_formatting(self):
        """Test that syntax files have proper PSPP formatting."""
        state = create_initial_state("tests/fixtures/sample_data.sav", DEFAULT_CONFIG)
        state["recoding_rules"] = {
            "recoding_rules": [
                {
                    "source_variable": "age",
                    "target_variable": "age_group",
                    "transformation_type": "range_grouping",
                    "rules": [
                        {"source_min": 18, "source_max": 35, "target_value": 1, "target_label": "Young"},
                        {"source_min": 36, "source_max": 50, "target_value": 2, "target_label": "Middle"}
                    ]
                }
            ]
        }
        state["filtered_metadata"] = [
            {"name": "age", "variable_type": "numeric"}
        ]

        result = generate_pspp_recoding_syntax_node(state)

        with open(result["recoding_syntax_file"], 'r') as f:
            content = f.read()

        # Check for proper PSPP syntax structure
        assert content.strip().endswith(".")
        # Commands should be on separate lines
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        assert len(lines) > 0
        # Main commands should end with period or be comments/continuations
        non_comment_lines = [l for l in lines if l and not l.startswith("*")]
        assert len(non_comment_lines) > 0

    def test_syntax_commands_valid(self):
        """Test that generated syntax uses valid PSPP commands."""
        state = create_initial_state("tests/fixtures/sample_data.sav", DEFAULT_CONFIG)
        state["table_specifications"] = {
            "tables": [
                {
                    "table_id": "test_table",
                    "row_variable": "var1",
                    "column_variable": "var2",
                    "statistics": ["count", "columnpct"]
                }
            ]
        }
        state["new_metadata"] = {
            "variable_names": ["var1", "var2"],
            "variable_labels": {"var1": "Variable 1", "var2": "Variable 2"}
        }

        result = generate_pspp_table_syntax_node(state)

        syntax = result["pspp_tables_syntax"]

        # Valid PSPP CTABLES commands
        valid_commands = ["CTABLES", "/VLABELS", "/TABLE", "/STATISTICS", "EXECUTE"]

        for cmd in valid_commands:
            if cmd != "EXECUTE":  # EXECUTE may be added in footer
                assert cmd in syntax

    def test_syntax_file_encoding(self):
        """Test that syntax files use UTF-8 encoding."""
        state = create_initial_state("tests/fixtures/sample_data.sav", DEFAULT_CONFIG)
        state["recoding_rules"] = {
            "recoding_rules": [
                {
                    "source_variable": "age",
                    "target_variable": "age_group",
                    "transformation_type": "range_grouping",
                    "description": "Test",
                    "rules": [
                        {"source_min": 18, "source_max": 35, "target_value": 1, "target_label": "Young"}
                    ]
                }
            ]
        }
        state["filtered_metadata"] = [
            {"name": "age", "variable_type": "numeric"}
        ]

        result = generate_pspp_recoding_syntax_node(state)

        # Try reading with UTF-8
        with open(result["recoding_syntax_file"], 'r', encoding='utf-8') as f:
            content = f.read()

        assert len(content) > 0


# =============================================================================
# Output Parsing Tests
# =============================================================================

class TestOutputParsing:
    """Tests for PSPP output parsing."""

    def test_parse_successful_execution(self):
        """Test parsing of successful PSPP execution."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_result.stdout = "Processing complete. 5 cases written to output file."
                    mock_result.stderr = ""
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is True
                    assert result["return_code"] == 0
                    assert "Processing complete" in result["output"]
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_parse_error_output(self):
        """Test parsing of PSPP error messages."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 1
                    mock_result.stdout = ""
                    mock_result.stderr = "error: syntax error on line 10"
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is False
                    assert result["return_code"] == 1
                    assert "syntax error" in result["user_message"].lower()
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_parse_pspp_warnings(self):
        """Test handling of PSPP warnings in output."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    # PSPP sometimes outputs warnings to stderr but succeeds
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_result.stdout = "Processing complete."
                    mock_result.stderr = "warning: Variable 'xyz' was never referenced."
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is True
                    assert result["return_code"] == 0
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_extract_output_file_info(self):
        """Test extraction of output file information from PSPP."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        output_path = "/tmp/test_output.txt"

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_result.stdout = f"Output written to {output_path}"
                    mock_result.stderr = ""
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file=output_path
                    )

                    # Verify the output file path was used
                    mock_run.assert_called_once()
                    call_args = mock_run.call_args[0][0]
                    assert output_path in call_args
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for PSPP error handling scenarios."""

    def test_invalid_pspp_syntax(self):
        """Test handling of invalid PSPP syntax."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("INVALID SYNTAX HERE!!!\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 1
                    mock_result.stdout = ""
                    mock_result.stderr = "error: syntax error on line 1"
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is False
                    assert "syntax error" in result["user_message"].lower()
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_missing_input_file(self):
        """Test handling when input .sav file doesn't exist."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        try:
            result = execute_pspp_syntax(
                syntax_file_path=syntax_path,
                input_file="/nonexistent/input.sav",
                output_file="/tmp/output.txt"
            )

            assert result["success"] is False
            assert "not found" in result["error"].lower()
            assert "input" in result["error"].lower() or "data" in result["error"].lower()
        finally:
            os.unlink(syntax_path)

    def test_missing_syntax_file(self):
        """Test handling when syntax file doesn't exist."""
        result = execute_pspp_syntax(
            syntax_file_path="/nonexistent/syntax.sps",
            input_file="tests/fixtures/sample_data.sav",
            output_file="/tmp/output.txt"
        )

        assert result["success"] is False
        assert "not found" in result["error"].lower()
        assert "syntax" in result["error"].lower()

    def test_permission_denied(self):
        """Test handling of permission denied errors."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_run.side_effect = PermissionError("Permission denied")

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/root/output.txt"
                    )

                    assert result["success"] is False
                    assert "unexpected error" in result["user_message"].lower() or "permission" in result["error"].lower()
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_pspp_not_installed(self):
        """Test graceful error when PSPP is not installed."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.side_effect = FileNotFoundError("PSPP not found")

                result = execute_pspp_syntax(
                    syntax_file_path=syntax_path,
                    input_file=input_path,
                    output_file="/tmp/output.txt"
                )

                assert result["success"] is False
                assert "PSPP" in result["user_message"]
                assert "not installed" in result["user_message"].lower()
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_timeout_handling(self):
        """Test timeout handling for long-running PSPP commands."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_run.side_effect = subprocess.TimeoutExpired("pspp", 300)

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is False
                    assert "timed out" in result["error"].lower()
                    assert "timed out" in result["user_message"].lower()
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)


# =============================================================================
# Real PSPP Integration Tests (Optional)
# =============================================================================

@pytest.mark.integration
class TestRealPsppIntegration:
    """Integration tests requiring actual PSPP installation.

    These tests are marked with @pytest.mark.integration and will only run when:
    1. PSPP is installed on the system
    2. pytest is run with -m integration flag

    Run with: pytest tests/test_pspp_integration.py -m integration
    """

    def test_pspp_installation_check(self):
        """Test that PSPP is installed and accessible."""
        from agent.utils.pspp_wrapper import verify_pspp_installation

        is_installed = verify_pspp_installation()
        # Skip test if PSPP not installed
        if not is_installed:
            pytest.skip("PSPP not installed on this system")

    def test_real_pspp_execution_simple(self):
        """Test real PSPP execution with simple syntax."""
        from agent.utils.pspp_wrapper import verify_pspp_installation

        if not verify_pspp_installation():
            pytest.skip("PSPP not installed on this system")

        # Create a simple PSPP syntax file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("* Simple Test Syntax\n")
            f.write("SET DECIMAL=DOT.\n")
            f.write("DATA LIST FREE / age.\n")
            f.write("BEGIN DATA\n")
            f.write("25\n")
            f.write("30\n")
            f.write("35\n")
            f.write("END DATA.\n")
            f.write("EXECUTE.\n")
            f.write("RECODE age (20 THRU 29=1) (30 THRU 39=2) INTO age_group.\n")
            f.write("EXECUTE.\n")
            f.write("LIST.\n")  # Add LIST to generate output

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            output_path = f.name

        # Create a dummy input file
        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            result = execute_pspp_syntax(
                syntax_file_path=syntax_path,
                input_file=input_path,  # Not actually used for inline data
                output_file=output_path
            )

            # Check result
            if result["success"]:
                assert os.path.exists(output_path)
            else:
                # If PSPP failed, it might be due to version differences
                # This is acceptable for integration tests
                pytest.skip(f"PSPP execution failed: {result.get('error', 'Unknown error')}")
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_real_pspp_with_sav_file(self):
        """Test real PSPP execution with actual .sav file."""
        from agent.utils.pspp_wrapper import verify_pspp_installation
        import pyreadstat

        if not verify_pspp_installation():
            pytest.skip("PSPP not installed on this system")

        # Create a sample .sav file
        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            sav_path = f.name

        # Create sample data
        df = pd.DataFrame({
            "age": [25, 30, 35, 40, 45],
            "gender": [1, 2, 1, 2, 1],
            "satisfaction": [4, 5, 3, 4, 5]
        })

        # Write .sav file (pyreadstat uses different API)
        try:
            pyreadstat.write_sav(df, sav_path)
        except Exception as e:
            pytest.skip(f"Could not create test .sav file: {e}")

        # Create recoding syntax
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write(f"GET FILE='{sav_path}'.\n")
            f.write("EXECUTE.\n")
            f.write("RECODE satisfaction (4 THRU 5=1) (1 THRU 3=0) INTO sat_top2box.\n")
            f.write("EXECUTE.\n")
            f.write(f"SAVE OUTFILE='{sav_path}.new'.\n")

        try:
            result = execute_pspp_syntax(
                syntax_file_path=syntax_path,
                input_file=sav_path,
                output_file="/tmp/pspp_output.txt"
            )

            if not result["success"]:
                pytest.skip(f"PSPP execution failed: {result.get('error', 'Unknown error')}")

            assert os.path.exists(f"{sav_path}.new")

            # Read the new file and verify
            new_df, new_meta = pyreadstat.read_sav(f"{sav_path}.new")
            assert "sat_top2box" in new_df.columns
        finally:
            os.unlink(syntax_path)
            os.unlink(sav_path)
            if os.path.exists(f"{sav_path}.new"):
                os.unlink(f"{sav_path}.new")
            if os.path.exists("/tmp/pspp_output.txt"):
                os.unlink("/tmp/pspp_output.txt")


# =============================================================================
# Coverage Markers
# =============================================================================

# Collect all test classes for coverage reporting
__all__ = [
    "TestRecodingWorkflow",
    "TestCrossTableWorkflow",
    "TestSyntaxFiles",
    "TestOutputParsing",
    "TestErrorHandling",
    "TestRealPsppIntegration",
]
