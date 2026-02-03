"""
Conditional Edge Routing Functions for Survey Analysis Workflow

This module defines routing functions for conditional edges in the LangGraph.
These functions implement the three-node pattern feedback loops for:
- Recoding rules (Steps 4-6)
- Indicators (Steps 9-11)
- Table specifications (Steps 12-14)

Each routing function examines the validation result and approval status
to determine whether to proceed, retry, or request human review.

Routing Logic:
- If validation fails AND iteration_count < max_iterations → Route back to generate node (retry)
- If validation fails AND iteration_count >= max_iterations → Route to review node (force human review)
- If validation passes but not approved → Route to review node (human input)
- If approved → Route to next phase node (proceed)

The max_iterations limit prevents infinite retry loops and forces human
intervention when automatic self-correction fails.
"""

from typing import Literal
from agent.state import WorkflowState
from agent.config import DEFAULT_CONFIG


# =============================================================================
# Routing Function Return Types
# =============================================================================

# Step 5 (validate_recoding_rules) routing
RecodingRoute = Literal[
    "generate_recoding_rules_node",  # Retry: validation failed or human rejected
    "review_recoding_rules_node",     # Review: validation passed, needs human approval
    "generate_pspp_recoding_syntax_node",  # Proceed: approved
]

# Step 10 (validate_indicators) routing
IndicatorRoute = Literal[
    "generate_indicators_node",       # Retry: validation failed or human rejected
    "review_indicators_node",         # Review: validation passed, needs human approval
    "generate_table_specifications_node",  # Proceed: approved
]

# Step 13 (validate_table_specifications) routing
TableSpecsRoute = Literal[
    "generate_table_specifications_node",  # Retry: validation failed or human rejected
    "review_table_specifications_node",    # Review: validation passed, needs human approval
    "generate_pspp_table_syntax_node",     # Proceed: approved
]


# =============================================================================
# Recoding Rules Routing (Steps 4-6)
# =============================================================================

def should_retry_recoding(state: WorkflowState) -> RecodingRoute:
    """
    Routing function after validate_recoding_rules_node (Step 5).

    Determines the next step based on validation result, iteration count, and approval status:
    - If validation failed AND iteration_count < max_iterations → retry generation
    - If validation failed AND iteration_count >= max_iterations → go to review (force human)
    - If validation passed but not approved → go to review
    - If approved → proceed to PSPP syntax generation

    The max_iterations check prevents infinite retry loops when automatic
    validation consistently fails, forcing human intervention for manual correction.

    Args:
        state: Current workflow state

    Returns:
        String name of next node to execute

    Flow:
        validate_recoding_rules_node (Step 5)
            ↓ (validation failed AND iterations < max)
            generate_recoding_rules_node (Step 4) [RETRY]
            ↓ (validation failed OR iterations >= max, not approved)
            review_recoding_rules_node (Step 6)
            ↓ (approved)
            generate_pspp_recoding_syntax_node (Step 7) [PROCEED]
    """
    # Get max_iterations from config
    max_iterations = state.get("config", DEFAULT_CONFIG).get("max_self_correction_iterations", 3)
    iteration_count = state.get("iteration_count", 0)

    # Check if validation failed
    validation_result = state.get("recoding_validation_result")
    if validation_result and not validation_result['is_valid']:
        # Retry if we haven't exceeded max iterations
        if iteration_count < max_iterations:
            return "generate_recoding_rules_node"
        # Force human review if max iterations reached
        return "review_recoding_rules_node"

    # Check if already approved (e.g., auto-approved or previously approved)
    if state.get("recoding_approved", False):
        return "generate_pspp_recoding_syntax_node"

    # Check if human review is required
    # If validation passed but not approved, go to review
    if state.get("requires_human_review", False):
        return "review_recoding_rules_node"

    # Default: go to review for human approval
    return "review_recoding_rules_node"


def should_approve_recoding(state: WorkflowState) -> RecodingRoute:
    """
    Routing function after review_recoding_rules_node (Step 6).

    Determines the next step based on human approval:
    - If approved → proceed to PSPP syntax generation
    - If rejected → retry generation with feedback

    When human rejects the artifact, feedback is captured in recoding_feedback
    and the next generate node uses this feedback to improve the artifact.

    Args:
        state: Current workflow state

    Returns:
        String name of next node to execute

    Flow:
        review_recoding_rules_node (Step 6)
            ↓ (approved)
            generate_pspp_recoding_syntax_node (Step 7) [PROCEED]
            ↓ (rejected with feedback)
            generate_recoding_rules_node (Step 4) [RETRY]
    """
    # Check if approved
    if state.get("recoding_approved", False):
        return "generate_pspp_recoding_syntax_node"

    # Rejected with feedback - retry
    return "generate_recoding_rules_node"


# =============================================================================
# Indicators Routing (Steps 9-11)
# =============================================================================

def should_retry_indicators(state: WorkflowState) -> IndicatorRoute:
    """
    Routing function after validate_indicators_node (Step 10).

    Determines the next step based on validation result, iteration count, and approval status:
    - If validation failed AND iteration_count < max_iterations → retry generation
    - If validation failed AND iteration_count >= max_iterations → go to review (force human)
    - If validation passed but not approved → go to review
    - If approved → proceed to table specifications

    The max_iterations check prevents infinite retry loops when automatic
    validation consistently fails, forcing human intervention for manual correction.

    Args:
        state: Current workflow state

    Returns:
        String name of next node to execute

    Flow:
        validate_indicators_node (Step 10)
            ↓ (validation failed AND iterations < max)
            generate_indicators_node (Step 9) [RETRY]
            ↓ (validation failed OR iterations >= max, not approved)
            review_indicators_node (Step 11)
            ↓ (approved)
            generate_table_specifications_node (Step 12) [PROCEED]
    """
    # Get max_iterations from config
    max_iterations = state.get("config", DEFAULT_CONFIG).get("max_self_correction_iterations", 3)
    iteration_count = state.get("iteration_count", 0)

    # Check if validation failed
    validation_result = state.get("indicator_validation_result")
    if validation_result and not validation_result['is_valid']:
        # Retry if we haven't exceeded max iterations
        if iteration_count < max_iterations:
            return "generate_indicators_node"
        # Force human review if max iterations reached
        return "review_indicators_node"

    # Check if already approved
    if state.get("indicators_approved", False):
        return "generate_table_specifications_node"

    # Check if human review is required
    if state.get("requires_human_review", False):
        return "review_indicators_node"

    # Default: go to review
    return "review_indicators_node"


def should_approve_indicators(state: WorkflowState) -> IndicatorRoute:
    """
    Routing function after review_indicators_node (Step 11).

    Determines the next step based on human approval:
    - If approved → proceed to table specifications
    - If rejected → retry generation with feedback

    When human rejects the artifact, feedback is captured in indicator_feedback
    and the next generate node uses this feedback to improve the artifact.

    Args:
        state: Current workflow state

    Returns:
        String name of next node to execute

    Flow:
        review_indicators_node (Step 11)
            ↓ (approved)
            generate_table_specifications_node (Step 12) [PROCEED]
            ↓ (rejected with feedback)
            generate_indicators_node (Step 9) [RETRY]
    """
    # Check if approved
    if state.get("indicators_approved", False):
        return "generate_table_specifications_node"

    # Rejected with feedback - retry
    return "generate_indicators_node"


# =============================================================================
# Table Specifications Routing (Steps 12-14)
# =============================================================================

def should_retry_table_specs(state: WorkflowState) -> TableSpecsRoute:
    """
    Routing function after validate_table_specifications_node (Step 13).

    Determines the next step based on validation result, iteration count, and approval status:
    - If validation failed AND iteration_count < max_iterations → retry generation
    - If validation failed AND iteration_count >= max_iterations → go to review (force human)
    - If validation passed but not approved → go to review
    - If approved → proceed to PSPP syntax generation

    The max_iterations check prevents infinite retry loops when automatic
    validation consistently fails, forcing human intervention for manual correction.

    Args:
        state: Current workflow state

    Returns:
        String name of next node to execute

    Flow:
        validate_table_specifications_node (Step 13)
            ↓ (validation failed AND iterations < max)
            generate_table_specifications_node (Step 12) [RETRY]
            ↓ (validation failed OR iterations >= max, not approved)
            review_table_specifications_node (Step 14)
            ↓ (approved)
            generate_pspp_table_syntax_node (Step 15) [PROCEED]
    """
    # Get max_iterations from config
    max_iterations = state.get("config", DEFAULT_CONFIG).get("max_self_correction_iterations", 3)
    iteration_count = state.get("iteration_count", 0)

    # Check if validation failed
    validation_result = state.get("table_validation_result")
    if validation_result and not validation_result['is_valid']:
        # Retry if we haven't exceeded max iterations
        if iteration_count < max_iterations:
            return "generate_table_specifications_node"
        # Force human review if max iterations reached
        return "review_table_specifications_node"

    # Check if already approved
    if state.get("table_specs_approved", False):
        return "generate_pspp_table_syntax_node"

    # Check if human review is required
    if state.get("requires_human_review", False):
        return "review_table_specifications_node"

    # Default: go to review
    return "review_table_specifications_node"


def should_approve_table_specs(state: WorkflowState) -> TableSpecsRoute:
    """
    Routing function after review_table_specifications_node (Step 14).

    Determines the next step based on human approval:
    - If approved → proceed to PSPP syntax generation
    - If rejected → retry generation with feedback

    When human rejects the artifact, feedback is captured in table_specs_feedback
    and the next generate node uses this feedback to improve the artifact.

    Args:
        state: Current workflow state

    Returns:
        String name of next node to execute

    Flow:
        review_table_specifications_node (Step 14)
            ↓ (approved)
            generate_pspp_table_syntax_node (Step 15) [PROCEED]
            ↓ (rejected with feedback)
            generate_table_specifications_node (Step 12) [RETRY]
    """
    # Check if approved
    if state.get("table_specs_approved", False):
        return "generate_pspp_table_syntax_node"

    # Rejected with feedback - retry
    return "generate_table_specifications_node"


# =============================================================================
# Edge Mapping Dictionaries
# =============================================================================

# Mapping for recoding rules conditional edges
RECODING_EDGE_MAPPING = {
    "generate_recoding_rules_node": "generate_recoding_rules_node",
    "review_recoding_rules_node": "review_recoding_rules_node",
    "generate_pspp_recoding_syntax_node": "generate_pspp_recoding_syntax_node",
}

# Mapping for indicators conditional edges
INDICATOR_EDGE_MAPPING = {
    "generate_indicators_node": "generate_indicators_node",
    "review_indicators_node": "review_indicators_node",
    "generate_table_specifications_node": "generate_table_specifications_node",
}

# Mapping for table specifications conditional edges
TABLE_SPECS_EDGE_MAPPING = {
    "generate_table_specifications_node": "generate_table_specifications_node",
    "review_table_specifications_node": "review_table_specifications_node",
    "generate_pspp_table_syntax_node": "generate_pspp_table_syntax_node",
}
