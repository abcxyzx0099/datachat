"""
Indicators Validation Module

This module provides validation functions for AI-generated indicators.
It checks that indicators are structurally correct, reference valid variables,
and follow business rules for valid indicator construction.

Validation Checks:
1. Structure completeness: Required keys and data types
2. Variables exist in metadata: Verify all variables exist in metadata
3. Indicator name uniqueness: No duplicate indicator names
4. Minimum size: Each indicator must have at least 2 variables
5. Maximum size warning: Warn if indicator has more than 10 variables
6. Variable uniqueness within indicator: No duplicate variables in same indicator

Example:
    >>> from agent.validation.indicators import validate_indicators
    >>> metadata = {"variable_names": ["sat_quality", "sat_price", ...]}
    >>> indicators = {"indicators": [...]}
    >>> result = validate_indicators(indicators, metadata)
    >>> print(result.is_valid)
    True
"""

import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# =============================================================================
# ValidationResult
# =============================================================================

@dataclass
class ValidationResult:
    """
    Standard validation result structure for indicators validation.

    Attributes:
        is_valid: Overall validation status (True if no errors)
        errors: Critical errors that must be fixed (blocks execution)
        warnings: Non-critical issues (informational)
        checks_performed: List of validation checks that were run
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    checks_performed: List[str]


# =============================================================================
# Main Validation Function
# =============================================================================

def validate_indicators(
    indicators: Dict[str, Any],
    metadata: Union[List[Dict[str, Any]], Dict[str, Any]]
) -> ValidationResult:
    """
    Validate indicators against metadata and business rules.

    Performs comprehensive validation of AI-generated indicators:
    - Checks JSON structure and required fields
    - Verifies all variables exist in metadata
    - Ensures indicator names are unique
    - Validates indicator sizes (minimum 2 variables)
    - Warns for oversized indicators (more than 10 variables)
    - Checks for duplicate variables within indicators

    Args:
        indicators: Dictionary containing "indicators" key with list of indicators
        metadata: Variable metadata. Can be:
            - Dict with "variable_names" key (from new_metadata structure)
            - List[Dict]: Filtered metadata list
            - Dict: Variable-centered metadata (from variable_centered_metadata)

    Returns:
        ValidationResult with:
            - is_valid: True if no errors found
            - errors: List of error messages (empty if valid)
            - warnings: List of warning messages
            - checks_performed: List of validation check names

    Example:
        >>> indicators = {
        ...     "indicators": [
        ...         {
        ...             "name": "Customer_Satisfaction",
        ...             "description": "Overall satisfaction",
        ...             "variables": ["sat_quality", "sat_price", "sat_service"]
        ...         }
        ...     ]
        ... }
        >>> metadata = {"variable_names": ["sat_quality", "sat_price", "sat_service"]}
        >>> result = validate_indicators(indicators, metadata)
        >>> print(result.is_valid)
        True
    """
    errors: List[str] = []
    warnings: List[str] = []
    checks_performed: List[str] = []

    # Normalize metadata to extract variable names
    variable_names = _extract_variable_names(metadata)

    # Check 1: Structure completeness
    check_name = "structure_completeness"
    checks_performed.append(check_name)
    structure_errors = _check_structure_completeness(indicators)
    errors.extend(structure_errors)

    # If structure is invalid, we can't continue with other checks
    if structure_errors:
        return ValidationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            checks_performed=checks_performed
        )

    indicators_list = indicators.get("indicators", [])

    # Empty indicators list is valid
    if len(indicators_list) == 0:
        logger.info("No indicators to validate (empty list is valid)")
        return ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            checks_performed=checks_performed
        )

    # Check 2: Variables exist in metadata
    check_name = "variables_exist_in_metadata"
    checks_performed.append(check_name)
    variable_errors = _check_variables_exist(indicators_list, variable_names)
    errors.extend(variable_errors)

    # Check 3: Indicator name uniqueness
    check_name = "indicator_name_uniqueness"
    checks_performed.append(check_name)
    name_errors = _check_indicator_name_uniqueness(indicators_list)
    errors.extend(name_errors)

    # Check 4 & 5: Size validation (min and max)
    check_name = "indicator_size_validation"
    checks_performed.append(check_name)
    size_errors, size_warnings = _check_indicator_sizes(indicators_list)
    errors.extend(size_errors)
    warnings.extend(size_warnings)

    # Check 6: Variable uniqueness within indicator
    check_name = "variable_uniqueness_within_indicator"
    checks_performed.append(check_name)
    uniqueness_errors = _check_variable_uniqueness_within_indicator(indicators_list)
    errors.extend(uniqueness_errors)

    # Determine overall validity
    is_valid = len(errors) == 0

    if is_valid:
        logger.info(f"Indicators validation passed: {len(indicators_list)} indicators validated")
    else:
        logger.warning(f"Indicators validation failed: {len(errors)} errors, {len(warnings)} warnings")

    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        checks_performed=checks_performed
    )


# =============================================================================
# Metadata Normalization
# =============================================================================

def _extract_variable_names(
    metadata: Union[List[Dict[str, Any]], Dict[str, Any]]
) -> List[str]:
    """
    Extract variable names from metadata.

    Args:
        metadata: Variable metadata in various formats:
            - Dict with "variable_names" key (new_metadata format)
            - List[Dict]: Filtered metadata list
            - Dict: Variable-centered metadata

    Returns:
        List of variable names
    """
    if isinstance(metadata, dict):
        # Check for new_metadata format (from Step 8)
        if "variable_names" in metadata:
            return metadata.get("variable_names", [])

        # Check for variable-centered format
        if "variables" in metadata:
            # Extract keys as variable names
            return list(metadata.get("variables", {}).keys())

        # Assume it's variable-centered with variable names as keys
        return list(metadata.keys())

    if isinstance(metadata, list):
        # Extract names from list of dicts
        return [var.get("name", "") for var in metadata if var.get("name")]

    return []


# =============================================================================
# Validation Check Functions
# =============================================================================

def _check_structure_completeness(indicators: Dict[str, Any]) -> List[str]:
    """
    Check 1: Validate the basic structure of indicators.

    Checks:
    - indicators key exists
    - indicators is a list (can be empty)
    - Each indicator has required fields: name, description, variables

    Args:
        indicators: Dictionary to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check top-level structure
    if not isinstance(indicators, dict):
        errors.append("Indicators must be a JSON object")
        return errors

    if "indicators" not in indicators:
        errors.append("Missing required key 'indicators'")
        return errors

    if not isinstance(indicators["indicators"], list):
        errors.append("'indicators' must be a list")
        return errors

    # Empty indicators list is valid (no indicators generated)
    indicators_list = indicators["indicators"]
    if len(indicators_list) == 0:
        return errors

    # Validate each indicator's structure
    required_fields = ["indicator_name", "description", "variables"]

    for idx, indicator in enumerate(indicators_list):
        if not isinstance(indicator, dict):
            errors.append(f"Indicator {idx} is not a JSON object")
            continue

        # Check required fields
        for field in required_fields:
            if field not in indicator:
                errors.append(f"Indicator {idx} missing required field '{field}'")

        # Check variables is a list
        if "variables" in indicator and not isinstance(indicator["variables"], list):
            errors.append(f"Indicator {idx} 'variables' field must be a list")

    return errors


def _check_variables_exist(
    indicators_list: List[Dict[str, Any]],
    variable_names: List[str]
) -> List[str]:
    """
    Check 2: Verify all variables referenced in indicators exist in metadata.

    Args:
        indicators_list: List of indicator dictionaries
        variable_names: List of valid variable names from metadata

    Returns:
        List of error messages for missing variables
    """
    errors = []

    # Convert to set for faster lookup
    valid_variables = set(variable_names)

    for idx, indicator in enumerate(indicators_list):
        indicator_name = indicator.get("indicator_name", f"Indicator {idx}")
        variables = indicator.get("variables", [])

        if not isinstance(variables, list):
            continue

        for var in variables:
            if not isinstance(var, str):
                errors.append(
                    f"Variable '{var}' in indicator '{indicator_name}' is not a string"
                )
                continue

            if var not in valid_variables:
                errors.append(
                    f"Variable '{var}' not found in metadata (referenced in indicator '{indicator_name}')"
                )

    return errors


def _check_indicator_name_uniqueness(indicators_list: List[Dict[str, Any]]) -> List[str]:
    """
    Check 3: Ensure all indicator names are unique.

    Args:
        indicators_list: List of indicator dictionaries

    Returns:
        List of error messages for duplicate names
    """
    errors = []
    seen_names = {}

    for idx, indicator in enumerate(indicators_list):
        name = indicator.get("indicator_name", "")

        if not name:
            errors.append(f"Indicator {idx} has empty or missing indicator_name")
            continue

        if name in seen_names:
            # Duplicate found
            first_idx = seen_names[name]
            errors.append(
                f"Duplicate indicator name '{name}' found at indices {first_idx} and {idx}"
            )
        else:
            seen_names[name] = idx

    return errors


def _check_indicator_sizes(indicators_list: List[Dict[str, Any]]) -> tuple[List[str], List[str]]:
    """
    Check 4 & 5: Validate indicator sizes.

    - Error: Each indicator must have at least 2 variables
    - Warning: Warn if indicator has more than 10 variables

    Args:
        indicators_list: List of indicator dictionaries

    Returns:
        Tuple of (errors, warnings) lists
    """
    errors = []
    warnings = []

    for idx, indicator in enumerate(indicators_list):
        indicator_name = indicator.get("indicator_name", f"Indicator {idx}")
        variables = indicator.get("variables", [])

        if not isinstance(variables, list):
            continue

        var_count = len(variables)

        # Check minimum size (error)
        if var_count < 2:
            errors.append(
                f"Indicator '{indicator_name}' has only {var_count} variable(s) (minimum: 2)"
            )

        # Check maximum size (warning, not error)
        elif var_count > 10:
            warnings.append(
                f"Indicator '{indicator_name}' has {var_count} variables (recommended max: 10)"
            )

    return errors, warnings


def _check_variable_uniqueness_within_indicator(indicators_list: List[Dict[str, Any]]) -> List[str]:
    """
    Check 6: Ensure variables within an indicator are unique.

    Args:
        indicators_list: List of indicator dictionaries

    Returns:
        List of error messages for duplicate variables
    """
    errors = []

    for idx, indicator in enumerate(indicators_list):
        indicator_name = indicator.get("indicator_name", f"Indicator {idx}")
        variables = indicator.get("variables", [])

        if not isinstance(variables, list):
            continue

        # Track seen variables within this indicator
        seen_vars = set()
        duplicates = set()

        for var in variables:
            if var in seen_vars:
                duplicates.add(var)
            else:
                seen_vars.add(var)

        # Report duplicates
        for var in duplicates:
            errors.append(
                f"Duplicate variable '{var}' in indicator '{indicator_name}'"
            )

    return errors
