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
    step_name = {
        "extract_spss_node": "step_1_extract_spss",
        "transform_metadata_node": "step_2_transform_metadata",
        "filter_metadata_node": "step_3_filter_metadata",
        "generate_recoding_rules_node": "step_4_generate_recoding_rules",
        "validate_recoding_rules_node": "step_5_validate_recoding_rules",
        "review_recoding_rules_node": "step_6_review_recoding_rules",
        "generate_pspp_recoding_syntax_node": "step_7_generate_pspp_recoding_syntax",
        "execute_pspp_recoding_node": "step_8_execute_pspp_recoding",
        "generate_indicators_node": "step_9_generate_indicators",
        "validate_indicators_node": "step_10_validate_indicators",
        "review_indicators_node": "step_11_review_indicators",
        "generate_table_specifications_node": "step_12_generate_table_specifications",
        "validate_table_specifications_node": "step_13_validate_table_specifications",
        "review_table_specifications_node": "step_14_review_table_specifications",
        "generate_pspp_table_syntax_node": "step_15_generate_pspp_table_syntax",
        "execute_pspp_tables_node": "step_16_execute_pspp_tables",
        "generate_python_statistics_script_node": "step_17_generate_statistics_script",
        "execute_python_statistics_script_node": "step_18_execute_statistics_script",
        "generate_filter_list_node": "step_19_generate_filter_list",
        "apply_filter_to_tables_node": "step_20_apply_filter_to_tables",
        "generate_powerpoint_node": "step_21_generate_powerpoint",
        "generate_html_dashboard_node": "step_22_generate_html_dashboard",
    }.get(node_name, "step_0_initial")

    state["current_step"] = step_name
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
