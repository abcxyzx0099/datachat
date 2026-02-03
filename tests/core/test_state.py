"""
Unit Tests for State Definitions (TypedDict Validation)

This module tests all TypedDict state classes and state utility functions.
Tests validate:
- State structure has all required fields
- State initialization with default values
- State utility functions (state_to_dict, get_state_summary)
- State evolution across all 22 workflow steps
- State transition tests at key points
- State immutability (no in-place modifications)
- TypedDict field validation and access patterns
- Type consistency across workflow

State Classes Tested:
- InputState
- ExtractionState
- RecodingState
- IndicatorState
- CrossTableState
- StatisticalAnalysisState
- FilteringState
- PresentationState
- ApprovalState
- TrackingState
- WorkflowState (combined state)
"""

import pytest
import copy
from typing import Dict, Any
import pandas as pd

from agent.state import (
    # Validation result
    ValidationResult,

    # Sub-states
    InputState,
    ExtractionState,
    RecodingState,
    IndicatorState,
    CrossTableState,
    StatisticalAnalysisState,
    FilteringState,
    PresentationState,
    ApprovalState,
    TrackingState,
    WorkflowState,

    # Utilities
    create_initial_state,
    state_to_dict,
    get_state_summary,
)

from agent.config import DEFAULT_CONFIG


# =============================================================================
# ValidationResult Tests
# =============================================================================

class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_creation_valid(self):
        """Test creating a valid ValidationResult."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Minor warning"],
            checks_performed=["check1", "check2"],
        )

        assert result['is_valid'] is True
        assert result['errors'] == []
        assert result['warnings'] == ["Minor warning"]
        assert result['checks_performed'] == ["check1", "check2"]

    def test_validation_result_creation_invalid(self):
        """Test creating an invalid ValidationResult."""
        result = ValidationResult(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
            checks_performed=["check1"],
        )

        assert result['is_valid'] is False
        assert result['errors'] == ["Error 1", "Error 2"]
        assert result['warnings'] == ["Warning 1"]
        assert result['checks_performed'] == ["check1"]

    def test_validation_result_empty_lists(self):
        """Test ValidationResult with empty lists."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            checks_performed=[],
        )

        assert result['is_valid'] is True
        assert result['errors'] == []
        assert result['warnings'] == []
        assert result['checks_performed'] == []


# =============================================================================
# InputState Tests
# =============================================================================

class TestInputState:
    """Tests for InputState TypedDict."""

    def test_input_state_creation(self):
        """Test creating InputState with required fields."""
        state: InputState = {
            "input_file_path": "test.sav",
            "original_metadata": None,
        }

        assert state["input_file_path"] == "test.sav"
        assert state["original_metadata"] is None

    def test_input_state_with_metadata(self):
        """Test InputState with populated metadata."""
        metadata = {"file_name": "test.sav", "n_rows": 100}
        state: InputState = {
            "input_file_path": "test.sav",
            "original_metadata": metadata,
        }

        assert state["original_metadata"] == metadata
        assert state["original_metadata"]["file_name"] == "test.sav"


# =============================================================================
# ExtractionState Tests
# =============================================================================

class TestExtractionState:
    """Tests for ExtractionState TypedDict."""

    def test_extraction_state_defaults(self):
        """Test ExtractionState with all None values."""
        state: ExtractionState = {
            "raw_data": None,
            "variable_centered_metadata": None,
            "filtered_metadata": None,
            "filtered_out_variables": None,
        }

        assert state["raw_data"] is None
        assert state["variable_centered_metadata"] is None
        assert state["filtered_metadata"] is None
        assert state["filtered_out_variables"] is None

    def test_extraction_state_partial_population(self):
        """Test ExtractionState with partial population."""
        import pandas as pd

        df = pd.DataFrame({"col1": [1, 2, 3]})
        state: ExtractionState = {
            "raw_data": df,
            "variable_centered_metadata": None,
            "filtered_metadata": None,
            "filtered_out_variables": None,
        }

        assert state["raw_data"] is not None
        assert len(state["raw_data"]) == 3


# =============================================================================
# RecodingState Tests
# =============================================================================

class TestRecodingState:
    """Tests for RecodingState TypedDict."""

    def test_recoding_state_defaults(self):
        """Test RecodingState with default values."""
        state: RecodingState = {
            "recoding_rules": None,
            "recoding_validation_result": None,
            "recoding_approved": False,
            "recoding_feedback": None,
            "new_metadata": None,
            "new_data_file": None,
        }

        assert state["recoding_rules"] is None
        assert state["recoding_validation_result"] is None
        assert state["recoding_approved"] is False
        assert state["recoding_feedback"] is None

    def test_recoding_state_with_rules(self):
        """Test RecodingState with recoding rules populated."""
        rules = {"var1": {"recodings": []}}

        state: RecodingState = {
            "recoding_rules": rules,
            "recoding_validation_result": None,
            "recoding_approved": False,
            "recoding_feedback": None,
            "new_metadata": None,
            "new_data_file": None,
        }

        assert state["recoding_rules"] == rules
        assert state["recoding_rules"]["var1"]["recodings"] == []

    def test_recoding_state_approval(self):
        """Test RecodingState approval fields."""
        state: RecodingState = {
            "recoding_rules": None,
            "recoding_validation_result": None,
            "recoding_approved": True,
            "recoding_feedback": "Approved with changes",
            "new_metadata": None,
            "new_data_file": None,
        }

        assert state["recoding_approved"] is True
        assert state["recoding_feedback"] == "Approved with changes"

    def test_recoding_state_with_validation_result(self):
        """Test RecodingState with ValidationResult."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            checks_performed=["check1"],
        )

        state: RecodingState = {
            "recoding_rules": {},
            "recoding_validation_result": result,
            "recoding_approved": False,
            "recoding_feedback": None,
            "new_metadata": None,
            "new_data_file": None,
        }

        assert state["recoding_validation_result"]['is_valid'] is True
        assert state["recoding_validation_result"]['errors'] == []


# =============================================================================
# IndicatorState Tests
# =============================================================================

class TestIndicatorState:
    """Tests for IndicatorState TypedDict."""

    def test_indicator_state_defaults(self):
        """Test IndicatorState with default values."""
        state: IndicatorState = {
            "indicators": None,
            "indicator_validation_result": None,
            "indicators_approved": False,
            "indicator_feedback": None,
        }

        assert state["indicators"] is None
        assert state["indicator_validation_result"] is None
        assert state["indicators_approved"] is False
        assert state["indicator_feedback"] is None

    def test_indicator_state_approved(self):
        """Test IndicatorState with approved indicators."""
        state: IndicatorState = {
            "indicators": {"indicator1": {"variables": ["var1", "var2"]}},
            "indicator_validation_result": None,
            "indicators_approved": True,
            "indicator_feedback": None,
        }

        assert state["indicators_approved"] is True
        assert state["indicators"] is not None
        assert "indicator1" in state["indicators"]


# =============================================================================
# CrossTableState Tests
# =============================================================================

class TestCrossTableState:
    """Tests for CrossTableState TypedDict."""

    def test_crosstable_state_defaults(self):
        """Test CrossTableState with default values."""
        state: CrossTableState = {
            "table_specifications": None,
            "table_validation_result": None,
            "table_specs_approved": False,
            "table_specs_feedback": None,
            "table_syntax_file": None,
            "cross_table_file": None,
        }

        assert state["table_specifications"] is None
        assert state["table_specs_approved"] is False

    def test_crosstable_state_with_files(self):
        """Test CrossTableState with file paths."""
        state: CrossTableState = {
            "table_specifications": {},
            "table_validation_result": None,
            "table_specs_approved": True,
            "table_specs_feedback": None,
            "table_syntax_file": "/tmp/tables.sps",
            "cross_table_file": "/tmp/crosstabs.txt",
        }

        assert state["table_syntax_file"] == "/tmp/tables.sps"
        assert state["cross_table_file"] == "/tmp/crosstabs.txt"


# =============================================================================
# StatisticalAnalysisState Tests
# =============================================================================

class TestStatisticalAnalysisState:
    """Tests for StatisticalAnalysisState TypedDict."""

    def test_statistical_analysis_state_defaults(self):
        """Test StatisticalAnalysisState with default values."""
        state: StatisticalAnalysisState = {
            "statistics_script": None,
            "statistical_summary": None,
        }

        assert state["statistics_script"] is None
        assert state["statistical_summary"] is None

    def test_statistical_analysis_state_populated(self):
        """Test StatisticalAnalysisState with populated fields."""
        summary = {
            "total_tests": 10,
            "significant_tests": 5,
            "results": [],
        }

        state: StatisticalAnalysisState = {
            "statistics_script": "/tmp/stats_script.py",
            "statistical_summary": summary,
        }

        assert state["statistics_script"] == "/tmp/stats_script.py"
        assert state["statistical_summary"]["total_tests"] == 10


# =============================================================================
# FilteringState Tests
# =============================================================================

class TestFilteringState:
    """Tests for FilteringState TypedDict."""

    def test_filtering_state_defaults(self):
        """Test FilteringState with default values."""
        state: FilteringState = {
            "filter_list": None,
            "filtered_tables": None,
            "total_tables_evaluated": 0,
            "significant_tables_count": 0,
            "filtering_valid": False,
        }

        assert state["filter_list"] is None
        assert state["total_tables_evaluated"] == 0
        assert state["significant_tables_count"] == 0
        assert state["filtering_valid"] is False

    def test_filtering_state_populated(self):
        """Test FilteringState with populated fields."""
        state: FilteringState = {
            "filter_list": {},
            "filtered_tables": {},
            "total_tables_evaluated": 100,
            "significant_tables_count": 25,
            "filtering_valid": True,
        }

        assert state["total_tables_evaluated"] == 100
        assert state["significant_tables_count"] == 25
        assert state["filtering_valid"] is True


# =============================================================================
# PresentationState Tests
# =============================================================================

class TestPresentationState:
    """Tests for PresentationState TypedDict."""

    def test_presentation_state_defaults(self):
        """Test PresentationState with default values."""
        state: PresentationState = {
            "powerpoint_file": None,
            "html_dashboard_file": None,
        }

        assert state["powerpoint_file"] is None
        assert state["html_dashboard_file"] is None

    def test_presentation_state_with_files(self):
        """Test PresentationState with output file paths."""
        state: PresentationState = {
            "powerpoint_file": "/output/presentation.pptx",
            "html_dashboard_file": "/output/dashboard.html",
        }

        assert state["powerpoint_file"] == "/output/presentation.pptx"
        assert state["html_dashboard_file"] == "/output/dashboard.html"


# =============================================================================
# ApprovalState Tests
# =============================================================================

class TestApprovalState:
    """Tests for ApprovalState TypedDict."""

    def test_approval_state_defaults(self):
        """Test ApprovalState with default values."""
        state: ApprovalState = {
            "current_step": 0,
            "requires_human_review": False,
            "iteration_count": 0,
        }

        assert state["current_step"] == 0
        assert state["requires_human_review"] is False
        assert state["iteration_count"] == 0

    def test_approval_state_iteration(self):
        """Test ApprovalState with iteration count."""
        state: ApprovalState = {
            "current_step": 5,
            "requires_human_review": True,
            "iteration_count": 2,
        }

        assert state["current_step"] == 5
        assert state["requires_human_review"] is True
        assert state["iteration_count"] == 2


# =============================================================================
# TrackingState Tests
# =============================================================================

class TestTrackingState:
    """Tests for TrackingState TypedDict."""

    def test_tracking_state_defaults(self):
        """Test TrackingState with default values."""
        state: TrackingState = {
            "errors": [],
            "warnings": [],
        }

        assert state["errors"] == []
        assert state["warnings"] == []

    def test_tracking_state_with_messages(self):
        """Test TrackingState with error and warning messages."""
        state: TrackingState = {
            "errors": ["Error 1", "Error 2"],
            "warnings": ["Warning 1"],
        }

        assert len(state["errors"]) == 2
        assert len(state["warnings"]) == 1
        assert state["errors"][0] == "Error 1"


# =============================================================================
# WorkflowState Tests (Combined State)
# =============================================================================

class TestWorkflowState:
    """Tests for WorkflowState combined TypedDict."""

    def test_workflow_state_structure(self):
        """Test WorkflowState has all required sub-state fields."""
        state = WorkflowState()

        # Check all expected fields are present
        expected_fields = [
            # InputState
            "input_file_path",
            "original_metadata",
            # ExtractionState
            "raw_data",
            "variable_centered_metadata",
            "filtered_metadata",
            "filtered_out_variables",
            # RecodingState
            "recoding_rules",
            "recoding_validation_result",
            "recoding_approved",
            "recoding_feedback",
            "new_metadata",
            "new_data_file",
            # IndicatorState
            "indicators",
            "indicator_validation_result",
            "indicators_approved",
            "indicator_feedback",
            # CrossTableState
            "table_specifications",
            "table_validation_result",
            "table_specs_approved",
            "table_specs_feedback",
            "table_syntax_file",
            "cross_table_file",
            # StatisticalAnalysisState
            "statistics_script",
            "statistical_summary",
            # FilteringState
            "filter_list",
            "filtered_tables",
            "total_tables_evaluated",
            "significant_tables_count",
            "filtering_valid",
            # PresentationState
            "powerpoint_file",
            "html_dashboard_file",
            # ApprovalState
            "current_step",
            "requires_human_review",
            "iteration_count",
            # TrackingState
            "errors",
            "warnings",
        ]

        for field in expected_fields:
            # Since total=False, we can check if the field can be set
            state[field] = None  # type: ignore

    def test_workflow_state_combines_sub_states(self):
        """Test that WorkflowState combines all sub-states."""
        state: WorkflowState = {
            # InputState
            "input_file_path": "test.sav",
            "original_metadata": None,
            # ExtractionState
            "raw_data": None,
            "variable_centered_metadata": None,
            "filtered_metadata": None,
            "filtered_out_variables": None,
            # RecodingState
            "recoding_rules": None,
            "recoding_validation_result": None,
            "recoding_approved": False,
            "recoding_feedback": None,
            "new_metadata": None,
            "new_data_file": None,
            # IndicatorState
            "indicators": None,
            "indicator_validation_result": None,
            "indicators_approved": False,
            "indicator_feedback": None,
            # CrossTableState
            "table_specifications": None,
            "table_validation_result": None,
            "table_specs_approved": False,
            "table_specs_feedback": None,
            "table_syntax_file": None,
            "cross_table_file": None,
            # StatisticalAnalysisState
            "statistics_script": None,
            "statistical_summary": None,
            # FilteringState
            "filter_list": None,
            "filtered_tables": None,
            "total_tables_evaluated": 0,
            "significant_tables_count": 0,
            "filtering_valid": False,
            # PresentationState
            "powerpoint_file": None,
            "html_dashboard_file": None,
            # ApprovalState
            "current_step": 0,
            "requires_human_review": False,
            "iteration_count": 0,
            # TrackingState
            "errors": [],
            "warnings": [],
        }

        # Verify all fields are accessible
        assert state["input_file_path"] == "test.sav"
        assert state["current_step"] == 0
        assert state["errors"] == []


# =============================================================================
# State Utility Function Tests
# =============================================================================

class TestCreateInitialState:
    """Tests for create_initial_state function."""

    def test_create_initial_state_basic(self):
        """Test creating initial state with file path."""
        state = create_initial_state("test.sav")

        assert state["input_file_path"] == "test.sav"
        assert state["current_step"] == 0
        assert state["iteration_count"] == 0
        assert state["errors"] == []
        assert state["warnings"] == []

    def test_create_initial_state_all_none(self):
        """Test that all optional fields are None or default."""
        state = create_initial_state("test.sav")

        # Check None fields
        assert state["original_metadata"] is None
        assert state["raw_data"] is None
        assert state["variable_centered_metadata"] is None
        assert state["recoding_rules"] is None

        # Check default bools
        assert state["recoding_approved"] is False
        assert state["indicators_approved"] is False
        assert state["table_specs_approved"] is False

        # Check default ints
        assert state["total_tables_evaluated"] == 0
        assert state["significant_tables_count"] == 0

    def test_create_initial_state_with_config(self):
        """Test creating initial state with custom config."""
        custom_config = DEFAULT_CONFIG.copy()
        custom_config["max_self_correction_iterations"] = 5

        state = create_initial_state("test.sav", custom_config)

        assert state["input_file_path"] == "test.sav"


class TestStateToDict:
    """Tests for state_to_dict function."""

    def test_state_to_dict_basic(self):
        """Test converting WorkflowState to dict."""
        state: WorkflowState = {
            "input_file_path": "test.sav",
            "current_step": 1,
            "errors": [],
            "warnings": [],
        }

        result = state_to_dict(state)

        assert isinstance(result, dict)
        assert result["input_file_path"] == "test.sav"
        assert result["current_step"] == 1

    def test_state_to_dict_with_validation_result(self):
        """Test that ValidationResult is converted to dict."""
        validation_result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Warning 1"],
            checks_performed=["check1"],
        )

        state: WorkflowState = {
            "input_file_path": "test.sav",
            "recoding_validation_result": validation_result,
            "current_step": 0,
            "errors": [],
            "warnings": [],
        }

        result = state_to_dict(state)

        assert result["recoding_validation_result"]["is_valid"] is True
        assert result["recoding_validation_result"]["warnings"] == ["Warning 1"]
        assert isinstance(result["recoding_validation_result"], dict)


class TestGetStateSummary:
    """Tests for get_state_summary function."""

    def test_get_state_summary_basic(self):
        """Test getting state summary."""
        state: WorkflowState = {
            "input_file_path": "test.sav",
            "current_step": 5,
            "requires_human_review": True,
            "iteration_count": 2,
            "errors": ["Error 1"],
            "warnings": ["Warning 1"],
            "recoding_approved": False,
            "indicators_approved": False,
            "table_specs_approved": True,
            "new_data_file": "/tmp/new.sav",
        }

        summary = get_state_summary(state)

        assert summary["current_step"] == 5
        assert summary["requires_human_review"] is True
        assert summary["iteration_count"] == 2
        assert summary["errors_count"] == 1
        assert summary["warnings_count"] == 1
        assert summary["recoding_approved"] is False
        assert summary["table_specs_approved"] is True
        assert summary["has_output_files"] is True

    def test_get_state_summary_no_errors(self):
        """Test state summary with no errors."""
        state: WorkflowState = {
            "input_file_path": "test.sav",
            "current_step": 0,
            "requires_human_review": False,
            "iteration_count": 0,
            "errors": [],
            "warnings": [],
        }

        summary = get_state_summary(state)

        assert summary["errors_count"] == 0
        assert summary["warnings_count"] == 0
        assert summary["has_output_files"] is False


# =============================================================================
# TypedDict Field Definition Tests
# =============================================================================

class TestInputStateFieldDefinitions:
    """Tests for InputState TypedDict field definitions."""

    def test_input_state_has_correct_fields(self):
        """Test InputState has all expected field definitions."""
        from typing import get_origin, get_args

        # Get annotations from InputState
        annotations = InputState.__annotations__

        expected_fields = ["input_file_path", "original_metadata"]

        assert set(annotations.keys()) == set(expected_fields)

        # Check input_file_path is str
        assert annotations["input_file_path"] == str

        # Check original_metadata is Optional[Dict[str, Any]]
        # In Python 3.10+, Optional[X] is X | None
        original_metadata_type = annotations["original_metadata"]
        assert original_metadata_type is not None

    def test_input_state_total_false(self):
        """Test InputState has total=False (optional fields)."""
        assert InputState.__total__ is False


class TestExtractionStateFieldDefinitions:
    """Tests for ExtractionState TypedDict field definitions."""

    def test_extraction_state_has_correct_fields(self):
        """Test ExtractionState has all expected field definitions."""
        annotations = ExtractionState.__annotations__

        expected_fields = [
            "raw_data",
            "variable_centered_metadata",
            "filtered_metadata",
            "filtered_out_variables",
        ]

        for field in expected_fields:
            assert field in annotations

    def test_extraction_state_total_false(self):
        """Test ExtractionState has total=False."""
        assert ExtractionState.__total__ is False


class TestRecodingStateFieldDefinitions:
    """Tests for RecodingState TypedDict field definitions."""

    def test_recoding_state_has_correct_fields(self):
        """Test RecodingState has all expected field definitions."""
        annotations = RecodingState.__annotations__

        expected_fields = [
            "recoding_rules",
            "recoding_validation_result",
            "recoding_approved",
            "recoding_feedback",
            "new_metadata",
            "new_data_file",
        ]

        for field in expected_fields:
            assert field in annotations

    def test_recoding_state_boolean_field(self):
        """Test recoding_approved is a boolean field."""
        annotations = RecodingState.__annotations__
        # Check that recoding_approved is bool (not Optional)
        field_type = annotations.get("recoding_approved")
        assert field_type is bool


class TestIndicatorStateFieldDefinitions:
    """Tests for IndicatorState TypedDict field definitions."""

    def test_indicator_state_has_correct_fields(self):
        """Test IndicatorState has all expected field definitions."""
        annotations = IndicatorState.__annotations__

        expected_fields = [
            "indicators",
            "indicator_validation_result",
            "indicators_approved",
            "indicator_feedback",
        ]

        for field in expected_fields:
            assert field in annotations


class TestFilteringStateFieldDefinitions:
    """Tests for FilteringState TypedDict field definitions."""

    def test_filtering_state_numeric_fields(self):
        """Test FilteringState has integer fields with defaults."""
        annotations = FilteringState.__annotations__

        # Check integer fields
        assert "total_tables_evaluated" in annotations
        assert "significant_tables_count" in annotations
        assert "filtering_valid" in annotations


class TestWorkflowStateFieldDefinitions:
    """Tests for WorkflowState combined TypedDict field definitions."""

    def test_workflow_state_inherits_all_sub_states(self):
        """Test WorkflowState inherits from all 10 sub-states."""
        annotations = WorkflowState.__annotations__

        # Check fields from each sub-state are present
        expected_input_fields = ["input_file_path", "original_metadata"]
        expected_extraction_fields = ["raw_data", "variable_centered_metadata",
                                     "filtered_metadata", "filtered_out_variables"]
        expected_recoding_fields = ["recoding_rules", "recoding_approved",
                                   "new_data_file"]
        expected_indicator_fields = ["indicators", "indicators_approved"]
        expected_crosstable_fields = ["table_specifications", "table_specs_approved"]
        expected_stats_fields = ["statistics_script", "statistical_summary"]
        expected_filtering_fields = ["filter_list", "total_tables_evaluated"]
        expected_presentation_fields = ["powerpoint_file", "html_dashboard_file"]
        expected_approval_fields = ["current_step", "requires_human_review"]
        expected_tracking_fields = ["errors", "warnings"]

        all_expected = (expected_input_fields + expected_extraction_fields +
                       expected_recoding_fields + expected_indicator_fields +
                       expected_crosstable_fields + expected_stats_fields +
                       expected_filtering_fields + expected_presentation_fields +
                       expected_approval_fields + expected_tracking_fields)

        for field in all_expected:
            assert field in annotations, f"Field {field} not in WorkflowState"

    def test_workflow_state_total_false(self):
        """Test WorkflowState has total=False for optional fields."""
        assert WorkflowState.__total__ is False


# =============================================================================
# State Evolution Tests
# =============================================================================

class TestStateEvolution:
    """Tests for state evolution across the 22-step workflow."""

    def test_state_evolution_step_0_to_1(self):
        """Test state evolution from Step 0 (initial) to Step 1 (extraction)."""
        # Step 0: Initial state
        state = create_initial_state("test.sav")
        assert state["current_step"] == 0
        assert state["raw_data"] is None
        assert state["original_metadata"] is None

        # Step 1: After extract_spss_node
        df = pd.DataFrame({"col1": [1, 2, 3]})
        metadata = {"file_name": "test.sav", "n_rows": 3}

        state_step_1 = {
            **state,
            "current_step": 1,
            "raw_data": df,
            "original_metadata": metadata,
        }

        assert state_step_1["current_step"] == 1
        assert state_step_1["raw_data"] is not None
        assert state_step_1["original_metadata"] is not None
        # Original state unchanged
        assert state["raw_data"] is None

    def test_state_evolution_step_1_to_2(self):
        """Test state evolution from Step 1 to Step 2 (transform metadata)."""
        state = create_initial_state("test.sav")
        state["current_step"] = 1
        state["raw_data"] = pd.DataFrame({"col1": [1, 2, 3]})
        state["original_metadata"] = {"file_name": "test.sav"}

        # Step 2: Add variable_centered_metadata
        variable_centered_metadata = {
            "variables": {"col1": {"name": "col1", "label": "Column 1"}},
            "n_variables": 1
        }

        state_step_2 = {
            **state,
            "current_step": 2,
            "variable_centered_metadata": variable_centered_metadata,
        }

        assert state_step_2["current_step"] == 2
        assert state_step_2["variable_centered_metadata"] is not None
        assert "variables" in state_step_2["variable_centered_metadata"]
        # Previous fields still present
        assert state_step_2["raw_data"] is not None

    def test_state_evolution_step_2_to_3(self):
        """Test state evolution from Step 2 to Step 3 (filter metadata)."""
        state = create_initial_state("test.sav")
        state["current_step"] = 2
        state["variable_centered_metadata"] = {"variables": {}}

        # Step 3: Add filtered_metadata and filtered_out_variables
        filtered_metadata = [{"name": "var1", "label": "Variable 1"}]
        filtered_out_variables = [{"name": "var2", "reason": "Binary"}]

        state_step_3 = {
            **state,
            "current_step": 3,
            "filtered_metadata": filtered_metadata,
            "filtered_out_variables": filtered_out_variables,
        }

        assert state_step_3["current_step"] == 3
        assert state_step_3["filtered_metadata"] is not None
        assert len(state_step_3["filtered_metadata"]) == 1
        assert state_step_3["filtered_out_variables"] is not None

    def test_state_evolution_step_3_to_4_recoding(self):
        """Test state evolution from Step 3 to Step 4 (recoding rules)."""
        state = create_initial_state("test.sav")
        state["current_step"] = 3
        state["filtered_metadata"] = [{"name": "var1"}]

        # Step 4: Add recoding rules
        recoding_rules = {"var1": {"recodings": []}}

        state_step_4 = {
            **state,
            "current_step": 4,
            "recoding_rules": recoding_rules,
        }

        assert state_step_4["current_step"] == 4
        assert state_step_4["recoding_rules"] is not None
        assert "var1" in state_step_4["recoding_rules"]

    def test_state_evolution_step_4_to_5_validation(self):
        """Test state evolution from Step 4 to Step 5 (validation)."""
        state = create_initial_state("test.sav")
        state["current_step"] = 4
        state["recoding_rules"] = {"var1": {"recodings": []}}

        # Step 5: Add validation result
        validation_result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Minor warning"],
            checks_performed=["structure_check"],
        )

        state_step_5 = {
            **state,
            "current_step": 5,
            "recoding_validation_result": validation_result,
        }

        assert state_step_5["current_step"] == 5
        assert state_step_5["recoding_validation_result"] is not None
        assert state_step_5["recoding_validation_result"]['is_valid'] is True

    def test_state_evolution_step_5_to_6_approval(self):
        """Test state evolution from Step 5 to Step 6 (approval)."""
        state = create_initial_state("test.sav")
        state["current_step"] = 5
        state["recoding_validation_result"] = ValidationResult(
            is_valid=True, errors=[], warnings=[], checks_performed=[]
        )

        # Step 6: Add approval
        state_step_6 = {
            **state,
            "current_step": 6,
            "recoding_approved": True,
            "recoding_feedback": None,
        }

        assert state_step_6["current_step"] == 6
        assert state_step_6["recoding_approved"] is True

    def test_state_evolution_step_6_to_8_new_dataset(self):
        """Test state evolution from Step 6 to Step 8 (new dataset)."""
        state = create_initial_state("test.sav")
        state["current_step"] = 6
        state["recoding_approved"] = True

        # Step 8: Add new data file and metadata
        new_metadata = {"file_name": "new_data.sav", "n_rows": 100}
        state_step_8 = {
            **state,
            "current_step": 8,
            "new_data_file": "/tmp/new_data.sav",
            "new_metadata": new_metadata,
        }

        assert state_step_8["current_step"] == 8
        assert state_step_8["new_data_file"] is not None
        assert state_step_8["new_metadata"] is not None

    def test_state_evolution_step_8_to_11_indicators(self):
        """Test state evolution from Step 8 to Step 11 (indicators)."""
        state = create_initial_state("test.sav")
        state["current_step"] = 8
        state["new_metadata"] = {"variables": {}}

        # Step 9: Add indicators
        indicators = {"indicator1": {"variables": ["var1", "var2"]}}
        state_step_9 = {**state, "current_step": 9, "indicators": indicators}
        assert state_step_9["indicators"] is not None

        # Step 10: Add validation
        validation = ValidationResult(is_valid=True, errors=[], warnings=[], checks_performed=[])
        state_step_10 = {**state_step_9, "current_step": 10, "indicator_validation_result": validation}
        assert state_step_10["indicator_validation_result"] is not None

        # Step 11: Add approval
        state_step_11 = {**state_step_10, "current_step": 11, "indicators_approved": True}
        assert state_step_11["current_step"] == 11
        assert state_step_11["indicators_approved"] is True

    def test_state_evolution_step_11_to_14_tables(self):
        """Test state evolution from Step 11 to Step 14 (table specifications)."""
        state = create_initial_state("test.sav")
        state["current_step"] = 11
        state["indicators"] = {"indicator1": {"variables": ["var1"]}}

        # Step 12: Add table specifications
        table_specs = {"tables": [{"id": "table1"}]}
        state_step_12 = {**state, "current_step": 12, "table_specifications": table_specs}
        assert state_step_12["table_specifications"] is not None

        # Step 13: Add validation
        validation = ValidationResult(is_valid=True, errors=[], warnings=[], checks_performed=[])
        state_step_13 = {**state_step_12, "current_step": 13, "table_validation_result": validation}
        assert state_step_13["table_validation_result"] is not None

        # Step 14: Add approval
        state_step_14 = {**state_step_13, "current_step": 14, "table_specs_approved": True}
        assert state_step_14["current_step"] == 14
        assert state_step_14["table_specs_approved"] is True

    def test_state_evolution_step_14_to_16_crosstabs(self):
        """Test state evolution from Step 14 to Step 16 (cross-tables)."""
        state = create_initial_state("test.sav")
        state["current_step"] = 14
        state["table_specs_approved"] = True

        # Step 16: Add cross-table file
        state_step_16 = {
            **state,
            "current_step": 16,
            "table_syntax_file": "/tmp/tables.sps",
            "cross_table_file": "/tmp/crosstabs.txt",
        }

        assert state_step_16["current_step"] == 16
        assert state_step_16["table_syntax_file"] is not None
        assert state_step_16["cross_table_file"] is not None

    def test_state_evolution_step_16_to_18_statistics(self):
        """Test state evolution from Step 16 to Step 18 (statistics)."""
        state = create_initial_state("test.sav")
        state["current_step"] = 16
        state["cross_table_file"] = "/tmp/crosstabs.txt"

        # Step 17: Add statistics script
        state_step_17 = {
            **state,
            "current_step": 17,
            "statistics_script": "#!/usr/bin/env python3\n...",
        }
        assert state_step_17["statistics_script"] is not None

        # Step 18: Add statistical summary
        summary = {"total_tests": 10, "significant_tests": 5}
        state_step_18 = {
            **state_step_17,
            "current_step": 18,
            "statistical_summary": summary,
        }
        assert state_step_18["current_step"] == 18
        assert state_step_18["statistical_summary"] is not None

    def test_state_evolution_step_18_to_20_filtering(self):
        """Test state evolution from Step 18 to Step 20 (filtering)."""
        state = create_initial_state("test.sav")
        state["current_step"] = 18
        state["statistical_summary"] = {"total_tests": 10}

        # Step 19: Add filter list
        filter_list = {"table1": {"include": True}}
        state_step_19 = {**state, "current_step": 19, "filter_list": filter_list}
        assert state_step_19["filter_list"] is not None

        # Step 20: Add filtered tables and counts
        filtered_tables = {"table1": {"chi_square": 5.2, "p_value": 0.02}}
        state_step_20 = {
            **state_step_19,
            "current_step": 20,
            "filtered_tables": filtered_tables,
            "total_tables_evaluated": 10,
            "significant_tables_count": 5,
            "filtering_valid": True,
        }
        assert state_step_20["current_step"] == 20
        assert state_step_20["filtered_tables"] is not None
        assert state_step_20["total_tables_evaluated"] == 10

    def test_state_evolution_step_20_to_22_presentation(self):
        """Test state evolution from Step 20 to Step 22 (presentation)."""
        state = create_initial_state("test.sav")
        state["current_step"] = 20
        state["filtered_tables"] = {"table1": {}}

        # Step 21: Add PowerPoint file
        state_step_21 = {
            **state,
            "current_step": 21,
            "powerpoint_file": "/output/presentation.pptx",
        }
        assert state_step_21["powerpoint_file"] is not None

        # Step 22: Add HTML dashboard
        state_step_22 = {
            **state_step_21,
            "current_step": 22,
            "html_dashboard_file": "/output/dashboard.html",
        }
        assert state_step_22["current_step"] == 22
        assert state_step_22["html_dashboard_file"] is not None


# =============================================================================
# State Transition Tests
# =============================================================================

class TestStateTransitions:
    """Tests for state transitions at key points."""

    def test_transition_step_3_to_4_extraction_to_recoding(self):
        """Test critical transition from extraction (Step 3) to recoding (Step 4)."""
        # Before transition: Step 3 complete
        state_before = create_initial_state("test.sav")
        state_before["current_step"] = 3
        state_before["raw_data"] = pd.DataFrame({"col1": [1, 2, 3]})
        state_before["filtered_metadata"] = [{"name": "var1"}]

        # After transition: Step 4 starts recoding
        state_after = {
            **state_before,
            "current_step": 4,
            "recoding_rules": {"var1": {"recodings": []}},
        }

        # Verify extraction fields are preserved
        assert state_after["raw_data"] is not None
        assert state_after["filtered_metadata"] is not None
        # Verify recoding fields are added
        assert state_after["recoding_rules"] is not None

    def test_transition_step_8_new_metadata_authoritative(self):
        """Test that Step 8 makes new_metadata the authoritative source."""
        state = create_initial_state("test.sav")
        state["current_step"] = 8
        state["original_metadata"] = {"n_rows": 100, "variables": {}}
        state["new_metadata"] = {"n_rows": 100, "variables": {"var1": {}, "var2": {}}}

        # new_metadata should be complete with all variables
        assert "variables" in state["new_metadata"]
        assert len(state["new_metadata"]["variables"]) >= 2

    def test_transition_step_16_all_data_tables_complete(self):
        """Test that Step 16 means all data tables are generated."""
        state = create_initial_state("test.sav")
        state["current_step"] = 16
        state["cross_table_file"] = "/tmp/crosstabs.txt"

        # At Step 16, all data tables should be generated
        assert state["cross_table_file"] is not None
        # Statistical analysis should be ready to run
        assert state["current_step"] == 16

    def test_transition_step_18_statistical_summary_ready(self):
        """Test that Step 18 provides statistical summary for filtering."""
        state = create_initial_state("test.sav")
        state["current_step"] = 18
        state["statistical_summary"] = {
            "tables": [
                {"name": "table1", "chi_square": 5.2, "p_value": 0.02, "cramers_v": 0.3}
            ]
        }

        # Statistical summary should be available for filtering
        assert state["statistical_summary"] is not None
        assert "tables" in state["statistical_summary"]

    def test_transition_step_20_significant_tables_ready(self):
        """Test that Step 20 provides significant_tables for PowerPoint."""
        state = create_initial_state("test.sav")
        state["current_step"] = 20
        state["filtered_tables"] = {
            "tables": [
                {"name": "table1", "is_significant": True}
            ]
        }
        state["filtering_valid"] = True  # Explicitly set to True

        # Significant tables should be ready for presentation
        assert state["filtered_tables"] is not None
        assert state["filtering_valid"] is True


# =============================================================================
# State Immutability Tests
# =============================================================================

class TestStateImmutability:
    """Tests for state immutability (nodes must return new state)."""

    def test_state_immutability_basic(self):
        """Test that modifying new state doesn't affect original."""
        original = create_initial_state("test.sav")

        # Simulate node creating new state
        new_state = {
            **original,
            "current_step": 1,
            "raw_data": pd.DataFrame({"col1": [1, 2, 3]}),
        }

        # Modify new state
        new_state["current_step"] = 2

        # Original should be unchanged
        assert original["current_step"] == 0
        assert original["raw_data"] is None

    def test_state_immutability_with_dict_merge(self):
        """Test immutability when using dict merge."""
        original = create_initial_state("test.sav")
        original_id = id(original)

        # Create new state using dict unpacking
        new_state = {**original, "current_step": 5}

        # Should be different object
        assert id(new_state) != original_id

        # Modifying new state shouldn't affect original
        new_state["errors"] = ["New error"]
        assert len(original["errors"]) == 0

    def test_state_immutability_nested_structures(self):
        """Test immutability with nested structures (lists, dicts)."""
        original = create_initial_state("test.sav")
        original["errors"] = ["error1"]
        original["warnings"] = ["warning1"]

        # Create new state with modified list
        new_state = {
            **original,
            "errors": original["errors"] + ["error2"],
            "warnings": original["warnings"].copy(),
        }

        # Verify new state has both errors
        assert len(new_state["errors"]) == 2
        # Verify original unchanged
        assert len(original["errors"]) == 1

    def test_state_immutability_validation_result(self):
        """Test immutability with ValidationResult objects."""
        original = create_initial_state("test.sav")
        validation = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Warning 1"],
            checks_performed=["check1"],
        )

        new_state = {
            **original,
            "recoding_validation_result": validation,
        }

        # Modify validation in new state
        new_validation = ValidationResult(
            is_valid=False,
            errors=["Error 1"],
            warnings=["Warning 1"],
            checks_performed=["check1"],
        )
        new_state["recoding_validation_result"] = new_validation

        # Original state should not have validation
        assert original.get("recoding_validation_result") is None

    def test_state_immutability_dataframe(self):
        """Test immutability with pandas DataFrame."""
        original = create_initial_state("test.sav")
        df = pd.DataFrame({"col1": [1, 2, 3]})

        new_state = {
            **original,
            "raw_data": df,
        }

        # Modify DataFrame in new state
        new_state["raw_data"]["col1"] = [4, 5, 6]

        # Original state shouldn't have DataFrame
        assert original["raw_data"] is None


# =============================================================================
# State Field Access Tests
# =============================================================================

class TestStateFieldAccess:
    """Tests for accessing optional fields before and after they're set."""

    def test_access_optional_field_before_set(self):
        """Test accessing optional field before it's set returns None or default."""
        state = create_initial_state("test.sav")

        # Access optional fields that haven't been set
        assert state.get("recoding_rules") is None
        assert state.get("indicators") is None
        assert state.get("table_specifications") is None
        assert state.get("statistical_summary") is None

    def test_access_optional_field_after_set(self):
        """Test accessing optional field after it's set."""
        state = create_initial_state("test.sav")
        state["recoding_rules"] = {"var1": {"recodings": []}}

        # Field should now be accessible
        assert state.get("recoding_rules") is not None
        assert state["recoding_rules"]["var1"]["recodings"] == []

    def test_field_existence_check(self):
        """Test checking if field exists in state."""
        state = create_initial_state("test.sav")

        # Check field existence
        assert "input_file_path" in state
        assert "current_step" in state
        assert "errors" in state

        # Optional fields not yet set
        # Note: In TypedDict with total=False, fields might not exist
        # until explicitly set, depending on implementation

    def test_typeddict_total_false_behavior(self):
        """Test TypedDict total=False allows optional fields."""
        state = WorkflowState()

        # Can set optional fields
        state["input_file_path"] = "test.sav"
        state["current_step"] = 0

        # Can access set fields
        assert state["input_file_path"] == "test.sav"

        # Unset fields may raise KeyError when accessed directly
        # but get() returns None
        assert state.get("recoding_rules") is None

    def test_default_values_for_int_and_bool_fields(self):
        """Test that int and bool fields have correct default values."""
        state = create_initial_state("test.sav")

        # Boolean fields default to False
        assert state["recoding_approved"] is False
        assert state["indicators_approved"] is False
        assert state["table_specs_approved"] is False
        assert state["filtering_valid"] is False

        # Integer fields default to 0
        assert state["total_tables_evaluated"] == 0
        assert state["significant_tables_count"] == 0
        assert state["iteration_count"] == 0
        assert state["current_step"] == 0

    def test_list_fields_are_mutable(self):
        """Test that list fields (errors, warnings) are mutable."""
        state = create_initial_state("test.sav")

        # Lists should be empty by default
        assert state["errors"] == []
        assert state["warnings"] == []

        # Can append to lists
        state["errors"].append("Error 1")
        state["warnings"].append("Warning 1")

        assert len(state["errors"]) == 1
        assert len(state["warnings"]) == 1


# =============================================================================
# Type Consistency Tests
# =============================================================================

class TestTypeConsistency:
    """Tests for type consistency across workflow."""

    def test_field_types_never_change(self):
        """Test that field types remain consistent across workflow."""
        state = create_initial_state("test.sav")

        # input_file_path is always str
        assert isinstance(state["input_file_path"], str)
        state["input_file_path"] = "/tmp/test.sav"
        assert isinstance(state["input_file_path"], str)

        # current_step is always int
        assert isinstance(state["current_step"], int)
        state["current_step"] = 5
        assert isinstance(state["current_step"], int)

        # errors is always list
        assert isinstance(state["errors"], list)
        state["errors"] = ["error1", "error2"]
        assert isinstance(state["errors"], list)

    def test_optional_field_types(self):
        """Test that optional fields maintain correct types when set."""
        state = create_initial_state("test.sav")

        # recoding_rules is Optional[Dict]
        state["recoding_rules"] = {"var1": {}}
        assert isinstance(state["recoding_rules"], dict)

        # raw_data is Optional[pandas.DataFrame]
        df = pd.DataFrame({"col1": [1, 2, 3]})
        state["raw_data"] = df
        assert isinstance(state["raw_data"], pd.DataFrame)

        # recoding_approved is bool (not optional)
        assert isinstance(state["recoding_approved"], bool)
        state["recoding_approved"] = True
        assert isinstance(state["recoding_approved"], bool)

    def test_validation_result_type_consistency(self):
        """Test ValidationResult fields maintain type consistency."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Warning"],
            checks_performed=["check1"],
        )

        assert isinstance(result['is_valid'], bool)
        assert isinstance(result['errors'], list)
        assert isinstance(result['warnings'], list)
        assert isinstance(result['checks_performed'], list)

    def test_list_field_element_types(self):
        """Test that list field elements maintain correct types."""
        state = create_initial_state("test.sav")

        # errors list contains strings
        state["errors"] = ["error1", "error2"]
        for error in state["errors"]:
            assert isinstance(error, str)

        # warnings list contains strings
        state["warnings"] = ["warning1"]
        for warning in state["warnings"]:
            assert isinstance(warning, str)


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================

class TestStateEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_state_creation(self):
        """Test creating empty WorkflowState."""
        state = WorkflowState()

        # Should be able to create empty state
        assert isinstance(state, dict)

    def test_state_with_partial_fields(self):
        """Test state with only some fields set."""
        state: WorkflowState = {
            "input_file_path": "test.sav",
            "current_step": 3,
        }

        assert state["input_file_path"] == "test.sav"
        assert state["current_step"] == 3
        assert state.get("recoding_rules") is None

    def test_state_copy_independence(self):
        """Test that state copies are independent."""
        original = create_initial_state("test.sav")
        copy_state = original.copy()

        # Modify copy
        copy_state["current_step"] = 5
        copy_state["errors"].append("Error")

        # Original should be unchanged (except for shared mutable references)
        assert original["current_step"] == 0

    def test_state_with_none_values(self):
        """Test state fields set to None."""
        state = create_initial_state("test.sav")

        # Explicitly set fields to None
        state["recoding_rules"] = None
        state["indicators"] = None
        state["raw_data"] = None

        assert state["recoding_rules"] is None
        assert state["indicators"] is None
        assert state["raw_data"] is None

    def test_state_field_overwrite(self):
        """Test overwriting state fields."""
        state = create_initial_state("test.sav")
        state["current_step"] = 5

        # Overwrite with new value
        state["current_step"] = 10
        assert state["current_step"] == 10


# =============================================================================
# State Serialization Tests
# =============================================================================

class TestStateSerialization:
    """Tests for state serialization and deserialization."""

    def test_state_to_dict_preserves_all_fields(self):
        """Test state_to_dict preserves all fields."""
        state: WorkflowState = {
            "input_file_path": "test.sav",
            "current_step": 5,
            "errors": ["error1"],
            "warnings": ["warning1"],
            "recoding_approved": True,
        }

        result = state_to_dict(state)

        assert result["input_file_path"] == "test.sav"
        assert result["current_step"] == 5
        assert result["errors"] == ["error1"]
        assert result["warnings"] == ["warning1"]

    def test_state_to_dict_converts_validation_result(self):
        """Test state_to_dict converts ValidationResult to dict."""
        validation = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Warning"],
            checks_performed=["check1"],
        )

        state: WorkflowState = {
            "input_file_path": "test.sav",
            "recoding_validation_result": validation,
        }

        result = state_to_dict(state)

        assert isinstance(result["recoding_validation_result"], dict)
        assert result["recoding_validation_result"]["is_valid"] is True
        assert result["recoding_validation_result"]["warnings"] == ["Warning"]

    def test_state_to_dict_with_multiple_validation_results(self):
        """Test state_to_dict with multiple ValidationResult objects."""
        recoding_validation = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            checks_performed=["check1"],
        )

        indicator_validation = ValidationResult(
            is_valid=False,
            errors=["Error"],
            warnings=[],
            checks_performed=["check2"],
        )

        state: WorkflowState = {
            "input_file_path": "test.sav",
            "recoding_validation_result": recoding_validation,
            "indicator_validation_result": indicator_validation,
        }

        result = state_to_dict(state)

        assert result["recoding_validation_result"]["is_valid"] is True
        assert result["indicator_validation_result"]["is_valid"] is False
        assert result["indicator_validation_result"]["errors"] == ["Error"]
