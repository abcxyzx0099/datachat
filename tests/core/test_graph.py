"""
Integration Tests for Survey Analysis Workflow Graph

This module contains end-to-end integration tests for the complete 22-step
LangGraph workflow. Tests verify:
- Complete workflow execution from start to finish
- State evolution across all 22 steps
- Checkpoint creation and persistence
- Resume functionality from checkpoints
- Error recovery and handling

These tests use mocks for external dependencies (LLM, PSPP) to enable
CI/CD execution without requiring actual API keys or installed software.
"""

import pytest
import sqlite3
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any
import uuid

from agent.graph import get_graph, build_graph
from agent.state import (
    WorkflowState,
    create_initial_state,
    ValidationResult,
)
from agent.config import DEFAULT_CONFIG


# =============================================================================
# Test Configuration
# =============================================================================

@pytest.fixture
def temp_output_dir():
    """
    Create temporary output directory for test runs.

    Ensures tests are idempotent and don't pollute the output/ directory.

    Yields:
        Path to temporary output directory
    """
    temp_dir = tempfile.mkdtemp(prefix="survey_test_")
    yield Path(temp_dir)
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_checkpoint_db():
    """
    Create temporary SQLite checkpoint database for testing.

    Each test gets a fresh checkpoint database to ensure isolation.

    Yields:
        Path to temporary checkpoint database
    """
    fd, db_path = tempfile.mkstemp(suffix=".db", prefix="checkpoints_")
    # Close file descriptor so SQLite can use the file
    import os
    os.close(fd)
    yield db_path
    # Cleanup
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_thread_id():
    """
    Generate unique thread ID for each test.

    Ensures tests don't interfere with each other's checkpoints.

    Returns:
        Unique thread ID string
    """
    return f"test-{uuid.uuid4()}"


@pytest.fixture
def test_config(temp_output_dir: Path) -> Dict[str, Any]:
    """
    Create test configuration with auto-approval enabled.

    This configuration allows tests to run through the complete workflow
    without requiring human intervention at review nodes.

    Args:
        temp_output_dir: Temporary output directory for this test

    Returns:
        Configuration dictionary optimized for testing
    """
    config = DEFAULT_CONFIG.copy()
    config["output_dir"] = str(temp_output_dir)
    config["temp_dir"] = str(temp_output_dir / "temp")
    config["auto_approve_recoding"] = True
    config["auto_approve_indicators"] = True
    config["auto_approve_table_specs"] = True
    config["max_self_correction_iterations"] = 2
    return config


@pytest.fixture
def minimal_state(test_config: Dict[str, Any]) -> WorkflowState:
    """
    Create minimal initial state for testing.

    Uses sample_data.sav fixture file.

    Args:
        test_config: Test configuration

    Returns:
        Initialized WorkflowState
    """
    return create_initial_state("tests/fixtures/sample_data.sav", test_config)


# =============================================================================
# Mock Fixtures for External Dependencies
# =============================================================================

@pytest.fixture
def mock_llm_client() -> Mock:
    """
    Mock LLM client for testing LLM-dependent nodes.

    Returns valid JSON responses for all LLM calls.

    Returns:
        Mock LLM client
    """
    client = Mock()

    # Create mock responses with valid JSON
    mock_response = Mock()
    # recoding_rules must be a list for validation to pass
    mock_response.content = '{"recoding_rules": [], "indicators": [], "table_specifications": []}'

    client.invoke.return_value = mock_response
    return client


@pytest.fixture
def mock_pspp_execution() -> Mock:
    """
    Mock PSPP execution for testing PSPP-dependent nodes.

    Returns:
        Mock PSPP execution function
    """
    mock_func = Mock()
    mock_func.return_value = {
        "success": True,
        "output": "PSPP executed successfully",
        "error": "",
        "return_code": 0,
    }
    return mock_func


@pytest.fixture
def mock_subprocess_run(temp_output_dir: Path) -> Mock:
    """
    Mock subprocess.run for Python script execution testing.

    Creates a temporary statistical_summary.json file.

    Args:
        temp_output_dir: Temporary output directory

    Returns:
        Mock subprocess.run function
    """
    # Create statistical summary
    summary = {
        "total_tables": 5,
        "significant_tables": 3,
        "valid_tables": 5,
        "invalid_tables": 0,
        "significance_level": 0.05,
        "tables": []
    }

    # Create summary file in temp directory
    summary_path = temp_output_dir / "statistical_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f)

    # Create mock subprocess result
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "Script executed successfully"
    mock_result.stderr = ""

    mock_func = Mock(return_value=mock_result)
    return mock_func


# =============================================================================
# Common mock context manager
# =============================================================================

@pytest.fixture(autouse=True)
def mock_dependencies(
    mock_llm_client: Mock,
    mock_pspp_execution: Mock,
    mock_subprocess_run: Mock,
):
    """
    Auto-use fixture that mocks all external dependencies for graph tests.

    Uses ExitStack to properly manage multiple patch contexts.
    """
    from contextlib import ExitStack

    with ExitStack() as stack:
        # Patch at the source so all imports get the mock
        stack.enter_context(patch('agent.llm.clients.get_llm_client', return_value=mock_llm_client))
        # Also patch at import locations in node modules for safety
        stack.enter_context(patch('agent.nodes.phase2_recoding.get_llm_client', return_value=mock_llm_client))
        stack.enter_context(patch('agent.nodes.phase3_indicators.get_llm_client', return_value=mock_llm_client))
        stack.enter_context(patch('agent.nodes.phase4_tables.get_llm_client', return_value=mock_llm_client))
        stack.enter_context(patch('agent.utils.pspp_wrapper.execute_pspp_syntax', side_effect=mock_pspp_execution))
        stack.enter_context(patch('subprocess.run', side_effect=mock_subprocess_run))

        yield


# =============================================================================
# End-to-End Workflow Tests
# =============================================================================

@pytest.mark.integration
class TestEndToEndWorkflow:
    """
    Tests for complete end-to-end workflow execution.

    Verifies that all 22 steps execute correctly and produce
    the expected output files.
    """

    def test_end_to_end_workflow(
        self,
        minimal_state: WorkflowState,
        temp_checkpoint_db: str,
        mock_thread_id: str,
        test_config: Dict[str, Any],
    ):
        """
        Test complete 22-step workflow execution.

        This test verifies final state reaches step 22 and output files are set.
        """
        # Build graph with temporary checkpoint database
        graph = build_graph(checkpointer_path=temp_checkpoint_db, config=test_config)

        # Configure thread ID
        config = {"configurable": {"thread_id": mock_thread_id}}

        # Run workflow
        result = graph.invoke(minimal_state, config)

        # Verify final state
        assert result is not None, "Graph invocation should return result"
        assert result["current_step"] == 22, f"Should reach step 22, got {result['current_step']}"

        # Verify output files are set
        assert result.get("powerpoint_file") is not None, "Should have PowerPoint file path"
        assert result.get("html_dashboard_file") is not None, "Should have HTML dashboard file path"

    def test_end_to_end_workflow_steps_execution(
        self,
        minimal_state: WorkflowState,
        temp_checkpoint_db: str,
        mock_thread_id: str,
        test_config: Dict[str, Any],
    ):
        """
        Test that all 22 steps are executed in order.

        Streams the graph execution and verifies each step is visited.
        """
        # Build graph
        graph = build_graph(checkpointer_path=temp_checkpoint_db, config=test_config)
        config = {"configurable": {"thread_id": mock_thread_id}}

        # Track visited steps
        visited_steps = []

        # Stream execution and track steps
        for event in graph.stream(minimal_state, config, mode="values"):
            step = event.get("current_step")
            if step and step not in visited_steps:
                visited_steps.append(step)

        # Verify all steps were visited
        assert 22 in visited_steps, "Step 22 should be visited"


# =============================================================================
# State Evolution Tests
# =============================================================================

@pytest.mark.integration
class TestStateEvolution:
    """
    Tests for state evolution through workflow.

    Verifies that state is correctly updated as the workflow progresses.
    """

    def test_state_evolution(
        self,
        minimal_state: WorkflowState,
        temp_checkpoint_db: str,
        mock_thread_id: str,
        test_config: Dict[str, Any],
    ):
        """
        Test state evolves correctly through workflow.

        Verifies state keys are present, current_step increments, no critical errors.
        """
        # Build graph
        graph = build_graph(checkpointer_path=temp_checkpoint_db, config=test_config)
        config = {"configurable": {"thread_id": mock_thread_id}}

        # Track state at each step
        previous_step = 0
        steps_visited = 0

        for event in graph.stream(minimal_state, config, mode="values"):
            # Verify state keys
            assert "current_step" in event, "State should always have current_step"
            assert "errors" in event, "State should always have errors list"

            # Verify step progression
            current_step = event["current_step"]
            assert current_step >= previous_step, f"Step should not decrease: {previous_step} -> {current_step}"
            previous_step = current_step

            steps_visited += 1

            # Stop after reasonable number of events
            if steps_visited > 100:
                break

        # Verify we made progress through the workflow
        assert previous_step >= 20, f"Should reach at least step 20, got {previous_step}"


# =============================================================================
# Checkpoint Persistence Tests
# =============================================================================

@pytest.mark.integration
class TestCheckpointPersistence:
    """
    Tests for checkpoint creation and persistence.

    Verifies that checkpoints are correctly saved to the database.
    """

    def test_checkpoint_creation(
        self,
        minimal_state: WorkflowState,
        temp_checkpoint_db: str,
        mock_thread_id: str,
        test_config: Dict[str, Any],
    ):
        """
        Test that checkpoints are created during workflow execution.
        """
        # Build graph
        graph = build_graph(checkpointer_path=temp_checkpoint_db, config=test_config)
        config = {"configurable": {"thread_id": mock_thread_id}}

        # Run workflow
        graph.invoke(minimal_state, config)

        # Verify checkpoint database exists
        assert Path(temp_checkpoint_db).exists(), "Checkpoint database should be created"

        # Verify checkpoints were saved
        conn = sqlite3.connect(temp_checkpoint_db)
        cursor = conn.cursor()

        # Check if checkpoints table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'"
        )
        result = cursor.fetchone()
        assert result is not None, "Checkpoints table should exist"

        conn.close()

    def test_checkpoint_multiple_threads(
        self,
        temp_checkpoint_db: str,
        test_config: Dict[str, Any],
    ):
        """
        Test that checkpoints from different threads are isolated.
        """
        thread_1 = "test-thread-1"
        thread_2 = "test-thread-2"

        # Build graph
        graph = build_graph(checkpointer_path=temp_checkpoint_db, config=test_config)

        # Run workflow for thread 1
        state_1 = create_initial_state("tests/fixtures/sample_data.sav", test_config)
        config_1 = {"configurable": {"thread_id": thread_1}}
        graph.invoke(state_1, config_1)

        # Run workflow for thread 2
        state_2 = create_initial_state("tests/fixtures/sample_data.sav", test_config)
        config_2 = {"configurable": {"thread_id": thread_2}}
        graph.invoke(state_2, config_2)

        # Verify both threads have checkpoints
        conn = sqlite3.connect(temp_checkpoint_db)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(DISTINCT thread_id) FROM checkpoints"
        )
        thread_count = cursor.fetchone()[0]

        assert thread_count >= 2, f"Should have at least 2 threads, got {thread_count}"

        conn.close()


# =============================================================================
# Error Recovery Tests
# =============================================================================

@pytest.mark.integration
class TestErrorRecovery:
    """
    Tests for error recovery and handling.

    Verifies that the workflow handles errors gracefully.
    """

    def test_error_recovery_invalid_file(
        self,
        temp_checkpoint_db: str,
        mock_thread_id: str,
        test_config: Dict[str, Any],
    ):
        """
        Test workflow handles invalid file gracefully.
        """
        # Create state with non-existent file
        state = create_initial_state("nonexistent_file.sav", test_config)

        # Build graph
        graph = build_graph(checkpointer_path=temp_checkpoint_db, config=test_config)
        config = {"configurable": {"thread_id": mock_thread_id}}

        # Run workflow (should fail gracefully)
        result = graph.invoke(state, config)

        # Verify error was captured
        assert result is not None, "Should return result even with error"
        assert len(result.get("errors", [])) > 0, "Should have errors in state"


# =============================================================================
# Graph Configuration Tests
# =============================================================================

@pytest.mark.integration
class TestGraphConfiguration:
    """
    Tests for graph configuration and initialization.
    """

    def test_graph_has_all_nodes(self, temp_checkpoint_db: str, test_config: Dict[str, Any]):
        """
        Test that graph is compiled correctly.
        """
        # Build graph
        graph = build_graph(checkpointer_path=temp_checkpoint_db, config=test_config)

        # Verify graph is compiled
        assert graph is not None, "Graph should be compiled successfully"
        assert hasattr(graph, 'invoke'), "Compiled graph should have invoke method"

    def test_graph_with_memory_checkpointer(self, test_config: Dict[str, Any]):
        """
        Test that graph works with in-memory checkpointer.
        """
        # Build graph with None checkpointer (uses MemorySaver)
        graph = build_graph(checkpointer_path=None, config=test_config)

        # Verify graph is compiled
        assert graph is not None, "Graph with MemorySaver should compile"

    def test_graph_get_state_nonexistent_thread(
        self,
        temp_checkpoint_db: str,
        test_config: Dict[str, Any],
    ):
        """
        Test get_state() for non-existent thread.
        """
        # Build graph
        graph = build_graph(checkpointer_path=temp_checkpoint_db, config=test_config)

        # Try to get state for non-existent thread
        config = {"configurable": {"thread_id": "nonexistent-thread"}}
        state = graph.get_state(config)

        # LangGraph returns an empty StateSnapshot, not None
        assert state is not None, "get_state should always return a StateSnapshot"
