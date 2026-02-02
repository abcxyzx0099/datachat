"""
Nodes for Step 8: Generate Indicators (Three-Node Pattern)

Implements the LangGraph three-node pattern:
1. Generate: LLM groups variables into indicators
2. Validate: Python validates indicators
3. Review: Human reviews indicators (optional)
"""

import json
from typing import Literal
from langgraph.types import interrupt

from ..state import State
from ..validators import IndicatorValidator
from ..prompts import (
    build_initial_indicators_prompt,
    build_indicators_validation_retry_prompt,
    build_indicators_human_feedback_prompt,
)


# ============================================================================
# NODE 1: GENERATE
# ============================================================================

def generate_indicators(state: State) -> State:
    """
    Generate indicators using LLM.

    Groups variables into semantic indicators for analysis.

    Args:
        state: Current workflow state

    Returns:
        Updated state with generated indicators
    """
    iteration = state["indicators_iteration"]
    feedback = state["indicators_feedback"]
    feedback_source = state["indicators_feedback_source"]

    # Build prompt based on feedback source
    if feedback_source == "validation" and feedback:
        prompt = build_indicators_validation_retry_prompt(
            metadata=state["variable_centered_metadata"],
            validation_result=feedback,
            iteration=iteration
        )
    elif feedback_source == "human" and feedback:
        prompt = build_indicators_human_feedback_prompt(
            metadata=state["variable_centered_metadata"],
            human_feedback=feedback,
            previous_indicators=state["indicators"].get("indicators", []),
            iteration=iteration
        )
    else:
        prompt = build_initial_indicators_prompt(
            metadata=state["variable_centered_metadata"]
        )

    # TODO: Call LLM here
    response = _mock_llm_response_indicators(prompt)

    # Parse LLM response
    try:
        indicators = _parse_indicators_response(response)
    except Exception as e:
        return {
            **state,
            "indicators": None,
            "messages": [
                *state["messages"],
                {"role": "error", "content": f"Failed to parse LLM response: {e}"}
            ]
        }

    return {
        **state,
        "indicators": indicators,
        "indicators_iteration": iteration + 1,
        "indicators_feedback": None,
        "indicators_feedback_source": None,
        "messages": [
            *state["messages"],
            {
                "role": "assistant",
                "content": f"Generated indicators (iteration {iteration})"
            }
        ]
    }


# ============================================================================
# NODE 2: VALIDATE
# ============================================================================

def validate_indicators(state: State) -> State:
    """
    Validate indicators using Python.

    Runs validation checks on the generated indicators.

    Args:
        state: Current workflow state

    Returns:
        Updated state with validation results
    """
    if state["indicators"] is None:
        return {
            **state,
            "indicators_validation": {
                "is_valid": False,
                "errors": ["No indicators generated"],
                "warnings": [],
                "checks_performed": []
            }
        }

    validator = IndicatorValidator(state["variable_centered_metadata"])
    indicators = state["indicators"].get("indicators", [])
    validation_result = validator.validate(indicators)

    validation_dict = {
        "is_valid": validation_result.is_valid,
        "errors": validation_result.errors,
        "warnings": validation_result.warnings,
        "checks_performed": validation_result.checks_performed
    }

    return {
        **state,
        "indicators_validation": validation_dict,
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

def review_indicators(state: State) -> State:
    """
    Review indicators with human input.

    Uses LangGraph's interrupt() for human approval.

    Args:
        state: Current workflow state

    Returns:
        Updated state with human feedback
    """
    if state["config"].get("auto_approve_indicators", False):
        return {
            **state,
            "indicators_approved": True,
            "indicators_feedback": None,
            "messages": [
                *state["messages"],
                {"role": "system", "content": "Indicators auto-approved"}
            ]
        }

    report = _generate_indicators_review_report(
        state["indicators"],
        state["indicators_validation"]
    )

    human_input = interrupt({
        "type": "approval_required",
        "task": "indicators",
        "report": report,
        "validation": state["indicators_validation"],
        "options": ["approve", "reject", "modify"],
        "message": "Please review the indicator groupings and provide your decision"
    })

    decision = human_input.get("decision", "approve")
    comments = human_input.get("comments", "")
    modified_indicators = human_input.get("modified_indicators")

    feedback = {
        "decision": decision,
        "comments": comments
    }

    if decision == "approve":
        return {
            **state,
            "indicators_approved": True,
            "indicators_feedback": None,
            "approval_comments": [
                *state["approval_comments"],
                {
                    "step": "indicators",
                    "decision": "approved",
                    "comments": comments
                }
            ],
            "messages": [
                *state["messages"],
                {"role": "human", "content": f"Approved: {comments}"}
            ]
        }
    elif decision == "modify" and modified_indicators:
        return {
            **state,
            "indicators": modified_indicators,
            "indicators_approved": True,
            "indicators_feedback": None,
            "approval_comments": [
                *state["approval_comments"],
                {
                    "step": "indicators",
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
            "indicators_approved": False,
            "indicators_feedback": feedback,
            "indicators_feedback_source": "human",
            "approval_comments": [
                *state["approval_comments"],
                {
                    "step": "indicators",
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

def after_indicators_validation(state: State) -> Literal["review_indicators", "generate_indicators"]:
    """Route after validation."""
    validation = state["indicators_validation"]
    iteration = state["indicators_iteration"]
    max_iterations = state["config"].get("max_iterations", 3)

    if validation.get("is_valid", False) or iteration >= max_iterations:
        return "review_indicators"

    return "generate_indicators"


def after_indicators_review(state: State) -> Literal["END", "generate_indicators"]:
    """Route after human review."""
    if state["indicators_approved"]:
        return "END"

    iteration = state["indicators_iteration"]
    max_iterations = state["config"].get("max_iterations", 3)

    if iteration >= max_iterations:
        return "END"

    return "generate_indicators"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _mock_llm_response_indicators(prompt: str) -> str:
    """Mock LLM response for testing."""
    return json.dumps({
        "indicators": [
            {
                "id": "IND_001",
                "description": "Respondent age distribution",
                "metric": "distribution",
                "underlying_variables": ["age_group"]
            },
            {
                "id": "IND_002",
                "description": "Gender distribution",
                "metric": "distribution",
                "underlying_variables": ["gender"]
            }
        ]
    })


def _parse_indicators_response(response: str) -> dict:
    """Parse LLM response into indicators."""
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


def _generate_indicators_review_report(
    indicators: dict,
    validation: dict
) -> str:
    """Generate a human-readable review report."""
    lines = ["# Indicators Review Report\n"]

    # Summary
    inds = indicators.get("indicators", [])
    lines.append("## Summary")
    lines.append(f"- Total Indicators: {len(inds)}")
    lines.append(f"- Single-variable: {sum(1 for i in inds if len(i.get('underlying_variables', [])) == 1)}")
    lines.append(f"- Multi-variable: {sum(1 for i in inds if len(i.get('underlying_variables', [])) > 1)}\n")

    # Indicators
    lines.append("## Indicators for Review\n")
    for ind in inds:
        lines.append(f"### {ind.get('id')}: {ind.get('description')}")
        lines.append(f"- **Metric**: {ind.get('metric')}")
        lines.append(f"- **Variables**: {', '.join(ind.get('underlying_variables', []))}")
        lines.append("")

    # Validation
    if validation.get("errors"):
        lines.append("## Validation Errors")
        for error in validation["errors"]:
            lines.append(f"- ❌ {error}")
        lines.append("")

    return "\n".join(lines)
