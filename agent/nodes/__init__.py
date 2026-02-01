"""
Node Implementations for Survey Analysis Workflow

This package contains all 22 node implementations organized by phase:

Phase 1 (Extraction): Steps 1-3
- extract_spss_node
- transform_metadata_node
- filter_metadata_node

Phase 2 (Recoding): Steps 4-8
- generate_recoding_rules_node
- validate_recoding_rules_node
- review_recoding_rules_node
- generate_pspp_recoding_syntax_node
- execute_pspp_recoding_node

Phase 3 (Indicators): Steps 9-11
- generate_indicators_node
- validate_indicators_node
- review_indicators_node

Phase 4 (Tables): Steps 12-16
- generate_table_specifications_node
- validate_table_specifications_node
- review_table_specifications_node
- generate_pspp_table_syntax_node
- execute_pspp_tables_node

Phase 5 (Statistics): Steps 17-18
- generate_python_statistics_script_node
- execute_python_statistics_script_node

Phase 6 (Filtering): Steps 19-20
- generate_filter_list_node
- apply_filter_to_tables_node

Phase 7 (PowerPoint): Step 21
- generate_powerpoint_node

Phase 8 (HTML Dashboard): Step 22
- generate_html_dashboard_node
"""

from typing import Callable
from agent.state import WorkflowState


# =============================================================================
# Placeholder Node Functions
# =============================================================================

def _placeholder_node(state: WorkflowState, node_name: str) -> WorkflowState:
    """
    Placeholder node function for unimplemented nodes.

    This function allows the graph to be constructed and compiled
    before all node implementations are complete.

    Args:
        state: Current workflow state
        node_name: Name of the node for logging

    Returns:
        Updated workflow state
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Executing placeholder node: {node_name}")

    # Update current step
    step_num = {
        "extract_spss_node": 1,
        "transform_metadata_node": 2,
        "filter_metadata_node": 3,
        "generate_recoding_rules_node": 4,
        "validate_recoding_rules_node": 5,
        "review_recoding_rules_node": 6,
        "generate_pspp_recoding_syntax_node": 7,
        "execute_pspp_recoding_node": 8,
        "generate_indicators_node": 9,
        "validate_indicators_node": 10,
        "review_indicators_node": 11,
        "generate_table_specifications_node": 12,
        "validate_table_specifications_node": 13,
        "review_table_specifications_node": 14,
        "generate_pspp_table_syntax_node": 15,
        "execute_pspp_tables_node": 16,
        "generate_python_statistics_script_node": 17,
        "execute_python_statistics_script_node": 18,
        "generate_filter_list_node": 19,
        "apply_filter_to_tables_node": 20,
        "generate_powerpoint_node": 21,
        "generate_html_dashboard_node": 22,
    }.get(node_name, 0)

    state["current_step"] = step_num
    return state


# =============================================================================
# Phase 1: Extraction & Preparation (Steps 1-3)
# =============================================================================

# Import actual implementations from phase1_extraction.py
from agent.nodes.phase1_extraction import (
    extract_spss_node,
    transform_metadata_node,
    filter_metadata_node,
)


# =============================================================================
# Phase 2: New Dataset Generation (Steps 4-8)
# =============================================================================

# Import actual implementations from phase2_recoding.py
from agent.nodes.phase2_recoding import (
    generate_recoding_rules_node,
    validate_recoding_rules_node,
    review_recoding_rules_node,
    generate_pspp_recoding_syntax_node,
    execute_pspp_recoding_node,
)


# =============================================================================
# Phase 3: Indicator Generation (Steps 9-11)
# =============================================================================

# Import actual implementations from phase3_indicators.py
from agent.nodes.phase3_indicators import (
    generate_indicators_node,
    validate_indicators_node,
    review_indicators_node,
)


# =============================================================================
# Phase 4: Cross-Table Generation (Steps 12-16)
# =============================================================================

# Import actual implementations from phase4_tables.py
from agent.nodes.phase4_tables import (
    generate_table_specifications_node,
    validate_table_specs_node as validate_table_specifications_node,
    review_table_specifications_node,
    generate_pspp_table_syntax_node,
    generate_pspp_crosstabs_syntax_node,  # Alternative CROSSTABS-based implementation
    execute_pspp_tables_node,  # Primary CTABLES-based implementation
    execute_pspp_crosstabs_node,  # Alternative CROSSTABS-based implementation
)


# =============================================================================
# Phase 5: Statistical Analysis (Steps 17-18)
# =============================================================================

# Import actual implementations from phase5_statistics.py
from agent.nodes.phase5_statistics import (
    generate_python_statistics_script_node,
    execute_python_statistics_script_node,
)


# =============================================================================
# Phase 6: Significant Tables Selection (Steps 19-20)
# =============================================================================

# Import actual implementations from phase6_filtering.py
from agent.nodes.phase6_filtering import (
    generate_filter_list_node,
    apply_filter_to_tables_node,
)


# =============================================================================
# Phase 7: Executive Summary Presentation (Step 21)
# =============================================================================

# Import actual implementation from phase7_powerpoint.py
from agent.nodes.phase7_powerpoint import (
    generate_powerpoint_node,
    select_chart_type,
    ChartType,
    SemanticHint,
    get_xl_chart_type,
    get_chart_type_description,
)


# =============================================================================
# Phase 8: Full Report Dashboard (Step 22)
# =============================================================================

# Import actual implementation from phase8_html_dashboard.py
from agent.nodes.phase8_html_dashboard import (
    generate_html_dashboard_node,
)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Phase 1
    "extract_spss_node",
    "transform_metadata_node",
    "filter_metadata_node",
    # Phase 2
    "generate_recoding_rules_node",
    "validate_recoding_rules_node",
    "review_recoding_rules_node",
    "generate_pspp_recoding_syntax_node",
    "execute_pspp_recoding_node",
    # Phase 3
    "generate_indicators_node",
    "validate_indicators_node",
    "review_indicators_node",
    # Phase 4
    "generate_table_specifications_node",
    "validate_table_specifications_node",
    "review_table_specifications_node",
    "generate_pspp_table_syntax_node",
    "generate_pspp_crosstabs_syntax_node",  # Alternative CROSSTABS implementation
    "execute_pspp_tables_node",  # Primary CTABLES implementation
    "execute_pspp_crosstabs_node",  # Alternative CROSSTABS implementation
    # Phase 5
    "generate_python_statistics_script_node",
    "execute_python_statistics_script_node",
    # Phase 6
    "generate_filter_list_node",
    "apply_filter_to_tables_node",
    # Phase 7
    "generate_powerpoint_node",
    "select_chart_type",
    "ChartType",
    "SemanticHint",
    "get_xl_chart_type",
    "get_chart_type_description",
    # Phase 8
    "generate_html_dashboard_node",
]
