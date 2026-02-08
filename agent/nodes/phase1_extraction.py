"""
Phase 1: Extraction Nodes (Steps 1-3)

This module contains nodes for extracting and preparing data from SPSS files:
- Step 1: extract_spss_node - Read .sav file and extract metadata
- Step 2: transform_metadata_node - Transform metadata to variable-centered format
- Step 3: filter_metadata_node - Filter metadata to variables requiring recoding
"""

import logging
from typing import Dict, Any, Optional
import pandas as pd
import pyreadstat

from agent.state import WorkflowState, STEP_1_EXTRACT_SPSS, STEP_2_TRANSFORM_METADATA, STEP_3_FILTER_METADATA
from agent.utils.file_io import read_spss_file
from agent.utils.tracing import trace_node

logger = logging.getLogger(__name__)


@trace_node("Step 1: Extract SPSS Data")
def extract_spss_node(state: WorkflowState) -> dict:
    """
    Step 1: Extract raw data and metadata from SPSS .sav file.

    This node reads the input SPSS file and extracts:
    - raw_data: Survey response data as pandas DataFrame
    - original_metadata: Raw metadata from pyreadstat including variable labels,
      value labels, variable types, and variable roles

    Metadata structure:
        {
            "file_name": str,
            "n_rows": int,
            "n_columns": int,
            "column_labels": Dict[str, str],        # variable_name -> label
            "column_value_labels": Dict[str, Dict], # variable_name -> {value: label}
            "variable_types": Dict[str, str]        # variable_name -> type
        }

    Args:
        state: Current workflow state. Must contain:
            - input_file_path: Path to the .sav file

    Returns:
        Updated workflow state with:
            - raw_data: pandas DataFrame with survey responses
            - original_metadata: Dict with SPSS metadata
            - current_step: Set to STEP_1_EXTRACT_SPSS
            - errors: List of errors (appended if any occur)
            - warnings: List of warnings (appended if any occur)

    Raises:
        FileNotFoundError: If the .sav file does not exist
        ValueError: If the file is not a valid SPSS format
        PermissionError: If the file cannot be read

    Example:
        >>> state = {"input_file_path": "survey_data.sav"}
        >>> new_state = extract_spss_node(state)
        >>> print(new_state["raw_data"].shape)
        (1000, 50)
        >>> print(new_state["original_metadata"]["n_rows"])
        1000
    """
    # Get input file path from state
    input_file_path = state.get("input_file_path")
    if not input_file_path:
        error_msg = "No input_file_path provided in state"
        logger.error(error_msg)
        return {
            "current_step": STEP_1_EXTRACT_SPSS,
            "errors": [error_msg],
        }

    logger.info(f"Step 1: Extracting SPSS file: {input_file_path}")

    try:
        # Read SPSS file using utility function
        df, metadata = read_spss_file(input_file_path)

        # Log extraction details
        logger.info(
            f"Successfully extracted {len(df)} rows and {len(df.columns)} columns "
            f"from {input_file_path}"
        )

        # Get column labels from metadata
        # pyreadstat returns column_labels as a list, so convert to dict
        raw_column_labels = getattr(metadata, "column_labels", [])
        if isinstance(raw_column_labels, list):
            # Convert list to dict by zipping with column names
            column_labels_dict = dict(zip(df.columns, raw_column_labels))
        else:
            # Already a dict (from some sources or tests)
            column_labels_dict = raw_column_labels

        # Build structured metadata dictionary
        original_metadata = {
            "file_name": input_file_path,
            "n_rows": len(df),
            "n_columns": len(df.columns),
            "column_labels": column_labels_dict,
            "column_value_labels": getattr(metadata, "variable_value_labels", {}),
            "variable_types": _extract_variable_types(metadata, df),
        }

        # Log metadata summary
        logger.info(
            f"Metadata extracted: {len(original_metadata['column_labels'])} variable labels, "
            f"{len(original_metadata['column_value_labels'])} variables with value labels"
        )

        # Check for empty data warning
        warnings = state.get("warnings", []).copy()
        if len(df) == 0:
            warning_msg = f"SPSS file contains no data: {input_file_path}"
            logger.warning(warning_msg)
            warnings.append(warning_msg)

        # NOTE: We do NOT store raw_data in the state to avoid LangGraph
        # checkpoint serialization errors. Step 2 will reload from the input file.
        # Return new state (DO NOT modify in-place)
        return {
            "current_step": STEP_1_EXTRACT_SPSS,
            "original_metadata": original_metadata,
            "warnings": warnings,
        }

    except FileNotFoundError as e:
        error_msg = f"SPSS file not found: {input_file_path}"
        logger.error(error_msg)
        return {
            "current_step": STEP_1_EXTRACT_SPSS,
            "errors": [error_msg],
        }

    except ValueError as e:
        error_msg = f"Invalid SPSS file format: {input_file_path} - {str(e)}"
        logger.error(error_msg)
        return {
            "current_step": STEP_1_EXTRACT_SPSS,
            "errors": [error_msg],
        }

    except PermissionError as e:
        error_msg = f"Permission denied reading SPSS file: {input_file_path}"
        logger.error(error_msg)
        return {
            "current_step": STEP_1_EXTRACT_SPSS,
            "errors": [error_msg],
        }

    except Exception as e:
        error_msg = f"Unexpected error extracting SPSS file: {input_file_path} - {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "current_step": STEP_1_EXTRACT_SPSS,
            "errors": [error_msg],
        }


def _extract_variable_types(metadata: Any, df: pd.DataFrame) -> Dict[str, str]:
    """
    Extract variable types from pyreadstat metadata.

    Args:
        metadata: pyreadstat metadata object
        df: pandas DataFrame from read_sav

    Returns:
        Dictionary mapping variable names to their types
    """
    variable_types = {}

    # Try to get variable types from metadata
    if hasattr(metadata, "variable_storage_types"):
        # pyreadstat provides storage types
        storage_types = metadata.variable_storage_types
        for var_name, storage_type in storage_types.items():
            # Map pyreadstat storage types to simplified types
            if storage_type in ("numeric", "float"):
                variable_types[var_name] = "numeric"
            elif storage_type == "string":
                variable_types[var_name] = "string"
            else:
                variable_types[var_name] = storage_type

    # Fallback: infer from DataFrame dtypes
    if not variable_types or len(variable_types) != len(df.columns):
        for col in df.columns:
            if col not in variable_types:
                dtype = df[col].dtype
                if pd.api.types.is_numeric_dtype(dtype):
                    variable_types[col] = "numeric"
                elif pd.api.types.is_string_dtype(dtype) or pd.api.types.is_object_dtype(dtype):
                    variable_types[col] = "string"
                else:
                    variable_types[col] = str(dtype)

    return variable_types


def _determine_type(series: pd.Series) -> str:
    """
    Determine the variable type from a pandas Series.

    Args:
        series: pandas Series to analyze

    Returns:
        One of: "numeric", "string", "date", "unknown"
    """
    dtype = series.dtype

    # Check for numeric types (int64, float64, etc.)
    if pd.api.types.is_integer_dtype(dtype) or pd.api.types.is_float_dtype(dtype):
        return "numeric"

    # Check for string/object types
    if pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
        return "string"

    # Check for datetime types
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "date"

    # Check for category dtype
    if pd.api.types.is_categorical_dtype(dtype):
        # Check if categories are numeric
        if series.cat.categories.dtype.kind in ('i', 'f', 'u'):
            return "numeric"
        return "string"

    # Fallback for unknown types
    logger.warning(f"Unknown dtype {dtype} for series {series.name}")
    return "unknown"


@trace_node("Step 2: Transform Metadata")
def transform_metadata_node(state: WorkflowState) -> dict:
    """
    Step 2: Transform metadata to variable-centered format.

    This node restructures the raw metadata from pyreadstat into a
    variable-centered format that is easier to work with in downstream
    processing steps. It computes additional metadata like min/max values
    and restructures the data for easier access.

    The variable-centered metadata structure:
        {
            "variables": {
                "var_name": {
                    "name": str,
                    "label": str,
                    "variable_type": str,  # "numeric" | "string" | "date"
                    "min_value": Optional[int|float],
                    "max_value": Optional[int|float],
                    "value_labels": Dict[int, str],
                    "distinct_count": int
                }
            },
            "n_variables": int,
            "n_numeric": int,
            "n_string": int,
            "n_date": int,
            "total_records": int
        }

    Args:
        state: Current workflow state. Must contain:
            - input_file_path: Path to the .sav file (for reloading data)
            - original_metadata: Raw metadata from Step 1

    Returns:
        Updated workflow state with:
            - variable_centered_metadata: Dict with variable-centered metadata
            - current_step: Set to STEP_2_TRANSFORM_METADATA
            - warnings: List of warnings (appended if any occur)
            - errors: List of errors (appended if any occur)

    Example:
        >>> state = {
        ...     "input_file_path": "survey.sav",
        ...     "original_metadata": {...}
        ... }
        >>> new_state = transform_metadata_node(state)
        >>> metadata = new_state["variable_centered_metadata"]
        >>> print(metadata["n_variables"])
        50
    """
    logger.info("Step 2: Transform metadata to variable-centered format")

    # Get input_file_path and original_metadata from state
    input_file_path = state.get("input_file_path")
    original_metadata = state.get("original_metadata")

    # Validate required state fields
    if not input_file_path:
        error_msg = "No input_file_path found in state - Step 1 must complete first"
        logger.error(error_msg)
        return {
            "current_step": STEP_2_TRANSFORM_METADATA,
            "errors": [error_msg],
        }

    if original_metadata is None:
        error_msg = "No original_metadata found in state - Step 1 must complete first"
        logger.error(error_msg)
        return {
            "current_step": STEP_2_TRANSFORM_METADATA,
            "errors": [error_msg],
        }

    # Reload data from file (needed to compute dtypes and value counts)
    # We don't store raw_data in state to avoid serialization issues
    try:
        df, _ = pyreadstat.read_sav(input_file_path, apply_value_formats=False)
    except FileNotFoundError:
        error_msg = f"SPSS file not found: {input_file_path}"
        logger.error(error_msg)
        return {
            "current_step": STEP_2_TRANSFORM_METADATA,
            "errors": [error_msg],
        }
    except Exception as e:
        error_msg = f"Error reading SPSS file: {input_file_path} - {str(e)}"
        logger.error(error_msg)
        return {
            "current_step": STEP_2_TRANSFORM_METADATA,
            "errors": [error_msg],
        }

    # Copy warnings list to avoid in-place modification
    warnings = state.get("warnings", []).copy()

    # Handle empty DataFrame edge case
    if df.empty:
        warning_msg = "Empty DataFrame - creating empty metadata structure"
        logger.warning(warning_msg)
        warnings.append(warning_msg)

        empty_metadata = {
            "variables": {},
            "n_variables": 0,
            "n_numeric": 0,
            "n_string": 0,
            "n_date": 0,
            "total_records": 0,
        }

        logger.info("Created empty metadata structure for empty DataFrame")
        return {
            "current_step": STEP_2_TRANSFORM_METADATA,
            "variable_centered_metadata": empty_metadata,
            "warnings": warnings,
        }

    # Get column_labels and column_value_labels from original_metadata
    column_labels = original_metadata.get("column_labels", {})
    column_value_labels = original_metadata.get("column_value_labels", {})

    # Initialize variable-centered metadata structure
    variables = {}
    n_numeric = 0
    n_string = 0
    n_date = 0
    n_unknown = 0

    # Process each column
    for column in df.columns:
        series = df[column]

        # Determine variable type
        variable_type = _determine_type(series)

        # Count types
        if variable_type == "numeric":
            n_numeric += 1
        elif variable_type == "string":
            n_string += 1
        elif variable_type == "date":
            n_date += 1
        else:
            n_unknown += 1

        # Get label (fallback to column name if not found)
        label = column_labels.get(column, column)

        # Get min/max values for numeric variables
        min_value = None
        max_value = None

        if variable_type == "numeric":
            # Use min/max with skipna=True to handle NaN values
            min_val = series.min(skipna=True)
            max_val = series.max(skipna=True)

            # Convert to Python native types, but keep None for all-NaN columns
            if pd.notna(min_val):
                min_value = float(min_val) if isinstance(min_val, float) else int(min_val)
            if pd.notna(max_val):
                max_value = float(max_val) if isinstance(max_val, float) else int(max_val)

        # Get value labels for this variable
        value_labels = column_value_labels.get(column, {})

        # Compute distinct count
        distinct_count = series.nunique(dropna=False)

        # Build variable info dictionary
        var_info = {
            "name": column,
            "label": label,
            "variable_type": variable_type,
            "min_value": min_value,
            "max_value": max_value,
            "value_labels": value_labels,
            "distinct_count": distinct_count,
        }

        variables[column] = var_info

        # Log warning for unknown type
        if variable_type == "unknown":
            warning_msg = f"Variable '{column}' has unknown type ({series.dtype})"
            logger.warning(warning_msg)
            warnings.append(warning_msg)

    # Build the complete variable-centered metadata structure
    variable_centered_metadata = {
        "variables": variables,
        "n_variables": len(variables),
        "n_numeric": n_numeric,
        "n_string": n_string,
        "n_date": n_date,
        "total_records": len(df),
    }

    # Log transformation summary
    logger.info(
        f"Metadata transformation complete: "
        f"{variable_centered_metadata['n_variables']} variables "
        f"({n_numeric} numeric, {n_string} string, {n_date} date"
        f"{f', {n_unknown} unknown' if n_unknown > 0 else ''})"
    )

    # Return new state (DO NOT modify in-place)
    return {
        "current_step": STEP_2_TRANSFORM_METADATA,
        "variable_centered_metadata": variable_centered_metadata,
        "warnings": warnings,
    }


@trace_node("Step 3: Filter Metadata")
def filter_metadata_node(state: WorkflowState) -> dict:
    """
    Step 3: Filter metadata to variables requiring recoding.

    This node filters the variable-centered metadata to exclude variables
    that don't require recoding based on business rules:
    - Binary variables (exactly 2 distinct values) - no room for recoding
    - High cardinality variables (> threshold distinct values) - typically IDs or open-ended text
    - "Other" text fields - open-ended feedback fields

    Filtered metadata is passed to Step 4 for LLM-orchestrated recoding.

    Args:
        state: Current workflow state. Must contain:
            - variable_centered_metadata: Metadata from Step 2
            - config: Configuration with filtering thresholds (optional)

    Returns:
        Updated workflow state with:
            - filtered_metadata: List of variable dicts requiring recoding
            - filtered_out_variables: List of dicts with filtered variable names and reasons
            - current_step: Set to STEP_3_FILTER_METADATA
            - warnings: List of warnings (appended if any occur)
            - errors: List of errors (appended if any occur)

    Example:
        >>> state = {
        ...     "variable_centered_metadata": {
        ...         "variables": {...},
        ...         "n_variables": 50
        ...     }
        ... }
        >>> new_state = filter_metadata_node(state)
        >>> print(len(new_state["filtered_metadata"]))
        35
        >>> print(len(new_state["filtered_out_variables"]))
        15
    """
    logger.info("Step 3: Filter metadata to variables requiring recoding")

    # Get variable_centered_metadata from state
    variable_centered_metadata = state.get("variable_centered_metadata")

    # Validate required state fields
    if variable_centered_metadata is None:
        error_msg = "No variable_centered_metadata found in state - Step 2 must complete first"
        logger.error(error_msg)
        return {
            "current_step": STEP_3_FILTER_METADATA,
            "errors": [error_msg],
        }

    # Get configuration for filtering threshold
    # Import here to avoid circular dependency
    from agent.config import DEFAULT_CONFIG
    config = state.get("config", DEFAULT_CONFIG)
    threshold = config.get("cardinality_threshold", 30)

    # Copy warnings list to avoid in-place modification
    warnings = state.get("warnings", []).copy()

    # Get variables dict from metadata
    variables = variable_centered_metadata.get("variables", {})

    if not variables:
        warning_msg = "No variables found in variable_centered_metadata"
        logger.warning(warning_msg)
        warnings.append(warning_msg)

        # Return empty filtered metadata
        return {
            "current_step": STEP_3_FILTER_METADATA,
            "filtered_metadata": [],
            "filtered_out_variables": [],
            "warnings": warnings,
        }

    # Track filtered and included variables
    filtered_out_variables = []
    filtered_metadata = []

    # Track filtering counts by reason
    filter_counts = {
        "binary": 0,
        "high_cardinality": 0,
        "other_field": 0,
    }

    # Process each variable
    for var_name, var_info in variables.items():
        should_filter, reason = _should_filter_variable(
            var_name, var_info, threshold
        )

        if should_filter:
            # Record filtered variable
            filter_counts[reason] = filter_counts.get(reason, 0) + 1

            filter_entry = {
                "name": var_name,
                "label": var_info.get("label", var_name),  # Include label for debugging
                "reason": _get_filter_reason_description(reason),
                "rule": reason,
                "distinct_count": var_info.get("distinct_count"),
                "type": var_info.get("variable_type"),
            }

            # Add threshold for high_cardinality
            if reason == "high_cardinality":
                filter_entry["threshold"] = threshold

            filtered_out_variables.append(filter_entry)
        else:
            # Include variable in filtered metadata
            filtered_metadata.append(var_info)

    # Log filtering summary
    total_vars = len(variables)
    included_vars = len(filtered_metadata)
    excluded_vars = len(filtered_out_variables)

    logger.info(
        f"Filtering complete: {included_vars}/{total_vars} variables included, "
        f"{excluded_vars} excluded (binary: {filter_counts['binary']}, "
        f"high_cardinality: {filter_counts['high_cardinality']}, "
        f"other_field: {filter_counts['other_field']})"
    )

    # Handle edge case: all variables filtered
    if included_vars == 0:
        warning_msg = (
            f"All {total_vars} variables were filtered out. "
            "No variables remain for recoding."
        )
        logger.warning(warning_msg)
        warnings.append(warning_msg)

    # Handle edge case: no variables filtered
    elif excluded_vars == 0:
        logger.info("No variables were filtered - all variables passed filters")

    # Handle edge case: single variable remaining
    elif included_vars == 1:
        logger.info(
            "Only 1 variable remains after filtering - "
            "single-variable analysis will be performed"
        )

    # Return new state (DO NOT modify in-place)
    return {
        "current_step": STEP_3_FILTER_METADATA,
        "filtered_metadata": filtered_metadata,
        "filtered_out_variables": filtered_out_variables,
        "warnings": warnings,
    }


def _should_filter_variable(
    var_name: str, var_info: dict, threshold: int
) -> tuple[bool, str]:
    """
    Determine if a variable should be filtered based on business rules.

    Filtering criteria (checked in order):
    1. Binary: Exactly 2 distinct values
    2. High cardinality: Distinct values > threshold
    3. Other field: Variable name contains "other"

    Args:
        var_name: Variable name
        var_info: Variable info dict from variable_centered_metadata
        threshold: High cardinality threshold from config

    Returns:
        Tuple of (should_filter: bool, reason: str)
        - reason is one of: "binary", "high_cardinality", "other_field", or None if not filtered

    Example:
        >>> var_info = {"distinct_count": 2, "variable_type": "numeric"}
        >>> should_filter, reason = _should_filter_variable("gender", var_info, 30)
        >>> print(should_filter, reason)
        (True, 'binary')
    """
    # Get distinct count
    distinct_count = var_info.get("distinct_count", 0)

    # Check 1: Binary variables (exactly 2 distinct values)
    if distinct_count == 2:
        return True, "binary"

    # Check 2: High cardinality (distinct values > threshold)
    if distinct_count > threshold:
        return True, "high_cardinality"

    # Check 3: Other text fields (name contains "other")
    if "other" in var_name.lower():
        return True, "other_field"

    # Variable passes all filters
    return False, ""


def _get_filter_reason_description(reason: str) -> str:
    """
    Get human-readable description for filter reason.

    Args:
        reason: Filter reason code ("binary", "high_cardinality", "other_field")

    Returns:
        Human-readable description

    Example:
        >>> _get_filter_reason_description("binary")
        'Binary variable (exactly 2 distinct values)'
    """
    descriptions = {
        "binary": "Binary variable (exactly 2 distinct values)",
        "high_cardinality": "High cardinality (too many distinct values)",
        "other_field": "Other text field (open-ended feedback)",
    }
    return descriptions.get(reason, "Unknown filter reason")
