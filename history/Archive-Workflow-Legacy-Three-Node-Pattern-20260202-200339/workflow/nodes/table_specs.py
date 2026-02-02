"""
Nodes for Step 9: Generate Table Specifications (Three-Node Pattern)

Implements the LangGraph three-node pattern:
1. Generate: LLM defines cross-table structure
2. Validate: Python validates table specs
3. Review: Human reviews table specs (optional)
"""

import json
from typing import Literal
from langgraph.types import interrupt

from ..state import State
from ..validators import TableSpecsValidator
from ..prompts import (
    build_initial_table_specs_prompt,
    build_table_specs_validation_retry_prompt,
    build_table_specs_human_feedback_prompt,
)


# ============================================================================
# NODE 1: GENERATE
# ============================================================================

def generate_table_specs(state: State) -> State:
    """
    Generate table specifications using LLM.

    Defines cross-tabulation table structure (rows, columns, weighting).

    Args:
        state: Current workflow state

    Returns:
        Updated state with generated table specifications
    """
    iteration = state["table_specs_iteration"]
    feedback = state["table_specs_feedback"]
    feedback_source = state["table_specs_feedback_source"]

    # Build prompt based on feedback source
    if feedback_source == "validation" and feedback:
        prompt = build_table_specs_validation_retry_prompt(
            indicators=state["indicators"].get("indicators", []),
            metadata=state["variable_centered_metadata"],
            validation_result=feedback,
            iteration=iteration
        )
    elif feedback_source == "human" and feedback:
        prompt = build_table_specs_human_feedback_prompt(
            indicators=state["indicators"].get("indicators", []),
            metadata=state["variable_centered_metadata"],
            human_feedback=feedback,
            previous_specs=state["table_specifications"],
            iteration=iteration
        )
    else:
        prompt = build_initial_table_specs_prompt(
            indicators=state["indicators"].get("indicators", []),
            metadata=state["variable_centered_metadata"]
        )

    # TODO: Call LLM here
    response = _mock_llm_response_table_specs(prompt)

    # Parse LLM response
    try:
        table_specs = _parse_table_specs_response(response)
    except Exception as e:
        return {
            **state,
            "table_specifications": None,
            "messages": [
                *state["messages"],
                {"role": "error", "content": f"Failed to parse LLM response: {e}"}
            ]
        }

    return {
        **state,
        "table_specifications": table_specs,
        "table_specs_iteration": iteration + 1,
        "table_specs_feedback": None,
        "table_specs_feedback_source": None,
        "messages": [
            *state["messages"],
            {
                "role": "assistant",
                "content": f"Generated table specifications (iteration {iteration})"
            }
        ]
    }


# ============================================================================
# NODE 2: VALIDATE
# ============================================================================

def validate_table_specs(state: State) -> State:
    """
    Validate table specifications using Python.

    Runs validation checks on the generated table specs.

    Args:
        state: Current workflow state

    Returns:
        Updated state with validation results
    """
    if state["table_specifications"] is None:
        return {
            **state,
            "table_specs_validation": {
                "is_valid": False,
                "errors": ["No table specifications generated"],
                "warnings": [],
                "checks_performed": []
            }
        }

    validator = TableSpecsValidator(
        metadata=state["variable_centered_metadata"],
        indicators=state["indicators"].get("indicators", [])
    )
    validation_result = validator.validate(state["table_specifications"])

    validation_dict = {
        "is_valid": validation_result.is_valid,
        "errors": validation_result.errors,
        "warnings": validation_result.warnings,
        "checks_performed": validation_result.checks_performed
    }

    return {
        **state,
        "table_specs_validation": validation_dict,
        "messages": [
            *state["messages"],
            {
                "role": "system",
                "content": f"Validation: {len(validation_result.errors)} errors, "
                          f"{len(validation_result.warnings)} warnings"
            }
        ]
    }


# ============================================================================
# NODE 3: REVIEW
# ============================================================================

def review_table_specs(state: State) -> State:
    """
    Review table specifications with human input.

    Uses LangGraph's interrupt() for human approval.

    Args:
        state: Current workflow state

    Returns:
        Updated state with human feedback
    """
    if state["config"].get("auto_approve_table_specs", False):
        return {
            **state,
            "table_specs_approved": True,
            "table_specs_feedback": None,
            "messages": [
                *state["messages"],
                {"role": "system", "content": "Table specifications auto-approved"}
            ]
        }

    report = _generate_table_specs_review_report(
        state["table_specifications"],
        state["table_specs_validation"]
    )

    human_input = interrupt({
        "type": "approval_required",
        "task": "table_specs",
        "report": report,
        "validation": state["table_specs_validation"],
        "options": ["approve", "reject", "modify"],
        "message": "Please review the table specifications and provide your decision"
    })

    decision = human_input.get("decision", "approve")
    comments = human_input.get("comments", "")
    modified_specs = human_input.get("modified_table_specs")

    feedback = {
        "decision": decision,
        "comments": comments
    }

    if decision == "approve":
        return {
            **state,
            "table_specs_approved": True,
            "table_specs_feedback": None,
            "approval_comments": [
                *state["approval_comments"],
                {
                    "step": "table_specs",
                    "decision": "approved",
                    "comments": comments
                }
            ],
            "messages": [
                *state["messages"],
                {"role": "human", "content": f"Approved: {comments}"}
            ]
        }
    elif decision == "modify" and modified_specs:
        return {
            **state,
            "table_specifications": modified_specs,
            "table_specs_approved": True,
            "table_specs_feedback": None,
            "approval_comments": [
                *state["approval_comments"],
                {
                    "step": "table_specs",
                    "decision": "modified",
                    "comments": comments
                }
            ],
            "messages": [
                *state["messages"],
                {"role": "human", "content": f"Modified: {comments}"}
            ]
        }
    else:  # reject
        return {
            **state,
            "table_specs_approved": False,
            "table_specs_feedback": feedback,
            "table_specs_feedback_source": "human",
            "approval_comments": [
                *state["approval_comments"],
                {
                    "step": "table_specs",
                    "decision": "rejected",
                    "comments": comments
                }
            ],
            "messages": [
                *state["messages"],
                {"role": "human", "content": f"Rejected: {comments}"}
            ]
        }


# ============================================================================
# EDGE FUNCTIONS
# ============================================================================

def after_table_specs_validation(state: State) -> Literal["review_table_specs", "generate_table_specs"]:
    """Route after validation."""
    validation = state["table_specs_validation"]
    iteration = state["table_specs_iteration"]
    max_iterations = state["config"].get("max_iterations", 3)

    if validation.get("is_valid", False) or iteration >= max_iterations:
        return "review_table_specs"

    return "generate_table_specs"


def after_table_specs_review(state: State) -> Literal["END", "generate_table_specs"]:
    """Route after human review."""
    if state["table_specs_approved"]:
        return "END"

    iteration = state["table_specs_iteration"]
    max_iterations = state["config"].get("max_iterations", 3)

    if iteration >= max_iterations:
        return "END"

    return "generate_table_specs"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _mock_llm_response_table_specs(prompt: str) -> str:
    """Mock LLM response for testing."""
    return json.dumps({
        "tables": [
            {
                "id": "TABLE_001",
                "description": "Age by Gender",
                "row_indicators": ["IND_001"],
                "column_indicators": ["IND_002"],
                "sort_rows": "none",
                "sort_columns": "none",
                "min_count": 30
            }
        ],
        "weighting_variable": None
    })


def _parse_table_specs_response(response: str) -> dict:
    """Parse LLM response into table specifications."""
    try:
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            json_str = response[json_start:json_end].strip()
        elif "```" in response:
            json_start = response.find("```") + 3
            json_end = response.find("```", json_start)
            json_str = response[json_start:json_end].strip()
        else:
            json_str = response.strip()

        return json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Failed to parse LLM response: {e}")


def _generate_table_specs_review_report(
    table_specs: dict,
    validation: dict
) -> str:
    """Generate a human-readable review report."""
    lines = ["# Table Specifications Review Report\n"]

    # Summary
    tables = table_specs.get("tables", [])
    lines.append("## Summary")
    lines.append(f"- Total Tables: {len(tables)}")
    lines.append(f"- Weighting Variable: {table_specs.get('weighting_variable', 'None')}\n")

    # Tables
    lines.append("## Tables for Review\n")
    for table in tables:
        lines.append(f"### {table.get('id')}: {table.get('description')}")
        lines.append(f"- **Row Indicators**: {', '.join(table.get('row_indicators', []))}")
        lines.append(f"- **Column Indicators**: {', '.join(table.get('column_indicators', []))}")
        lines.append(f"- **Sort Rows**: {table.get('sort_rows', 'none')}")
        lines.append(f"- **Sort Columns**: {table.get('sort_columns', 'none')}")
        lines.append(f"- **Min Count**: {table.get('min_count', 30)}")
        lines.append("")

    # Validation
    if validation.get("errors"):
        lines.append("## Validation Errors")
        for error in validation["errors"]:
            lines.append(f"- ❌ {error}")
        lines.append("")

    return "\n".join(lines)
