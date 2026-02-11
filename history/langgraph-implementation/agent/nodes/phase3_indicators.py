"""
Phase 3: Indicator Nodes (Steps 9-11)

This module contains nodes for generating and validating indicators:
- Step 9: generate_indicators_node - LLM generates indicators JSON
- Step 10: validate_indicators_node - Validate indicators structure
- Step 11: review_indicators_node - Human review and approval
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from agent.state import (
    WorkflowState, ValidationResult,
    STEP_9_GENERATE_INDICATORS, STEP_10_VALIDATE_INDICATORS,
    STEP_11_REVIEW_INDICATORS
)
from agent.llm.clients import get_llm_client
from agent.llm.prompts import generate_indicators_prompt
from agent.config import DEFAULT_CONFIG
from agent.utils.tracing import trace_node

logger = logging.getLogger(__name__)


# =============================================================================
# Step 9: Generate Indicators
# =============================================================================

@trace_node("Step 9: Generate Indicators")
def generate_indicators_node(state: WorkflowState) -> dict:
    """
    Step 9: Generate indicators using LLM.

    This node invokes the LLM to group semantically related variables into
    indicators (composite measures) for cross-tabulation analysis. The node
    handles three scenarios:

    1. Initial generation: No feedback, generate indicators from scratch
    2. Validation retry: Validation failed, use validation error messages as feedback
    3. Human feedback retry: Human rejected indicators, use human feedback for revision

    The node generates a prompt, invokes the LLM, parses the JSON response,
    validates the structure, and saves the indicators to a JSON file.

    Args:
        state: Current workflow state. Must contain:
            - new_metadata: Metadata from new_data.sav (variable names, labels)
            - iteration_count: Current iteration number (for retry logic)
            - indicator_validation_result: Optional validation result from Step 10
            - indicator_feedback: Optional feedback from validation or human review

    Returns:
        Updated workflow state with:
            - indicators: Dict containing generated indicator definitions
            - current_step: Set to STEP_9_GENERATE_INDICATORS
            - iteration_count: Incremented if this is a retry
            - errors: List of errors (appended if any occur)
            - warnings: List of warnings (appended if any occur)

    Raises:
        ValueError: If new_metadata is missing or empty
        RuntimeError: If LLM invocation fails after retries

    Example:
        >>> state = {
        ...     "new_metadata": {"variable_names": ["sat_quality", "sat_price", ...]},
        ...     "iteration_count": 0
        ... }
        >>> new_state = generate_indicators_node(state)
        >>> print(new_state["indicators"]["indicators"][0]["name"])
        'Customer_Satisfaction_Index'
    """
    # Get new_metadata from state
    new_metadata = state.get("new_metadata")
    if not new_metadata:
        error_msg = "No new_metadata available in state. Cannot generate indicators."
        logger.error(error_msg)
        return {
            "current_step": STEP_9_GENERATE_INDICATORS,
            "errors": [error_msg],
        }

    logger.info("Step 9: Generating indicators")

    # Determine feedback type
    iteration_count = state.get("iteration_count", 0)
    validation_result = state.get("indicator_validation_result")
    human_feedback = state.get("indicator_feedback")

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

        # Build metadata list from new_metadata structure
        # new_metadata has: variable_names, variable_labels, value_labels
        metadata_list = _build_metadata_list(new_metadata)

        # Generate prompt with appropriate feedback
        prompt = generate_indicators_prompt(
            metadata=metadata_list,
            validation_feedback=validation_feedback,
            human_feedback=human_feedback if iteration_count > 0 else None
        )

        logger.info("Invoking LLM to generate indicators...")
        logger.debug(f"Prompt length: {len(prompt)} characters")

        # Invoke LLM
        response = llm_client.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)

        logger.info(f"LLM response received: {len(response_text)} characters")

        # Parse JSON response
        try:
            indicators = parse_llm_response(response_text)
        except ValueError as e:
            error_msg = f"Failed to parse LLM response as JSON: {str(e)}"
            logger.error(error_msg)
            logger.debug(f"LLM response: {response_text[:500]}...")

            # Store error as feedback for retry
            return {
                "current_step": STEP_9_GENERATE_INDICATORS,
                "iteration_count": iteration_count + 1,
                "indicator_feedback": error_msg,
                "errors": [error_msg],
            }

        # Validate indicators structure
        validation_error = _validate_indicators_structure(indicators)
        if validation_error:
            error_msg = f"Invalid indicators structure: {validation_error}"
            logger.error(error_msg)

            return {
                "current_step": STEP_9_GENERATE_INDICATORS,
                "iteration_count": iteration_count + 1,
                "indicator_feedback": error_msg,
                "errors": [error_msg],
            }

        # Get indicator count
        indicator_count = len(indicators.get("indicators", []))
        logger.info(f"Successfully generated {indicator_count} indicators")

        # Save to file
        output_path = _save_indicators(indicators, config)
        logger.info(f"Indicators saved to: {output_path}")

        # Prepare warnings
        warnings = state.get("warnings", []).copy()

        # Warn if no indicators generated (allowed case)
        if indicator_count == 0:
            warning_msg = (
                "No indicators generated. All variables will be analyzed individually. "
                "This is allowed if no meaningful groupings exist."
            )
            logger.warning(warning_msg)
            warnings.append(warning_msg)

        # Clear previous feedback on successful generation
        new_state = {
            "current_step": STEP_9_GENERATE_INDICATORS,
            "indicators": indicators,
            "indicator_feedback": None,  # Clear feedback on success
            "warnings": warnings,
        }

        # Only increment iteration_count if this was a retry
        if iteration_count > 0:
            new_state["iteration_count"] = iteration_count + 1

        return new_state

    except Exception as e:
        error_msg = f"Unexpected error generating indicators: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "current_step": STEP_9_GENERATE_INDICATORS,
            "errors": [error_msg],
        }


def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Parse LLM response text to extract JSON indicators.

    Handles common LLM formatting issues:
    - JSON wrapped in markdown code blocks (```json ... ```)
    - JSON with leading/trailing text
    - JSON with comments
    - Malformed JSON (missing quotes, trailing commas)

    Args:
        response_text: Raw text response from LLM

    Returns:
        Parsed dictionary containing indicators

    Raises:
        ValueError: If JSON cannot be extracted or parsed

    Example:
        >>> response = '{"indicators": [...]}'
        >>> indicators = parse_llm_response(response)
        >>> print(indicators["indicators"][0]["name"])
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


def _validate_indicators_structure(indicators: Dict[str, Any]) -> Optional[str]:
    """
    Validate the structure of generated indicators.

    Checks for:
    - Required top-level key "indicators"
    - indicators is a list
    - Each indicator has required fields (name, description, variables)
    - Variables array is valid (2-10 variables)
    - Variable names are strings

    Args:
        indicators: Parsed indicators dictionary

    Returns:
        None if valid, error message string if invalid
    """
    if not isinstance(indicators, dict):
        return "Indicators must be a JSON object"

    if "indicators" not in indicators:
        return "Missing required key 'indicators'"

    if not isinstance(indicators["indicators"], list):
        return "'indicators' must be a list"

    # Empty indicators list is allowed (warning, not error)
    if len(indicators["indicators"]) == 0:
        return None

    # Validate each indicator
    required_fields = ["name", "description", "variables"]

    for i, indicator in enumerate(indicators["indicators"]):
        if not isinstance(indicator, dict):
            return f"Indicator {i} is not a JSON object"

        # Check required fields
        for field in required_fields:
            if field not in indicator:
                return f"Indicator {i} missing required field '{field}'"

        # Validate variables array
        if not isinstance(indicator["variables"], list):
            return f"Indicator {i} 'variables' field must be a list"

        var_count = len(indicator["variables"])
        if var_count < 2:
            return f"Indicator {i} has only {var_count} variable(s). Minimum 2 required."

        if var_count > 10:
            return f"Indicator {i} has {var_count} variables. Maximum 10 allowed."

        # Validate variable names are strings
        for j, var in enumerate(indicator["variables"]):
            if not isinstance(var, str):
                return f"Indicator {i} variable {j} is not a string: {type(var).__name__}"

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


def _save_indicators(indicators: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Save indicators to JSON file with timestamp.

    Args:
        indicators: Indicators dictionary
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
    filename = f"indicators_{timestamp}.json"
    filepath = temp_dir / filename

    # Add timestamp to the indicators object
    indicators_with_metadata = {
        "generated_at": datetime.now().isoformat(),
        "indicator_count": len(indicators.get("indicators", [])),
        "indicators": indicators.get("indicators", [])
    }

    # Save with pretty formatting
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(indicators_with_metadata, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(indicators.get('indicators', []))} indicators to {filepath}")
    return str(filepath)


def _build_metadata_list(new_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build metadata list from new_metadata structure for LLM prompt.

    The new_metadata from Step 8 has:
    - variable_names: list of variable names
    - variable_labels: dict mapping names to labels
    - value_labels: dict mapping names to value labels

    This function converts to a list format expected by the indicator prompt.

    Args:
        new_metadata: Metadata dictionary from Step 8

    Returns:
        List of variable metadata dictionaries
    """
    metadata_list = []

    variable_names = new_metadata.get("variable_names", [])
    variable_labels = new_metadata.get("variable_labels", {})
    value_labels = new_metadata.get("value_labels", {})

    for var_name in variable_names:
        var_label = variable_labels.get(var_name, var_name)
        var_value_labels = value_labels.get(var_name, {})

        # Determine variable type from value labels
        if var_value_labels:
            # Has value labels => categorical
            var_type = "categorical"
        else:
            # No value labels => assume numeric
            var_type = "numeric"

        metadata_list.append({
            "name": var_name,
            "label": var_label,
            "variable_type": var_type,
            "value_labels": var_value_labels
        })

    return metadata_list


# =============================================================================
# Step 10: Validate Indicators
# =============================================================================

@trace_node("Step 10: Validate Indicators")
def validate_indicators_node(state: WorkflowState) -> dict:
    """
    Step 10: Validate indicators structure and references.

    This node validates:
    - JSON structure is correct
    - Indicator names are unique
    - Variables exist in new_metadata
    - Variables are not duplicated across indicators
    - Indicator sizes are within limits (2-10 variables)
    - Variable types are compatible (no mixing demographics with attitudinal)

    Args:
        state: Current workflow state. Must contain:
            - indicators: Generated indicators
            - new_metadata: Metadata from new_data.sav

    Returns:
        Updated workflow state with:
            - indicator_validation_result: ValidationResult object
            - current_step: Set to STEP_10_VALIDATE_INDICATORS
            - errors: List of errors (appended if validation fails)
            - warnings: List of warnings (appended if any warnings)

    Example:
        >>> state = {
        ...     "indicators": {"indicators": [...]},
        ...     "new_metadata": {"variable_names": [...]}
        ... }
        >>> new_state = validate_indicators_node(state)
        >>> print(new_state["indicator_validation_result"].is_valid)
        True
    """
    logger.info("Step 10: Validating indicators")

    # Get inputs from state
    indicators = state.get("indicators")
    new_metadata = state.get("new_metadata")

    # Validate required inputs
    if not indicators:
        error_msg = "No indicators available in state for validation"
        logger.error(error_msg)
        return {
            "current_step": STEP_10_VALIDATE_INDICATORS,
            "errors": [error_msg],
        }

    if not new_metadata:
        error_msg = "No new_metadata available in state for validation"
        logger.error(error_msg)
        return {
            "current_step": STEP_10_VALIDATE_INDICATORS,
            "errors": [error_msg],
        }

    try:
        # Import validation function
        from agent.validation.indicators import validate_indicators

        # Run validation
        logger.info(f"Validating {len(indicators.get('indicators', []))} indicators")
        validation_result = validate_indicators(indicators, new_metadata)

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
            "current_step": STEP_10_VALIDATE_INDICATORS,
            "indicator_validation_result": validation_result,
        }

        # Append errors to tracking state
        if validation_result['errors']:
            new_state["errors"] = validation_result['errors']

        # Append warnings to tracking state
        if validation_result['warnings']:
            new_state["warnings"] = validation_result['warnings']

        return new_state

    except Exception as e:
        error_msg = f"Unexpected error during indicators validation: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "current_step": STEP_10_VALIDATE_INDICATORS,
            "errors": [error_msg],
        }


@trace_node("Step 11: Review Indicators")
def review_indicators_node(state: WorkflowState) -> dict:
    """
    Step 11: Human review and approval of indicators.

    This node implements the human-in-the-loop review pattern using LangGraph's
    interrupt mechanism. It generates a markdown review document and pauses the
    workflow to wait for human approval/rejection.

    The node:
    1. Generates a comprehensive markdown review document
    2. Saves it to output/reviews/indicators_review.md
    3. Triggers LangGraph interrupt to pause workflow
    4. Returns state unchanged (approval status set by human via UI)

    Human actions via Agent Chat UI:
    - Approve: Sets indicators_approved=True, workflow proceeds to Step 12
    - Reject with feedback: Sets indicator_feedback, workflow retries Step 9
    - Modify: Human can manually edit indicators before approval

    Args:
        state: Current workflow state. Must contain:
            - indicators: Generated indicators from Step 9
            - indicator_validation_result: Validation result from Step 10
            - iteration_count: Current iteration number
            - indicator_feedback: Previous feedback (if retry)

    Returns:
        Updated workflow state with:
            - current_step: Set to STEP_11_REVIEW_INDICATORS
            - requires_human_review: Set to True

    Note:
        - DOES NOT set indicators_approved - this is set by human via UI
        - Workflow resumes via conditional routing in agent/edges.py
        - Use should_approve_indicators() routing function after this node
    """
    logger.info("Step 11: Generating indicators review document for human approval")

    # Get required inputs from state
    indicators = state.get("indicators")
    validation_result = state.get("indicator_validation_result")
    iteration_count = state.get("iteration_count", 0)
    previous_feedback = state.get("indicator_feedback")
    config = state.get("config", DEFAULT_CONFIG)

    # Check for auto-approval (CI/CD and testing mode)
    auto_approve = config.get("auto_approve_indicators", False)

    # Validate required inputs
    if not indicators:
        error_msg = "No indicators available in state for review"
        logger.error(error_msg)
        return {
            "current_step": STEP_11_REVIEW_INDICATORS,
            "errors": [error_msg],
            "requires_human_review": not auto_approve,
            "indicators_approved": auto_approve,
        }

    try:
        # Generate markdown review document
        review_doc = _generate_indicators_review_markdown(
            indicators=indicators,
            validation_result=validation_result,
            iteration_count=iteration_count,
            previous_feedback=previous_feedback
        )

        # Save review document to fixed path
        output_dir = Path(config.get("output_dir", "output"))
        reviews_dir = output_dir / "reviews"
        reviews_dir.mkdir(parents=True, exist_ok=True)

        review_path = reviews_dir / "indicators_review.md"
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
                "step": 11,
                "task": "indicators",
                "review_document_path": str(review_path),
                "validation_passed": validation_result['is_valid'] if validation_result else False,
                "iteration": iteration_count,
                "message": (
                    "Please review the indicators at: {}\n\n"
                    "Actions:\n"
                    "- Approve: Indicators look correct, proceed to table specification\n"
                    "- Reject with Feedback: Indicators need revision, provide feedback below\n"
                    "- Modify: You will manually edit the indicators"
                ).format(review_path)
            })

        # Return state with approval status
        return {
            "current_step": STEP_11_REVIEW_INDICATORS,
            "requires_human_review": not auto_approve,
            "indicators_approved": auto_approve,
        }

    except Exception as e:
        error_msg = f"Error during indicators review: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "current_step": STEP_11_REVIEW_INDICATORS,
            "errors": [error_msg],
            "requires_human_review": not auto_approve,
            "indicators_approved": auto_approve,
        }


def _generate_indicators_review_markdown(
    indicators: Dict[str, Any],
    validation_result: Optional[ValidationResult],
    iteration_count: int,
    previous_feedback: Optional[str]
) -> str:
    """
    Generate markdown review document for indicators.

    Creates a comprehensive, human-readable review document with:
    - Summary statistics
    - Validation results
    - Individual indicator details with variable lists
    - Action instructions

    Args:
        indicators: Generated indicators dictionary
        validation_result: ValidationResult from Step 10
        iteration_count: Current iteration number
        previous_feedback: Previous feedback (if retry)

    Returns:
        Complete markdown document as string
    """
    lines = []

    # Header
    lines.append("# Indicators Review")
    lines.append("")
    lines.append("**Status**: Pending Your Review")
    lines.append("")

    # Summary
    lines.append("## Summary")
    indicators_list = indicators.get("indicators", [])
    lines.append(f"- Total Indicators: {len(indicators_list)}")

    # Count total variables
    all_variables = set()
    for indicator in indicators_list:
        for var in indicator.get("variables", []):
            all_variables.add(var)

    lines.append(f"- Unique Variables Used: {len(all_variables)}")
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

    # Indicators Detail
    lines.append("## Indicators")
    lines.append("")

    if not indicators_list:
        lines.append("*No indicators generated.*")
        lines.append("")
    else:
        for i, indicator in enumerate(indicators_list, 1):
            name = indicator.get("name", "N/A")
            description = indicator.get("description", "")
            variables = indicator.get("variables", [])

            lines.append(f"### Indicator {i}: {name}")
            lines.append("")

            if description:
                lines.append(f"**Description**: {description}")
                lines.append("")

            lines.append(f"**Variables** ({len(variables)}):")
            for var in variables:
                lines.append(f"- {var}")
            lines.append("")

    # Actions Section
    lines.append("## Actions")
    lines.append("")
    lines.append("Please review and select an action:")
    lines.append("")
    lines.append("- [ ] **Approve** - Indicators look correct, proceed to table specification")
    lines.append("- [ ] **Reject with Feedback** - Indicators need revision, provide feedback below")
    lines.append("- [ ] **Modify** - You will manually edit the indicators")
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
    lines.append("- Add indicator for customer satisfaction variables")
    lines.append("- Remove demographic variables from Product_Quality indicator")
    lines.append("- Split Customer_Experience into two smaller indicators")
    lines.append("- Rename indicator to use more descriptive name")
    lines.append("")

    return "\n".join(lines)
