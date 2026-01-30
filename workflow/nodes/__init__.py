"""
LangGraph nodes for the survey analysis workflow.

This package provides node implementations for all workflow steps.
Each AI-powered step (4, 8, 9) follows the three-node pattern:
- Generate: LLM creates output
- Validate: Python validates output
- Review: Human reviews output (optional)
"""

from .recoding import (
    generate_recoding,
    validate_recoding,
    review_recoding,
    after_recoding_validation,
    after_recoding_review,
)
from .indicators import (
    generate_indicators,
    validate_indicators,
    review_indicators,
    after_indicators_validation,
    after_indicators_review,
)
from .table_specs import (
    generate_table_specs,
    validate_table_specs,
    review_table_specs,
    after_table_specs_validation,
    after_table_specs_review,
)
from .presentation import (
    generate_powerpoint,
)

__all__ = [
    # Recoding nodes (Step 4)
    "generate_recoding",
    "validate_recoding",
    "review_recoding",
    "after_recoding_validation",
    "after_recoding_review",
    # Indicator nodes (Step 8)
    "generate_indicators",
    "validate_indicators",
    "review_indicators",
    "after_indicators_validation",
    "after_indicators_review",
    # Table specs nodes (Step 9)
    "generate_table_specs",
    "validate_table_specs",
    "review_table_specs",
    "after_table_specs_validation",
    "after_table_specs_review",
    # Presentation nodes (Phase 7: Step 21)
    "generate_powerpoint",
]
