"""
Main LangGraph workflow construction.

Builds the LangGraph StateGraph for the survey analysis workflow.
Implements the explicit node pattern (no factory functions).
"""

from langgraph.graph import StateGraph, START, END
from typing import Any

from .state import State
from .nodes import (
    # Recoding nodes (Step 4)
    generate_recoding,
    validate_recoding,
    review_recoding,
    after_recoding_validation,
    after_recoding_review,
    # Indicator nodes (Step 8)
    generate_indicators,
    validate_indicators,
    review_indicators,
    after_indicators_validation,
    after_indicators_review,
    # Table specs nodes (Step 9)
    generate_table_specs,
    validate_table_specs,
    review_table_specs,
    after_table_specs_validation,
    after_table_specs_review,
)


def create_workflow() -> Any:
    """
    Create the LangGraph workflow for survey analysis.

    This function builds a StateGraph that implements the three-node pattern
    for Steps 4, 8, and 9 (recoding, indicators, table specifications).

    The workflow uses explicit node definitions and conditional edges
    to control flow between generate → validate → review nodes.

    Returns:
        Compiled LangGraph workflow
    """
    # Create the state graph
    workflow = StateGraph(State)

    # ========================================================================
    # ADD ALL NODES EXPLICITLY
    # ========================================================================

    # Step 4: Recoding Rules (Three-Node Pattern)
    workflow.add_node("generate_recoding", generate_recoding)
    workflow.add_node("validate_recoding", validate_recoding)
    workflow.add_node("review_recoding", review_recoding)

    # Step 8: Indicators (Three-Node Pattern)
    workflow.add_node("generate_indicators", generate_indicators)
    workflow.add_node("validate_indicators", validate_indicators)
    workflow.add_node("review_indicators", review_indicators)

    # Step 9: Table Specifications (Three-Node Pattern)
    workflow.add_node("generate_table_specs", generate_table_specs)
    workflow.add_node("validate_table_specs", validate_table_specs)
    workflow.add_node("review_table_specs", review_table_specs)

    # ========================================================================
    # ADD EDGES EXPLICITLY
    # ========================================================================

    # Entry points (these would be connected to previous workflow steps)
    # For now, we start with recoding rules generation
    workflow.add_edge(START, "generate_recoding")

    # -----------------------------------------------------------------------
    # Step 4: Recoding Rules Flow
    # -----------------------------------------------------------------------
    # Generate → Validate
    workflow.add_edge("generate_recoding", "validate_recoding")

    # Validate → Review or Retry
    workflow.add_conditional_edges(
        "validate_recoding",
        after_recoding_validation,
        {
            "review_recoding": "review_recoding",
            "generate_recoding": "generate_recoding"
        }
    )

    # Review → END or Retry
    workflow.add_conditional_edges(
        "review_recoding",
        after_recoding_review,
        {
            "END": END,
            "generate_recoding": "generate_recoding"
        }
    )

    # -----------------------------------------------------------------------
    # Step 8: Indicators Flow
    # -----------------------------------------------------------------------
    # Entry: Connect from previous step (would be Step 7 in full workflow)
    # For standalone testing, we can add a separate start or connect from recoding END
    # workflow.add_edge("review_recoding", "generate_indicators")  # Uncomment for full workflow

    # Generate → Validate
    workflow.add_edge("generate_indicators", "validate_indicators")

    # Validate → Review or Retry
    workflow.add_conditional_edges(
        "validate_indicators",
        after_indicators_validation,
        {
            "review_indicators": "review_indicators",
            "generate_indicators": "generate_indicators"
        }
    )

    # Review → END or Retry
    workflow.add_conditional_edges(
        "review_indicators",
        after_indicators_review,
        {
            "END": END,
            "generate_indicators": "generate_indicators"
        }
    )

    # -----------------------------------------------------------------------
    # Step 9: Table Specifications Flow
    # -----------------------------------------------------------------------
    # Entry: Connect from previous step (would be Step 8 approval in full workflow)
    # workflow.add_edge("review_indicators", "generate_table_specs")  # Uncomment for full workflow

    # Generate → Validate
    workflow.add_edge("generate_table_specs", "validate_table_specs")

    # Validate → Review or Retry
    workflow.add_conditional_edges(
        "validate_table_specs",
        after_table_specs_validation,
        {
            "review_table_specs": "review_table_specs",
            "generate_table_specs": "generate_table_specs"
        }
    )

    # Review → END or Retry
    workflow.add_conditional_edges(
        "review_table_specs",
        after_table_specs_review,
        {
            "END": END,
            "generate_table_specs": "generate_table_specs"
        }
    )

    # ========================================================================
    # COMPILE WORKFLOW
    # ========================================================================
    app = workflow.compile()

    return app


# ============================================================================
# WORKFLOW VISUALIZATION (for documentation)
# ============================================================================

def get_workflow_structure() -> str:
    """
    Return a text representation of the workflow structure.

    Useful for documentation and debugging.
    """
    return """
Survey Analysis LangGraph Workflow Structure
=============================================

Step 4: Recoding Rules (Three-Node Pattern)
-------------------------------------------
┌─────────────────┐
│  generate_      │
│  recoding       │
│  (LLM)          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  validate_      │     ┌──────────────┐
│  recoding       │────▶│ review_      │◀────────────┐
│  (Python)       │     │ recoding     │             │
└─────────────────┘     │ (Human)      │             │
                        └──────┬───────┘             │
                               │                     │
                               ▼                     │
                         ┌─────────┐               │
                         │   END   │               │
                         └─────────┘               │
                                                  │
                               ┌───────────────────┘
                               │
                               ▼
                        (retry on rejection)

Step 8: Indicators (Three-Node Pattern)
----------------------------------------
┌─────────────────┐
│  generate_      │
│  indicators     │
│  (LLM)          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│  validate_      │────▶│ review_      │◀────────────┐
│  indicators     │     │ indicators   │             │
│  (Python)       │     │ (Human)      │             │
└─────────────────┘     └──────┬───────┘             │
                               │                     │
                               ▼                     │
                         ┌─────────┐               │
                         │   END   │               │
                         └─────────┘               │
                                                  │
                               ┌───────────────────┘
                               │
                               ▼
                        (retry on rejection)

Step 9: Table Specifications (Three-Node Pattern)
--------------------------------------------------
┌─────────────────┐
│  generate_      │
│  table_specs    │
│  (LLM)          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│  validate_      │────▶│ review_      │◀────────────┐
│  table_specs    │     │ table_specs  │             │
│  (Python)       │     │ (Human)      │             │
└─────────────────┘     └──────┬───────┘             │
                               │                     │
                               ▼                     │
                         ┌─────────┐               │
                         │   END   │               │
                         └─────────┘               │
                                                  │
                               ┌───────────────────┘
                               │
                               ▼
                        (retry on rejection)

Notes:
------
- Each step follows the same three-node pattern: Generate → Validate → Review
- Conditional edges control routing based on validation results and human decisions
- Max iterations = 3 to prevent infinite loops
- Human review uses LangGraph's interrupt() mechanism
- Auto-approval can be enabled via config
"""
