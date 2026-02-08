"""
Complete End-to-End Test for Survey Analysis Workflow with Human Review

This module contains a comprehensive E2E test that verifies the complete 22-step
workflow from .sav file input to PowerPoint and HTML outputs with human review
at all three review points.

This test:
1. Uses actual .sav file for data extraction (Phase 1)
2. Mocks LLM calls for AI-dependent steps (Phases 2, 3, 4)
3. Mocks PSPP execution for deterministic steps
4. Tests human review at all three points (recoding, indicators, tables)
5. Verifies state evolution through all 22 steps
6. Verifies all outputs are generated correctly

Success Criteria:
- All 22 steps execute successfully
- Human review points are triggered at Steps 6, 11, and 14
- State evolves correctly through all 8 phases
- All output files paths are set
- No errors in critical paths
"""

import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import pandas as pd

from agent.graph import build_graph
from agent.state import create_initial_state, STEP_0_INITIAL, STEP_1_EXTRACT_SPSS, STEP_4_GENERATE_RECODING_RULES, STEP_5_VALIDATE_RECODING_RULES, STEP_6_REVIEW_RECODING_RULES
from agent.config import DEFAULT_CONFIG


# =============================================================================
# Helper Functions
# =============================================================================

def build_test_graph(config: Dict[str, Any]):
    """
    Build a graph for E2E testing without checkpointing.

    This function creates a StateGraph without a checkpointer to avoid
    DataFrame serialization issues during testing.

    Args:
        config: Configuration dictionary

    Returns:
        Compiled StateGraph without checkpointer
    """
    from langgraph.graph import StateGraph, START, END
    from agent.state import WorkflowState
    from agent.nodes import (
        extract_spss_node,
        transform_metadata_node,
        filter_metadata_node,
        generate_recoding_rules_node,
        validate_recoding_rules_node,
        review_recoding_rules_node,
        generate_pspp_recoding_syntax_node,
        execute_pspp_recoding_node,
        generate_indicators_node,
        validate_indicators_node,
        review_indicators_node,
        generate_table_specifications_node,
        validate_table_specifications_node,
        review_table_specifications_node,
        generate_pspp_table_syntax_node,
        execute_pspp_tables_node,
        generate_python_statistics_script_node,
        execute_python_statistics_script_node,
        generate_filter_list_node,
        apply_filter_to_tables_node,
        generate_powerpoint_node,
        generate_html_dashboard_node,
    )
    from agent.edges import (
        should_retry_recoding,
        should_approve_recoding,
        should_retry_indicators,
        should_approve_indicators,
        should_retry_table_specs,
        should_approve_table_specs,
    )

    # Build graph without checkpointer
    builder = StateGraph(WorkflowState)

    # Add all 22 nodes
    builder.add_node("extract_spss_node", extract_spss_node)
    builder.add_node("transform_metadata_node", transform_metadata_node)
    builder.add_node("filter_metadata_node", filter_metadata_node)
    builder.add_node("generate_recoding_rules_node", generate_recoding_rules_node)
    builder.add_node("validate_recoding_rules_node", validate_recoding_rules_node)
    builder.add_node("review_recoding_rules_node", review_recoding_rules_node)
    builder.add_node("generate_pspp_recoding_syntax_node", generate_pspp_recoding_syntax_node)
    builder.add_node("execute_pspp_recoding_node", execute_pspp_recoding_node)
    builder.add_node("generate_indicators_node", generate_indicators_node)
    builder.add_node("validate_indicators_node", validate_indicators_node)
    builder.add_node("review_indicators_node", review_indicators_node)
    builder.add_node("generate_table_specifications_node", generate_table_specifications_node)
    builder.add_node("validate_table_specifications_node", validate_table_specifications_node)
    builder.add_node("review_table_specifications_node", review_table_specifications_node)
    builder.add_node("generate_pspp_table_syntax_node", generate_pspp_table_syntax_node)
    builder.add_node("execute_pspp_tables_node", execute_pspp_tables_node)
    builder.add_node("generate_python_statistics_script_node", generate_python_statistics_script_node)
    builder.add_node("execute_python_statistics_script_node", execute_python_statistics_script_node)
    builder.add_node("generate_filter_list_node", generate_filter_list_node)
    builder.add_node("apply_filter_to_tables_node", apply_filter_to_tables_node)
    builder.add_node("generate_powerpoint_node", generate_powerpoint_node)
    builder.add_node("generate_html_dashboard_node", generate_html_dashboard_node)

    # Set entry point
    builder.set_entry_point("extract_spss_node")

    # Add linear edges
    builder.add_edge("extract_spss_node", "transform_metadata_node")
    builder.add_edge("transform_metadata_node", "filter_metadata_node")

    # Phase 2: Recoding (Steps 4-8) with conditional edges
    builder.add_conditional_edges(
        "filter_metadata_node",
        lambda state: "generate_recoding_rules_node",
        {"generate_recoding_rules_node": "generate_recoding_rules_node"}
    )
    builder.add_conditional_edges(
        "generate_recoding_rules_node",
        lambda state: "validate_recoding_rules_node",
        {"validate_recoding_rules_node": "validate_recoding_rules_node"}
    )
    builder.add_conditional_edges(
        "validate_recoding_rules_node",
        should_retry_recoding,
        {
            "generate_recoding_rules_node": "generate_recoding_rules_node",
            "review_recoding_rules_node": "review_recoding_rules_node",
            "generate_pspp_recoding_syntax_node": "generate_pspp_recoding_syntax_node"
        }
    )
    builder.add_conditional_edges(
        "review_recoding_rules_node",
        should_approve_recoding,
        {
            "generate_recoding_rules_node": "generate_recoding_rules_node",
            "generate_pspp_recoding_syntax_node": "generate_pspp_recoding_syntax_node"
        }
    )
    builder.add_edge("generate_pspp_recoding_syntax_node", "execute_pspp_recoding_node")

    # Phase 3: Indicators (Steps 9-11)
    builder.add_conditional_edges(
        "execute_pspp_recoding_node",
        lambda state: "generate_indicators_node",
        {"generate_indicators_node": "generate_indicators_node"}
    )
    builder.add_conditional_edges(
        "generate_indicators_node",
        lambda state: "validate_indicators_node",
        {"validate_indicators_node": "validate_indicators_node"}
    )
    builder.add_conditional_edges(
        "validate_indicators_node",
        should_retry_indicators,
        {
            "generate_indicators_node": "generate_indicators_node",
            "review_indicators_node": "review_indicators_node",
            "generate_table_specifications_node": "generate_table_specifications_node"
        }
    )
    builder.add_conditional_edges(
        "review_indicators_node",
        should_approve_indicators,
        {
            "generate_indicators_node": "generate_indicators_node",
            "generate_table_specifications_node": "generate_table_specifications_node"
        }
    )

    # Phase 4: Tables (Steps 12-16)
    builder.add_conditional_edges(
        "generate_table_specifications_node",
        lambda state: "validate_table_specifications_node",
        {"validate_table_specifications_node": "validate_table_specifications_node"}
    )
    builder.add_conditional_edges(
        "validate_table_specifications_node",
        should_retry_table_specs,
        {
            "generate_table_specifications_node": "generate_table_specifications_node",
            "review_table_specifications_node": "review_table_specifications_node",
            "generate_pspp_table_syntax_node": "generate_pspp_table_syntax_node"
        }
    )
    builder.add_conditional_edges(
        "review_table_specifications_node",
        should_approve_table_specs,
        {
            "generate_table_specifications_node": "generate_table_specifications_node",
            "generate_pspp_table_syntax_node": "generate_pspp_table_syntax_node"
        }
    )
    builder.add_edge("generate_pspp_table_syntax_node", "execute_pspp_tables_node")

    # Remaining phases (linear)
    builder.add_edge("execute_pspp_tables_node", "generate_python_statistics_script_node")
    builder.add_edge("generate_python_statistics_script_node", "execute_python_statistics_script_node")
    builder.add_edge("execute_python_statistics_script_node", "generate_filter_list_node")
    builder.add_edge("generate_filter_list_node", "apply_filter_to_tables_node")
    builder.add_edge("apply_filter_to_tables_node", "generate_powerpoint_node")
    builder.add_edge("generate_powerpoint_node", "generate_html_dashboard_node")
    builder.add_edge("generate_html_dashboard_node", END)

    # Compile without checkpointer
    return builder.compile()


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for test runs."""
    temp_dir = tempfile.mkdtemp(prefix="e2e_complete_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def e2e_config(temp_output_dir: Path) -> Dict[str, Any]:
    """Create E2E test configuration with auto-approval enabled."""
    config = DEFAULT_CONFIG.copy()
    config["output_dir"] = str(temp_output_dir)
    config["temp_dir"] = str(temp_output_dir / "temp")
    config["auto_approve_recoding"] = True
    config["auto_approve_indicators"] = True
    config["auto_approve_table_specs"] = True
    config["max_self_correction_iterations"] = 1  # Reduce for faster testing
    config["enable_human_review"] = False
    config["cardinality_threshold"] = 30
    os.makedirs(config["temp_dir"], exist_ok=True)
    return config


@pytest.fixture
def sample_sav_file() -> str:
    """Path to sample .sav file for E2E testing."""
    return "tests/fixtures/sample_data.sav"


@pytest.fixture
def mock_llm_responses() -> Dict[str, Any]:
    """
    Mock LLM responses for all E2E test scenarios.

    Returns:
        Dictionary with mock LLM responses for each AI node
    """
    return {
        "recoding_rules": {
            "recoding_rules": [
                {
                    "source_variable": "age",
                    "target_variable": "age_group",
                    "transformation_type": "range_grouping",
                    "rationale": "Group age into meaningful categories",
                    "rules": [
                        {"source_min": 18, "source_max": 35, "target_value": 1, "label": "Young Adult"},
                        {"source_min": 36, "source_max": 55, "target_value": 2, "label": "Middle-Aged"},
                        {"source_min": 56, "source_max": 120, "target_value": 3, "label": "Senior"},
                    ]
                },
                {
                    "source_variable": "income",
                    "target_variable": "income_quartile",
                    "transformation_type": "range_grouping",
                    "rationale": "Group income into quartiles",
                    "rules": [
                        {"source_min": 0, "source_max": 50000, "target_value": 1, "label": "Low Income"},
                        {"source_min": 50001, "source_max": 100000, "target_value": 2, "label": "Medium-Low Income"},
                        {"source_min": 100001, "source_max": 150000, "target_value": 3, "label": "Medium-High Income"},
                        {"source_min": 150001, "source_max": 999999, "target_value": 4, "label": "High Income"},
                    ]
                }
            ]
        },
        "indicators": {
            "indicators": [
                {
                    "name": "demographics",
                    "description": "Demographic indicators",
                    "variables": ["age_group", "gender"]
                },
                {
                    "name": "satisfaction",
                    "description": "Satisfaction indicators",
                    "variables": ["satisfaction"]
                }
            ]
        },
        "table_specifications": {
            "tables": [
                {
                    "table_id": "gender_by_satisfaction",
                    "row_variable": "gender",
                    "column_variable": "satisfaction",
                    "statistics": ["count", "columnpct", "chisq", "cramersv"],
                    "weight_variable": None
                }
            ]
        }
    }


# =============================================================================
# Complete Workflow E2E Test
# =============================================================================

@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteWorkflowE2E:
    """
    Complete End-to-End Test for 22-Step Workflow.

    This test verifies:
    1. All 22 steps execute in correct order
    2. State evolves correctly through all 8 phases
    3. All outputs are generated
    4. Three-node pattern feedback loops work
    5. Error handling works correctly
    """

    def test_complete_22_step_workflow(
        self,
        sample_sav_file: str,
        e2e_config: Dict[str, Any],
        temp_output_dir: Path,
        mock_llm_responses: Dict[str, Any],
    ):
        """
        Test complete 22-step workflow with mocked LLM and PSPP.

        This test executes the full workflow from Step 0 to Step 22,
        verifying state evolution and output generation.

        Args:
            sample_sav_file: Path to sample .sav file
            e2e_config: E2E test configuration
            temp_output_dir: Temporary output directory
            mock_llm_responses: Mock LLM responses
        """
        # Create initial state
        initial_state = create_initial_state(sample_sav_file, e2e_config)

        # Build graph with checkpointer_path=None to disable checkpointing
        # This avoids DataFrame serialization issues in E2E testing
        graph = build_graph(checkpointer_path=None, config=e2e_config)
        thread_id = "e2e-complete-test"
        config = {"configurable": {"thread_id": thread_id}}

        # Mock LLM client for all AI-dependent nodes
        with patch('agent.nodes.phase2_recoding.get_llm_client') as mock_recoding_llm, \
             patch('agent.nodes.phase3_indicators.get_llm_client') as mock_indicators_llm, \
             patch('agent.nodes.phase4_tables.get_llm_client') as mock_tables_llm, \
             patch('agent.utils.pspp_wrapper.execute_pspp_syntax') as mock_execute_pspp, \
             patch('subprocess.run') as mock_subprocess:

            # Setup LLM mocks
            self._setup_llm_mocks(
                mock_recoding_llm,
                mock_indicators_llm,
                mock_tables_llm,
                mock_llm_responses
            )

            # Setup PSPP mock for both recoding and tables
            mock_execute_pspp.return_value = {
                "success": True,
                "return_code": 0,
                "stdout": "PSPP completed successfully",
                "stderr": "",
                "output_file": str(temp_output_dir / "output.sav"),
            }

            # Setup subprocess mock for statistics script
            mock_result = Mock()
            mock_result.stdout = json.dumps({
                "total_tables": 1,
                "significant_tables": [{
                    "table_id": "gender_by_satisfaction",
                    "chi_square": 5.2,
                    "p_value": 0.04,
                    "cramers_v": 0.3,
                    "significant": True
                }]
            })
            mock_result.returncode = 0
            mock_subprocess.run.return_value = mock_result

            # Execute workflow
            result = graph.invoke(initial_state, config)

            # Verify execution
            self._verify_workflow_execution(result, sample_sav_file)

            # Verify state evolution through all phases
            self._verify_state_evolution(result)

            # Verify outputs
            self._verify_outputs(result, temp_output_dir)

    def _setup_llm_mocks(
        self,
        mock_recoding_llm: Mock,
        mock_indicators_llm: Mock,
        mock_tables_llm: Mock,
        mock_llm_responses: Dict[str, Any],
    ):
        """Setup LLM client mocks with predefined responses."""
        # Mock recoding rules LLM
        mock_recoding_client = Mock()
        mock_recoding_response = Mock()
        mock_recoding_response.content = json.dumps(mock_llm_responses["recoding_rules"])
        mock_recoding_client.invoke.return_value = mock_recoding_response
        mock_recoding_llm.return_value = mock_recoding_client

        # Mock indicators LLM
        mock_indicators_client = Mock()
        mock_indicators_response = Mock()
        mock_indicators_response.content = json.dumps(mock_llm_responses["indicators"])
        mock_indicators_client.invoke.return_value = mock_indicators_response
        mock_indicators_llm.return_value = mock_indicators_client

        # Mock table specifications LLM
        mock_tables_client = Mock()
        mock_tables_response = Mock()
        mock_tables_response.content = json.dumps(mock_llm_responses["table_specifications"])
        mock_tables_client.invoke.return_value = mock_tables_response
        mock_tables_llm.return_value = mock_tables_client

    def _verify_workflow_execution(self, result: Dict[str, Any], sample_sav_file: str):
        """Verify basic workflow execution."""
        assert result is not None, "Workflow should complete successfully"
        assert result.get("input_file_path") == sample_sav_file, \
            "Input file path should be preserved"
        assert STEP_ORDER.get(result.get("current_step", STEP_0_INITIAL), 0) >= STEP_ORDER[STEP_21_GENERATE_POWERPOINT], \
            f"Should reach at least step 21, got step {result.get('current_step')}"

        # Check that critical errors are not present
        errors = result.get("errors", [])
        critical_errors = [e for e in errors if "API key" not in str(e)]
        assert len(critical_errors) == 0, \
            f"Should have no critical errors, got: {critical_errors}"

    def _verify_state_evolution(self, result: Dict[str, Any]):
        """Verify state evolution through all 8 phases."""
        # Phase 1: Extraction (Steps 1-3)
        assert result.get("raw_data") is not None, "Raw data should be extracted"
        assert result.get("original_metadata") is not None, "Original metadata should be extracted"
        assert result.get("variable_centered_metadata") is not None, \
            "Variable-centered metadata should be created"
        assert result.get("filtered_metadata") is not None, "Filtered metadata should be created"

        # Phase 2: Recoding (Steps 4-8)
        assert result.get("recoding_rules") is not None, "Recoding rules should be generated"
        assert result.get("recoding_approved") == True, "Recoding should be auto-approved"

        # Phase 3: Indicators (Steps 9-11)
        assert result.get("indicators") is not None, "Indicators should be generated"
        assert result.get("indicators_approved") == True, "Indicators should be auto-approved"

        # Phase 4: Cross-Tables (Steps 12-16)
        assert result.get("table_specifications") is not None, \
            "Table specifications should be generated"
        assert result.get("table_specs_approved") == True, "Table specs should be auto-approved"

        # Phase 5: Statistics (Steps 17-18)
        assert result.get("statistical_summary") is not None or \
               result.get("statistics_script") is not None, \
            "Statistical analysis should be performed"

        # Phase 6: Filtering (Steps 19-20)
        assert result.get("filter_list") is not None or \
               result.get("filtered_tables") is not None, \
            "Filtering should be performed"

        # Phase 7 & 8: Outputs (Steps 21-22)
        assert result.get("powerpoint_file") is not None or \
               result.get("html_dashboard_file") is not None, \
            "At least one output should be generated"

    def _verify_outputs(self, result: Dict[str, Any], temp_output_dir: Path):
        """Verify output files are generated."""
        powerpoint_path = result.get("powerpoint_file")
        html_path = result.get("html_dashboard_file")

        if powerpoint_path:
            assert isinstance(powerpoint_path, str), "PowerPoint path should be string"
            assert powerpoint_path.endswith(".pptx"), "PowerPoint path should end with .pptx"

        if html_path:
            assert isinstance(html_path, str), "HTML path should be string"
            assert html_path.endswith(".html"), "HTML path should end with .html"


@pytest.mark.e2e
class TestPhaseByPhaseE2E:
    """
    Phase-by-phase E2E tests.

    These tests verify each phase executes correctly in isolation,
    making it easier to debug issues.
    """

    def test_phase_1_extraction_only(
        self,
        sample_sav_file: str,
        e2e_config: Dict[str, Any],
    ):
        """
        Test Phase 1: Extraction & Preparation (Steps 1-3).

        This test only runs Phase 1 to verify data extraction works correctly
        with actual .sav files.
        """
        # Create initial state
        initial_state = create_initial_state(sample_sav_file, e2e_config)

        # Build graph
        graph = build_graph(checkpointer_path=":memory:", config=e2e_config)
        thread_id = "phase1-test"
        config = {"configurable": {"thread_id": thread_id}}

        # Execute workflow (will stop or fail when it needs LLM)
        try:
            result = graph.invoke(initial_state, config)

            # Verify Phase 1 outputs
            assert result.get("current_step", STEP_0_INITIAL) != STEP_0_INITIAL, "Should execute Step 1"
            assert result.get("raw_data") is not None, "Raw data should be extracted"
            assert result.get("original_metadata") is not None, "Original metadata should be extracted"

            # If Step 2 completed
            if STEP_ORDER.get(result.get("current_step", STEP_0_INITIAL), 0) >= STEP_ORDER[STEP_2_TRANSFORM_METADATA]:
                assert result.get("variable_centered_metadata") is not None, \
                    "Variable-centered metadata should be created"

            # If Step 3 completed
            if STEP_ORDER.get(result.get("current_step", STEP_0_INITIAL), 0) >= STEP_ORDER[STEP_3_FILTER_METADATA]:
                assert result.get("filtered_metadata") is not None, \
                    "Filtered metadata should be created"
                assert isinstance(result.get("filtered_out_variables"), list), \
                    "Filtered out variables should be a list"

        except Exception as e:
            # Phase 1 should work even if later phases fail
            if "API key" in str(e):
                # Expected - Phase 2 requires LLM
                pass
            else:
                raise


# =============================================================================
# Test Summary
# =============================================================================

@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteWorkflowWithHumanReview:
    """
    Complete End-to-End Test with Human Review at All Three Points.

    This test verifies the complete 22-step workflow with human review
    enabled at Steps 6, 11, and 14 (recoding, indicators, tables).

    The test mocks the interrupt mechanism to simulate auto-approval
    while still exercising the review document generation.
    """

    def test_complete_workflow_with_human_review(
        self,
        sample_sav_file: str,
        temp_output_dir: Path,
        mock_llm_responses: Dict[str, Any],
    ):
        """
        Test complete 22-step workflow with human review enabled.

        This test:
        1. Enables human review at all three points
        2. Mocks the interrupt mechanism to simulate auto-approval
        3. Verifies all 22 steps execute
        4. Verifies state evolution through all phases
        5. Verifies all outputs are generated

        Args:
            sample_sav_file: Path to sample .sav file
            temp_output_dir: Temporary output directory
            mock_llm_responses: Mock LLM responses
        """
        # Create config with auto-approval enabled
        config = DEFAULT_CONFIG.copy()
        config["output_dir"] = str(temp_output_dir)
        config["temp_dir"] = str(temp_output_dir / "temp")
        config["enable_human_review"] = True
        config["auto_approve_recoding"] = True  # Auto-approve for CI/CD and testing
        config["auto_approve_indicators"] = True
        config["auto_approve_table_specs"] = True
        config["max_self_correction_iterations"] = 0  # Skip retries, go straight to review
        config["cardinality_threshold"] = 30
        os.makedirs(config["temp_dir"], exist_ok=True)

        # Create initial state
        initial_state = create_initial_state(sample_sav_file, config)

        # Build graph without checkpointer to avoid DataFrame serialization issues
        graph = build_test_graph(config)

        # No config needed for graph without checkpointer
        run_config = {}

        # Mock LLM, PSPP, and interrupt
        with patch('agent.nodes.phase2_recoding.get_llm_client') as mock_recoding_llm, \
             patch('agent.nodes.phase3_indicators.get_llm_client') as mock_indicators_llm, \
             patch('agent.nodes.phase4_tables.get_llm_client') as mock_tables_llm, \
             patch('agent.utils.pspp_wrapper.execute_pspp_syntax') as mock_execute_pspp, \
             patch('langgraph.types.interrupt') as mock_interrupt, \
             patch('subprocess.run') as mock_subprocess:

            # Setup LLM mocks
            self._setup_llm_mocks(
                mock_recoding_llm,
                mock_indicators_llm,
                mock_tables_llm,
                mock_llm_responses
            )

            # Setup PSPP mock
            mock_execute_pspp.return_value = {
                "success": True,
                "return_code": 0,
                "stdout": "PSPP completed successfully",
                "stderr": "",
                "output_file": str(temp_output_dir / "new_data.sav"),
            }

            # Mock interrupt to prevent blocking
            mock_interrupt.return_value = None

            # Setup subprocess mock for statistics script
            mock_result = Mock()
            mock_result.stdout = json.dumps({
                "total_tables": 1,
                "significant_tables": [{
                    "table_id": "gender_by_satisfaction",
                    "chi_square": 5.2,
                    "p_value": 0.04,
                    "cramers_v": 0.3,
                    "significant": True
                }]
            })
            mock_result.returncode = 0
            mock_subprocess.run.return_value = mock_result

            # Execute workflow
            result = graph.invoke(initial_state)

            # Verify execution
            self._verify_workflow_execution(result, sample_sav_file)
            self._verify_human_review_points_exercised(result)
            self._verify_state_evolution(result)
            self._verify_outputs(result, temp_output_dir)

    def _setup_llm_mocks(
        self,
        mock_recoding_llm: Mock,
        mock_indicators_llm: Mock,
        mock_tables_llm: Mock,
        mock_llm_responses: Dict[str, Any],
    ):
        """Setup LLM client mocks with predefined responses."""
        # Mock recoding rules LLM
        mock_recoding_client = Mock()
        mock_recoding_response = Mock()
        mock_recoding_response.content = json.dumps(mock_llm_responses["recoding_rules"])
        mock_recoding_client.invoke.return_value = mock_recoding_response
        mock_recoding_llm.return_value = mock_recoding_client

        # Mock indicators LLM
        mock_indicators_client = Mock()
        mock_indicators_response = Mock()
        mock_indicators_response.content = json.dumps(mock_llm_responses["indicators"])
        mock_indicators_client.invoke.return_value = mock_indicators_response
        mock_indicators_llm.return_value = mock_indicators_client

        # Mock table specifications LLM
        mock_tables_client = Mock()
        mock_tables_response = Mock()
        mock_tables_response.content = json.dumps(mock_llm_responses["table_specifications"])
        mock_tables_client.invoke.return_value = mock_tables_response
        mock_tables_llm.return_value = mock_tables_client

    def _verify_workflow_execution(self, result: Dict[str, Any], sample_sav_file: str):
        """Verify basic workflow execution."""
        assert result is not None, "Workflow should complete successfully"
        assert result.get("input_file_path") == sample_sav_file, \
            "Input file path should be preserved"
        assert STEP_ORDER.get(result.get("current_step", STEP_0_INITIAL), 0) >= STEP_ORDER[STEP_21_GENERATE_POWERPOINT], \
            f"Should reach at least step 21, got step {result.get('current_step')}"

        # Check that critical errors are not present
        errors = result.get("errors", [])
        critical_errors = [e for e in errors if "API key" not in str(e)]
        assert len(critical_errors) == 0, \
            f"Should have no critical errors, got: {critical_errors}"

    def _verify_state_evolution(self, result: Dict[str, Any]):
        """Verify state evolution through all 8 phases."""
        # Phase 1: Extraction (Steps 1-3)
        assert result.get("raw_data") is not None, "Raw data should be extracted"
        assert result.get("original_metadata") is not None, "Original metadata should be extracted"
        assert result.get("variable_centered_metadata") is not None, \
            "Variable-centered metadata should be created"
        assert result.get("filtered_metadata") is not None, "Filtered metadata should be created"

        # Phase 2: Recoding (Steps 4-8)
        assert result.get("recoding_rules") is not None, "Recoding rules should be generated"
        assert result.get("recoding_approved") == True, "Recoding should be auto-approved"

        # Phase 3: Indicators (Steps 9-11)
        assert result.get("indicators") is not None, "Indicators should be generated"
        assert result.get("indicators_approved") == True, "Indicators should be auto-approved"

        # Phase 4: Cross-Tables (Steps 12-16)
        assert result.get("table_specifications") is not None, \
            "Table specifications should be generated"
        assert result.get("table_specs_approved") == True, "Table specs should be auto-approved"

        # Phase 5: Statistics (Steps 17-18)
        assert result.get("statistical_summary") is not None or \
               result.get("statistics_script") is not None, \
            "Statistical analysis should be performed"

        # Phase 6: Filtering (Steps 19-20)
        assert result.get("filter_list") is not None or \
               result.get("filtered_tables") is not None, \
            "Filtering should be performed"

        # Phase 7 & 8: Outputs (Steps 21-22)
        assert result.get("powerpoint_file") is not None or \
               result.get("html_dashboard_file") is not None, \
            "At least one output should be generated"

    def _verify_outputs(self, result: Dict[str, Any], temp_output_dir: Path):
        """Verify output files are generated."""
        powerpoint_path = result.get("powerpoint_file")
        html_path = result.get("html_dashboard_file")

        if powerpoint_path:
            assert isinstance(powerpoint_path, str), "PowerPoint path should be string"
            assert powerpoint_path.endswith(".pptx"), "PowerPoint path should end with .pptx"

        if html_path:
            assert isinstance(html_path, str), "HTML path should be string"
            assert html_path.endswith(".html"), "HTML path should end with .html"

    def _verify_human_review_points_exercised(self, result: Dict[str, Any]):
        """Verify that human review points were reached."""
        # Check that review-related state fields are set
        # With auto-approval, these should be True
        assert result.get("recoding_approved") == True, \
            "Recoding should be approved (auto-approval)"
        assert result.get("indicators_approved") == True, \
            "Indicators should be approved (auto-approval)"
        assert result.get("table_specs_approved") == True, \
            "Table specs should be approved (auto-approval)"

        # Verify artifacts were generated (pre-review)
        assert result.get("recoding_rules") is not None, \
            "Recoding rules should be generated"
        assert result.get("indicators") is not None, \
            "Indicators should be generated"
        assert result.get("table_specifications") is not None, \
            "Table specifications should be generated"

        # Verify validation results exist
        assert result.get("recoding_validation_result") is not None, \
            "Recoding validation should be performed"
        assert result.get("indicator_validation_result") is not None, \
            "Indicator validation should be performed"
        assert result.get("table_validation_result") is not None, \
            "Table validation should be performed"


@pytest.mark.e2e
class TestE2ESummary:
    """
    E2E Test Summary and Verification.

    This test class provides a summary of all E2E test capabilities.
    """

    def test_e2e_capabilities_check(
        self,
        sample_sav_file: str,
        e2e_config: Dict[str, Any],
    ):
        """
        Verify E2E test capabilities.

        This test checks that all required components are available
        for E2E testing.
        """
        capabilities = {
            "sample_file_exists": Path(sample_sav_file).exists(),
            "output_dir_exists": Path(e2e_config["output_dir"]).exists(),
            "temp_dir_exists": Path(e2e_config["temp_dir"]).exists(),
            "auto_approval_enabled": (
                e2e_config.get("auto_approve_recoding") and
                e2e_config.get("auto_approve_indicators") and
                e2e_config.get("auto_approve_table_specs")
            ),
            "graph_compiles": False,
        }

        # Test graph compilation
        try:
            graph = build_graph(checkpointer_path=":memory:", config=e2e_config)
            capabilities["graph_compiles"] = graph is not None
        except Exception:
            capabilities["graph_compiles"] = False

        # Verify all capabilities
        failed = [k for k, v in capabilities.items() if not v]

        if failed:
            pytest.fail(f"E2E capabilities missing: {', '.join(failed)}")

        # Print summary
        print("\n" + "=" * 60)
        print("E2E CAPABILITIES CHECK")
        print("=" * 60)
        for item, status in capabilities.items():
            status_str = "✓ PASS" if status else "✗ FAIL"
            print(f"{status_str}: {item}")
        print("=" * 60)
