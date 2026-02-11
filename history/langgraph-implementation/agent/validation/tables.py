"""
Table Specifications Validation Module

This module provides validation functions for AI-generated table specifications.
It checks that table specifications are structurally correct, reference valid variables,
and follow business rules for valid cross-tabulation tables.

Validation Checks:
1. Structure completeness: Required keys and data types
2. Row variable exists: Verify row variables exist in metadata/indicators
3. Column variable exists: Verify column variables exist in metadata/indicators
4. Variables are categorical: Verify variables are categorical (string or recoded numeric)
5. Statistics are valid: Verify statistics are valid values
6. Table ID uniqueness: Ensure all table_id values are unique
7. Weight variable validation: Verify weight variable exists (if present)

Example:
    >>> from agent.validation.tables import validate_table_specs
    >>> metadata = {"variable_names": ["gender", "sat_quality", ...], "indicators": [...]}
    >>> table_specs = {"tables": [...]}
    >>> result = validate_table_specs(table_specs, metadata)
    >>> print(result.is_valid)
    True
"""

import logging
from typing import Dict, List, Any, Optional, Union
from agent.state import ValidationResult, create_validation_result

logger = logging.getLogger(__name__)


# =============================================================================
# Main Validation Function
# =============================================================================

def validate_table_specs(
    table_specs: Dict[str, Any],
    metadata: Union[List[Dict[str, Any]], Dict[str, Any]]
) -> ValidationResult:
    """
    Validate table specifications against metadata and business rules.

    Performs comprehensive validation of AI-generated table specifications:
    - Checks JSON structure and required fields
    - Verifies row variables exist in metadata or indicators
    - Verifies column variables exist in metadata or indicators
    - Ensures variables are categorical (not continuous)
    - Validates statistics are valid values
    - Ensures table IDs are unique
    - Validates weight variable (if present)

    Args:
        table_specs: Dictionary containing "tables" key with list of table specs
        metadata: Variable metadata. Can be:
            - Dict with "variable_names" key (from new_metadata structure)
            - Dict with "indicators" key (from indicators state)
            - List[Dict]: Filtered metadata list
            - Dict: Variable-centered metadata (from variable_centered_metadata)

    Returns:
        ValidationResult with:
            - is_valid: True if no errors found
            - errors: List of error messages (empty if valid)
            - warnings: List of warning messages
            - checks_performed: List of validation check names

    Example:
        >>> table_specs = {
        ...     "tables": [
        ...         {
        ...             "table_id": "gender_x_satisfaction",
        ...             "row_variable": "gender",
        ...             "column_variable": "Customer_Satisfaction",
        ...             "weight_variable": None,
        ...             "statistics": ["count", "columnpct", "chisq", "cramersv"]
        ...         }
        ...     ]
        ... }
        >>> metadata = {"variable_names": ["gender"], "indicators": [{"name": "Customer_Satisfaction", ...}]}
        >>> result = validate_table_specs(table_specs, metadata)
        >>> print(result.is_valid)
        True
    """
    errors: List[str] = []
    warnings: List[str] = []
    checks_performed: List[str] = []

    # Normalize metadata to extract variables and indicators
    variable_names, variable_types, indicator_names = _normalize_metadata(metadata)

    # Check 1: Structure completeness
    check_name = "structure_completeness"
    checks_performed.append(check_name)
    structure_errors = _check_structure_completeness(table_specs)
    errors.extend(structure_errors)

    # If structure is invalid, we can't continue with other checks
    if structure_errors:
        return create_validation_result(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            checks_performed=checks_performed
        )

    tables_list = table_specs.get("tables", [])

    # Empty tables list is valid but should warn
    if len(tables_list) == 0:
        warnings.append("No table specifications generated (empty list)")
        return create_validation_result(
            is_valid=True,
            errors=[],
            warnings=warnings,
            checks_performed=checks_performed
        )

    # Check 2: Row variable exists
    check_name = "row_variable_exists"
    checks_performed.append(check_name)
    row_errors = _check_row_variables_exist(tables_list, variable_names, indicator_names)
    errors.extend(row_errors)

    # Check 3: Column variable exists
    check_name = "column_variable_exists"
    checks_performed.append(check_name)
    column_errors = _check_column_variables_exist(tables_list, variable_names, indicator_names)
    errors.extend(column_errors)

    # Check 4: Variables are categorical
    check_name = "variables_are_categorical"
    checks_performed.append(check_name)
    categorical_errors = _check_variables_are_categorical(
        tables_list,
        variable_names,
        variable_types,
        indicator_names
    )
    errors.extend(categorical_errors)

    # Check 5: Statistics are valid
    check_name = "statistics_are_valid"
    checks_performed.append(check_name)
    statistics_errors = _check_statistics_are_valid(tables_list)
    errors.extend(statistics_errors)

    # Check 6: Table ID uniqueness
    check_name = "table_id_uniqueness"
    checks_performed.append(check_name)
    uniqueness_errors = _check_table_id_uniqueness(tables_list)
    errors.extend(uniqueness_errors)

    # Check 7: Weight variable validation (if present)
    check_name = "weight_variable_validation"
    checks_performed.append(check_name)
    weight_errors, weight_warnings = _check_weight_variables(
        tables_list,
        variable_names
    )
    errors.extend(weight_errors)
    warnings.extend(weight_warnings)

    # Determine overall validity
    is_valid = len(errors) == 0

    if is_valid:
        logger.info(f"Table specifications validation passed: {len(tables_list)} tables validated")
    else:
        logger.warning(
            f"Table specifications validation failed: {len(errors)} errors, "
            f"{len(warnings)} warnings"
        )

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
) -> tuple[set[str], Dict[str, str], set[str]]:
    """
    Normalize metadata to extract variable names, types, and indicator names.

    Args:
        metadata: Variable metadata in various formats:
            - Dict with "variable_names" key (new_metadata format)
            - Dict with "indicators" key (indicators state)
            - List[Dict]: Filtered metadata list
            - Dict: Variable-centered metadata

    Returns:
        Tuple of (variable_names set, variable_types dict, indicator_names set)
    """
    variable_names = set()
    variable_types: Dict[str, str] = {}
    indicator_names = set()

    if isinstance(metadata, dict):
        # Check for new_metadata format (from Step 8)
        if "variable_names" in metadata:
            variable_names = set(metadata.get("variable_names", []))

            # Try to extract variable types from value_labels
            value_labels = metadata.get("value_labels", {})
            for var_name in variable_names:
                if var_name in value_labels and value_labels[var_name]:
                    # Has value labels => categorical
                    variable_types[var_name] = "categorical"
                else:
                    # No value labels => assume numeric
                    variable_types[var_name] = "numeric"

        # Check for indicators state (from Step 11)
        if "indicators" in metadata:
            indicators_list = metadata.get("indicators", [])
            for indicator in indicators_list:
                # Handle both "name" and "indicator_name" fields
                name = indicator.get("name") or indicator.get("indicator_name")
                if name:
                    indicator_names.add(name)

        # Check for variable-centered format
        if "variables" in metadata:
            for var_name, var_data in metadata.get("variables", {}).items():
                variable_names.add(var_name)
                var_type = var_data.get("variable_type", "unknown")
                variable_types[var_name] = var_type

        # If still empty, assume variable-centered with keys as names
        if not variable_names and not indicator_names:
            for key in metadata.keys():
                if key not in ["variable_names", "variable_labels", "value_labels", "indicators", "variables"]:
                    variable_names.add(key)

    if isinstance(metadata, list):
        # Extract from list of dicts
        for var in metadata:
            var_name = var.get("name", "")
            if var_name:
                variable_names.add(var_name)
                var_type = var.get("variable_type", "unknown")
                variable_types[var_name] = var_type

    return variable_names, variable_types, indicator_names


# =============================================================================
# Validation Check Functions
# =============================================================================

def _check_structure_completeness(table_specs: Dict[str, Any]) -> List[str]:
    """
    Check 1: Validate the basic structure of table specifications.

    Checks:
    - tables key exists
    - tables is a list
    - Each table has required fields: table_id, row_variable, column_variable, statistics

    Args:
        table_specs: Dictionary to validate

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check top-level structure
    if not isinstance(table_specs, dict):
        errors.append("Table specifications must be a JSON object")
        return errors

    if "tables" not in table_specs:
        errors.append("Missing required key 'tables'")
        return errors

    if not isinstance(table_specs["tables"], list):
        errors.append("'tables' must be a list")
        return errors

    # Empty tables list is valid but check required fields for non-empty
    tables_list = table_specs["tables"]
    if len(tables_list) == 0:
        return errors

    # Validate each table's structure
    required_fields = ["table_id", "row_variable", "column_variable", "statistics"]

    for idx, table in enumerate(tables_list):
        if not isinstance(table, dict):
            errors.append(f"Table {idx} is not a JSON object")
            continue

        # Check required fields
        for field in required_fields:
            if field not in table:
                errors.append(f"Table {idx} missing required field '{field}'")

        # Check statistics is a list
        if "statistics" in table and not isinstance(table["statistics"], list):
            errors.append(f"Table {idx} 'statistics' field must be a list")

        # weight_variable is optional but must be null or string if present
        weight_var = table.get("weight_variable")
        if weight_var is not None and not isinstance(weight_var, str):
            errors.append(f"Table {idx} 'weight_variable' must be null or a string")

    return errors


def _check_row_variables_exist(
    tables_list: List[Dict[str, Any]],
    variable_names: set[str],
    indicator_names: set[str]
) -> List[str]:
    """
    Check 2: Verify all row variables exist in metadata or indicators.

    Args:
        tables_list: List of table specification dictionaries
        variable_names: Set of valid variable names from metadata
        indicator_names: Set of valid indicator names

    Returns:
        List of error messages for missing variables
    """
    errors = []

    # Combine all valid names
    all_valid_names = variable_names | indicator_names

    for idx, table in enumerate(tables_list):
        row_var = table.get("row_variable", "")

        if not row_var:
            errors.append(f"Table {idx} has empty or missing row_variable")
            continue

        if row_var not in all_valid_names:
            errors.append(
                f"Row variable '{row_var}' not found in metadata (table {idx})"
            )

    return errors


def _check_column_variables_exist(
    tables_list: List[Dict[str, Any]],
    variable_names: set[str],
    indicator_names: set[str]
) -> List[str]:
    """
    Check 3: Verify all column variables exist in metadata or indicators.

    Column variables can be:
    - Regular variables from metadata
    - Indicators (composite variables from Step 11)

    Args:
        tables_list: List of table specification dictionaries
        variable_names: Set of valid variable names from metadata
        indicator_names: Set of valid indicator names

    Returns:
        List of error messages for missing variables
    """
    errors = []

    # Combine all valid names
    all_valid_names = variable_names | indicator_names

    for idx, table in enumerate(tables_list):
        col_var = table.get("column_variable", "")

        if not col_var:
            errors.append(f"Table {idx} has empty or missing column_variable")
            continue

        if col_var not in all_valid_names:
            errors.append(
                f"Column variable '{col_var}' not found in metadata or indicators (table {idx})"
            )

    return errors


def _check_variables_are_categorical(
    tables_list: List[Dict[str, Any]],
    variable_names: set[str],
    variable_types: Dict[str, str],
    indicator_names: set[str]
) -> List[str]:
    """
    Check 4: Verify variables are categorical (not continuous).

    Rules:
    - Variables from metadata must be categorical (string or recoded numeric)
    - Indicators are always categorical (by construction)
    - Recoded variables (ending in _recoded, _group, etc.) are categorical

    Args:
        tables_list: List of table specification dictionaries
        variable_names: Set of valid variable names from metadata
        variable_types: Dict mapping variable names to their types
        indicator_names: Set of valid indicator names

    Returns:
        List of error messages for non-categorical variables
    """
    errors = []

    for idx, table in enumerate(tables_list):
        row_var = table.get("row_variable", "")
        col_var = table.get("column_variable", "")

        # Check row variable
        if row_var:
            if row_var in indicator_names:
                # Indicators are always categorical
                pass
            elif row_var in variable_names:
                var_type = variable_types.get(row_var, "unknown")

                # Check if variable is categorical
                # Categorical if:
                # - Type is "string"
                # - Type is "categorical"
                # - Variable name indicates it's recoded (_recoded, _group, _bracket)
                is_categorical = (
                    var_type in ("string", "categorical") or
                    any(suffix in row_var.lower() for suffix in ["_recoded", "_group", "_bracket", "_bin"])
                )

                if not is_categorical:
                    errors.append(
                        f"Row variable '{row_var}' is not categorical (type: {var_type}) (table {idx})"
                    )

        # Check column variable
        if col_var:
            if col_var in indicator_names:
                # Indicators are always categorical
                pass
            elif col_var in variable_names:
                var_type = variable_types.get(col_var, "unknown")

                # Check if variable is categorical
                is_categorical = (
                    var_type in ("string", "categorical") or
                    any(suffix in col_var.lower() for suffix in ["_recoded", "_group", "_bracket", "_bin"])
                )

                if not is_categorical:
                    errors.append(
                        f"Column variable '{col_var}' is not categorical (type: {var_type}) (table {idx})"
                    )

    return errors


def _check_statistics_are_valid(tables_list: List[Dict[str, Any]]) -> List[str]:
    """
    Check 5: Verify statistics are valid values.

    Valid statistics:
    - count: Cell count (n)
    - columnpct: Column percentage
    - chisq: Chi-square test
    - cramersv: Cramer's V effect size

    Args:
        tables_list: List of table specification dictionaries

    Returns:
        List of error messages for invalid statistics
    """
    errors = []

    valid_statistics = {"count", "columnpct", "chisq", "cramersv"}

    for idx, table in enumerate(tables_list):
        statistics = table.get("statistics", [])

        if not isinstance(statistics, list):
            # This is caught by structure check
            continue

        for stat in statistics:
            if stat not in valid_statistics:
                errors.append(
                    f"Invalid statistic '{stat}' in table {idx}. "
                    f"Valid values: {', '.join(sorted(valid_statistics))}"
                )

    return errors


def _check_table_id_uniqueness(tables_list: List[Dict[str, Any]]) -> List[str]:
    """
    Check 6: Ensure all table_id values are unique.

    Args:
        tables_list: List of table specification dictionaries

    Returns:
        List of error messages for duplicate table IDs
    """
    errors = []
    seen_ids: Dict[str, int] = {}

    for idx, table in enumerate(tables_list):
        table_id = table.get("table_id", "")

        if not table_id:
            errors.append(f"Table {idx} has empty or missing table_id")
            continue

        if table_id in seen_ids:
            # Duplicate found
            first_idx = seen_ids[table_id]
            errors.append(
                f"Duplicate table_id '{table_id}' found at indices {first_idx} and {idx}"
            )
        else:
            seen_ids[table_id] = idx

    return errors


def _check_weight_variables(
    tables_list: List[Dict[str, Any]],
    variable_names: set[str]
) -> tuple[List[str], List[str]]:
    """
    Check 7: Validate weight variables (if present).

    Checks:
    - Weight variable exists in metadata
    - Warning if weight might introduce bias

    Args:
        tables_list: List of table specification dictionaries
        variable_names: Set of valid variable names from metadata

    Returns:
        Tuple of (errors, warnings) lists
    """
    errors = []
    warnings = []

    for idx, table in enumerate(tables_list):
        weight_var = table.get("weight_variable")

        # Skip if no weight variable
        if weight_var is None:
            continue

        # Check if weight variable is a string
        if not isinstance(weight_var, str):
            errors.append(
                f"Table {idx} weight_variable must be null or a string (found: {type(weight_var).__name__})"
            )
            continue

        # Skip if empty string
        if not weight_var:
            continue

        # Check if weight variable exists in metadata
        if weight_var not in variable_names:
            errors.append(
                f"Weight variable '{weight_var}' not found in metadata (table {idx})"
            )
        else:
            # Warning about potential bias
            warnings.append(
                f"Table {idx} uses weight variable '{weight_var}'. "
                f"Ensure weights are appropriately calibrated to avoid bias."
            )

    return errors, warnings
