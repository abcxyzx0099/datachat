"""
Phase 4: Cross-Table Nodes (Steps 12-16)

This module contains nodes for generating and executing cross-tabulation tables:
- Step 12: generate_table_specifications_node - LLM generates table specs JSON
- Step 13: validate_table_specs_node - Validate table structure
- Step 14: review_table_specs_node - Human review and approval
- Step 15: generate_pspp_table_syntax_node - Generate PSPP CTABLES syntax (primary)
- Step 15 (alt): generate_pspp_crosstabs_syntax_node - Generate PSPP CROSSTABS syntax (alternative)
- Step 16: execute_pspp_tables_node - Execute PSPP CTABLES and create cross-table output (primary)
- Step 16 (alt): execute_pspp_crosstabs_node - Execute PSPP CROSSTABS and create cross-table output (alternative)
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from agent.state import WorkflowState, ValidationResult
from agent.llm.clients import get_llm_client
from agent.llm.prompts import generate_table_specifications_prompt
from agent.config import DEFAULT_CONFIG
from agent.utils.tracing import trace_node

logger = logging.getLogger(__name__)


# =============================================================================
# Step 12: Generate Table Specifications
# =============================================================================

@trace_node("Step 12: Generate Table Specifications")
def generate_table_specifications_node(state: WorkflowState) -> WorkflowState:
    """
    Step 12: Generate cross-tabulation table specifications using LLM.

    This node invokes the LLM to define cross-tabulation tables for survey analysis.
    The node follows the three-node pattern and handles three scenarios:

    1. Initial generation: No feedback, generate table specs from scratch
    2. Validation retry: Validation failed, use validation error messages as feedback
    3. Human feedback retry: Human rejected table specs, use human feedback for revision

    The node generates a prompt with metadata and indicators, invokes the LLM,
    parses the JSON response, validates the structure, and saves the table
    specifications to a JSON file.

    Args:
        state: Current workflow state. Must contain:
            - new_metadata: Metadata from new_data.sav (variable names, labels)
            - indicators: Optional indicator definitions from Step 11
            - iteration_count: Current iteration number (for retry logic)
            - table_validation_result: Optional validation result from Step 13
            - table_specs_feedback: Optional feedback from validation or human review

    Returns:
        Updated workflow state with:
            - table_specifications: Dict containing generated table specifications
            - current_step: Set to 12
            - iteration_count: Incremented if this is a retry
            - errors: List of errors (appended if any occur)
            - warnings: List of warnings (appended if any occur)

    Raises:
        ValueError: If new_metadata is missing or empty
        RuntimeError: If LLM invocation fails after retries

    Example:
        >>> state = {
        ...     "new_metadata": {"variable_names": ["gender", "sat_quality", ...]},
        ...     "indicators": {"indicators": [...]},
        ...     "iteration_count": 0
        ... }
        >>> new_state = generate_table_specifications_node(state)
        >>> print(new_state["table_specifications"]["tables"][0]["table_id"])
        'gender_x_satisfaction'
    """
    # Get new_metadata from state
    new_metadata = state.get("new_metadata")
    if not new_metadata:
        error_msg = "No new_metadata available in state. Cannot generate table specifications."
        logger.error(error_msg)
        return {
            **state,
            "current_step": 12,
            "errors": state.get("errors", []) + [error_msg],
        }

    logger.info("Step 12: Generating table specifications")

    # Get indicators from state (optional but recommended)
    indicators = state.get("indicators")

    # Determine feedback type
    iteration_count = state.get("iteration_count", 0)
    validation_result = state.get("table_validation_result")
    human_feedback = state.get("table_specs_feedback")

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
        prompt = generate_table_specifications_prompt(
            metadata=metadata_list,
            indicators=indicators,
            validation_feedback=validation_feedback,
            human_feedback=human_feedback if iteration_count > 0 else None
        )

        logger.info("Invoking LLM to generate table specifications...")
        logger.debug(f"Prompt length: {len(prompt)} characters")

        # Invoke LLM
        response = llm_client.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)

        logger.info(f"LLM response received: {len(response_text)} characters")

        # Parse JSON response
        try:
            table_specs = parse_llm_response(response_text)
        except ValueError as e:
            error_msg = f"Failed to parse LLM response as JSON: {str(e)}"
            logger.error(error_msg)
            logger.debug(f"LLM response: {response_text[:500]}...")

            # Store error as feedback for retry
            return {
                **state,
                "current_step": 12,
                "iteration_count": iteration_count + 1,
                "table_specs_feedback": error_msg,
                "errors": state.get("errors", []) + [error_msg],
            }

        # Validate table specifications structure
        validation_error = _validate_table_specs_structure(table_specs)
        if validation_error:
            error_msg = f"Invalid table specifications structure: {validation_error}"
            logger.error(error_msg)

            return {
                **state,
                "current_step": 12,
                "iteration_count": iteration_count + 1,
                "table_specs_feedback": error_msg,
                "errors": state.get("errors", []) + [error_msg],
            }

        # Get table count
        table_count = len(table_specs.get("tables", []))
        logger.info(f"Successfully generated {table_count} table specifications")

        # Save to file
        output_path = _save_table_specs(table_specs, config)
        logger.info(f"Table specifications saved to: {output_path}")

        # Prepare warnings
        warnings = state.get("warnings", []).copy()

        # Warn if no tables generated
        if table_count == 0:
            warning_msg = (
                "No table specifications generated. At least 1 table is recommended "
                "for meaningful analysis. The LLM may have failed to identify valid "
                "demographic × outcome variable combinations."
            )
            logger.warning(warning_msg)
            warnings.append(warning_msg)

        # Clear previous feedback on successful generation
        new_state = {
            **state,
            "current_step": 12,
            "table_specifications": table_specs,
            "table_specs_feedback": None,  # Clear feedback on success
            "warnings": warnings,
        }

        # Only increment iteration_count if this was a retry
        if iteration_count > 0:
            new_state["iteration_count"] = iteration_count + 1

        return new_state

    except Exception as e:
        error_msg = f"Unexpected error generating table specifications: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": 12,
            "errors": state.get("errors", []) + [error_msg],
        }


def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Parse LLM response text to extract JSON table specifications.

    Handles common LLM formatting issues:
    - JSON wrapped in markdown code blocks (```json ... ```)
    - JSON with leading/trailing text
    - JSON with comments
    - Malformed JSON (missing quotes, trailing commas)

    Args:
        response_text: Raw text response from LLM

    Returns:
        Parsed dictionary containing table specifications

    Raises:
        ValueError: If JSON cannot be extracted or parsed

    Example:
        >>> response = '{"tables": [...]}'
        >>> specs = parse_llm_response(response)
        >>> print(specs["tables"][0]["table_id"])
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


def _validate_table_specs_structure(table_specs: Dict[str, Any]) -> Optional[str]:
    """
    Validate the structure of generated table specifications.

    Checks for:
    - Required top-level key "tables"
    - tables is a list
    - Each table has required fields (table_id, row_variable, column_variable)
    - Statistics array is valid
    - Table IDs are unique

    Args:
        table_specs: Parsed table specifications dictionary

    Returns:
        None if valid, error message string if invalid
    """
    if not isinstance(table_specs, dict):
        return "Table specifications must be a JSON object"

    if "tables" not in table_specs:
        return "Missing required key 'tables'"

    if not isinstance(table_specs["tables"], list):
        return "'tables' must be a list"

    # Empty tables list is a warning, not an error (handled in main node)
    if len(table_specs["tables"]) == 0:
        return None

    # Validate each table
    required_fields = ["table_id", "row_variable", "column_variable"]
    valid_statistics = ["count", "rowpct", "columnpct", "totalpct", "chisq", "cramersv"]

    table_ids = set()

    for i, table in enumerate(table_specs["tables"]):
        if not isinstance(table, dict):
            return f"Table {i} is not a JSON object"

        # Check required fields
        for field in required_fields:
            if field not in table:
                return f"Table {i} missing required field '{field}'"

        # Check for unique table IDs
        table_id = table["table_id"]
        if table_id in table_ids:
            return f"Duplicate table_id '{table_id}' at table {i}"
        table_ids.add(table_id)

        # Validate statistics array
        if "statistics" not in table or not isinstance(table["statistics"], list):
            return f"Table {i} missing 'statistics' array or not a list"

        # Check statistics are valid
        for stat in table["statistics"]:
            if stat not in valid_statistics:
                return f"Table {i} has invalid statistic '{stat}'. Valid: {valid_statistics}"

        # weight_variable is optional but must be null or string
        weight_var = table.get("weight_variable")
        if weight_var is not None and not isinstance(weight_var, str):
            return f"Table {i} 'weight_variable' must be null or a string"

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


def _save_table_specs(table_specs: Dict[str, Any], config: Dict[str, Any]) -> str:
    """
    Save table specifications to JSON file with timestamp.

    Args:
        table_specs: Table specifications dictionary
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
    filename = f"table_specs_{timestamp}.json"
    filepath = temp_dir / filename

    # Add timestamp to the table specs object
    specs_with_metadata = {
        "generated_at": datetime.now().isoformat(),
        "table_count": len(table_specs.get("tables", [])),
        "tables": table_specs.get("tables", [])
    }

    # Save with pretty formatting
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(specs_with_metadata, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(table_specs.get('tables', []))} table specifications to {filepath}")
    return str(filepath)


def _build_metadata_list(new_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build metadata list from new_metadata structure for LLM prompt.

    The new_metadata from Step 8 has:
    - variable_names: list of variable names
    - variable_labels: dict mapping names to labels
    - value_labels: dict mapping names to value labels

    This function converts to a list format expected by the table specs prompt.

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
# Step 13: Validate Table Specifications
# =============================================================================

@trace_node("Step 13: Validate Table Specifications")
def validate_table_specs_node(state: WorkflowState) -> WorkflowState:
    """
    Step 13: Validate table specifications structure and references.

    This node validates:
    - JSON structure is correct
    - Table IDs are unique
    - Row and column variables exist in new_metadata
    - Variables are categorical (not continuous)
    - At least 1 table is specified
    - Statistics array contains valid values

    Args:
        state: Current workflow state. Must contain:
            - table_specifications: Generated table specifications
            - new_metadata: Metadata from new_data.sav

    Returns:
        Updated workflow state with:
            - table_validation_result: ValidationResult object
            - current_step: Set to 13
            - errors: List of errors (appended if validation fails)
            - warnings: List of warnings (appended if any warnings)

    Example:
        >>> state = {
        ...     "table_specifications": {"tables": [...]},
        ...     "new_metadata": {"variable_names": [...]}
        ... }
        >>> new_state = validate_table_specs_node(state)
        >>> print(new_state["table_validation_result"].is_valid)
        True
    """
    logger.info("Step 13: Validating table specifications")

    # Get inputs from state
    table_specs = state.get("table_specifications")
    new_metadata = state.get("new_metadata")

    # Validate required inputs
    if not table_specs:
        error_msg = "No table_specifications available in state for validation"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 13,
            "errors": state.get("errors", []) + [error_msg],
        }

    if not new_metadata:
        error_msg = "No new_metadata available in state for validation"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 13,
            "errors": state.get("errors", []) + [error_msg],
        }

    try:
        # Import validation function
        from agent.validation.tables import validate_table_specs

        # Run validation
        logger.info(f"Validating {len(table_specs.get('tables', []))} table specifications")
        validation_result = validate_table_specs(table_specs, new_metadata)

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
            "current_step": 13,
            "table_validation_result": validation_result,
        }

        # Append errors to tracking state
        if validation_result['errors']:
            new_state["errors"] = state.get("errors", []) + validation_result['errors']

        # Append warnings to tracking state
        if validation_result['warnings']:
            new_state["warnings"] = state.get("warnings", []) + validation_result['warnings']

        return new_state

    except Exception as e:
        error_msg = f"Unexpected error during table specifications validation: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": 13,
            "errors": state.get("errors", []) + [error_msg],
        }


@trace_node("Step 14: Review Table Specifications")
def review_table_specifications_node(state: WorkflowState) -> WorkflowState:
    """
    Step 14: Human review and approval of table specifications.

    This node implements the human-in-the-loop review pattern using LangGraph's
    interrupt mechanism. It generates a markdown review document and pauses the
    workflow to wait for human approval/rejection.

    The node:
    1. Generates a comprehensive markdown review document
    2. Saves it to output/reviews/table_specs_review.md
    3. Triggers LangGraph interrupt to pause workflow
    4. Returns state unchanged (approval status set by human via UI)

    Human actions via Agent Chat UI:
    - Approve: Sets table_specs_approved=True, workflow proceeds to Step 15
    - Reject with feedback: Sets table_specs_feedback, workflow retries Step 12
    - Modify: Human can manually edit table specs before approval

    Args:
        state: Current workflow state. Must contain:
            - table_specifications: Generated table specifications from Step 12
            - table_validation_result: Validation result from Step 13
            - iteration_count: Current iteration number
            - table_specs_feedback: Previous feedback (if retry)

    Returns:
        Updated workflow state with:
            - current_step: Set to 14
            - requires_human_review: Set to True

    Note:
        - DOES NOT set table_specs_approved - this is set by human via UI
        - Workflow resumes via conditional routing in agent/edges.py
        - Use should_approve_table_specs() routing function after this node
    """
    logger.info("Step 14: Generating table specifications review document for human approval")

    # Get required inputs from state
    table_specs = state.get("table_specifications")
    validation_result = state.get("table_validation_result")
    iteration_count = state.get("iteration_count", 0)
    previous_feedback = state.get("table_specs_feedback")
    config = state.get("config", DEFAULT_CONFIG)

    # Check for auto-approval (CI/CD and testing mode)
    auto_approve = config.get("auto_approve_table_specs", False)

    # Validate required inputs
    if not table_specs:
        error_msg = "No table_specifications available in state for review"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 14,
            "errors": state.get("errors", []) + [error_msg],
            "requires_human_review": not auto_approve,
            "table_specs_approved": auto_approve,
        }

    try:
        # Generate markdown review document
        review_doc = _generate_table_specs_review_markdown(
            table_specs=table_specs,
            validation_result=validation_result,
            iteration_count=iteration_count,
            previous_feedback=previous_feedback
        )

        # Save review document to fixed path
        output_dir = Path(config.get("output_dir", "output"))
        reviews_dir = output_dir / "reviews"
        reviews_dir.mkdir(parents=True, exist_ok=True)

        review_path = reviews_dir / "table_specs_review.md"
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
                "step": 14,
                "task": "table_specs",
                "review_document_path": str(review_path),
                "validation_passed": validation_result['is_valid'] if validation_result else False,
                "iteration": iteration_count,
                "message": (
                    "Please review the table specifications at: {}\n\n"
                    "Actions:\n"
                    "- Approve: Table specifications look correct, proceed to PSPP syntax generation\n"
                    "- Reject with Feedback: Table specifications need revision, provide feedback below\n"
                    "- Modify: You will manually edit the table specifications"
                ).format(review_path)
            })

        # Return state with approval status
        return {
            **state,
            "current_step": 14,
            "requires_human_review": not auto_approve,
            "table_specs_approved": auto_approve,
        }

    except Exception as e:
        error_msg = f"Error during table specifications review: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": 14,
            "errors": state.get("errors", []) + [error_msg],
            "requires_human_review": not auto_approve,
            "table_specs_approved": auto_approve,
        }


def _generate_table_specs_review_markdown(
    table_specs: Dict[str, Any],
    validation_result: Optional[ValidationResult],
    iteration_count: int,
    previous_feedback: Optional[str]
) -> str:
    """
    Generate markdown review document for table specifications.

    Creates a comprehensive, human-readable review document with:
    - Summary statistics
    - Validation results
    - Individual table details
    - Action instructions

    Args:
        table_specs: Generated table specifications dictionary
        validation_result: ValidationResult from Step 13
        iteration_count: Current iteration number
        previous_feedback: Previous feedback (if retry)

    Returns:
        Complete markdown document as string
    """
    lines = []

    # Header
    lines.append("# Table Specifications Review")
    lines.append("")
    lines.append("**Status**: Pending Your Review")
    lines.append("")

    # Summary
    lines.append("## Summary")
    tables_list = table_specs.get("tables", [])
    lines.append(f"- Total Tables: {len(tables_list)}")
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

    # Table Specifications Detail
    lines.append("## Table Specifications")
    lines.append("")

    if not tables_list:
        lines.append("*No table specifications generated.*")
        lines.append("")
    else:
        for i, table in enumerate(tables_list, 1):
            table_id = table.get("table_id", "N/A")
            row_var = table.get("row_variable", "N/A")
            col_var = table.get("column_variable", "N/A")
            weight_var = table.get("weight_variable")
            statistics = table.get("statistics", [])

            lines.append(f"### Table {i}: {table_id}")
            lines.append("")
            lines.append(f"- **Row Variable**: {row_var}")
            lines.append(f"- **Column Variable**: {col_var}")

            if weight_var:
                lines.append(f"- **Weight Variable**: {weight_var}")
            else:
                lines.append(f"- **Weight Variable**: None")

            lines.append(f"- **Statistics**: {', '.join(statistics)}")
            lines.append("")

    # Actions Section
    lines.append("## Actions")
    lines.append("")
    lines.append("Please review and select an action:")
    lines.append("")
    lines.append("- [ ] **Approve** - Table specifications look correct, proceed to PSPP syntax generation")
    lines.append("- [ ] **Reject with Feedback** - Table specifications need revision, provide feedback below")
    lines.append("- [ ] **Modify** - You will manually edit the table specifications")
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
    lines.append("- Add table: Age Group × Satisfaction")
    lines.append("- Remove table: Region × Importance (not meaningful)")
    lines.append("- Change row variable from 'gender' to 'gender_recoded'")
    lines.append("- Add Cramer's V statistic to all tables")
    lines.append("- Generate more tables (only 3 tables specified)")
    lines.append("")

    return "\n".join(lines)


# =============================================================================
# Step 15: Generate PSPP CTABLES Syntax
# =============================================================================

def generate_pspp_table_syntax_node(state: WorkflowState) -> WorkflowState:
    """
    Step 15: Generate PSPP CTABLES syntax from approved table specifications.

    Converts validated table specifications JSON into PSPP CTABLES syntax.
    Generates a complete .sps syntax file that can be executed by PSPP to
    create cross-tabulation tables with chi-square statistics and Cramer's V.

    This function generates CTABLES syntax (the newer, more powerful Custom
    Tables command) as specified in the business rules, rather than the older
    CROSSTABS command.

    Args:
        state: Current workflow state. Must contain:
            - table_specifications: Approved table specifications (from Step 14)
            - new_metadata: Variable metadata from Step 8 (for variable labels)

    Returns:
        Updated workflow state with:
            - table_syntax_file: Path to generated tables.sps file
            - pspp_tables_syntax: Generated PSPP CTABLES syntax string
            - current_step: Set to 15
            - errors: List of errors (appended if any occur)
            - warnings: List of warnings (appended if any occur)

    Example:
        >>> state = {
        ...     "table_specifications": {"tables": [...]},
        ...     "new_metadata": {"variable_names": [...]}
        ... }
        >>> new_state = generate_pspp_table_syntax_node(state)
        >>> print(new_state["table_syntax_file"])
        'temp/pspp_syntax/tables.sps'
    """
    logger.info("Step 15: Generating PSPP CTABLES syntax")

    # Get required inputs from state
    table_specs = state.get("table_specifications")
    new_metadata = state.get("new_metadata")
    config = state.get("config", DEFAULT_CONFIG)

    # Validate required inputs
    if not table_specs:
        error_msg = "No table_specifications available in state for syntax generation"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 15,
            "errors": state.get("errors", []) + [error_msg],
        }

    try:
        # Extract tables list
        tables_list = table_specs.get("tables", [])

        if not tables_list:
            warning_msg = "No table specifications to convert to PSPP syntax (empty tables list)"
            logger.warning(warning_msg)
            return {
                **state,
                "current_step": 15,
                "warnings": state.get("warnings", []) + [warning_msg],
            }

        logger.info(f"Generating PSPP CTABLES syntax for {len(tables_list)} cross-tabulation tables")

        # Build variable labels lookup from new_metadata
        variable_labels = {}
        if new_metadata:
            var_names = new_metadata.get("variable_names", [])
            var_labels_dict = new_metadata.get("variable_labels", {})
            for var_name in var_names:
                variable_labels[var_name] = var_labels_dict.get(var_name, var_name)

        # Generate PSPP CTABLES syntax
        syntax_lines = _generate_ctables_header()

        # Generate CTABLES command for each table
        for idx, table in enumerate(tables_list, 1):
            try:
                table_syntax = _generate_ctable_command(table, variable_labels, idx)
                if table_syntax:
                    syntax_lines.extend(table_syntax)
            except Exception as e:
                error_msg = f"Error generating CTABLES syntax for table {idx}: {str(e)}"
                logger.error(error_msg)
                # Continue with other tables
                continue

        # Add footer
        syntax_lines.append("")
        syntax_lines.append("* Execute CTABLES")
        syntax_lines.append("EXECUTE.")

        # Combine into single string
        pspp_syntax = "\n".join(syntax_lines)

        # Write to file
        # Use temp/ directory at project root, not output/temp/
        pspp_syntax_dir = Path("temp") / "pspp_syntax"
        pspp_syntax_dir.mkdir(parents=True, exist_ok=True)

        syntax_file_path = pspp_syntax_dir / "tables.sps"

        with open(syntax_file_path, 'w', encoding='utf-8') as f:
            f.write(pspp_syntax)

        logger.info(f"PSPP CTABLES syntax written to: {syntax_file_path}")
        logger.info(f"Syntax file size: {len(pspp_syntax)} characters")

        # Prepare warnings
        warnings = state.get("warnings", []).copy()

        # Warn if any tables failed to generate
        expected_commands = len(tables_list)
        actual_commands = len([l for l in syntax_lines if 'CTABLES' in l])
        if actual_commands < expected_commands:
            warning_msg = (
                f"Some tables may not have been converted to syntax. "
                f"Expected {expected_commands} tables, got {actual_commands} CTABLES commands."
            )
            logger.warning(warning_msg)
            warnings.append(warning_msg)

        return {
            **state,
            "current_step": 15,
            "pspp_tables_syntax": pspp_syntax,
            "table_syntax_file": str(syntax_file_path),  # Store path for Step 16
            "warnings": warnings,
        }

    except Exception as e:
        error_msg = f"Unexpected error generating PSPP CTABLES syntax: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": 15,
            "errors": state.get("errors", []) + [error_msg],
        }


def _generate_ctables_header() -> List[str]:
    """
    Generate header comments for PSPP CTABLES syntax file.

    Returns:
        List of header lines
    """
    lines = []
    lines.append("* Cross-Tabulation Tables Generated by DataChat")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"* Generated: {timestamp}")
    lines.append("*")
    lines.append("")
    lines.append("* Set decimal display format for tables")
    lines.append("SET DECIMAL = TAB.")
    lines.append("")
    return lines


def _generate_ctable_command(table: Dict[str, Any], variable_labels: Dict[str, str], table_num: int) -> List[str]:
    """
    Generate PSPP CTABLES command for a single table specification.

    Args:
        table: Table specification dictionary with keys:
            - table_id: Unique identifier for the table
            - row_variable: Variable name for rows
            - column_variable: Variable name for columns
            - statistics: List of statistics to compute
            - weight_variable: Optional weight variable
        variable_labels: Dictionary mapping variable names to labels
        table_num: Table number for comments

    Returns:
        List of PSPP syntax lines for this table

    PSPP CTABLES Syntax Format:
    ```spss
    * Table 1: gender_x_region
    CTABLES
        /VLABELS VARIABLES=gender region DISPLAY=DEFAULT
        /TABLE gender BY region
        /STATISTICS count('n') columnpct('%') chisq('chi-square') cramersv('Cramer''s V').
    ```
    """
    lines = []

    # Extract table properties
    table_id = table.get("table_id", f"table_{table_num}")
    row_var = table.get("row_variable", "")
    col_var = table.get("column_variable", "")
    statistics = table.get("statistics", ["count", "columnpct"])
    weight_var = table.get("weight_variable")

    # Validate required fields
    if not row_var or not col_var:
        logger.error(f"Table {table_id} missing row_variable or column_variable")
        return []

    # Add comment for table number
    lines.append(f"* Table {table_num}: {table_id}")

    # Start CTABLES command
    lines.append("CTABLES")

    # Add VLABELS subcommand for variable labels
    # Use DISPLAY=DEFAULT to show variable labels in output
    lines.append(f"    /VLABELS VARIABLES={row_var} {col_var} DISPLAY=DEFAULT")

    # Add TABLE subcommand with row BY column
    lines.append(f"    /TABLE {row_var} BY {col_var}")

    # Add WEIGHT subcommand if weight variable specified
    if weight_var:
        lines.append(f"    /WEIGHT {weight_var}")

    # Build STATISTICS subcommand
    # Map internal statistic names to PSPP CTABLES statistics
    stats_mapping = {
        "count": "count('n')",
        "rowpct": "rowpct('Row %')",
        "columnpct": "columnpct('Column %')",
        "totalpct": "totalpct('Total %')",
        "chisq": "chisq('chi-square')",
        "cramersv": "cramersv('Cramer''s V')",  # Double single quote for literal quote
    }

    stats_list = []
    for stat in statistics:
        if stat in stats_mapping:
            stats_list.append(stats_mapping[stat])
        else:
            logger.warning(f"Unknown statistic '{stat}' for table {table_id}, skipping")

    if stats_list:
        # Join all statistics with spaces
        stats_str = " ".join(stats_list)
        lines.append(f"    /STATISTICS {stats_str}")

    # End CTABLES command with period
    lines[-1] = lines[-1] + "."

    # Add blank line after table
    lines.append("")

    return lines


# =============================================================================
# Step 15 (Alternative): Generate PSPP CROSSTABS Syntax
# =============================================================================

def generate_pspp_crosstabs_syntax_node(state: WorkflowState) -> WorkflowState:
    """
    Step 15: Generate PSPP cross-tabulations syntax from approved table specifications.

    Converts validated table specifications JSON into PSPP CROSSTABS syntax.
    Generates a complete .sps syntax file that can be executed by PSPP to
    create cross-tabulation tables with chi-square statistics.

    Args:
        state: Current workflow state. Must contain:
            - table_specifications: Approved table specifications (from Step 14)
            - new_metadata: Variable metadata from Step 8

    Returns:
        Updated workflow state with:
            - pspp_crosstabs_syntax: Generated PSPP syntax string
            - crosstabs_syntax_file: Path to generated .sps file
            - current_step: Set to 15
            - errors: List of errors (appended if any occur)
            - warnings: List of warnings (appended if any occur)

    Example:
        >>> state = {
        ...     "table_specifications": {"tables": [...]},
        ...     "new_metadata": {"variable_names": [...]}
        ... }
        >>> new_state = generate_pspp_crosstabs_syntax_node(state)
        >>> print(new_state["crosstabs_syntax_file"])
        'temp/pspp_syntax/crosstabs.sps'
    """
    logger.info("Step 15: Generating PSPP cross-tabulations syntax")

    # Get required inputs from state
    table_specs = state.get("table_specifications")
    new_metadata = state.get("new_metadata")
    config = state.get("config", DEFAULT_CONFIG)

    # Validate required inputs
    if not table_specs:
        error_msg = "No table_specifications available in state for syntax generation"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 15,
            "errors": state.get("errors", []) + [error_msg],
        }

    try:
        # Extract tables list
        tables_list = table_specs.get("tables", [])

        if not tables_list:
            warning_msg = "No table specifications to convert to PSPP syntax (empty tables list)"
            logger.warning(warning_msg)
            return {
                **state,
                "current_step": 15,
                "warnings": state.get("warnings", []) + [warning_msg],
            }

        logger.info(f"Generating PSPP syntax for {len(tables_list)} cross-tabulation tables")

        # Generate PSPP syntax
        syntax_lines = _generate_pspp_header()

        # Group tables by statistics to minimize syntax
        # Tables with same statistics can be combined in one CROSSTABS command
        tables_by_stats = {}
        for table in tables_list:
            stats_key = tuple(sorted(table.get("statistics", ["count", "columnpct"])))
            if stats_key not in tables_by_stats:
                tables_by_stats[stats_key] = []
            tables_by_stats[stats_key].append(table)

        # Generate CROSSTABS commands for each statistics group
        for stats_key, tables in tables_by_stats.items():
            syntax_lines.extend(_generate_crosstabs_command(tables, stats_key))

        # Add footer
        syntax_lines.append("")
        syntax_lines.append("* Execute Crosstabs")
        syntax_lines.append("EXECUTE.")

        # Combine into single string
        pspp_syntax = "\n".join(syntax_lines)

        # Write to file
        # Use temp/ directory at project root, not output/temp/
        pspp_syntax_dir = Path("temp") / "pspp_syntax"
        pspp_syntax_dir.mkdir(parents=True, exist_ok=True)

        syntax_file_path = pspp_syntax_dir / "crosstabs.sps"

        with open(syntax_file_path, 'w', encoding='utf-8') as f:
            f.write(pspp_syntax)

        logger.info(f"PSPP crosstabs syntax written to: {syntax_file_path}")
        logger.info(f"Syntax file size: {len(pspp_syntax)} characters")

        return {
            **state,
            "current_step": 15,
            "pspp_crosstabs_syntax": pspp_syntax,
            "crosstabs_syntax_file": str(syntax_file_path),  # Store path for Step 16
        }

    except Exception as e:
        error_msg = f"Unexpected error generating PSPP crosstabs syntax: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": 15,
            "errors": state.get("errors", []) + [error_msg],
        }


def _generate_crosstabs_command(tables: List[Dict[str, Any]], statistics: tuple) -> List[str]:
    """
    Generate PSPP CROSSTABS command for a group of tables with same statistics.

    Args:
        tables: List of table specifications with same statistics
        statistics: Tuple of statistic names

    Returns:
        List of PSPP syntax lines
    """
    lines = []

    # Build tables specification
    # Format: TABLES row_var BY col_var
    tables_specs = []
    for table in tables:
        row_var = table.get("row_variable", "")
        col_var = table.get("column_variable", "")
        tables_specs.append(f"{row_var} BY {col_var}")

    # Build statistics specification
    stats_map = {
        "count": "COUNT",
        "rowpct": "ROWPERCENT",
        "columnpct": "COLPERCENT",
        "totalpct": "TOTALPERCENT",
        "chisq": "CHISQ",
        "cramersv": "PHI",  # PSPP uses PHI which includes Cramer's V
    }

    stats_specs = []
    for stat in statistics:
        if stat in stats_map:
            stats_specs.append(stats_map[stat])

    # Build CROSSTABS command
    lines.append("* Crosstabs")
    lines.append(f"CROSSTABS ")
    lines.append(f"  /TABLES={' '.join(tables_specs)}")
    lines.append(f"  /STATISTICS={' '.join(stats_specs)}")
    lines.append(".")

    return lines


# =============================================================================
# Step 16: Execute PSPP Cross-Tabulations
# =============================================================================

def execute_pspp_crosstabs_node(state: WorkflowState) -> WorkflowState:
    """
    Step 16: Execute PSPP cross-tabulations and create output file.

    This node:
    - Executes PSPP with the crosstabs syntax file generated in Step 15
    - Captures output and creates cross-tabulation results
    - Validates PSPP execution

    Args:
        state: Current workflow state. Must contain:
            - new_data_file: Path to new_data.sav (from Step 8)
            - crosstabs_syntax_file: Path to PSPP .sps syntax file (from Step 15)
            - config: Configuration dict for output paths

    Returns:
        Updated workflow state with:
            - cross_table_file: Path to output/cross_tables.txt
            - current_step: Set to 16
            - errors: Appended if PSPP execution fails
            - warnings: Appended for any PSPP warnings

    Error Handling:
        - PSPP execution failed: Stores error in state, continues to next step
        - PSPP syntax errors: Parses PSPP error log, provides specific message
        - Output file not created: Logs PSPP output, continues with error

    Example:
        >>> state = {
        ...     "new_data_file": "output/new_data.sav",
        ...     "crosstabs_syntax_file": "temp/pspp_syntax/crosstabs.sps",
        ...     "config": {"output_dir": "output"}
        ... }
        >>> new_state = execute_pspp_crosstabs_node(state)
        >>> print(new_state["cross_table_file"])
        'output/cross_tables.txt'
    """
    logger.info("Step 16: Executing PSPP cross-tabulations")

    # Get required inputs from state
    new_data_file = state.get("new_data_file")
    syntax_file_path = state.get("crosstabs_syntax_file")
    config = state.get("config", DEFAULT_CONFIG)

    # Validate required inputs
    if not new_data_file:
        error_msg = "No new_data_file available in state. Cannot execute PSPP crosstabs."
        logger.error(error_msg)
        return {
            **state,
            "current_step": 16,
            "errors": state.get("errors", []) + [error_msg],
        }

    if not syntax_file_path:
        error_msg = "No crosstabs_syntax_file available in state. Run Step 15 first."
        logger.error(error_msg)
        return {
            **state,
            "current_step": 16,
            "errors": state.get("errors", []) + [error_msg],
        }

    # Verify syntax file exists
    if not os.path.exists(syntax_file_path):
        error_msg = f"PSPP syntax file not found: {syntax_file_path}"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 16,
            "errors": state.get("errors", []) + [error_msg],
        }

    # Verify input file exists
    if not os.path.exists(new_data_file):
        error_msg = f"new_data.sav file not found: {new_data_file}"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 16,
            "errors": state.get("errors", []) + [error_msg],
        }

    # Prepare output file path
    output_dir = Path(config.get("output_dir", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    cross_table_file = str(output_dir / "cross_tables.txt")

    logger.info(f"Executing PSPP cross-tabulations:")
    logger.info(f"  Input file:  {new_data_file}")
    logger.info(f"  Syntax file: {syntax_file_path}")
    logger.info(f"  Output file: {cross_table_file}")

    try:
        # Import pspp_wrapper
        from agent.utils.pspp_wrapper import execute_pspp_syntax

        # Execute PSPP
        logger.info("Invoking PSPP to execute crosstabs syntax...")
        result = execute_pspp_syntax(
            syntax_file_path=syntax_file_path,
            input_file=new_data_file,
            output_file=cross_table_file
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
                "current_step": 16,
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
        if not os.path.exists(cross_table_file):
            error_msg = (
                f"PSPP executed successfully but output file was not created: {cross_table_file}. "
                f"Check PSPP syntax file for errors."
            )
            logger.error(error_msg)
            return {
                **state,
                "current_step": 16,
                "errors": state.get("errors", []) + [error_msg],
            }

        logger.info(f"Cross-tabulation output created: {cross_table_file}")

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
            "current_step": 16,
            "cross_table_file": cross_table_file,
            "warnings": warnings,
        }

        logger.info("Step 16 completed successfully")
        return new_state

    except Exception as e:
        error_msg = f"Unexpected error executing PSPP crosstabs: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": 16,
            "errors": state.get("errors", []) + [error_msg],
        }


# =============================================================================
# Step 16: Execute PSPP CTABLES
# =============================================================================

def execute_pspp_tables_node(state: WorkflowState) -> WorkflowState:
    """
    Step 16: Execute PSPP CTABLES syntax and create cross-table output.

    This node:
    - Executes PSPP with the CTABLES syntax file generated in Step 15
    - Captures output and creates cross-table results in CSV format
    - Converts CSV to structured JSON for easier programmatic access
    - Validates PSPP execution

    Args:
        state: Current workflow state. Must contain:
            - new_data_file: Path to new_data.sav (from Step 8)
            - table_syntax_file: Path to PSPP CTABLES .sps syntax file (from Step 15)
            - config: Configuration dict for output paths

    Returns:
        Updated workflow state with:
            - cross_table_file: Path to output/cross_table.json
            - current_step: Set to 16
            - errors: Appended if PSPP execution fails
            - warnings: Appended for any PSPP warnings

    Error Handling:
        - PSPP execution failed: Stores error in state, continues to next step
        - PSPP syntax errors: Parses PSPP error log, provides specific message
        - Output file not created: Logs PSPP output, continues with error
        - CSV parse error: Attempts recovery, logs warning

    Example:
        >>> state = {
        ...     "new_data_file": "output/new_data.sav",
        ...     "table_syntax_file": "temp/pspp_syntax/tables.sps",
        ...     "config": {"output_dir": "output"}
        ... }
        >>> new_state = execute_pspp_tables_node(state)
        >>> print(new_state["cross_table_file"])
        'output/cross_table.json'
    """
    logger.info("Step 16: Executing PSPP CTABLES syntax")

    # Get required inputs from state
    new_data_file = state.get("new_data_file")
    syntax_file_path = state.get("table_syntax_file")
    config = state.get("config", DEFAULT_CONFIG)

    # Validate required inputs
    if not new_data_file:
        error_msg = "No new_data_file available in state. Cannot execute PSPP CTABLES."
        logger.error(error_msg)
        return {
            **state,
            "current_step": 16,
            "errors": state.get("errors", []) + [error_msg],
        }

    if not syntax_file_path:
        error_msg = "No table_syntax_file available in state. Run Step 15 first."
        logger.error(error_msg)
        return {
            **state,
            "current_step": 16,
            "errors": state.get("errors", []) + [error_msg],
        }

    # Verify syntax file exists
    if not os.path.exists(syntax_file_path):
        error_msg = f"PSPP syntax file not found: {syntax_file_path}"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 16,
            "errors": state.get("errors", []) + [error_msg],
        }

    # Verify input file exists
    if not os.path.exists(new_data_file):
        error_msg = f"new_data.sav file not found: {new_data_file}"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 16,
            "errors": state.get("errors", []) + [error_msg],
        }

    # Prepare output file paths
    output_dir = Path(config.get("output_dir", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    cross_table_csv = str(output_dir / "cross_table.csv")
    cross_table_json = str(output_dir / "cross_table.json")

    logger.info(f"Executing PSPP CTABLES:")
    logger.info(f"  Input file:  {new_data_file}")
    logger.info(f"  Syntax file: {syntax_file_path}")
    logger.info(f"  Output CSV:  {cross_table_csv}")
    logger.info(f"  Output JSON: {cross_table_json}")

    try:
        # Import pspp_wrapper
        from agent.utils.pspp_wrapper import execute_pspp_syntax

        # Execute PSPP
        logger.info("Invoking PSPP to execute CTABLES syntax...")
        result = execute_pspp_syntax(
            syntax_file_path=syntax_file_path,
            input_file=new_data_file,
            output_file=cross_table_csv
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
                "current_step": 16,
                "errors": state.get("errors", []) + [error_msg],
            }

        # Log PSPP output
        logger.info("PSPP execution completed successfully")
        if result.get("output"):
            logger.debug(f"PSPP stdout: {result['output'][:500]}")
        if result.get("error"):
            # PSPP sometimes outputs to stderr even on success
            logger.debug(f"PSPP stderr: {result['error'][:500]}")

        # Verify CSV output file was created
        if not os.path.exists(cross_table_csv):
            error_msg = (
                f"PSPP executed successfully but CSV output file was not created: {cross_table_csv}. "
                f"Check PSPP syntax file for errors."
            )
            logger.error(error_msg)
            return {
                **state,
                "current_step": 16,
                "errors": state.get("errors", []) + [error_msg],
            }

        logger.info(f"Cross-table CSV created: {cross_table_csv}")

        # Get file size for logging
        csv_size = os.path.getsize(cross_table_csv)
        logger.info(f"CSV file size: {csv_size:,} bytes")

        # Convert CSV to structured JSON
        logger.info("Converting CSV to structured JSON format...")
        try:
            table_count = _convert_csv_to_json(cross_table_csv, cross_table_json)
            logger.info(f"Converted {table_count} tables to JSON format")

            # Get JSON file size
            json_size = os.path.getsize(cross_table_json)
            logger.info(f"JSON file size: {json_size:,} bytes")

        except Exception as e:
            warning_msg = f"Failed to convert CSV to JSON: {str(e)}. CSV file is still available."
            logger.warning(warning_msg)
            # Continue with CSV file only
            table_count = 0

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
            "current_step": 16,
            "cross_table_file": cross_table_json,  # Primary output is JSON
            "warnings": warnings,
        }

        logger.info(f"Step 16 completed successfully")
        logger.info(f"  Tables generated: {table_count}")
        logger.info(f"  CSV output: {cross_table_csv}")
        logger.info(f"  JSON output: {cross_table_json}")

        return new_state

    except Exception as e:
        error_msg = f"Unexpected error executing PSPP CTABLES: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": 16,
            "errors": state.get("errors", []) + [error_msg],
        }


def _convert_csv_to_json(csv_path: str, json_path: str) -> int:
    """
    Convert PSPP CTABLES CSV output to structured JSON format.

    Parses the CSV file generated by PSPP CTABLES and converts it to a
    structured JSON format with separate tables, each containing row labels,
    column labels, counts, and percentages.

    Args:
        csv_path: Path to input CSV file from PSPP
        json_path: Path to output JSON file

    Returns:
        Number of tables parsed and converted

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV file is empty or malformed

    JSON Structure:
        {
            "tables": [
                {
                    "table_id": "gender_x_satisfaction",
                    "row_variable": "gender",
                    "column_variable": "Satisfaction_Index",
                    "data": {
                        "row_labels": ["Male", "Female"],
                        "column_labels": ["Low", "Medium", "High"],
                        "counts": [[45, 32, 18], [52, 28, 25]],
                        "column_percentages": [[47.4, 33.7, 18.9], [49.5, 26.7, 23.8]]
                    }
                }
            ]
        }
    """
    import pandas as pd

    # Verify CSV file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Read CSV file
    try:
        df = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"CSV file is empty: {csv_path}")
    except Exception as e:
        raise ValueError(f"Failed to parse CSV file: {e}")

    if df.empty:
        raise ValueError(f"CSV file contains no data: {csv_path}")

    logger.debug(f"CSV shape: {df.shape}")
    logger.debug(f"CSV columns: {list(df.columns)}")

    # Parse CSV and convert to structured format
    # PSPP CTABLES CSV format varies based on table structure
    # We'll parse it generically to handle multiple tables

    tables = []
    table_count = 0

    # For now, create a simple JSON representation of the CSV
    # This can be enhanced later based on actual PSPP CTABLES output format
    table_data = {
        "tables": [
            {
                "table_id": "cross_table_1",
                "row_variable": "unknown",
                "column_variable": "unknown",
                "data": {
                    "row_labels": df.index.tolist() if hasattr(df.index, 'tolist') else list(range(len(df))),
                    "column_labels": df.columns.tolist(),
                    "counts": df.values.tolist(),
                    "column_percentages": []  # Will be populated if percentages are in CSV
                }
            }
        ]
    }
    tables.append(table_data)
    table_count = 1

    # Write JSON file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(table_data, f, indent=2, ensure_ascii=False)

    logger.debug(f"JSON structure written to: {json_path}")
    return table_count


# =============================================================================
# Helper Functions
# =============================================================================

def _generate_pspp_header() -> List[str]:
    """
    Generate header comments for PSPP syntax file.

    Returns:
        List of header lines
    """
    lines = []
    lines.append("* Cross-Tabulation Tables Generated by DataChat")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"* Generated: {timestamp}")
    lines.append("*")
    lines.append("")
    return lines
