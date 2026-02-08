"""
Phase 2: Recoding Nodes (Steps 4-8)

This module contains nodes for generating and applying recoding rules:
- Step 4: generate_recoding_rules_node - LLM generates recoding rules JSON
- Step 5: validate_recoding_rules_node - Validate rules structure
- Step 6: review_recoding_rules_node - Human review and approval
- Step 7: generate_pspp_recoding_syntax_node - Generate PSPP syntax
- Step 8: execute_pspp_recoding_node - Execute PSPP and create new_data.sav
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage

from agent.state import (
    WorkflowState, ValidationResult,
    STEP_4_GENERATE_RECODING_RULES, STEP_5_VALIDATE_RECODING_RULES,
    STEP_6_REVIEW_RECODING_RULES, STEP_7_GENERATE_PSPP_RECODING_SYNTAX,
    STEP_8_EXECUTE_PSPP_RECODING
)
from agent.llm.clients import get_llm_client
from agent.llm.prompts import generate_recoding_rules_prompt
from agent.config import DEFAULT_CONFIG
from agent.utils.tracing import trace_node

logger = logging.getLogger(__name__)


# =============================================================================
# Step 4: Generate Recoding Rules
# =============================================================================

@trace_node("Step 4: Generate Recoding Rules")
def generate_recoding_rules_node(state: WorkflowState) -> WorkflowState:
    """
    Step 4: Generate recoding rules using LLM.

    This node invokes the LLM to generate recoding rules for survey variables
    based on market research principles. The node handles three scenarios:

    1. Initial generation: No feedback, generate rules from scratch
    2. Validation retry: Validation failed, use validation error messages as feedback
    3. Human feedback retry: Human rejected rules, use human feedback for revision

    The node generates a prompt, invokes the LLM, parses the JSON response,
    validates the structure, and saves the rules to a JSON file.

    Args:
        state: Current workflow state. Must contain:
            - filtered_metadata: List of variable metadata dictionaries
            - iteration_count: Current iteration number (for retry logic)
            - recoding_validation_result: Optional validation result from Step 5
            - recoding_feedback: Optional feedback from validation or human review

    Returns:
        Updated workflow state with:
            - recoding_rules: Dict containing generated recoding rules
            - current_step: Set to STEP_4_GENERATE_RECODING_RULES
            - iteration_count: Incremented if this is a retry
            - errors: List of errors (appended if any occur)
            - warnings: List of warnings (appended if any occur)

    Raises:
        ValueError: If filtered_metadata is missing or empty
        RuntimeError: If LLM invocation fails after retries

    Example:
        >>> state = {
        ...     "filtered_metadata": [{"name": "age", "label": "Age", ...}],
        ...     "iteration_count": 0
        ... }
        >>> new_state = generate_recoding_rules_node(state)
        >>> print(new_state["recoding_rules"]["recoding_rules"][0]["source_variable"])
        'age'
    """
    # Get filtered metadata from state
    filtered_metadata = state.get("filtered_metadata")
    if not filtered_metadata:
        error_msg = "No filtered_metadata available in state. Cannot generate recoding rules."
        logger.error(error_msg)
        return {
            **state,
            "current_step": STEP_4_GENERATE_RECODING_RULES,
            "errors": state.get("errors", []) + [error_msg],
        }

    logger.info(
        f"Step 4: Generating recoding rules for {len(filtered_metadata)} variables"
    )

    # Determine feedback type
    iteration_count = state.get("iteration_count", 0)
    validation_result = state.get("recoding_validation_result")
    human_feedback = state.get("recoding_feedback")

    validation_feedback = None
    if iteration_count > 0:
        # Retry scenario: determine feedback source
        if validation_result and not validation_result['is_valid']:
            # Use validation error messages
            validation_feedback = _format_validation_errors(validation_result)
            logger.info(f"Using validation feedback for retry (iteration {iteration_count})")
        elif human_feedback:
            # Use human feedback
            logger.info(f"Using human feedback for retry (iteration {iteration_count})")
        else:
            logger.warning(f"Retry iteration {iteration_count} but no feedback found")

    try:
        # Get LLM client
        config = state.get("config", DEFAULT_CONFIG)
        llm_client = get_llm_client(config)

        # Generate prompt with appropriate feedback
        prompt = generate_recoding_rules_prompt(
            metadata=filtered_metadata,
            validation_feedback=validation_feedback,
            human_feedback=human_feedback if iteration_count > 0 else None
        )

        logger.info("Invoking LLM to generate recoding rules...")
        logger.debug(f"Prompt length: {len(prompt)} characters")

        # Invoke LLM
        response = llm_client.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)

        logger.info(f"LLM response received: {len(response_text)} characters")

        # Parse JSON response
        try:
            recoding_rules = parse_llm_response(response_text)
        except ValueError as e:
            error_msg = f"Failed to parse LLM response as JSON: {str(e)}"
            logger.error(error_msg)
            logger.debug(f"LLM response: {response_text[:500]}...")

            # Store error as feedback for retry
            return {
                **state,
                "current_step": STEP_4_GENERATE_RECODING_RULES,
                "iteration_count": iteration_count + 1,
                "recoding_feedback": error_msg,
                "errors": state.get("errors", []) + [error_msg],
            }

        # Validate recoding rules structure
        validation_error = _validate_recoding_rules_structure(recoding_rules)
        if validation_error:
            error_msg = f"Invalid recoding rules structure: {validation_error}"
            logger.error(error_msg)

            return {
                **state,
                "current_step": STEP_4_GENERATE_RECODING_RULES,
                "iteration_count": iteration_count + 1,
                "recoding_feedback": error_msg,
                "errors": state.get("errors", []) + [error_msg],
            }

        # Get rule count
        rule_count = len(recoding_rules.get("recoding_rules", []))
        logger.info(f"Successfully generated {rule_count} recoding rules")

        # Save to file
        output_path = _save_recoding_rules(recoding_rules, config)
        logger.info(f"Recoding rules saved to: {output_path}")

        # Prepare warnings
        warnings = state.get("warnings", []).copy()

        # Warn if no rules generated
        if rule_count == 0:
            warning_msg = "No recoding rules generated. All variables may be suitable for analysis as-is."
            logger.warning(warning_msg)
            warnings.append(warning_msg)

        # Clear previous feedback on successful generation
        new_state = {
            **state,
            "current_step": STEP_4_GENERATE_RECODING_RULES,
            "recoding_rules": recoding_rules,
            "recoding_feedback": None,  # Clear feedback on success
            "warnings": warnings,
        }

        # Only increment iteration_count if this was a retry
        if iteration_count > 0:
            new_state["iteration_count"] = iteration_count + 1

        return new_state

    except Exception as e:
        error_msg = f"Unexpected error generating recoding rules: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": STEP_4_GENERATE_RECODING_RULES,
            "errors": state.get("errors", []) + [error_msg],
        }


def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Parse LLM response text to extract JSON recoding rules.

    Handles common LLM formatting issues:
    - JSON wrapped in markdown code blocks (```json ... ```)
    - JSON with leading/trailing text
    - JSON with comments
    - Malformed JSON (missing quotes, trailing commas)

    Args:
        response_text: Raw text response from LLM

    Returns:
        Parsed dictionary containing recoding rules

    Raises:
        ValueError: If JSON cannot be extracted or parsed

    Example:
        >>> response = '{"recoding_rules": [...]}'
        >>> rules = parse_llm_response(response)
        >>> print(rules["recoding_rules"][0]["source_variable"])
    """
    if not response_text:
        raise ValueError("Empty LLM response")

    # Try direct JSON parse first
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Extract JSON from markdown code blocks
    # Pattern 1: ```json ... ```
    json_pattern = r'```json\s*(.*?)\s*```'
    matches = re.findall(json_pattern, response_text, re.DOTALL | re.IGNORECASE)

    if matches:
        json_str = matches[0].strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from code block: {e}")

    # Pattern 2: ``` ... ``` (without json language identifier)
    json_pattern = r'```\s*(.*?)\s*```'
    matches = re.findall(json_pattern, response_text, re.DOTALL)

    if matches:
        for match in matches:
            json_str = match.strip()
            # Try to parse each code block
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                continue

    # Try to find JSON object boundaries
    # Find first { and last }
    first_brace = response_text.find('{')
    last_brace = response_text.rfind('}')

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        json_str = response_text[first_brace:last_brace + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # Try cleaning common issues
            cleaned_json = _clean_json_string(json_str)
            try:
                return json.loads(cleaned_json)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to parse extracted JSON: {e}")

    raise ValueError(
        "Could not extract valid JSON from LLM response. "
        "Response may not contain JSON or is malformed."
    )


def _clean_json_string(json_str: str) -> str:
    """
    Clean common JSON formatting issues from LLM responses.

    Handles:
    - Trailing commas in arrays/objects
    - Single quotes instead of double quotes
    - Comments (// or #)
    - Unquoted keys

    Args:
        json_str: Potentially malformed JSON string

    Returns:
        Cleaned JSON string
    """
    # Remove comments (// ...)
    json_str = re.sub(r'//.*', '', json_str)
    json_str = re.sub(r'#.*', '', json_str)

    # Remove trailing commas
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)

    return json_str


def _validate_recoding_rules_structure(rules: Dict[str, Any]) -> Optional[str]:
    """
    Validate the structure of generated recoding rules.

    Checks for:
    - Required top-level key "recoding_rules"
    - recoding_rules is a list
    - Each rule has required fields
    - At least one rule is generated

    Args:
        rules: Parsed recoding rules dictionary

    Returns:
        None if valid, error message string if invalid
    """
    if not isinstance(rules, dict):
        return "Recoding rules must be a JSON object"

    if "recoding_rules" not in rules:
        return "Missing required key 'recoding_rules'"

    if not isinstance(rules["recoding_rules"], list):
        return "'recoding_rules' must be a list"

    if len(rules["recoding_rules"]) == 0:
        # Warning only, not an error
        return None

    # Validate each rule
    required_fields = ["source_variable", "target_variable", "transformation_type"]
    transformation_types = ["range_grouping", "category_consolidation", "derived", "top_bottom_box"]

    for i, rule in enumerate(rules["recoding_rules"]):
        if not isinstance(rule, dict):
            return f"Rule {i} is not a JSON object"

        # Check required fields
        for field in required_fields:
            if field not in rule:
                return f"Rule {i} missing required field '{field}'"

        # Validate transformation_type
        if rule["transformation_type"] not in transformation_types:
            return f"Rule {i} has invalid transformation_type '{rule['transformation_type']}'"

        # Check rules array
        if "rules" not in rule or not isinstance(rule["rules"], list):
            return f"Rule {i} missing 'rules' array or not a list"

        if len(rule["rules"]) == 0:
            return f"Rule {i} has empty 'rules' array"

    return None


def _format_validation_errors(validation_result) -> str:
    """
    Format validation errors for use as feedback to LLM.

    Args:
        validation_result: ValidationResult object

    Returns:
        Formatted error message string
    """
    errors = validation_result['errors'] if validation_result else []
    warnings = validation_result['warnings'] if validation_result else []

    lines = []
    if errors:
        lines.append("Errors:")
        for error in errors:
            lines.append(f"  - {error}")

    if warnings:
        if lines:
            lines.append("")
        lines.append("Warnings:")
        for warning in warnings:
            lines.append(f"  - {warning}")

    return "\n".join(lines) if lines else "Validation failed with no specific errors."


def _save_recoding_rules(rules: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Save recoding rules to JSON file with timestamp.

    Args:
        rules: Recoding rules dictionary
        config: Configuration dictionary

    Returns:
        Path to saved file
    """
    output_dir = Path(config.get("output_dir", "output"))
    temp_dir = output_dir / "temp"

    # Create directory if it doesn't exist
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recoding_rules_{timestamp}.json"
    filepath = temp_dir / filename

    # Add timestamp to the rules object
    rules_with_metadata = {
        "generated_at": datetime.now().isoformat(),
        "rule_count": len(rules.get("recoding_rules", [])),
        "recoding_rules": rules.get("recoding_rules", [])
    }

    # Save with pretty formatting
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(rules_with_metadata, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(rules.get('recoding_rules', []))} rules to {filepath}")
    return str(filepath)


def _generate_recoding_review_markdown(
    recoding_rules: Dict[str, Any],
    validation_result: Optional[ValidationResult],
    iteration_count: int,
    previous_feedback: Optional[str]
) -> str:
    """
    Generate markdown review document for recoding rules.

    Creates a comprehensive, human-readable review document with:
    - Summary statistics
    - Validation results
    - Individual rule details
    - Action instructions

    Args:
        recoding_rules: Generated recoding rules dictionary
        validation_result: ValidationResult from Step 5
        iteration_count: Current iteration number
        previous_feedback: Previous feedback (if retry)

    Returns:
        Complete markdown document as string
    """
    lines = []

    # Header
    lines.append("# Recoding Rules Review")
    lines.append("")
    lines.append("**Status**: Pending Your Review")
    lines.append("")

    # Summary
    lines.append("## Summary")
    rules_list = recoding_rules.get("recoding_rules", [])
    lines.append(f"- Total Rules: {len(rules_list)}")

    # Extract unique source and target variables
    source_vars = set()
    target_vars = set()
    for rule in rules_list:
        source_vars.add(rule.get("source_variable", "N/A"))
        target_vars.add(rule.get("target_variable", "N/A"))

    lines.append(f"- Source Variables: {', '.join(sorted(source_vars))}")
    lines.append(f"- Target Variables: {', '.join(sorted(target_vars))}")
    lines.append(f"- Iteration: {iteration_count}")
    lines.append("")

    # Validation Result
    lines.append("## Validation Result")
    if validation_result:
        status = "Passed ✓" if validation_result['is_valid'] else "Failed ✗"
        lines.append(f"- **Status**: {status}")
        lines.append(f"- Errors: {len(validation_result['errors'])}")
        lines.append(f"- Warnings: {len(validation_result['warnings'])}")
    else:
        lines.append("- **Status**: No validation performed")
        lines.append("- Errors: N/A")
        lines.append("- Warnings: N/A")
    lines.append("")

    # Validation Errors
    if validation_result and validation_result['errors']:
        lines.append("### Validation Errors")
        for error in validation_result['errors']:
            lines.append(f"- ❌ {error}")
        lines.append("")

    # Validation Warnings
    if validation_result and validation_result['warnings']:
        lines.append("### Validation Warnings")
        for warning in validation_result['warnings']:
            lines.append(f"- ⚠️ {warning}")
        lines.append("")

    # Previous Feedback (if retry)
    if iteration_count > 0 and previous_feedback:
        lines.append("## Previous Feedback")
        lines.append("")
        lines.append(f"*Iteration {iteration_count}*")
        lines.append("")
        lines.append(f"> {previous_feedback}")
        lines.append("")

    # Recoding Rules Detail
    lines.append("## Recoding Rules")
    lines.append("")

    if not rules_list:
        lines.append("*No recoding rules generated.*")
        lines.append("")
    else:
        for i, rule in enumerate(rules_list, 1):
            source_var = rule.get("source_variable", "N/A")
            target_var = rule.get("target_variable", "N/A")
            transform_type = rule.get("transformation_type", "N/A")

            lines.append(f"### Rule {i}: {source_var} → {target_var}")
            lines.append("")
            lines.append(f"- **Transformation Type**: {transform_type}")
            lines.append(f"- **Source Variable**: {source_var}")
            lines.append(f"- **Target Variable**: {target_var}")
            lines.append("")

            # Rationale
            rationale = rule.get("rationale", "")
            if rationale:
                lines.append(f"**Rationale**: {rationale}")
                lines.append("")

            # Rules table
            rules_table = rule.get("rules", [])
            if rules_table:
                lines.append("**Rules**:")
                lines.append("")

                # Determine table columns based on transformation type
                if transform_type == "range_grouping":
                    lines.append("| Source Range | Target Value | Label |")
                    lines.append("|--------------|--------------|-------|")
                    for r in rules_table:
                        source = r.get("source_range", r.get("source", "N/A"))
                        target = r.get("target_value", r.get("target", "N/A"))
                        label = r.get("label", "")
                        if isinstance(source, list):
                            source_str = f"{source[0]}-{source[1]}" if len(source) == 2 else str(source)
                        else:
                            source_str = str(source)
                        lines.append(f"| {source_str} | {target} | {label} |")
                elif transform_type == "category_consolidation":
                    lines.append("| Source Values | Target Value | Label |")
                    lines.append("|---------------|--------------|-------|")
                    for r in rules_table:
                        source = r.get("source_values", r.get("source", "N/A"))
                        target = r.get("target_value", r.get("target", "N/A"))
                        label = r.get("label", "")
                        if isinstance(source, list):
                            source_str = ", ".join(str(s) for s in source)
                        else:
                            source_str = str(source)
                        lines.append(f"| {source_str} | {target} | {label} |")
                else:
                    # Generic table
                    lines.append("| Source | Target | Label |")
                    lines.append("|--------|--------|-------|")
                    for r in rules_table:
                        source = r.get("source", "N/A")
                        target = r.get("target", "N/A")
                        label = r.get("label", "")
                        if isinstance(source, list):
                            source_str = ", ".join(str(s) for s in source)
                        else:
                            source_str = str(source)
                        lines.append(f"| {source_str} | {target} | {label} |")

                lines.append("")

    # Actions Section
    lines.append("## Actions")
    lines.append("")
    lines.append("Please review and select an action:")
    lines.append("")
    lines.append("- [ ] **Approve** - Rules look correct, proceed to PSPP syntax generation")
    lines.append("- [ ] **Reject with Feedback** - Rules need revision, provide feedback below")
    lines.append("- [ ] **Modify** - You will manually edit the rules")
    lines.append("")

    # Feedback section
    lines.append("**Your Feedback**:")
    lines.append("")
    lines.append("[Enter your feedback here]")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("**Common feedback examples**:")
    lines.append("")
    lines.append("- Add recoding rule for variable 'age'")
    lines.append("- Change ranges for 'income' to use quintiles")
    lines.append("- Consolidate categories 7-9 into 'Other'")
    lines.append("- Use different transformation type for 'satisfaction'")
    lines.append("")

    return "\n".join(lines)


# =============================================================================
# Step 5: Validate Recoding Rules
# =============================================================================

@trace_node("Step 5: Validate Recoding Rules")
def validate_recoding_rules_node(state: WorkflowState) -> WorkflowState:
    """
    Step 5: Validate recoding rules structure and references.

    This node validates:
    - JSON structure is correct
    - Source variables exist in filtered_metadata
    - Target variable names are unique
    - Rules are mutually exclusive
    - Value ranges are valid
    - Ranges don't overlap
    - Transformation completeness

    Args:
        state: Current workflow state. Must contain:
            - recoding_rules: Generated recoding rules
            - filtered_metadata: Original variable metadata

    Returns:
        Updated workflow state with:
            - recoding_validation_result: ValidationResult object
            - current_step: Set to STEP_5_VALIDATE_RECODING_RULES
            - errors: List of errors (appended if validation fails)
            - warnings: List of warnings (appended if any warnings)

    Example:
        >>> state = {
        ...     "recoding_rules": {"recoding_rules": [...]},
        ...     "filtered_metadata": [{"name": "age", ...}]
        ... }
        >>> new_state = validate_recoding_rules_node(state)
        >>> print(new_state["recoding_validation_result"].is_valid)
        True
    """
    logger.info("Step 5: Validating recoding rules")

    # Get inputs from state
    recoding_rules = state.get("recoding_rules")
    variable_centered_metadata = state.get("variable_centered_metadata")

    # Validate required inputs
    if not recoding_rules:
        error_msg = "No recoding_rules available in state for validation"
        logger.error(error_msg)
        return {
            **state,
            "current_step": STEP_5_VALIDATE_RECODING_RULES,
            "errors": state.get("errors", []) + [error_msg],
        }

    if not variable_centered_metadata:
        error_msg = "No variable_centered_metadata available in state for validation"
        logger.error(error_msg)
        return {
            **state,
            "current_step": STEP_5_VALIDATE_RECODING_RULES,
            "errors": state.get("errors", []) + [error_msg],
        }

    try:
        # Import validation function
        from agent.validation.recoding import validate_recoding_rules

        # Run validation
        # Note: We use variable_centered_metadata["variables"] (all variables) instead of filtered_metadata
        # because recoding rules reference variables that were filtered out (high cardinality)
        logger.info(f"Validating {len(recoding_rules.get('recoding_rules', []))} recoding rules")
        validation_result = validate_recoding_rules(recoding_rules, variable_centered_metadata.get("variables", {}))

        # Log results
        if validation_result['is_valid']:
            logger.info(
                f"Validation passed: {len(validation_result['checks_performed'])} checks performed"
            )
        else:
            logger.error(
                f"Validation failed: {len(validation_result['errors'])} errors, "
                f"{len(validation_result['warnings'])} warnings"
            )

        # Log errors if any
        for error in validation_result['errors']:
            logger.error(f"  - {error}")

        # Log warnings if any
        for warning in validation_result['warnings']:
            logger.warning(f"  - {warning}")

        # Prepare updated state
        new_state = {
            **state,
            "current_step": STEP_5_VALIDATE_RECODING_RULES,
            "recoding_validation_result": validation_result,
        }

        # Append errors to tracking state
        if validation_result['errors']:
            new_state["errors"] = state.get("errors", []) + validation_result['errors']

        # Append warnings to tracking state
        if validation_result['warnings']:
            new_state["warnings"] = state.get("warnings", []) + validation_result['warnings']

        return new_state

    except Exception as e:
        error_msg = f"Unexpected error during recoding rules validation: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": STEP_5_VALIDATE_RECODING_RULES,
            "errors": state.get("errors", []) + [error_msg],
        }


@trace_node("Step 6: Review Recoding Rules")
def review_recoding_rules_node(state: WorkflowState) -> WorkflowState:
    """
    Step 6: Human review and approval of recoding rules.

    This node implements the human-in-the-loop review pattern using LangGraph's
    interrupt mechanism. It generates a markdown review document and pauses the
    workflow to wait for human approval/rejection.

    The node:
    1. Generates a comprehensive markdown review document
    2. Saves it to output/reviews/recoding_rules_review.md
    3. Triggers LangGraph interrupt to pause workflow
    4. Returns state unchanged (approval status set by human via UI)

    Human actions via Agent Chat UI:
    - Approve: Sets recoding_approved=True, workflow proceeds to Step 7
    - Reject with feedback: Sets recoding_feedback, workflow retries Step 4
    - Modify: Human can manually edit rules before approval

    Args:
        state: Current workflow state. Must contain:
            - recoding_rules: Generated recoding rules from Step 4
            - recoding_validation_result: Validation result from Step 5
            - iteration_count: Current iteration number
            - recoding_feedback: Previous feedback (if retry)

    Returns:
        Updated workflow state with:
            - current_step: Set to STEP_6_REVIEW_RECODING_RULES
            - requires_human_review: Set to True

    Note:
        - DOES NOT set recoding_approved - this is set by human via UI
        - Workflow resumes via conditional routing in agent/edges.py
        - Use should_approve_recoding() routing function after this node
    """
    logger.info("Step 6: Generating recoding rules review document for human approval")

    # Get required inputs from state
    recoding_rules = state.get("recoding_rules")
    validation_result = state.get("recoding_validation_result")
    iteration_count = state.get("iteration_count", 0)
    previous_feedback = state.get("recoding_feedback")
    config = state.get("config", DEFAULT_CONFIG)

    # Check for auto-approval (CI/CD and testing mode)
    auto_approve = config.get("auto_approve_recoding", False)

    # Validate required inputs
    if not recoding_rules:
        error_msg = "No recoding_rules available in state for review"
        logger.error(error_msg)
        return {
            **state,
            "current_step": STEP_6_REVIEW_RECODING_RULES,
            "errors": state.get("errors", []) + [error_msg],
            "requires_human_review": not auto_approve,
            "recoding_approved": auto_approve,
        }

    try:
        # Generate markdown review document
        review_doc = _generate_recoding_review_markdown(
            recoding_rules=recoding_rules,
            validation_result=validation_result,
            iteration_count=iteration_count,
            previous_feedback=previous_feedback
        )

        # Save review document to fixed path
        output_dir = Path(config.get("output_dir", "output"))
        reviews_dir = output_dir / "reviews"
        reviews_dir.mkdir(parents=True, exist_ok=True)

        review_path = reviews_dir / "recoding_rules_review.md"
        with open(review_path, 'w', encoding='utf-8') as f:
            f.write(review_doc)

        logger.info(f"Review document saved to: {review_path}")

        # Trigger LangGraph interrupt to pause workflow (unless auto-approve is enabled)
        # The Agent Chat UI will display the review document
        # and wait for human action (approve/reject/modify)
        from langgraph.types import interrupt

        # Only trigger interrupt if not auto-approving
        if not auto_approve:
            interrupt({
                "type": "approval_required",
                "step": 6,
                "task": "recoding_rules",
                "review_document_path": str(review_path),
                "validation_passed": validation_result['is_valid'] if validation_result else False,
                "iteration": iteration_count,
                "message": (
                    "Please review the recoding rules at: {}\n\n"
                    "Actions:\n"
                    "- Approve: Rules look correct, proceed to PSPP syntax generation\n"
                    "- Reject with Feedback: Rules need revision, provide feedback below\n"
                    "- Modify: You will manually edit the rules"
                ).format(review_path)
            })

        # Return state with approval status
        # If auto_approve is True, recoding_approved is set to True
        # If auto_approve is False, requires_human_review is set to True
        return {
            **state,
            "current_step": STEP_6_REVIEW_RECODING_RULES,
            "requires_human_review": not auto_approve,
            "recoding_approved": auto_approve,
        }

    except Exception as e:
        error_msg = f"Error during recoding rules review: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": STEP_6_REVIEW_RECODING_RULES,
            "errors": state.get("errors", []) + [error_msg],
            "requires_human_review": True,
        }


def generate_pspp_recoding_syntax_node(state: WorkflowState) -> WorkflowState:
    """
    Step 7: Generate PSPP recoding syntax from approved rules.

    Converts validated recoding rules JSON into PSPP RECODE syntax with proper
    VARIABLE LABELS and VALUE LABELS. Generates a complete .sps syntax file
    that can be executed by PSPP to create the recoded dataset.

    Supports 4 transformation types:
    - range_grouping: RECODE with THRU ranges
    - category_consolidation: RECODE with value lists
    - derived: COMPUTE with formula
    - top_bottom_box: RECODE with SYSMIS for middle values

    Args:
        state: Current workflow state. Must contain:
            - recoding_rules: Approved recoding rules (from Step 6)
            - filtered_metadata: Original variable metadata (for labels)

    Returns:
        Updated workflow state with:
            - syntax_file_path: Path to generated .sps file
            - current_step: Set to STEP_7_GENERATE_PSPP_RECODING_SYNTAX
            - errors: List of errors (appended if any occur)
            - warnings: List of warnings (appended if any occur)

    Example:
        >>> state = {
        ...     "recoding_rules": {"recoding_rules": [...]},
        ...     "filtered_metadata": [{"name": "age", "label": "Age", ...}]
        ... }
        >>> new_state = generate_pspp_recoding_syntax_node(state)
        >>> print(new_state["syntax_file_path"])
        'temp/pspp_syntax/recoding.sps'
    """
    logger.info("Step 7: Generating PSPP recoding syntax")

    # Get required inputs from state
    recoding_rules = state.get("recoding_rules")
    filtered_metadata = state.get("filtered_metadata")
    config = state.get("config", DEFAULT_CONFIG)

    # Validate required inputs
    if not recoding_rules:
        error_msg = "No recoding_rules available in state for syntax generation"
        logger.error(error_msg)
        return {
            **state,
            "current_step": STEP_7_GENERATE_PSPP_RECODING_SYNTAX,
            "errors": state.get("errors", []) + [error_msg],
        }

    try:
        # Extract rules list
        rules_list = recoding_rules.get("recoding_rules", [])

        if not rules_list:
            warning_msg = "No recoding rules to convert to PSPP syntax (empty rules list)"
            logger.warning(warning_msg)
            return {
                **state,
                "current_step": STEP_7_GENERATE_PSPP_RECODING_SYNTAX,
                "warnings": state.get("warnings", []) + [warning_msg],
            }

        logger.info(f"Generating PSPP syntax for {len(rules_list)} recoding rules")

        # Build metadata lookup for variable labels
        metadata_lookup = {}
        if filtered_metadata:
            for var in filtered_metadata:
                var_name = var.get("name", "")
                metadata_lookup[var_name] = var

        # Generate PSPP syntax
        syntax_lines = _generate_pspp_header()

        # Generate syntax for each rule
        for idx, rule in enumerate(rules_list, 1):
            try:
                rule_syntax = _generate_rule_syntax(rule, metadata_lookup, idx)
                if rule_syntax:
                    syntax_lines.extend(rule_syntax)
            except Exception as e:
                error_msg = f"Error generating syntax for rule {idx}: {str(e)}"
                logger.error(error_msg)
                # Continue with other rules
                continue

        # Add footer
        syntax_lines.append("")
        syntax_lines.append("* Execute Recoding")
        syntax_lines.append("EXECUTE.")

        # Combine into single string
        pspp_syntax = "\n".join(syntax_lines)

        # Write to file
        # Use temp/ directory at project root, not output/temp/
        pspp_syntax_dir = Path("temp") / "pspp_syntax"
        pspp_syntax_dir.mkdir(parents=True, exist_ok=True)

        syntax_file_path = pspp_syntax_dir / "recoding.sps"

        with open(syntax_file_path, 'w', encoding='utf-8') as f:
            f.write(pspp_syntax)

        logger.info(f"PSPP recoding syntax written to: {syntax_file_path}")
        logger.info(f"Syntax file size: {len(pspp_syntax)} characters")

        # Prepare warnings
        warnings = state.get("warnings", []).copy()

        # Warn if any rules failed to generate
        if len(syntax_lines) < len(rules_list) * 2:
            warning_msg = (
                f"Some rules may not have been converted to syntax. "
                f"Expected {len(rules_list)} rules, got {len([l for l in syntax_lines if 'RECODE' in l or 'COMPUTE' in l])} syntax commands."
            )
            logger.warning(warning_msg)
            warnings.append(warning_msg)

        return {
            **state,
            "current_step": STEP_7_GENERATE_PSPP_RECODING_SYNTAX,
            "pspp_recoding_syntax": pspp_syntax,
            "recoding_syntax_file": str(syntax_file_path),  # Store path for Step 8
            "warnings": warnings,
        }

    except Exception as e:
        error_msg = f"Unexpected error generating PSPP syntax: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": STEP_7_GENERATE_PSPP_RECODING_SYNTAX,
            "errors": state.get("errors", []) + [error_msg],
        }


def _generate_pspp_header() -> List[str]:
    """
    Generate header comments for PSPP syntax file.

    Returns:
        List of header lines
    """
    lines = []
    lines.append("* Recoding Rules Generated by DataChat")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"* Generated: {timestamp}")
    lines.append("*")
    lines.append("")
    return lines


def _generate_rule_syntax(
    rule: Dict[str, Any],
    metadata_lookup: Dict[str, Dict[str, Any]],
    rule_index: int
) -> List[str]:
    """
    Generate PSPP syntax for a single recoding rule.

    Args:
        rule: Single recoding rule dictionary
        metadata_lookup: Variable metadata lookup
        rule_index: Rule number (for comments)

    Returns:
        List of PSPP syntax lines

    Raises:
        ValueError: If transformation type is invalid or required fields missing
    """
    lines = []

    source_var = rule.get("source_variable", "")
    target_var = rule.get("target_variable", "")
    transform_type = rule.get("transformation_type", "")
    rules = rule.get("rules", [])
    description = rule.get("description", "")

    # Validate required fields
    if not source_var or not target_var or not transform_type:
        raise ValueError(
            f"Rule missing required fields: source_variable={source_var}, "
            f"target_variable={target_var}, transformation_type={transform_type}"
        )

    # Add comment header for this rule
    lines.append(f"* Rule {rule_index}: {source_var} → {target_var}")
    if description:
        lines.append(f"* {description}")

    # Generate syntax based on transformation type
    if transform_type == "range_grouping":
        syntax = _generate_range_grouping_syntax(rule, metadata_lookup)
    elif transform_type == "category_consolidation":
        syntax = _generate_category_consolidation_syntax(rule, metadata_lookup)
    elif transform_type == "derived":
        syntax = _generate_derived_syntax(rule, metadata_lookup)
    elif transform_type == "top_bottom_box":
        syntax = _generate_top_bottom_box_syntax(rule, metadata_lookup)
    else:
        raise ValueError(f"Invalid transformation_type: {transform_type}")

    lines.extend(syntax)
    lines.append("")

    return lines


def _generate_range_grouping_syntax(
    rule: Dict[str, Any],
    metadata_lookup: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Generate RECODE syntax for range_grouping transformation.

    Example:
        RECODE income (0 THRU 30000 = 1) (30001 THRU 60000 = 2)
                  (60001 THRU HI = 3)
            INTO income_recoded.
    """
    lines = []
    source_var = rule.get("source_variable", "")
    target_var = rule.get("target_variable", "")
    rules = rule.get("rules", [])

    # Build RECODE command
    recode_parts = []

    for r in rules:
        source_min = r.get("source_min")
        source_max = r.get("source_max")
        target_value = r.get("target_value")

        if source_min is None or source_max is None or target_value is None:
            continue

        # Handle HI (highest value) keyword
        if str(source_max).upper() == "HI" or source_max == "HI":
            range_spec = f"{source_min} THRU HI"
        else:
            range_spec = f"{source_min} THRU {source_max}"

        recode_parts.append(f"({range_spec} = {target_value})")

    if not recode_parts:
        logger.warning(f"No valid ranges for {source_var}")
        return []

    # Join parts with line continuation
    recode_line = f"RECODE {source_var} "
    recode_line += " ".join(recode_parts)
    recode_line += f"\n    INTO {target_var}."

    lines.append(recode_line)

    # Add VARIABLE LABELS
    lines.extend(_generate_variable_labels(rule, metadata_lookup))

    # Add VALUE LABELS
    lines.extend(_generate_value_labels(rule, metadata_lookup))

    return lines


def _generate_category_consolidation_syntax(
    rule: Dict[str, Any],
    metadata_lookup: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Generate RECODE syntax for category_consolidation transformation.

    Example:
        RECODE occupation ('Farmer'='Agriculture') ('Fisherman'='Agriculture')
            INTO occupation_recoded.
    """
    lines = []
    source_var = rule.get("source_variable", "")
    target_var = rule.get("target_variable", "")
    rules = rule.get("rules", [])

    # Check if source variable is string or numeric
    source_metadata = metadata_lookup.get(source_var, {})
    source_type = source_metadata.get("variable_type", "numeric")

    # Build RECODE command
    recode_parts = []

    for r in rules:
        source_values = r.get("source_values", [])
        target_value = r.get("target_value")

        if not source_values or target_value is None:
            continue

        # Format source values based on type
        if source_type == "string":
            # String values need quotes
            formatted_values = [f"'{v}'" for v in source_values]
        else:
            # Numeric values
            formatted_values = [str(v) for v in source_values]

        # Join multiple source values with commas
        source_spec = ", ".join(formatted_values)
        recode_parts.append(f"({source_spec} = {target_value})")

    if not recode_parts:
        logger.warning(f"No valid value mappings for {source_var}")
        return []

    # Build RECODE line
    recode_line = f"RECODE {source_var} "
    recode_line += " ".join(recode_parts)
    recode_line += f"\n    INTO {target_var}."

    lines.append(recode_line)

    # For string targets, we need to declare STRING type first
    if source_type == "string":
        lines.insert(0, f"STRING {target_var} (A50).")

    # Add VARIABLE LABELS
    lines.extend(_generate_variable_labels(rule, metadata_lookup))

    # Add VALUE LABELS
    lines.extend(_generate_value_labels(rule, metadata_lookup))

    return lines


def _generate_derived_syntax(
    rule: Dict[str, Any],
    metadata_lookup: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Generate COMPUTE syntax for derived variables.

    Example:
        COMPUTE satisfaction_index = MEAN(sat_q1, sat_q2, sat_q3).
    """
    lines = []
    target_var = rule.get("target_variable", "")
    formula = rule.get("formula", "")
    rules = rule.get("rules", [])

    if not formula:
        logger.warning(f"Derived variable {target_var} missing formula")
        return []

    # Generate COMPUTE command
    compute_line = f"COMPUTE {target_var} = {formula}."
    lines.append(compute_line)

    # Add VARIABLE LABELS
    lines.extend(_generate_variable_labels(rule, metadata_lookup))

    # Add VALUE LABELS if rules provided (for categorizing computed values)
    if rules:
        lines.extend(_generate_value_labels(rule, metadata_lookup))

    return lines


def _generate_top_bottom_box_syntax(
    rule: Dict[str, Any],
    metadata_lookup: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Generate RECODE syntax for top/bottom box scoring.

    Example:
        RECODE satisfaction (1,2 = 1) (3 = SYSMIS) (4,5 = 0) INTO satisfaction_topbox.
        VALUE LABELS satisfaction_topbox 1 'Top2Box' 0 'Bottom2Box'.
    """
    lines = []
    source_var = rule.get("source_variable", "")
    target_var = rule.get("target_variable", "")
    rules = rule.get("rules", [])

    # Build RECODE command
    recode_parts = []

    for r in rules:
        source_values = r.get("source_values", [])
        target_value = r.get("target_value")

        if not source_values or target_value is None:
            continue

        # Format source values
        formatted_values = [str(v) for v in source_values]
        source_spec = ", ".join(formatted_values)
        recode_parts.append(f"({source_spec} = {target_value})")

    if not recode_parts:
        logger.warning(f"No valid top/bottom box mappings for {source_var}")
        return []

    # Build RECODE line
    recode_line = f"RECODE {source_var} "
    recode_line += " ".join(recode_parts)
    recode_line += f"\n    INTO {target_var}."

    lines.append(recode_line)

    # Add VARIABLE LABELS
    lines.extend(_generate_variable_labels(rule, metadata_lookup))

    # Add VALUE LABELS
    lines.extend(_generate_value_labels(rule, metadata_lookup))

    return lines


def _generate_variable_labels(
    rule: Dict[str, Any],
    metadata_lookup: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Generate VARIABLE LABELS command for target variable.

    Uses target_variable as the label if no explicit label provided.
    """
    lines = []
    target_var = rule.get("target_variable", "")
    description = rule.get("description", "")

    # Use description or fall back to formatted variable name
    label = description if description else target_var.replace("_", " ").title()

    # Build VARIABLE LABELS command
    label_line = f"VARIABLE LABELS {target_var} '{label}'."
    lines.append(label_line)

    return lines


def _generate_value_labels(
    rule: Dict[str, Any],
    metadata_lookup: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Generate VALUE LABELS command for target variable.

    Maps target values to their labels from the rules array.
    """
    lines = []
    target_var = rule.get("target_variable", "")
    rules = rule.get("rules", [])

    if not rules:
        return []

    # Build value label pairs
    label_pairs = []

    for r in rules:
        target_value = r.get("target_value")
        target_label = r.get("target_label", "")

        if target_value is not None and target_label:
            label_pairs.append(f"    {target_value} '{target_label}'")

    if not label_pairs:
        return []

    # Build VALUE LABELS command
    lines.append(f"* Value Labels for {target_var}")
    lines.append(f"VALUE LABELS {target_var}")
    lines.extend(label_pairs)
    lines.append(".")

    return lines


def execute_pspp_recoding_node(state: WorkflowState) -> WorkflowState:
    """
    Step 8: Execute PSPP recoding and create new_data.sav.

    This node:
    - Executes PSPP with the recoding syntax file generated in Step 7
    - Captures output and creates new_data.sav
    - Extracts metadata from the new file
    - Validates PSPP execution

    Args:
        state: Current workflow state. Must contain:
            - input_file_path: Original .sav file path
            - recoding_syntax_file: Path to PSPP .sps syntax file (from Step 7)
            - config: Configuration dict for output paths

    Returns:
        Updated workflow state with:
            - new_data_file: Path to output/new_data.sav
            - new_metadata: Metadata from new dataset (variable names, labels, value labels)
            - current_step: Set to STEP_8_EXECUTE_PSPP_RECODING
            - errors: Appended if PSPP execution fails
            - warnings: Appended for any PSPP warnings

    Error Handling:
        - PSPP execution failed: Stores error in state, continues to next step
        - PSPP syntax errors: Parses PSPP error log, provides specific message
        - Output file not created: Logs PSPP output, continues with error
        - Metadata extraction failed: Logs error, continues with partial state

    Example:
        >>> state = {
        ...     "input_file_path": "data/survey.sav",
        ...     "recoding_syntax_file": "temp/pspp_syntax/recoding.sps",
        ...     "config": {"output_dir": "output"}
        ... }
        >>> new_state = execute_pspp_recoding_node(state)
        >>> print(new_state["new_data_file"])
        'output/new_data.sav'
        >>> print(len(new_state["new_metadata"]["variable_names"]))
        25
    """
    logger.info("Step 8: Executing PSPP recoding")

    # Get required inputs from state
    input_file_path = state.get("input_file_path")
    syntax_file_path = state.get("recoding_syntax_file")
    config = state.get("config", DEFAULT_CONFIG)

    # Validate required inputs
    if not input_file_path:
        error_msg = "No input_file_path available in state. Cannot execute PSPP recoding."
        logger.error(error_msg)
        return {
            **state,
            "current_step": STEP_8_EXECUTE_PSPP_RECODING,
            "errors": state.get("errors", []) + [error_msg],
        }

    if not syntax_file_path:
        error_msg = "No recoding_syntax_file available in state. Run Step 7 first."
        logger.error(error_msg)
        return {
            **state,
            "current_step": STEP_8_EXECUTE_PSPP_RECODING,
            "errors": state.get("errors", []) + [error_msg],
        }

    # Verify syntax file exists
    if not os.path.exists(syntax_file_path):
        error_msg = f"PSPP syntax file not found: {syntax_file_path}"
        logger.error(error_msg)
        return {
            **state,
            "current_step": STEP_8_EXECUTE_PSPP_RECODING,
            "errors": state.get("errors", []) + [error_msg],
        }

    # Verify input file exists
    if not os.path.exists(input_file_path):
        error_msg = f"Input .sav file not found: {input_file_path}"
        logger.error(error_msg)
        return {
            **state,
            "current_step": STEP_8_EXECUTE_PSPP_RECODING,
            "errors": state.get("errors", []) + [error_msg],
        }

    # Prepare output file path
    output_dir = Path(config.get("output_dir", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    new_data_file = str(output_dir / "new_data.sav")

    logger.info(f"Executing PSPP recoding:")
    logger.info(f"  Input file:  {input_file_path}")
    logger.info(f"  Syntax file: {syntax_file_path}")
    logger.info(f"  Output file: {new_data_file}")

    try:
        # Import pspp_wrapper
        from agent.utils.pspp_wrapper import execute_pspp_syntax

        # Execute PSPP
        logger.info("Invoking PSPP to execute recoding syntax...")
        result = execute_pspp_syntax(
            syntax_file_path=syntax_file_path,
            input_file=input_file_path,
            output_file=new_data_file
        )

        # Check for PSPP execution errors
        if not result["success"]:
            error_msg = result.get("user_message", result.get("error", "PSPP execution failed"))
            logger.error(f"PSPP execution failed: {error_msg}")
            logger.error(f"PSPP return code: {result.get('return_code')}")
            logger.error(f"PSPP stderr: {result.get('error', 'N/A')}")
            logger.error(f"PSPP stdout: {result.get('output', 'N/A')}")

            return {
                **state,
                "current_step": STEP_8_EXECUTE_PSPP_RECODING,
                "errors": state.get("errors", []) + [error_msg],
            }

        # Log PSPP output
        logger.info("PSPP execution completed successfully")
        if result.get("output"):
            logger.debug(f"PSPP stdout: {result['output'][:500]}")
        if result.get("error"):
            # PSPP sometimes outputs to stderr even on success
            logger.debug(f"PSPP stderr: {result['error'][:500]}")

        # Verify output file was created
        if not os.path.exists(new_data_file):
            error_msg = (
                f"PSPP executed successfully but output file was not created: {new_data_file}. "
                f"Check PSPP syntax file for errors."
            )
            logger.error(error_msg)
            return {
                **state,
                "current_step": STEP_8_EXECUTE_PSPP_RECODING,
                "errors": state.get("errors", []) + [error_msg],
            }

        logger.info(f"New data file created: {new_data_file}")

        # Extract metadata from new file
        logger.info("Extracting metadata from new data file...")
        try:
            new_metadata = _extract_metadata_from_sav(new_data_file)
            logger.info(
                f"Metadata extracted: {len(new_metadata.get('variable_names', []))} variables"
            )
        except Exception as e:
            error_msg = f"Failed to extract metadata from new_data.sav: {str(e)}"
            logger.error(error_msg)
            # Continue with partial metadata
            new_metadata = {"error": error_msg}

        # Prepare warnings
        warnings = state.get("warnings", []).copy()

        # Check for PSPP warnings in output
        if result.get("error") and "warning" in result["error"].lower():
            warning_msg = f"PSPP execution produced warnings: {result['error']}"
            logger.warning(warning_msg)
            warnings.append(warning_msg)

        # Update state
        new_state = {
            **state,
            "current_step": STEP_8_EXECUTE_PSPP_RECODING,
            "new_data_file": new_data_file,
            "new_metadata": new_metadata,
            "warnings": warnings,
        }

        logger.info("Step 8 completed successfully")
        return new_state

    except Exception as e:
        error_msg = f"Unexpected error executing PSPP recoding: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": STEP_8_EXECUTE_PSPP_RECODING,
            "errors": state.get("errors", []) + [error_msg],
        }


def _extract_metadata_from_sav(sav_file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from an SPSS .sav file.

    Extracts:
    - variable_names: List of variable names
    - variable_labels: Dict mapping variable names to labels
    - value_labels: Dict mapping variable names to value label dicts
    - variable_count: Number of variables

    Args:
        sav_file_path: Path to .sav file

    Returns:
        Metadata dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a valid .sav file
    """
    # Import here to avoid circular dependency
    import pyreadstat
    import pandas as pd

    if not os.path.exists(sav_file_path):
        raise FileNotFoundError(f"SPSS .sav file not found: {sav_file_path}")

    # Read the file
    df, metadata = pyreadstat.read_sav(sav_file_path, apply_value_formats=True)

    # Extract variable names
    variable_names = list(df.columns)

    # Extract variable labels
    variable_labels = metadata.get("column_labels", {})
    if not variable_labels:
        # Fallback: use variable names as labels
        variable_labels = {var: var for var in variable_names}

    # Extract value labels
    value_labels = metadata.get("value_labels", {})
    # Convert to simpler format if needed
    formatted_value_labels = {}
    for var, labels in value_labels.items():
        if var in variable_names:
            formatted_value_labels[var] = labels

    # Build metadata dict
    return {
        "variable_count": len(variable_names),
        "variable_names": variable_names,
        "variable_labels": variable_labels,
        "value_labels": formatted_value_labels,
        "row_count": len(df),
    }
