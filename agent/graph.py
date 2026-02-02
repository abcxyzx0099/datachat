"""
LangGraph StateGraph Construction for Survey Analysis Workflow

This module constructs the 22-step LangGraph StateGraph for processing SPSS survey
files through data extraction, AI-orchestrated recoding, indicator generation,
cross-table creation, statistical analysis, significance filtering, and
presentation generation.

Graph Structure:
- 22 nodes organized into 8 phases
- Linear edges connecting sequential steps
- Conditional edges for three-node pattern feedback loops
- SQLite-based checkpointer for resumable execution

Three-Node Pattern:
The graph implements three human-in-the-loop review points with retry logic:
1. Recoding Rules (Steps 4-6): Generate → Validate → Review
2. Indicators (Steps 9-11): Generate → Validate → Review
3. Table Specifications (Steps 12-14): Generate → Validate → Review

Each pattern allows:
- Automatic retry on validation failure
- Human review and approval
- Feedback-driven regeneration
"""

import os
import logging
from typing import Optional, Dict, Any

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# LangSmith tracing (optional - requires LANGSMITH_API_KEY environment variable)
# Note: LangGraph automatically picks up LANGSMITH_* environment variables when set
# The tracing is configured through the LangSmith environment variables
LANGSMITH_AVAILABLE = os.environ.get("LANGSMITH_API_KEY") and os.environ.get("LANGSMITH_TRACING") == "true"

# Try to import SqliteSaver if available (langgraph >= 1.0.3)
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False
    SqliteSaver = None  # type: ignore

from agent.state import WorkflowState, create_initial_state
from agent.config import DEFAULT_CONFIG, get_config_with_env_overrides

# Import all 22 nodes
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

# Import conditional edge routing functions
from agent.edges import (
    should_retry_recoding,
    should_approve_recoding,
    should_retry_indicators,
    should_approve_indicators,
    should_retry_table_specs,
    should_approve_table_specs,
    RECODING_EDGE_MAPPING,
    INDICATOR_EDGE_MAPPING,
    TABLE_SPECS_EDGE_MAPPING,
)


# =============================================================================
# Graph Construction
# =============================================================================

def build_graph(
    checkpointer_path: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> StateGraph:
    """
    Build and compile the LangGraph StateGraph for survey analysis.

    This function constructs the complete 22-node workflow graph with:
    - All nodes added to the graph
    - Linear edges connecting sequential steps
    - Conditional edges for three-node pattern feedback loops
    - SQLite checkpointer for state persistence

    Args:
        checkpointer_path: Path to SQLite database for checkpointing.
                          If None, uses in-memory MemorySaver.
                          If False, disables checkpointing entirely (for testing).
        config: Optional configuration dictionary. If None, uses DEFAULT_CONFIG.

    Returns:
        Compiled StateGraph ready for execution

    Graph Flow:
        Phase 1 (Extraction): Steps 1-3
        Phase 2 (Recoding): Steps 4-8 with three-node pattern (4-6)
        Phase 3 (Indicators): Steps 9-11 with three-node pattern
        Phase 4 (Tables): Steps 12-16 with three-node pattern (12-14)
        Phase 5 (Statistics): Steps 17-18
        Phase 6 (Filtering): Steps 19-20
        Phase 7 (PowerPoint): Step 21
        Phase 8 (HTML Dashboard): Step 22
    """
    if config is None:
        config = get_config_with_env_overrides(DEFAULT_CONFIG.copy())

    # Initialize checkpointer
    # Check for CHECKPOINT_DB_PATH environment variable first
    env_db_path = os.getenv("CHECKPOINT_DB_PATH")
    db_path = env_db_path if env_db_path else checkpointer_path

    # Special case: checkpointer_path=False means disable checkpointing
    if checkpointer_path is False:
        checkpointer = None
        logging.info("Checkpointing disabled (checkpointer_path=False)")
    elif db_path and SQLITE_AVAILABLE:
        # Use SQLite for persistent checkpointing
        import sqlite3
        conn = sqlite3.connect(db_path, check_same_thread=False)
        checkpointer = SqliteSaver(conn)
        logging.info(f"Using SQLite checkpointer: {db_path}")
    elif db_path and not SQLITE_AVAILABLE:
        # SQLite requested but not available
        logging.warning(
            "SQLite checkpointer requested but langgraph-checkpoint-sqlite "
            "is not installed. Using MemorySaver instead. "
            "Install with: pip install langgraph-checkpoint-sqlite"
        )
        checkpointer = MemorySaver()
        logging.info("Using in-memory MemorySaver checkpointer")
    else:
        # No path specified, use in-memory
        checkpointer = MemorySaver()
        logging.info("Using in-memory MemorySaver checkpointer")

    # Initialize StateGraph with WorkflowState
    builder = StateGraph(WorkflowState)

    # =============================================================================
    # Add 22 Nodes
    # =============================================================================

    # Phase 1: Extraction & Preparation (Steps 1-3)
    builder.add_node("extract_spss_node", extract_spss_node)
    builder.add_node("transform_metadata_node", transform_metadata_node)
    builder.add_node("filter_metadata_node", filter_metadata_node)

    # Phase 2: New Dataset Generation (Steps 4-8)
    builder.add_node("generate_recoding_rules_node", generate_recoding_rules_node)
    builder.add_node("validate_recoding_rules_node", validate_recoding_rules_node)
    builder.add_node("review_recoding_rules_node", review_recoding_rules_node)
    builder.add_node("generate_pspp_recoding_syntax_node", generate_pspp_recoding_syntax_node)
    builder.add_node("execute_pspp_recoding_node", execute_pspp_recoding_node)

    # Phase 3: Indicator Generation (Steps 9-11)
    builder.add_node("generate_indicators_node", generate_indicators_node)
    builder.add_node("validate_indicators_node", validate_indicators_node)
    builder.add_node("review_indicators_node", review_indicators_node)

    # Phase 4: Cross-Table Generation (Steps 12-16)
    builder.add_node("generate_table_specifications_node", generate_table_specifications_node)
    builder.add_node("validate_table_specifications_node", validate_table_specifications_node)
    builder.add_node("review_table_specifications_node", review_table_specifications_node)
    builder.add_node("generate_pspp_table_syntax_node", generate_pspp_table_syntax_node)
    builder.add_node("execute_pspp_tables_node", execute_pspp_tables_node)

    # Phase 5: Statistical Analysis (Steps 17-18)
    builder.add_node("generate_python_statistics_script_node", generate_python_statistics_script_node)
    builder.add_node("execute_python_statistics_script_node", execute_python_statistics_script_node)

    # Phase 6: Significant Tables Selection (Steps 19-20)
    builder.add_node("generate_filter_list_node", generate_filter_list_node)
    builder.add_node("apply_filter_to_tables_node", apply_filter_to_tables_node)

    # Phase 7: Executive Summary Presentation (Step 21)
    builder.add_node("generate_powerpoint_node", generate_powerpoint_node)

    # Phase 8: Full Report Dashboard (Step 22)
    builder.add_node("generate_html_dashboard_node", generate_html_dashboard_node)

    # =============================================================================
    # Set Entry Point
    # =============================================================================

    builder.set_entry_point("extract_spss_node")

    # =============================================================================
    # Add Linear Edges (Sequential Flow)
    # =============================================================================

    # Phase 1: Step 1 → 2 → 3
    builder.add_edge("extract_spss_node", "transform_metadata_node")
    builder.add_edge("transform_metadata_node", "filter_metadata_node")

    # Phase 2: Step 3 → 4, then conditional from 4/5/6
    builder.add_edge("filter_metadata_node", "generate_recoding_rules_node")

    # Phase 2: Step 7 → 8 (after three-node pattern)
    builder.add_edge("generate_pspp_recoding_syntax_node", "execute_pspp_recoding_node")

    # Phase 3: Step 8 → 9, then conditional from 9/10/11
    builder.add_edge("execute_pspp_recoding_node", "generate_indicators_node")

    # Phase 4: Step 15 → 16 (after three-node pattern)
    builder.add_edge("generate_pspp_table_syntax_node", "execute_pspp_tables_node")

    # Phase 5: Step 16 → 17 → 18
    builder.add_edge("execute_pspp_tables_node", "generate_python_statistics_script_node")
    builder.add_edge("generate_python_statistics_script_node", "execute_python_statistics_script_node")

    # Phase 6: Step 18 → 19 → 20
    builder.add_edge("execute_python_statistics_script_node", "generate_filter_list_node")
    builder.add_edge("generate_filter_list_node", "apply_filter_to_tables_node")

    # Phase 7 & 8: Step 20 → 21 → 22 → END
    builder.add_edge("apply_filter_to_tables_node", "generate_powerpoint_node")
    builder.add_edge("generate_powerpoint_node", "generate_html_dashboard_node")
    builder.add_edge("generate_html_dashboard_node", END)

    # =============================================================================
    # Add Conditional Edges (Three-Node Pattern Feedback Loops)
    # =============================================================================

    # Three-Node Pattern 1: Recoding Rules (Steps 4-6)
    # After validate_recoding_rules_node (Step 5): retry or review
    builder.add_conditional_edges(
        "validate_recoding_rules_node",
        should_retry_recoding,
        RECODING_EDGE_MAPPING,
    )

    # After review_recoding_rules_node (Step 6): retry or proceed
    builder.add_conditional_edges(
        "review_recoding_rules_node",
        should_approve_recoding,
        RECODING_EDGE_MAPPING,
    )

    # Three-Node Pattern 2: Indicators (Steps 9-11)
    # After validate_indicators_node (Step 10): retry or review
    builder.add_conditional_edges(
        "validate_indicators_node",
        should_retry_indicators,
        INDICATOR_EDGE_MAPPING,
    )

    # After review_indicators_node (Step 11): retry or proceed
    builder.add_conditional_edges(
        "review_indicators_node",
        should_approve_indicators,
        INDICATOR_EDGE_MAPPING,
    )

    # Three-Node Pattern 3: Table Specifications (Steps 12-14)
    # After validate_table_specifications_node (Step 13): retry or review
    builder.add_conditional_edges(
        "validate_table_specifications_node",
        should_retry_table_specs,
        TABLE_SPECS_EDGE_MAPPING,
    )

    # After review_table_specifications_node (Step 14): retry or proceed
    builder.add_conditional_edges(
        "review_table_specifications_node",
        should_approve_table_specs,
        TABLE_SPECS_EDGE_MAPPING,
    )

    # =============================================================================
    # Compile Graph with Checkpointer and LangSmith Tracing
    # =============================================================================

    # Prepare callbacks
    callbacks = []

    # Add LangSmith tracing if API key is available
    if LANGSMITH_AVAILABLE:
        project_name = os.environ.get("LANGSMITH_PROJECT", "DataChat-Survey-Analyzer")
        logging.info(f"LangSmith tracing enabled for project: {project_name}")
    else:
        logging.info("LangSmith tracing not configured or disabled")

    # Compile the graph with checkpointer
    graph = builder.compile(checkpointer=checkpointer)

    logging.info("LangGraph StateGraph compiled successfully")
    logging.info(f"Total nodes: 22")
    logging.info(f"Three-node patterns: 3 (recoding, indicators, table_specs)")

    return graph


# =============================================================================
# Graph Entry Point Functions
# =============================================================================

def get_graph(
    checkpointer_path: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> StateGraph:
    """
    Get the compiled LangGraph StateGraph.

    This is the main entry point for retrieving the graph instance.
    Uses default checkpoint path if not specified.

    Args:
        checkpointer_path: Optional path to SQLite database.
                          Defaults to "checkpoints.db" in project root.
        config: Optional configuration dictionary.

    Returns:
        Compiled StateGraph ready for execution

    Example:
        >>> from agent.graph import get_graph
        >>> graph = get_graph()
        >>> result = graph.invoke(initial_state, config)
    """
    if checkpointer_path is None:
        # Default to checkpoints.db in project root
        checkpointer_path = os.path.join(os.getcwd(), "checkpoints.db")

    return build_graph(checkpointer_path=checkpointer_path, config=config)


def run_analysis(
    input_file_path: str,
    thread_id: str = "default",
    checkpointer_path: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> WorkflowState:
    """
    Run the survey analysis workflow on an input file.

    This is the main entry point for executing the complete workflow.
    Creates initial state, initializes the graph, and runs the analysis.

    Args:
        input_file_path: Path to input .sav file (SPSS survey data)
        thread_id: Thread ID for checkpointing (enables resumable execution)
        checkpointer_path: Optional path to SQLite database.
                          Defaults to "checkpoints.db" in project root.
        config: Optional configuration dictionary.

    Returns:
        Final workflow state after completion

    Example:
        >>> from agent.graph import run_analysis
        >>> result = run_analysis("survey_data.sav", thread_id="analysis-1")
        >>> print(result["powerpoint_file"])
        'output/20240201_153045/presentation.pptx'

    Resumable Execution:
        To resume after interruption, use the same thread_id:

        >>> result = run_analysis("survey_data.sav", thread_id="analysis-1")
        # ... workflow interrupted at Step 6 (human review)
        >>> # After providing feedback, resume with same thread_id:
        >>> result = run_analysis("survey_data.sav", thread_id="analysis-1")
        # Workflow continues from Step 6
    """
    # Load configuration
    if config is None:
        config = get_config_with_env_overrides(DEFAULT_CONFIG.copy())

    # Create initial state
    initial_state = create_initial_state(input_file_path, config)

    # Get compiled graph
    graph = get_graph(checkpointer_path=checkpointer_path, config=config)

    # Configure thread ID for checkpointing
    run_config = {"configurable": {"thread_id": thread_id}}

    logging.info(f"Starting survey analysis: {input_file_path}")
    logging.info(f"Thread ID: {thread_id}")

    # Invoke graph
    try:
        result = graph.invoke(initial_state, run_config)
        logging.info("Survey analysis completed successfully")
        return result
    except Exception as e:
        logging.error(f"Survey analysis failed: {e}")
        raise


def resume_analysis(
    thread_id: str,
    checkpointer_path: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> WorkflowState:
    """
    Resume a previously interrupted or paused analysis workflow.

    This function loads an existing checkpoint by thread_id and continues
    execution from where it left off. Useful for:
    - Resuming after human review interrupts
    - Continuing after crashes or manual pauses
    - Debugging from a specific checkpoint

    Args:
        thread_id: Thread ID of the existing analysis to resume
        checkpointer_path: Optional path to SQLite database.
                          Defaults to "checkpoints.db" in project root.
        config: Optional configuration dictionary.

    Returns:
        Final workflow state after completion

    Raises:
        ValueError: If no checkpoint exists for the given thread_id

    Example:
        >>> from agent.graph import resume_analysis
        >>> # Resume analysis after human review
        >>> result = resume_analysis(thread_id="analysis-1")
        >>> print(f"Resumed from checkpoint, current step: {result['current_step']}")

    Checkpoint Restoration:
        The function loads the most recent checkpoint for the thread_id
        and continues execution from that point. All state accumulated
        up to the checkpoint is preserved.
    """
    # Load configuration
    if config is None:
        config = get_config_with_env_overrides(DEFAULT_CONFIG.copy())

    # Get compiled graph
    graph = get_graph(checkpointer_path=checkpointer_path, config=config)

    # Configure thread ID for checkpoint restoration
    run_config = {"configurable": {"thread_id": thread_id}}

    logging.info(f"Resuming survey analysis for thread: {thread_id}")

    # Check if checkpoint exists
    try:
        state_snapshot = graph.get_state(run_config)
        if state_snapshot is None:
            raise ValueError(
                f"No checkpoint found for thread_id '{thread_id}'. "
                f"Use run_analysis() to start a new analysis."
            )
        logging.info(f"Found checkpoint: {state_snapshot.metadata.get('step', 'unknown')}")
    except Exception as e:
        logging.error(f"Failed to load checkpoint: {e}")
        raise ValueError(
            f"Cannot resume analysis for thread_id '{thread_id}': {e}"
        )

    # Resume execution (None input loads from checkpoint)
    try:
        result = graph.invoke(None, run_config)
        logging.info("Survey analysis resumed and completed successfully")
        return result
    except Exception as e:
        logging.error(f"Survey analysis resumption failed: {e}")
        raise


def list_checkpoints(
    thread_id: Optional[str] = None,
    checkpointer_path: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> list:
    """
    List all checkpoints in the database.

    This function retrieves checkpoint history for debugging and audit purposes.
    Can filter by thread_id or list all checkpoints.

    Args:
        thread_id: Optional thread ID to filter checkpoints.
                   If None, lists all checkpoints across all threads.
        checkpointer_path: Optional path to SQLite database.
                          Defaults to "checkpoints.db" in project root.
        config: Optional configuration dictionary.

    Returns:
        List of checkpoint tuples containing checkpoint information

    Example:
        >>> from agent.graph import list_checkpoints
        >>> # List all checkpoints for a thread
        >>> checkpoints = list_checkpoints(thread_id="analysis-1")
        >>> for cp in checkpoints:
        ...     print(f"Step: {cp.metadata.get('step')}, ID: {cp.config['configurable']['checkpoint_id']}")
    """
    # Get compiled graph
    graph = get_graph(checkpointer_path=checkpointer_path, config=config)

    # Configure thread ID filter
    # Note: LangGraph requires thread_id to be set, even if empty
    run_config = {"configurable": {"thread_id": thread_id if thread_id else ""}}

    # List checkpoints
    checkpoints = list(graph.get_state_history(run_config))

    logging.info(f"Found {len(checkpoints)} checkpoints")
    if thread_id:
        logging.info(f"Filtered by thread_id: {thread_id}")

    return checkpoints


# =============================================================================
# CLI Interface
# =============================================================================

if __name__ == "__main__":
    import argparse

    # Create subparsers for different commands
    parser = argparse.ArgumentParser(
        description="Run survey analysis workflow on SPSS data file"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run new analysis")
    run_parser.add_argument(
        "input_file",
        help="Path to input .sav file (SPSS survey data)"
    )
    run_parser.add_argument(
        "--thread-id",
        default="default",
        help="Thread ID for checkpointing (enables resumable execution)"
    )
    run_parser.add_argument(
        "--checkpoint-db",
        default="checkpoints.db",
        help="Path to SQLite database for checkpointing"
    )
    run_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume existing analysis")
    resume_parser.add_argument(
        "--thread-id",
        required=True,
        help="Thread ID of analysis to resume"
    )
    resume_parser.add_argument(
        "--checkpoint-db",
        default="checkpoints.db",
        help="Path to SQLite database for checkpointing"
    )
    resume_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    # List checkpoints command
    list_parser = subparsers.add_parser("list", help="List checkpoints")
    list_parser.add_argument(
        "--thread-id",
        help="Filter by thread ID (optional, lists all if not provided)"
    )
    list_parser.add_argument(
        "--checkpoint-db",
        default="checkpoints.db",
        help="Path to SQLite database for checkpointing"
    )
    list_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    # For backward compatibility, if no subcommand specified, assume "run"
    args = parser.parse_args()
    if args.command is None:
        # If input_file is provided as positional arg, treat as "run" command
        import sys
        if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            # Re-parse as run command
            sys.argv.insert(1, 'run')
            args = parser.parse_args()

    # Configure logging
    if hasattr(args, 'verbose'):
        log_level = logging.DEBUG if args.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Execute command
    if args.command == "run":
        result = run_analysis(
            input_file_path=args.input_file,
            thread_id=args.thread_id,
            checkpointer_path=args.checkpoint_db,
        )

        # Print summary
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"Input: {args.input_file}")
        print(f"Thread ID: {args.thread_id}")
        print(f"Current Step: {result.get('current_step', 'Unknown')}")
        if result.get("powerpoint_path"):
            print(f"PowerPoint: {result['powerpoint_path']}")
        if result.get("html_dashboard_path"):
            print(f"HTML Dashboard: {result['html_dashboard_path']}")
        if result.get("errors"):
            print(f"Errors: {len(result['errors'])}")
        if result.get("warnings"):
            print(f"Warnings: {len(result['warnings'])}")
        print("=" * 60)

    elif args.command == "resume":
        result = resume_analysis(
            thread_id=args.thread_id,
            checkpointer_path=args.checkpoint_db,
        )

        # Print summary
        print("\n" + "=" * 60)
        print("ANALYSIS RESUMED AND COMPLETE")
        print("=" * 60)
        print(f"Thread ID: {args.thread_id}")
        print(f"Current Step: {result.get('current_step', 'Unknown')}")
        if result.get("powerpoint_path"):
            print(f"PowerPoint: {result['powerpoint_path']}")
        if result.get("html_dashboard_path"):
            print(f"HTML Dashboard: {result['html_dashboard_path']}")
        if result.get("errors"):
            print(f"Errors: {len(result['errors'])}")
        if result.get("warnings"):
            print(f"Warnings: {len(result['warnings'])}")
        print("=" * 60)

    elif args.command == "list":
        checkpoints = list_checkpoints(
            thread_id=args.thread_id,
            checkpointer_path=args.checkpoint_db,
        )

        # Print checkpoints
        print("\n" + "=" * 60)
        print("CHECKPOINTS")
        print("=" * 60)
        print(f"Total checkpoints: {len(checkpoints)}")
        if args.thread_id:
            print(f"Filtered by thread_id: {args.thread_id}")

        for i, cp in enumerate(checkpoints, 1):
            config = cp.config.get('configurable', {})
            checkpoint_id = config.get('checkpoint_id', 'unknown')
            thread_id = config.get('thread_id', 'unknown')
            step = cp.metadata.get('step', 'unknown')
            timestamp = cp.metadata.get('source', 'unknown')

            print(f"\n{i}. Checkpoint ID: {checkpoint_id[:8]}...")
            print(f"   Thread ID: {thread_id}")
            print(f"   Step: {step}")
            print(f"   Source: {timestamp}")

        print("=" * 60)

    else:
        parser.print_help()


# =============================================================================
# LangGraph Studio Entry Point
# =============================================================================

def graph_for_studio(config: Optional[Dict[str, Any]] = None) -> StateGraph:
    """
    Graph factory function for LangGraph Studio.

    This function provides the expected signature for LangGraph Studio's
    graph discovery mechanism. It accepts a single config parameter
    (compatible with RunnableConfig) and returns the compiled graph.

    Args:
        config: Optional configuration dictionary (RunnableConfig compatible)

    Returns:
        Compiled StateGraph ready for execution

    Example:
        This is used automatically by LangGraph Studio when starting
        the dev server with 'langgraph dev'
    """
    # Use default checkpoint path for Studio (in-memory)
    return get_graph(checkpointer_path=None, config=config)
