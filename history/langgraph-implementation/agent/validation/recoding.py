"""
Recoding Rules Validation Module

This module provides validation functions for AI-generated recoding rules.
It checks that recoding rules are structurally correct, reference valid variables,
and follow business rules for valid recoding transformations.

Validation Checks:
1. Structure completeness: Required keys and data types
2. Source variable exists: Verify source variables in metadata
3. Target variable uniqueness: No duplicate target names
4. Range validity: Numeric ranges are valid (min <= max)
5. Target uniqueness within rules: No duplicate target values in a rule
6. Source non-overlap: Ranges don't overlap within a rule
7. Transformation completeness: Ranges cover full source range
8. Variable type match: Transformation type matches source variable type

Example:
    >>> from agent.validation.recoding import validate_recoding_rules
    >>> metadata = [{"name": "age", "variable_type": "numeric", ...}]
    >>> rules = {"recoding_rules": [...]}
    >>> result = validate_recoding_rules(rules, metadata)
    >>> print(result.is_valid)
    True
"""

import logging
from typing import Dict, List, Any, Optional, Union
from agent.state import ValidationResult, create_validation_result

logger = logging.getLogger(__name__)


# =============================================================================
# ValidationResult
# =============================================================================


# =============================================================================
# Main Validation Function
# =============================================================================

def validate_recoding_rules(
    recoding_rules: Dict[str, Any],
    metadata: Union[List[Dict[str, Any]], Dict[str, Any]]
) -> ValidationResult:
    """
    Validate recoding rules against metadata and business rules.

    Performs comprehensive validation of AI-generated recoding rules:
    - Checks JSON structure and required fields
    - Verifies source variables exist in metadata
    - Ensures target variable names are unique
    - Validates numeric ranges (min <= max)
    - Detects overlapping ranges
    - Checks for gaps in range coverage
    - Validates transformation type matches variable type

    Args:
        recoding_rules: Dictionary containing "recoding_rules" key with list of rules
        metadata: Variable metadata. Can be:
            - List[Dict]: Filtered metadata list (from state["filtered_metadata"])
            - Dict: Variable-centered metadata (from state["variable_centered_metadata"])

    Returns:
        ValidationResult with:
            - is_valid: True if no errors found
            - errors: List of error messages (empty if valid)
            - warnings: List of warning messages
            - checks_performed: List of validation check names

    Example:
        >>> rules = {
        ...     "recoding_rules": [
        ...         {
        ...             "source_variable": "age",
        ...             "target_variable": "age_group",
        ...             "transformation_type": "range_grouping",
        ...             "rules": [
        ...                 {"source_min": 18, "source_max": 24, "target_value": 1, "target_label": "18-24"},
        ...                 {"source_min": 25, "source_max": 34, "target_value": 2, "target_label": "25-34"}
        ...             ],
        ...             "description": "Group age into ranges"
        ...         }
        ...     ]
        ... }
        >>> metadata = [{"name": "age", "variable_type": "numeric", "min_value": 18, "max_value": 99}]
        >>> result = validate_recoding_rules(rules, metadata)
        >>> print(result.is_valid)
        True
    """
    errors: List[str] = []
    warnings: List[str] = []
    checks_performed: List[str] = []

    # Normalize metadata to variable-centered dict
    variable_metadata = _normalize_metadata(metadata)

    # Check 1: Structure completeness
    check_name = "structure_completeness"
    checks_performed.append(check_name)
    structure_errors = _check_structure_completeness(recoding_rules)
    errors.extend(structure_errors)

    # If structure is invalid, we can't continue with other checks
    if structure_errors:
        return create_validation_result(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            checks_performed=checks_performed
        )

    rules_list = recoding_rules.get("recoding_rules", [])

    # Check 2: Source variable exists
    check_name = "source_variable_exists"
    checks_performed.append(check_name)
    source_errors = _check_source_variables_exist(rules_list, variable_metadata)
    errors.extend(source_errors)

    # Check 3: Target variable uniqueness (across all rules)
    check_name = "target_variable_uniqueness"
    checks_performed.append(check_name)
    target_errors = _check_target_variable_uniqueness(rules_list)
    errors.extend(target_errors)

    # Check 8: Variable type match (do this early to filter valid rules)
    check_name = "variable_type_match"
    checks_performed.append(check_name)
    type_errors = _check_transformation_type_match(rules_list, variable_metadata)
    errors.extend(type_errors)

    # Per-rule validation checks
    for rule_idx, rule in enumerate(rules_list):
        source_var = rule.get("source_variable", "")
        transformation_type = rule.get("transformation_type", "")
        rule_list = rule.get("rules", [])

        # Get source variable metadata
        var_metadata = variable_metadata.get(source_var, {})

        # Skip detailed validation if source variable doesn't exist
        if not var_metadata:
            continue

        # Check 4: Range validity (for range_grouping type)
        if transformation_type == "range_grouping":
            check_name = f"range_validity_{source_var}"
            checks_performed.append(check_name)
            range_errors = check_numeric_ranges(rule_list, source_var)
            errors.extend(range_errors)

            # Check 6: Source non-overlap
            check_name = f"source_non_overlap_{source_var}"
            checks_performed.append(check_name)
            overlap_errors = check_range_overlap(rule_list, source_var)
            errors.extend(overlap_errors)

            # Check 7: Transformation completeness
            check_name = f"coverage_completeness_{source_var}"
            checks_performed.append(check_name)
            coverage_warnings = check_coverage_completeness(
                rule_list,
                source_var,
                var_metadata.get("min_value"),
                var_metadata.get("max_value")
            )
            warnings.extend(coverage_warnings)

        # Check 5: Target uniqueness within rules
        check_name = f"target_uniqueness_within_rule_{source_var}"
        checks_performed.append(check_name)
        target_uniqueness_errors = _check_target_uniqueness_within_rule(rule_list, source_var)
        errors.extend(target_uniqueness_errors)

    # Determine overall validity
    is_valid = len(errors) == 0

    if is_valid:
        logger.info(f"Recoding rules validation passed: {len(rules_list)} rules validated")
    else:
        logger.warning(f"Recoding rules validation failed: {len(errors)} errors, {len(warnings)} warnings")

    return create_validation_result(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        checks_performed=checks_performed
    )


# =============================================================================
# Metadata Normalization
# =============================================================================

def _normalize_metadata(
    metadata: Union[List[Dict[str, Any]], Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    Normalize metadata to a variable-centered dictionary.

    Args:
        metadata: Either a list of variable dicts or a variable-centered dict

    Returns:
        Dictionary mapping variable names to their metadata
    """
    if isinstance(metadata, dict):
        # Already variable-centered
        return metadata

    if isinstance(metadata, list):
        # Convert list to dict
        return {var.get("name", ""): var for var in metadata}

    return {}


# =============================================================================
# Validation Check Functions
# =============================================================================

def _check_structure_completeness(recoding_rules: Dict[str, Any]) -> List[str]:
    """
    Check 1: Validate the basic structure of recoding rules.

    Checks:
    - recoding_rules key exists
    - recoding_rules is a list
    - Each rule has required fields
    - Each rule has at least one transformation rule

    Args:
        recoding_rules: Dictionary to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check top-level structure
    if not isinstance(recoding_rules, dict):
        errors.append("Recoding rules must be a JSON object")
        return errors

    if "recoding_rules" not in recoding_rules:
        errors.append("Missing required key 'recoding_rules'")
        return errors

    if not isinstance(recoding_rules["recoding_rules"], list):
        errors.append("'recoding_rules' must be a list")
        return errors

    rules_list = recoding_rules["recoding_rules"]

    if len(rules_list) == 0:
        # This is a warning, not an error - no rules to validate
        return errors

    # Validate each rule's structure
    required_fields = ["source_variable", "target_variable", "transformation_type", "rules"]
    valid_transformation_types = ["range_grouping", "category_consolidation", "derived", "top_bottom_box"]

    for idx, rule in enumerate(rules_list):
        if not isinstance(rule, dict):
            errors.append(f"Rule {idx} is not a JSON object")
            continue

        # Check required fields
        for field in required_fields:
            if field not in rule:
                errors.append(f"Rule {idx} missing required field '{field}'")

        # Validate transformation_type
        transformation_type = rule.get("transformation_type")
        if transformation_type and transformation_type not in valid_transformation_types:
            errors.append(
                f"Rule {idx} has invalid transformation_type '{transformation_type}'. "
                f"Valid types: {', '.join(valid_transformation_types)}"
            )

        # Check rules array
        if "rules" in rule:
            if not isinstance(rule["rules"], list):
                errors.append(f"Rule {idx} 'rules' must be a list")
            elif len(rule["rules"]) == 0:
                errors.append(f"Rule {idx} has empty 'rules' array")

    return errors


def _check_source_variables_exist(
    rules_list: List[Dict[str, Any]],
    variable_metadata: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Check 2: Verify all source variables exist in metadata.

    Args:
        rules_list: List of recoding rules
        variable_metadata: Dictionary mapping variable names to metadata

    Returns:
        List of error messages for missing variables
    """
    errors = []

    for idx, rule in enumerate(rules_list):
        source_var = rule.get("source_variable", "")

        if not source_var:
            errors.append(f"Rule {idx} has empty or missing source_variable")
            continue

        # For derived variables, source_variable may be comma-separated
        source_vars = [v.strip() for v in source_var.split(",")]

        for var in source_vars:
            if var not in variable_metadata:
                errors.append(
                    f"Source variable '{var}' in rule {idx} not found in metadata"
                )

    return errors


def _check_target_variable_uniqueness(rules_list: List[Dict[str, Any]]) -> List[str]:
    """
    Check 3: Ensure all target variable names are unique across all rules.

    Args:
        rules_list: List of recoding rules

    Returns:
        List of error messages for duplicate targets
    """
    errors = []
    target_vars = {}

    for idx, rule in enumerate(rules_list):
        target_var = rule.get("target_variable", "")

        if not target_var:
            errors.append(f"Rule {idx} has empty or missing target_variable")
            continue

        if target_var in target_vars:
            # Duplicate found
            first_idx = target_vars[target_var]
            errors.append(
                f"Duplicate target variable '{target_var}' in rules {first_idx} and {idx}"
            )
        else:
            target_vars[target_var] = idx

    return errors


def _check_transformation_type_match(
    rules_list: List[Dict[str, Any]],
    variable_metadata: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Check 8: Verify transformation type matches source variable type.

    Rules:
    - range_grouping: Requires numeric variable
    - category_consolidation: Requires numeric/string with value_labels
    - derived: Can use any variable type (computed from formula)
    - top_bottom_box: Requires numeric variable

    Args:
        rules_list: List of recoding rules
        variable_metadata: Dictionary mapping variable names to metadata

    Returns:
        List of error messages for type mismatches
    """
    errors = []

    type_requirements = {
        "range_grouping": {"expected": "numeric", "reason": "ranges require numeric values"},
        "category_consolidation": {"expected": None, "reason": "can be any type with categories"},
        "derived": {"expected": None, "reason": "computed from formula"},
        "top_bottom_box": {"expected": "numeric", "reason": "scoring requires numeric values"}
    }

    for idx, rule in enumerate(rules_list):
        source_var = rule.get("source_variable", "")
        transformation_type = rule.get("transformation_type", "")

        # For derived variables, get the first source variable
        if "," in source_var:
            source_var = source_var.split(",")[0].strip()

        var_metadata = variable_metadata.get(source_var, {})
        var_type = var_metadata.get("variable_type", "unknown")

        requirement = type_requirements.get(transformation_type, {})

        if requirement.get("expected") and var_type != requirement["expected"]:
            errors.append(
                f"Invalid transformation type '{transformation_type}' for variable '{source_var}' "
                f"(type: {var_type}). {requirement['reason']}"
            )

    return errors


def _check_target_uniqueness_within_rule(
    rule_list: List[Dict[str, Any]],
    source_var: str
) -> List[str]:
    """
    Check 5: Ensure all target values are unique within a single rule.

    Args:
        rule_list: List of transformation rules for a single source variable
        source_var: Source variable name (for error messages)

    Returns:
        List of error messages for duplicate target values
    """
    errors = []
    target_values = {}

    for idx, rule in enumerate(rule_list):
        target_value = rule.get("target_value")

        if target_value is None:
            continue

        if target_value in target_values:
            first_idx = target_values[target_value]
            errors.append(
                f"Duplicate target value '{target_value}' in rule for '{source_var}' "
                f"(found at indices {first_idx} and {idx})"
            )
        else:
            target_values[target_value] = idx

    return errors


# =============================================================================
# Helper Functions for Validation Checks
# =============================================================================

def check_numeric_ranges(rule_list: List[Dict[str, Any]], source_var: str) -> List[str]:
    """
    Check 4: Validate numeric ranges are well-formed.

    Checks:
    - source_min is numeric
    - source_max is numeric
    - source_min <= source_max

    Args:
        rule_list: List of transformation rules
        source_var: Source variable name (for error messages)

    Returns:
        List of error messages for invalid ranges
    """
    errors = []

    for idx, rule in enumerate(rule_list):
        source_min = rule.get("source_min")
        source_max = rule.get("source_max")

        # Check if values are present
        if source_min is None:
            errors.append(
                f"Rule for '{source_var}' index {idx} missing 'source_min'"
            )
            continue

        if source_max is None:
            errors.append(
                f"Rule for '{source_var}' index {idx} missing 'source_max'"
            )
            continue

        # Check if values are numeric
        try:
            min_val = float(source_min)
            max_val = float(source_max)
        except (ValueError, TypeError):
            errors.append(
                f"Invalid range [{source_min}, {source_max}] in rule for '{source_var}' "
                f"(index {idx}): values must be numeric"
            )
            continue

        # Check min <= max
        if min_val > max_val:
            errors.append(
                f"Invalid range [{source_min}, {source_max}] in rule for '{source_var}' "
                f"(index {idx}): source_min must be <= source_max"
            )

    return errors


def check_range_overlap(rule_list: List[Dict[str, Any]], source_var: str) -> List[str]:
    """
    Check 6: Detect overlapping ranges within a rule.

    Two ranges [a, b] and [c, d] overlap if:
    - Not (b < c or d < a)
    - Equivalent: a <= d and c <= b

    Args:
        rule_list: List of transformation rules with source_min/source_max
        source_var: Source variable name (for error messages)

    Returns:
        List of error messages for overlapping ranges
    """
    errors = []

    # Collect all ranges
    ranges = []
    for idx, rule in enumerate(rule_list):
        source_min = rule.get("source_min")
        source_max = rule.get("source_max")

        if source_min is not None and source_max is not None:
            try:
                min_val = float(source_min)
                max_val = float(source_max)
                ranges.append((idx, min_val, max_val))
            except (ValueError, TypeError):
                # Skip non-numeric ranges (error already reported in check_numeric_ranges)
                continue

    # Check for overlaps
    for i, (idx_i, min_i, max_i) in enumerate(ranges):
        for j, (idx_j, min_j, max_j) in enumerate(ranges):
            if i >= j:  # Avoid duplicate checks and self-comparison
                continue

            # Check if ranges overlap
            # Ranges [min_i, max_i] and [min_j, max_j] overlap if:
            # min_i <= max_j AND min_j <= max_i
            if min_i <= max_j and min_j <= max_i:
                errors.append(
                    f"Overlapping ranges in rule for '{source_var}': "
                    f"[{min_i}, {max_i}] (index {idx_i}) overlaps with [{min_j}, {max_j}] (index {idx_j})"
                )

    return errors


def check_coverage_completeness(
    rule_list: List[Dict[str, Any]],
    source_var: str,
    var_min: Optional[Union[int, float]],
    var_max: Optional[Union[int, float]]
) -> List[str]:
    """
    Check 7: Find gaps in range coverage.

    Identifies gaps between consecutive ranges and warnings for:
    - Gaps in coverage
    - Ranges extending beyond variable bounds

    Args:
        rule_list: List of transformation rules
        source_var: Source variable name (for error messages)
        var_min: Minimum value of source variable
        var_max: Maximum value of source variable

    Returns:
        List of warning messages (not errors, as gaps may be intentional)
    """
    warnings = []

    if var_min is None or var_max is None:
        # Can't check coverage without bounds
        return warnings

    # Collect and sort ranges
    ranges = []
    for rule in rule_list:
        source_min = rule.get("source_min")
        source_max = rule.get("source_max")

        if source_min is not None and source_max is not None:
            try:
                min_val = float(source_min)
                max_val = float(source_max)
                ranges.append((min_val, max_val))
            except (ValueError, TypeError):
                continue

    if not ranges:
        return warnings

    # Sort by source_min
    ranges.sort(key=lambda x: x[0])

    # Check for gaps
    for i in range(len(ranges) - 1):
        current_max = ranges[i][1]
        next_min = ranges[i + 1][0]

        # Gap exists if next_min > current_max (with small tolerance for float comparison)
        if next_min > current_max + 0.001:
            gap_start = current_max + 1
            gap_end = next_min - 1

            if gap_start <= gap_end:
                warnings.append(
                    f"Gap in coverage for '{source_var}': values {gap_start}-{gap_end} not covered"
                )

    # Check if ranges extend beyond variable bounds
    overall_min = ranges[0][0]
    overall_max = ranges[-1][1]

    if overall_min > var_min:
        warnings.append(
            f"Coverage for '{source_var}' starts at {overall_min}, "
            f"but variable minimum is {var_min} (values {var_min}-{overall_min - 1} not covered)"
        )

    if overall_max < var_max:
        warnings.append(
            f"Coverage for '{source_var}' ends at {overall_max}, "
            f"but variable maximum is {var_max} (values {overall_max + 1}-{var_max} not covered)"
        )

    return warnings
