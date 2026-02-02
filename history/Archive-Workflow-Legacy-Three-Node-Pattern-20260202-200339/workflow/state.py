"""
State management for LangGraph survey analysis workflow.

Defines the unified state class that manages data flow through all workflow steps.
"""

from typing import TypedDict, Literal, Annotated, Optional, Dict, Any, List
from langgraph.graph.message import add_messages


# ============================================================================
# CORE WORKFLOW STATE
# ============================================================================

class State(TypedDict):
    """
    Unified state for the entire survey analysis workflow.

    This state evolves through all phases of the workflow, from data extraction
    to final output generation. Fields are organized by the step that populates them.
    """

    # --------------------------------------------------------------------
    # Core workflow state (messages for LangGraph)
    # --------------------------------------------------------------------
    messages: Annotated[list, add_messages]
    config: Dict[str, Any]

    # --------------------------------------------------------------------
    # Phase 1: Extraction & Preparation (Steps 1-3)
    # --------------------------------------------------------------------
    raw_data: Optional[object]  # pandas DataFrame
    original_metadata: Optional[Dict[str, Any]]
    variable_centered_metadata: Optional[List[Dict[str, Any]]]
    filtered_metadata: Optional[List[Dict[str, Any]]]
    filtered_out_variables: Optional[List[Dict[str, Any]]]

    # --------------------------------------------------------------------
    # Phase 2: New Variable Generation (Steps 4-7)
    # --------------------------------------------------------------------
    # Step 4: Recoding Rules (Three-Node Pattern)
    recoding_rules: Optional[Dict[str, Any]]
    recoding_validation: Optional[Dict[str, Any]]
    recoding_feedback: Optional[Dict[str, Any]]
    recoding_iteration: int
    recoding_feedback_source: Optional[Literal["validation", "human"]]
    recoding_rules_approved: bool

    # Step 5-6: PSPP Syntax Generation and Execution
    pspp_recoding_syntax: Optional[str]
    pspp_recoding_syntax_path: Optional[str]
    recoded_data_path: Optional[str]

    # --------------------------------------------------------------------
    # Phase 3: Indicator Generation (Step 8)
    # --------------------------------------------------------------------
    # Step 8: Indicators (Three-Node Pattern)
    indicators: Optional[Dict[str, Any]]
    indicators_validation: Optional[Dict[str, Any]]
    indicators_feedback: Optional[Dict[str, Any]]
    indicators_iteration: int
    indicators_feedback_source: Optional[Literal["validation", "human"]]
    indicators_approved: bool

    # --------------------------------------------------------------------
    # Phase 4: Cross-Table Generation (Steps 9-11)
    # --------------------------------------------------------------------
    # Step 9: Table Specifications (Three-Node Pattern)
    table_specifications: Optional[Dict[str, Any]]
    table_specs_validation: Optional[Dict[str, Any]]
    table_specs_feedback: Optional[Dict[str, Any]]
    table_specs_iteration: int
    table_specs_feedback_source: Optional[Literal["validation", "human"]]
    table_specs_approved: bool

    # Weighting variable identification
    weighting_variable: Optional[str]

    # Step 10-11: PSPP Syntax and Execution
    pspp_table_syntax: Optional[str]
    pspp_table_syntax_path: Optional[str]
    cross_table_sav_path: Optional[str]

    # --------------------------------------------------------------------
    # Phase 5-6: Statistical Analysis & Filtering (Steps 12-13)
    # --------------------------------------------------------------------
    all_small_tables: Optional[List[Dict[str, Any]]]
    significant_tables: Optional[List[Dict[str, Any]]]
    significant_tables_json_path: Optional[str]

    # --------------------------------------------------------------------
    # Phase 7: Presentation (Steps 14-15)
    # --------------------------------------------------------------------
    powerpoint_path: Optional[str]
    html_dashboard_path: Optional[str]
    charts_generated: Optional[List[Dict[str, Any]]]

    # --------------------------------------------------------------------
    # Cross-Step: Approval Tracking (Human-in-the-Loop)
    # --------------------------------------------------------------------
    approval_comments: List[Dict[str, Any]]
    pending_approval_step: Optional[str]

    # --------------------------------------------------------------------
    # Cross-Step: Execution Tracking
    # --------------------------------------------------------------------
    execution_log: List[Dict[str, Any]]
    errors: List[str]
    warnings: List[str]


# ============================================================================
# STATE INITIALIZATION
# ============================================================================

def create_initial_state(
    spss_file_path: str,
    config: Optional[Dict[str, Any]] = None
) -> State:
    """
    Create an initial state object for the workflow.

    Args:
        spss_file_path: Path to input .sav file
        config: Optional configuration parameters

    Returns:
        Initialized State dictionary
    """
    if config is None:
        config = {}

    # Set default configuration values
    default_config = {
        "output_dir": "output",
        "max_iterations": 3,
        "cardinality_threshold": 30,
        "filter_binary": True,
        "filter_other_text": True,
        "auto_approve_recoding": False,
        "auto_approve_indicators": False,
        "auto_approve_table_specs": False,
    }
    default_config.update(config)

    return State(
        # Core
        messages=[],
        config=default_config,

        # Input
        raw_data=None,
        original_metadata=None,
        variable_centered_metadata=None,
        filtered_metadata=None,
        filtered_out_variables=None,

        # Step 4: Recoding Rules
        recoding_rules=None,
        recoding_validation=None,
        recoding_feedback=None,
        recoding_iteration=1,
        recoding_feedback_source=None,
        recoding_rules_approved=False,

        # PSPP Recoding
        pspp_recoding_syntax=None,
        pspp_recoding_syntax_path=None,
        recoded_data_path=None,

        # Step 8: Indicators
        indicators=None,
        indicators_validation=None,
        indicators_feedback=None,
        indicators_iteration=1,
        indicators_feedback_source=None,
        indicators_approved=False,

        # Step 9: Table Specifications
        table_specifications=None,
        table_specs_validation=None,
        table_specs_feedback=None,
        table_specs_iteration=1,
        table_specs_feedback_source=None,
        table_specs_approved=False,
        weighting_variable=None,

        # PSPP Tables
        pspp_table_syntax=None,
        pspp_table_syntax_path=None,
        cross_table_sav_path=None,

        # Statistical Analysis
        all_small_tables=None,
        significant_tables=None,
        significant_tables_json_path=None,

        # Presentation
        powerpoint_path=None,
        html_dashboard_path=None,
        charts_generated=None,

        # Approval Tracking
        approval_comments=[],
        pending_approval_step=None,

        # Execution Tracking
        execution_log=[],
        errors=[],
        warnings=[],
    )
