"""
Nodes for Step 4: Generate Recoding Rules (Three-Node Pattern)

Implements the LangGraph three-node pattern:
1. Generate: LLM creates recoding rules
2. Validate: Python validates rules
3. Review: Human reviews rules (optional)
"""

import json
from typing import Literal, Dict, Any
from langgraph.types import interrupt

from ..state import State
from ..validators import RecodingValidator
from ..prompts import (
    build_initial_recoding_prompt,
    build_recoding_validation_retry_prompt,
    build_recoding_human_feedback_prompt,
)


# ============================================================================
# NODE 1: GENERATE
# ============================================================================

def generate_recoding(state: State) -> State:
    """
    Generate recoding rules using LLM.

    This is the first node in the three-node pattern. It calls the LLM
    to generate recoding rules based on variable metadata.

    Args:
        state: Current workflow state

    Returns:
        Updated state with generated recoding rules
    """
    iteration = state["recoding_iteration"]
    feedback = state["recoding_feedback"]
    feedback_source = state["recoding_feedback_source"]

    # Build prompt based on feedback source
    if feedback_source == "validation" and feedback:
        # Retry after validation failure
        prompt = build_recoding_validation_retry_prompt(
            metadata=state["filtered_metadata"],
            validation_result=feedback,
            iteration=iteration
        )
    elif feedback_source == "human" and feedback:
        # Retry after human rejection
        prompt = build_recoding_human_feedback_prompt(
            metadata=state["filtered_metadata"],
            human_feedback=feedback,
            previous_rules=state["recoding_rules"].get("recoding_rules", []),
            iteration=iteration
        )
    else:
        # Initial generation
        prompt = build_initial_recoding_prompt(
            metadata=state["filtered_metadata"]
        )

    # TODO: Call LLM here
    # For now, we'll create a placeholder
    # In production, you would use: response = llm.invoke(prompt)
    response = _mock_llm_response(prompt)

    # Parse LLM response
    try:
        recoding_rules = _parse_recoding_response(response)
    except Exception as e:
        # If parsing fails, create an error state
        return {
            **state,
            "recoding_rules": None,
            "messages": [
                *state["messages"],
                {"role": "error", "content": f"Failed to parse LLM response: {e}"}
            ]
        }

    # Update state
    return {
        **state,
        "recoding_rules": recoding_rules,
        "recoding_iteration": iteration + 1,
        "recoding_feedback": None,
        "recoding_feedback_source": None,
        "messages": [
            *state["messages"],
            {
                "role": "assistant",
                "content": f"Generated recoding rules (iteration {iteration})"
            }
        ]
    }


# ============================================================================
# NODE 2: VALIDATE
# ============================================================================

def validate_recoding(state: State) -> State:
    """
    Validate recoding rules using Python.

    This is the second node in the three-node pattern. It runs Python
    validation checks on the generated recoding rules.

    Args:
        state: Current workflow state

    Returns:
        Updated state with validation results
    """
    if state["recoding_rules"] is None:
        return {
            **state,
            "recoding_validation": {
                "is_valid": False,
                "errors": ["No recoding rules generated"],
                "warnings": [],
                "checks_performed": []
            }
        }

    # Create validator and validate
    validator = RecodingValidator(state["filtered_metadata"])
    rules = state["recoding_rules"].get("recoding_rules", [])
    validation_result = validator.validate(rules)

    # Convert to dict for state
    validation_dict = {
        "is_valid": validation_result.is_valid,
        "errors": validation_result.errors,
        "warnings": validation_result.warnings,
        "checks_performed": validation_result.checks_performed
    }

    return {
        **state,
        "recoding_validation": validation_dict,
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

def review_recoding(state: State) -> State:
    """
    Review recoding rules with human input.

    This is the third node in the three-node pattern. It uses LangGraph's
    interrupt() mechanism to pause execution and wait for human approval.

    Args:
        state: Current workflow state

    Returns:
        Updated state with human feedback
    """
    # Check if auto-approval is enabled
    if state["config"].get("auto_approve_recoding", False):
        return {
            **state,
            "recoding_rules_approved": True,
            "recoding_feedback": None,
            "messages": [
                *state["messages"],
                {"role": "system", "content": "Recoding rules auto-approved"}
            ]
        }

    # Create human-readable review report
    report = _generate_recoding_review_report(
        state["recoding_rules"],
        state["recoding_validation"]
    )

    # Use LangGraph interrupt to pause for human input
    human_input = interrupt({
        "type": "approval_required",
        "task": "recoding_rules",
        "report": report,
        "validation": state["recoding_validation"],
        "options": ["approve", "reject", "modify"],
        "message": "Please review the recoding rules and provide your decision"
    })

    # Process human decision
    decision = human_input.get("decision", "approve")
    comments = human_input.get("comments", "")
    modified_rules = human_input.get("modified_rules")

    feedback = {
        "decision": decision,
        "comments": comments
    }

    # Update state based on decision
    if decision == "approve":
        return {
            **state,
            "recoding_rules_approved": True,
            "recoding_feedback": None,
            "approval_comments": [
                *state["approval_comments"],
                {
                    "step": "recoding_rules",
                    "decision": "approved",
                    "comments": comments
                }
            ],
            "messages": [
                *state["messages"],
                {"role": "human", "content": f"Approved: {comments}"}
            ]
        }
    elif decision == "modify" and modified_rules:
        return {
            **state,
            "recoding_rules": modified_rules,
            "recoding_rules_approved": True,
            "recoding_feedback": None,
            "approval_comments": [
                *state["approval_comments"],
                {
                    "step": "recoding_rules",
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
            "recoding_rules_approved": False,
            "recoding_feedback": feedback,
            "recoding_feedback_source": "human",
            "approval_comments": [
                *state["approval_comments"],
                {
                    "step": "recoding_rules",
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

def after_recoding_validation(state: State) -> Literal["review_recoding", "generate_recoding"]:
    """
    Route after validation.

    If validation passes or max iterations reached, go to review.
    Otherwise, retry generation.

    Args:
        state: Current workflow state

    Returns:
        Next node name
    """
    validation = state["recoding_validation"]
    iteration = state["recoding_iteration"]
    max_iterations = state["config"].get("max_iterations", 3)

    # Check if validation passed
    if validation.get("is_valid", False):
        return "review_recoding"

    # Check if max iterations reached
    if iteration >= max_iterations:
        return "review_recoding"

    # Retry generation
    return "generate_recoding"


def after_recoding_review(state: State) -> Literal["END", "generate_recoding"]:
    """
    Route after human review.

    If approved, go to END. If rejected, retry generation.

    Args:
        state: Current workflow state

    Returns:
        Next node name or END
    """
    if state["recoding_rules_approved"]:
        return "END"

    # Check if max iterations reached
    iteration = state["recoding_iteration"]
    max_iterations = state["config"].get("max_iterations", 3)

    if iteration >= max_iterations:
        # Can't retry anymore, force approval
        return "END"

    return "generate_recoding"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _mock_llm_response(prompt: str) -> str:
    """
    Mock LLM response for testing.

    In production, replace this with actual LLM call.
    """
    return json.dumps({
        "recoding_rules": [
            {
                "source_variable": "age",
                "target_variable": "age_group",
                "rule_type": "range",
                "transformations": [
                    {"source": [18, 24], "target": 1, "label": "18-24"},
                    {"source": [25, 34], "target": 2, "label": "25-34"},
                    {"source": [35, 44], "target": 3, "label": "35-44"},
                    {"source": [45, 54], "target": 4, "label": "45-54"},
                    {"source": [55, 99], "target": 5, "label": "55+"}
                ],
                "rationale": "Group age into meaningful segments"
            }
        ]
    })


def _parse_recoding_response(response: str) -> Dict[str, Any]:
    """Parse LLM response into recoding rules."""
    # Try to extract JSON from response
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


def _generate_recoding_review_report(
    recoding_rules: Dict[str, Any],
    validation: Dict[str, Any]
) -> str:
    """Generate a human-readable review report."""
    lines = ["# Recoding Rules Review Report\n"]

    # Validation summary
    lines.append("## Validation Summary")
    rules = recoding_rules.get("recoding_rules", [])
    lines.append(f"- Total Rules: {len(rules)}")
    lines.append(f"- Errors: {len(validation.get('errors', []))}")
    lines.append(f"- Warnings: {len(validation.get('warnings', []))}\n")

    # Rules
    lines.append("## Rules for Review\n")
    for i, rule in enumerate(rules, 1):
        lines.append(f"### Rule {i}: {rule.get('target_variable')}")
        lines.append(f"- **Source**: {rule.get('source_variable')}")
        lines.append(f"- **Type**: {rule.get('rule_type')}")
        lines.append(f"- **Rationale**: {rule.get('rationale', 'N/A')}")

        # Transformations
        lines.append("\n**Transformations**:")
        lines.append("| Source | Target | Label |")
        lines.append("|--------|--------|-------|")
        for transform in rule.get("transformations", []):
            source = transform.get("source")
            if isinstance(source, list):
                source_str = f"{source[0]}-{source[1]}" if len(source) == 2 else str(source)
            else:
                source_str = str(source)
            lines.append(
                f"| {source_str} | {transform.get('target')} | {transform.get('label')} |"
            )
        lines.append("")

    # Validation errors
    if validation.get("errors"):
        lines.append("## Validation Errors")
        for error in validation["errors"]:
            lines.append(f"- ❌ {error}")
        lines.append("")

    # Validation warnings
    if validation.get("warnings"):
        lines.append("## Validation Warnings")
        for warning in validation["warnings"]:
            lines.append(f"- ⚠️ {warning}")
        lines.append("")

    return "\n".join(lines)
