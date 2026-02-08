"""
State Definitions for Survey Analysis Workflow

This module defines all TypedDict state classes for the 22-step LangGraph workflow.
The state is organized into 10 sub-states that combine into a single WorkflowState.

State Architecture:
- InputState: Initial input configuration (Step 0)
- ExtractionState: Data extraction and preparation (Steps 1-3)
- RecodingState: New dataset generation (Steps 4-8)
- IndicatorState: Indicator generation (Steps 9-11)
- CrossTableState: Cross-table generation (Steps 12-16)
- StatisticalAnalysisState: Statistical tests (Steps 17-18)
- FilteringState: Significant tables selection (Steps 19-20)
- PresentationState: Output generation (Steps 21-22)
- ApprovalState: Human-in-the-loop tracking (cross-step)
- TrackingState: Execution logging (cross-step)

All sub-states use total=False for optional fields, allowing incremental
population as the workflow progresses.
"""

from typing import TypedDict, Optional, Dict, List, Any, Literal, Annotated
import pandas as pd


# =============================================================================
# State Reducers
# =============================================================================

def error_reducer(existing: List[str], new: List[str]) -> List[str]:
    """
    Reducer for accumulating errors without duplicates.

    This reducer is used by LangGraph to automatically merge error lists
    when nodes return new errors. It prevents duplicate error messages from
    accumulating in the state.

    Args:
        existing: Current list of errors in state
        new: New errors to add (from node return value)

    Returns:
        Combined list with duplicates removed

    Example:
        >>> error_reducer(["error1"], ["error1", "error2"])
        ['error1', 'error2']
    """
    # Add new errors that aren't already in existing
    return existing + [e for e in new if e not in existing]


def warning_reducer(existing: List[str], new: List[str]) -> List[str]:
    """
    Reducer for accumulating warnings without duplicates.

    This reducer is used by LangGraph to automatically merge warning lists
    when nodes return new warnings. It prevents duplicate warning messages from
    accumulating in the state.

    Args:
        existing: Current list of warnings in state
        new: New warnings to add (from node return value)

    Returns:
        Combined list with duplicates removed

    Example:
        >>> warning_reducer(["warn1"], ["warn1", "warn2"])
        ['warn1', 'warn2']
    """
    # Add new warnings that aren't already in existing
    return existing + [w for w in new if w not in existing]


# =============================================================================
# Step Name Constants
# =============================================================================

# Step identifier constants for the 22-step workflow
# These constants provide human-readable step names instead of numeric identifiers
STEP_0_INITIAL = "step_0_initial"
STEP_1_EXTRACT_SPSS = "step_1_extract_spss"
STEP_2_TRANSFORM_METADATA = "step_2_transform_metadata"
STEP_3_FILTER_METADATA = "step_3_filter_metadata"
STEP_4_GENERATE_RECODING_RULES = "step_4_generate_recoding_rules"
STEP_5_VALIDATE_RECODING_RULES = "step_5_validate_recoding_rules"
STEP_6_REVIEW_RECODING_RULES = "step_6_review_recoding_rules"
STEP_7_GENERATE_PSPP_RECODING_SYNTAX = "step_7_generate_pspp_recoding_syntax"
STEP_8_EXECUTE_PSPP_RECODING = "step_8_execute_pspp_recoding"
STEP_9_GENERATE_INDICATORS = "step_9_generate_indicators"
STEP_10_VALIDATE_INDICATORS = "step_10_validate_indicators"
STEP_11_REVIEW_INDICATORS = "step_11_review_indicators"
STEP_12_GENERATE_TABLE_SPECIFICATIONS = "step_12_generate_table_specifications"
STEP_13_VALIDATE_TABLE_SPECIFICATIONS = "step_13_validate_table_specifications"
STEP_14_REVIEW_TABLE_SPECIFICATIONS = "step_14_review_table_specifications"
STEP_15_GENERATE_PSPP_TABLE_SYNTAX = "step_15_generate_pspp_table_syntax"
STEP_16_EXECUTE_PSPP_TABLES = "step_16_execute_pspp_tables"
STEP_17_GENERATE_STATISTICS_SCRIPT = "step_17_generate_statistics_script"
STEP_18_EXECUTE_STATISTICS_SCRIPT = "step_18_execute_statistics_script"
STEP_19_GENERATE_FILTER_LIST = "step_19_generate_filter_list"
STEP_20_APPLY_FILTER_TO_TABLES = "step_20_apply_filter_to_tables"
STEP_21_GENERATE_POWERPOINT = "step_21_generate_powerpoint"
STEP_22_GENERATE_HTML_DASHBOARD = "step_22_generate_html_dashboard"

# Mapping of step names to their numeric order (for ordering/comparison)
STEP_ORDER = {
    STEP_0_INITIAL: 0,
    STEP_1_EXTRACT_SPSS: 1,
    STEP_2_TRANSFORM_METADATA: 2,
    STEP_3_FILTER_METADATA: 3,
    STEP_4_GENERATE_RECODING_RULES: 4,
    STEP_5_VALIDATE_RECODING_RULES: 5,
    STEP_6_REVIEW_RECODING_RULES: 6,
    STEP_7_GENERATE_PSPP_RECODING_SYNTAX: 7,
    STEP_8_EXECUTE_PSPP_RECODING: 8,
    STEP_9_GENERATE_INDICATORS: 9,
    STEP_10_VALIDATE_INDICATORS: 10,
    STEP_11_REVIEW_INDICATORS: 11,
    STEP_12_GENERATE_TABLE_SPECIFICATIONS: 12,
    STEP_13_VALIDATE_TABLE_SPECIFICATIONS: 13,
    STEP_14_REVIEW_TABLE_SPECIFICATIONS: 14,
    STEP_15_GENERATE_PSPP_TABLE_SYNTAX: 15,
    STEP_16_EXECUTE_PSPP_TABLES: 16,
    STEP_17_GENERATE_STATISTICS_SCRIPT: 17,
    STEP_18_EXECUTE_STATISTICS_SCRIPT: 18,
    STEP_19_GENERATE_FILTER_LIST: 19,
    STEP_20_APPLY_FILTER_TO_TABLES: 20,
    STEP_21_GENERATE_POWERPOINT: 21,
    STEP_22_GENERATE_HTML_DASHBOARD: 22,
}

# Reverse mapping for backward compatibility (numeric to string)
NUMERIC_TO_STEP_NAME = {
    0: STEP_0_INITIAL,
    1: STEP_1_EXTRACT_SPSS,
    2: STEP_2_TRANSFORM_METADATA,
    3: STEP_3_FILTER_METADATA,
    4: STEP_4_GENERATE_RECODING_RULES,
    5: STEP_5_VALIDATE_RECODING_RULES,
    6: STEP_6_REVIEW_RECODING_RULES,
    7: STEP_7_GENERATE_PSPP_RECODING_SYNTAX,
    8: STEP_8_EXECUTE_PSPP_RECODING,
    9: STEP_9_GENERATE_INDICATORS,
    10: STEP_10_VALIDATE_INDICATORS,
    11: STEP_11_REVIEW_INDICATORS,
    12: STEP_12_GENERATE_TABLE_SPECIFICATIONS,
    13: STEP_13_VALIDATE_TABLE_SPECIFICATIONS,
    14: STEP_14_REVIEW_TABLE_SPECIFICATIONS,
    15: STEP_15_GENERATE_PSPP_TABLE_SYNTAX,
    16: STEP_16_EXECUTE_PSPP_TABLES,
    17: STEP_17_GENERATE_STATISTICS_SCRIPT,
    18: STEP_18_EXECUTE_STATISTICS_SCRIPT,
    19: STEP_19_GENERATE_FILTER_LIST,
    20: STEP_20_APPLY_FILTER_TO_TABLES,
    21: STEP_21_GENERATE_POWERPOINT,
    22: STEP_22_GENERATE_HTML_DASHBOARD,
}

# Review steps (three-node pattern approval steps)
REVIEW_STEPS = {
    STEP_6_REVIEW_RECODING_RULES,
    STEP_11_REVIEW_INDICATORS,
    STEP_14_REVIEW_TABLE_SPECIFICATIONS,
}


# =============================================================================
# ValidationResult
# =============================================================================

class ValidationResult(TypedDict, total=False):
    """
    Standard validation result structure for artifact validation.

    Used by validation nodes to return structured validation results
    for AI-generated artifacts (recoding rules, indicators, table specifications).

    Converted to TypedDict for LangGraph Studio compatibility (Pydantic v2 serialization).

    Attributes:
        is_valid: Overall validation status
        errors: Critical errors that must be fixed
        warnings: Non-critical issues
        checks_performed: List of validation checks run
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    checks_performed: List[str]


def create_validation_result(
    is_valid: bool,
    errors: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
    checks_performed: Optional[List[str]] = None
) -> ValidationResult:
    """
    Factory function to create ValidationResult instances.

    This provides a convenient way to create validation results
    while maintaining TypedDict compatibility.

    Args:
        is_valid: Overall validation status
        errors: Critical errors that must be fixed
        warnings: Non-critical issues
        checks_performed: List of validation checks run

    Returns:
        ValidationResult TypedDict instance
    """
    return ValidationResult(
        is_valid=is_valid,
        errors=errors or [],
        warnings=warnings or [],
        checks_performed=checks_performed or []
    )


# =============================================================================
# Sub-State Definitions
# =============================================================================

class InputState(TypedDict, total=False):
    """
    Initial input configuration - populated at workflow start (Step 0).

    Fields:
        input_file_path: Path to input .sav file
    """
    input_file_path: str


class ExtractionState(TypedDict, total=False):
    """
    Data extraction and preparation - Steps 1-3.

    Fields populated incrementally:
    - Step 1: original_metadata (raw_data is NOT stored to avoid serialization issues)
    - Step 2: variable_centered_metadata
    - Step 3: filtered_metadata, filtered_out_variables

    Fields:
        original_metadata: Raw metadata from pyreadstat extracted in Step 1
        raw_data: DEPRECATED - Not stored in state to avoid LangGraph serialization issues.
                    Data is reloaded from input_file_path when needed.
        variable_centered_metadata: Metadata restructured by variable (Step 2)
        filtered_metadata: Metadata after filtering (variables requiring recoding)
        filtered_out_variables: Variables removed with reasons
    """
    original_metadata: Optional[Dict[str, Any]]  # Raw metadata from pyreadstat (Step 1)
    raw_data: Optional[Any]  # pandas DataFrame - DEPRECATED, not populated
    variable_centered_metadata: Optional[Dict[str, Any]]  # Variable-centered metadata structure
    filtered_metadata: Optional[List[Dict[str, Any]]]
    filtered_out_variables: Optional[List[Dict[str, str]]]


class RecodingState(TypedDict, total=False):
    """
    New dataset generation through LLM-orchestrated recoding - Steps 4-8.

    Three-node pattern fields (Steps 4-6):
    - Step 4: recoding_rules
    - Step 5: recoding_validation_result
    - Step 6: recoding_approved, recoding_feedback

    PSPP execution fields (Steps 7-8):
    - Step 7: (syntax generation - tracked in execution log)
    - Step 8: new_data_file, new_metadata

    Fields:
        recoding_rules: AI-generated recoding rules
        recoding_validation_result: Automated validation results
        recoding_approved: Human approval status
        recoding_feedback: Feedback from validation or human
        new_metadata: Complete metadata from new_data.sav
        new_data_file: Path to new dataset .sav file
    """
    recoding_rules: Optional[Dict[str, Any]]
    recoding_validation_result: Optional[ValidationResult]
    recoding_approved: bool
    recoding_feedback: Optional[str]
    new_metadata: Optional[Dict[str, Any]]
    new_data_file: Optional[str]


class IndicatorState(TypedDict, total=False):
    """
    Indicator generation and semantic grouping - Steps 9-11.

    Three-node pattern:
    - Step 9: indicators
    - Step 10: indicator_validation_result
    - Step 11: indicators_approved, indicator_feedback

    Fields:
        indicators: Generated indicator definitions
        indicator_validation_result: Validation results
        indicators_approved: Human approval status
        indicator_feedback: Feedback from validation or human
    """
    indicators: Optional[Dict[str, Any]]
    indicator_validation_result: Optional[ValidationResult]
    indicators_approved: bool
    indicator_feedback: Optional[str]


class CrossTableState(TypedDict, total=False):
    """
    Cross-table specification and generation - Steps 12-16.

    Three-node pattern (Steps 12-14):
    - Step 12: table_specifications
    - Step 13: table_validation_result
    - Step 14: table_specs_approved, table_specs_feedback

    PSPP execution (Steps 15-16):
    - Step 15: table_syntax_file (PSPP CTABLES syntax)
    - Step 16: cross_table_file

    Fields:
        table_specifications: Table structure definitions
        table_validation_result: Validation results
        table_specs_approved: Human approval status
        table_specs_feedback: Feedback from validation or human
        table_syntax_file: Path to PSPP CTABLES syntax file (.sps)
        cross_table_file: Path to cross-table output file
    """
    table_specifications: Optional[Dict[str, Any]]
    table_validation_result: Optional[ValidationResult]
    table_specs_approved: bool
    table_specs_feedback: Optional[str]
    table_syntax_file: Optional[str]
    cross_table_file: Optional[str]


class StatisticalAnalysisState(TypedDict, total=False):
    """
    Python script generation and Chi-square statistics computation - Steps 17-18.

    Fields:
        statistics_script: Path to generated stats_script.py (Step 17)
        statistical_summary: Statistical test results (chi-square, Cramer's V) (Step 18)
    """
    statistics_script: Optional[str]
    statistical_summary: Optional[Dict[str, Any]]


class FilteringState(TypedDict, total=False):
    """
    Filter list generation and significant tables selection - Steps 19-20.

    Fields:
        filter_list: Pass/fail status for all tables
        filtered_tables: Tables filtered by significance
        total_tables_evaluated: Total number of tables evaluated (Step 20)
        significant_tables_count: Number of significant tables after filtering (Step 20)
        filtering_valid: Whether filtering validation passed (Step 20)
    """
    filter_list: Optional[Dict[str, Any]]
    filtered_tables: Optional[Dict[str, Any]]
    total_tables_evaluated: int
    significant_tables_count: int
    filtering_valid: bool


class PresentationState(TypedDict, total=False):
    """
    Final output generation - Steps 21-22.

    Fields:
        powerpoint_file: Generated PowerPoint file path
        html_dashboard_file: Generated HTML dashboard path
    """
    powerpoint_file: Optional[str]
    html_dashboard_file: Optional[str]


class ApprovalState(TypedDict, total=False):
    """
    Human-in-the-loop approval tracking (crosses all steps).

    Used by the three-node pattern to track:
    - Which step requires approval
    - How many iterations have occurred
    - Whether human review is required

    Fields:
        current_step: Current step identifier (string constant from STEP_* constants)
        requires_human_review: Whether current step needs human input
        iteration_count: Number of iterations for current step (for retry logic)
    """
    current_step: str
    requires_human_review: bool
    iteration_count: int


class TrackingState(TypedDict, total=False):
    """
    Execution tracking (crosses all steps).

    Updated throughout workflow execution to track:
    - Errors that occur during processing
    - Warnings that should be flagged to user
    - Step-by-step execution log

    Fields:
        errors: Error messages accumulated during workflow (with reducer)
        warnings: Warning messages accumulated during workflow (with reducer)

    Note: errors and warnings use Annotated with reducers to automatically
    accumulate new values without duplicates when nodes return updates.
    """
    errors: Annotated[List[str], error_reducer]
    warnings: Annotated[List[str], warning_reducer]


# =============================================================================
# Combined WorkflowState
# =============================================================================

class WorkflowState(
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
    TypedDict,
    total=False
):
    """
    Combined workflow state for the 22-step survey analysis workflow.

    This TypedDict inherits all sub-states, using total=False to allow
    optional fields. Fields are incrementally populated as workflow progresses.

    State Evolution:
    - Step 0: InputState fields populated
    - Steps 1-3: ExtractionState fields populated
    - Steps 4-8: RecodingState fields populated (with three-node pattern)
    - Steps 9-11: IndicatorState fields populated (with three-node pattern)
    - Steps 12-16: CrossTableState fields populated (with three-node pattern)
    - Steps 17-18: StatisticalAnalysisState fields populated
    - Steps 19-20: FilteringState fields populated
    - Steps 21-22: PresentationState fields populated
    - Cross-step: ApprovalState and TrackingState updated throughout

    Immutability:
    Nodes must return new state dictionaries, never modify existing state
    in-place. LangGraph handles state merging automatically.
    """
    pass


# =============================================================================
# State Initialization
# =============================================================================

def create_initial_state(input_file_path: str, config: Optional[Dict[str, Any]] = None) -> WorkflowState:
    """
    Create initial workflow state with populated input fields.

    Initializes all fields with appropriate default values:
    - InputState: Populated with provided values
    - All other states: Set to None or default values
    - Lists: Initialized as empty lists
    - Integers: Initialized to 0
    - Booleans: Initialized to False

    Args:
        input_file_path: Path to input .sav file (SPSS survey data)
        config: Optional configuration parameters. If None, uses default config.

    Returns:
        Initialized WorkflowState ready for workflow execution

    Example:
        >>> from agent.state import create_initial_state
        >>> state = create_initial_state("survey_data.sav")
        >>> print(state["input_file_path"])
        'survey_data.sav'
    """
    # Import config module for default configuration
    from agent.config import DEFAULT_CONFIG

    if config is None:
        config = DEFAULT_CONFIG.copy()

    return WorkflowState(
        # ========================================
        # InputState - Populated
        # ========================================
        input_file_path=input_file_path
        if hasattr(WorkflowState, '__annotations__') and 'input_file_path' in WorkflowState.__annotations__ else input_file_path,  # type: ignore

        # ========================================
        # ExtractionState - All None
        # ========================================
        original_metadata=None,
        raw_data=None,
        variable_centered_metadata=None,
        filtered_metadata=None,
        filtered_out_variables=None,

        # ========================================
        # RecodingState - All None/default
        # ========================================
        recoding_rules=None,
        recoding_validation_result=None,
        recoding_approved=False,
        recoding_feedback=None,
        new_metadata=None,
        new_data_file=None,

        # ========================================
        # IndicatorState - All None/default
        # ========================================
        indicators=None,
        indicator_validation_result=None,
        indicators_approved=False,
        indicator_feedback=None,

        # ========================================
        # CrossTableState - All None/default
        # ========================================
        table_specifications=None,
        table_validation_result=None,
        table_specs_approved=False,
        table_specs_feedback=None,
        table_syntax_file=None,
        cross_table_file=None,

        # ========================================
        # StatisticalAnalysisState - All None
        # ========================================
        statistics_script=None,
        statistical_summary=None,

        # ========================================
        # FilteringState - All None/default
        # ========================================
        filter_list=None,
        filtered_tables=None,
        total_tables_evaluated=0,
        significant_tables_count=0,
        filtering_valid=False,

        # ========================================
        # PresentationState - All None
        # ========================================
        powerpoint_file=None,
        html_dashboard_file=None,

        # ========================================
        # ApprovalState - Initialized
        # ========================================
        current_step=STEP_0_INITIAL,
        requires_human_review=False,
        iteration_count=0,

        # ========================================
        # TrackingState - Initialized empty
        # ========================================
        errors=[],
        warnings=[],
    )


# =============================================================================
# State Utilities
# =============================================================================

def state_to_dict(state: WorkflowState) -> Dict[str, Any]:
    """
    Convert WorkflowState to a regular dictionary for serialization.

    Args:
        state: WorkflowState to convert

    Returns:
        Dictionary representation of state
    """
    return dict(state)


def get_state_summary(state: WorkflowState) -> Dict[str, Any]:
    """
    Get a summary of the current state for logging/debugging.

    Args:
        state: WorkflowState to summarize

    Returns:
        Dictionary with state summary information
    """
    return {
        "current_step": state.get("current_step"),
        "requires_human_review": state.get("requires_human_review"),
        "iteration_count": state.get("iteration_count"),
        "errors_count": len(state.get("errors", [])),
        "warnings_count": len(state.get("warnings", [])),
        "recoding_approved": state.get("recoding_approved", False),
        "indicators_approved": state.get("indicators_approved", False),
        "table_specs_approved": state.get("table_specs_approved", False),
        "has_output_files": bool(
            state.get("new_data_file")
            or state.get("cross_table_file")
            or state.get("powerpoint_file")
            or state.get("html_dashboard_file")
        ),
    }


# =============================================================================
# DataFrame Serialization for LangGraph Checkpoints
# =============================================================================

def serialize_state_for_checkpoint(state: WorkflowState) -> Dict[str, Any]:
    """
    Convert WorkflowState to a format suitable for LangGraph checkpointing.

    This function converts pandas DataFrames to a serializable format that
    LangGraph's msgpack serializer can handle.

    Args:
        state: WorkflowState to serialize

    Returns:
        Serialized state dictionary with DataFrames converted to dict format
    """
    serialized = {}
    for key, value in state.items():
        if isinstance(value, pd.DataFrame):
            # Convert DataFrame to dict representation
            serialized[key] = {
                '__type__': 'DataFrame',
                'data': value.to_dict('records'),
                'columns': list(value.columns),
                'dtypes': {col: str(dtype) for col, dtype in value.dtypes.items()}
            }
        else:
            serialized[key] = value
    return serialized


def deserialize_state_from_checkpoint(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Restore WorkflowState from serialized checkpoint format.

    This function converts DataFrame dicts back to pandas DataFrames.

    Args:
        data: Serialized state dictionary from checkpoint

    Returns:
        Deserialized state dictionary with DataFrames restored
    """
    restored = {}
    for key, value in data.items():
        if isinstance(value, dict) and value.get('__type__') == 'DataFrame':
            # Reconstruct DataFrame from dict representation
            df_data = value['data']
            columns = value['columns']
            dtypes = value.get('dtypes', {})

            # Create DataFrame
            df = pd.DataFrame(df_data, columns=columns)

            # Convert dtypes if needed
            for col, dtype_str in dtypes.items():
                if col in df.columns:
                    try:
                        # Handle common dtype conversions
                        if 'int' in dtype_str.lower():
                            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                        elif 'float' in dtype_str.lower():
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    except (ValueError, TypeError):
                        # Keep original dtype if conversion fails
                        pass

            restored[key] = df
        else:
            restored[key] = value
    return restored
