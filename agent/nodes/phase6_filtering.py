"""
Phase 6: Filtering Nodes (Steps 19-20)

This module contains nodes for filtering tables by statistical significance:
- Step 19: generate_filter_list_node - Evaluate tables against filtering criteria
- Step 20: apply_filter_to_tables_node - Filter to significant tables only
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from agent.state import WorkflowState
from agent.config import DEFAULT_CONFIG

logger = logging.getLogger(__name__)


# =============================================================================
# Step 19: Generate Filter List
# =============================================================================

def generate_filter_list_node(state: WorkflowState) -> WorkflowState:
    """
    Step 19: Generate filter list based on statistical significance criteria.

    This node evaluates each table from the statistical summary against
    filtering criteria to determine which tables should be included in
    the final presentation.

    Filter criteria (all must pass):
    1. Statistical significance: p_value < significance_level (default: 0.05)
    2. Effect size: cramers_v >= min_cramers_v (default: 0.1)
    3. Validity: is_valid must be True (no statistical assumption violations)

    The filter list includes pass/fail status for each criterion and an
    overall include/exclude decision with reason.

    Args:
        state: Current workflow state. Must contain:
            - statistical_summary: Statistical test results from Step 18
            - config: Configuration dict (optional, uses DEFAULT_CONFIG)

    Returns:
        Updated workflow state with:
            - filter_list: Dict with filters list and summary statistics
            - filter_list_json_path: Path to saved filter_list.json
            - current_step: Set to 19
            - errors: List of errors (appended if any occur)
            - warnings: List of warnings (appended if any occur)

    Example:
        >>> state = {
        ...     "statistical_summary": {
        ...         "tables": [
        ...             {
        ...                 "table_name": "gender_x_satisfaction",
        ...                 "p_value": 0.0023,
        ...                 "cramers_v": 0.18,
        ...                 "is_valid": True
        ...             }
        ...         ]
        ...     }
        ... }
        >>> new_state = generate_filter_list_node(state)
        >>> print(new_state["filter_list"]["summary"]["included"])
        1
    """
    logger.info("Step 19: Generating filter list")

    # Get required inputs from state
    statistical_summary = state.get("statistical_summary")
    config = state.get("config", DEFAULT_CONFIG)

    # Validate required inputs
    if not statistical_summary:
        error_msg = "No statistical_summary found in state - Step 18 must complete first"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 19,
            "errors": state.get("errors", []) + [error_msg],
        }

    # Get filtering thresholds from config
    significance_level = config.get("significance_level", 0.05)
    min_cramers_v = config.get("min_cramers_v", 0.1)
    min_cell_count = config.get("min_cell_count", 10)

    logger.info(
        f"Filter criteria: p < {significance_level}, "
        f"Cramer's V >= {min_cramers_v}, "
        f"min_cell_count >= {min_cell_count}"
    )

    try:
        # Extract tables from statistical summary
        tables = statistical_summary.get("tables", [])

        if not tables:
            warning_msg = "No tables found in statistical_summary - creating empty filter list"
            logger.warning(warning_msg)
            warnings = state.get("warnings", []).copy()
            warnings.append(warning_msg)

            # Create empty filter list
            filter_list = {
                "filters": [],
                "summary": {
                    "total_tables": 0,
                    "included": 0,
                    "excluded": 0,
                    "criteria": {
                        "significance_level": significance_level,
                        "min_cramers_v": min_cramers_v,
                        "min_cell_count": min_cell_count,
                    }
                },
                "generated_at": datetime.now().isoformat(),
            }

            return {
                **state,
                "current_step": 19,
                "filter_list": filter_list,
                "warnings": warnings,
            }

        logger.info(f"Evaluating {len(tables)} tables against filter criteria")

        # Evaluate each table against filter criteria
        filters = []
        included_count = 0
        excluded_count = 0

        # Track exclusion reasons for summary
        exclusion_reasons = {
            "not_significant": 0,
            "effect_size_too_small": 0,
            "invalid_table": 0,
            "multiple_failures": 0,
        }

        for table_stats in tables:
            table_name = table_stats.get("table_name", "unknown")

            # Evaluate against criteria
            filter_result = _should_include_table(
                table_stats, significance_level, min_cramers_v
            )

            # Build filter entry
            filter_entry = {
                "table_id": table_name,
                "include": filter_result["include"],
                "p_value": table_stats.get("p_value"),
                "cramers_v": table_stats.get("cramers_v"),
                "is_valid": table_stats.get("is_valid", True),
                "passes_significance": filter_result["passes_significance"],
                "passes_cramers_v": filter_result["passes_cramers_v"],
                "passes_validity": filter_result["passes_validity"],
                "reason": filter_result["reason"],
            }

            filters.append(filter_entry)

            # Update counts
            if filter_result["include"]:
                included_count += 1
            else:
                excluded_count += 1
                # Track exclusion reason
                if "not statistically significant" in filter_result["reason"].lower():
                    exclusion_reasons["not_significant"] += 1
                elif "effect size" in filter_result["reason"].lower():
                    exclusion_reasons["effect_size_too_small"] += 1
                elif "invalid" in filter_result["reason"].lower():
                    exclusion_reasons["invalid_table"] += 1
                else:
                    exclusion_reasons["multiple_failures"] += 1

        # Build summary
        summary = {
            "total_tables": len(tables),
            "included": included_count,
            "excluded": excluded_count,
            "inclusion_rate": round(included_count / len(tables) * 100, 2) if tables else 0,
            "exclusion_reasons": exclusion_reasons,
            "criteria": {
                "significance_level": significance_level,
                "min_cramers_v": min_cramers_v,
                "min_cell_count": min_cell_count,
            }
        }

        # Build complete filter list
        filter_list = {
            "filters": filters,
            "summary": summary,
            "generated_at": datetime.now().isoformat(),
        }

        # Create output directory
        temp_dir = Path(config.get("temp_dir", "temp")) / "filters"
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Save filter list to JSON
        filter_list_path = temp_dir / "filter_list.json"
        with open(filter_list_path, 'w', encoding='utf-8') as f:
            json.dump(filter_list, f, indent=2)

        logger.info(f"Filter list saved to: {filter_list_path}")

        # Log summary
        logger.info(
            f"Filter list generation complete: "
            f"{included_count}/{len(tables)} tables included, "
            f"{excluded_count} excluded"
        )
        logger.info(
            f"Exclusion reasons: "
            f"not_significant={exclusion_reasons['not_significant']}, "
            f"effect_size_too_small={exclusion_reasons['effect_size_too_small']}, "
            f"invalid={exclusion_reasons['invalid_table']}, "
            f"multiple={exclusion_reasons['multiple_failures']}"
        )

        # Prepare warnings
        warnings = state.get("warnings", []).copy()

        # Warn if no tables passed filters
        if included_count == 0:
            warning_msg = (
                f"No tables passed the filter criteria. "
                f"This may indicate: (1) no significant relationships in the data, "
                f"(2) filter thresholds too strict, or (3) sample size too small. "
                f"Consider adjusting significance_level or min_cramers_v in config."
            )
            logger.warning(warning_msg)
            warnings.append(warning_msg)

        # Warn if all tables passed filters
        elif excluded_count == 0:
            logger.info(
                f"All {len(tables)} tables passed filters - "
                "this may indicate filter thresholds are too lenient"
            )

        # Warn if low inclusion rate (< 20%)
        elif summary["inclusion_rate"] < 20:
            warning_msg = (
                f"Low inclusion rate: {summary['inclusion_rate']:.1f}% "
                f"({included_count}/{len(tables)} tables). "
                f"Consider reviewing filter thresholds or data quality."
            )
            logger.warning(warning_msg)
            warnings.append(warning_msg)

        # Return new state
        return {
            **state,
            "current_step": 19,
            "filter_list": filter_list,
            "warnings": warnings,
        }

    except Exception as e:
        error_msg = f"Unexpected error generating filter list: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": 19,
            "errors": state.get("errors", []) + [error_msg],
        }


def _should_include_table(
    table_stats: Dict[str, Any],
    significance_level: float,
    min_cramers_v: float,
) -> Dict[str, Any]:
    """
    Evaluate a table against filtering criteria.

    A table is included if it passes ALL of the following checks:
    1. Statistical significance: p_value < significance_level
    2. Effect size: cramers_v >= min_cramers_v
    3. Validity: is_valid must be True

    Args:
        table_stats: Table statistics from statistical_summary
        significance_level: P-value threshold (default: 0.05)
        min_cramers_v: Minimum Cramer's V (default: 0.1)

    Returns:
        Dictionary with:
            - include: bool (True if all checks pass)
            - passes_significance: bool
            - passes_cramers_v: bool
            - passes_validity: bool
            - reason: str (explanation of decision)

    Example:
        >>> table_stats = {
        ...     "table_name": "gender_x_satisfaction",
        ...     "p_value": 0.0023,
        ...     "cramers_v": 0.18,
        ...     "is_valid": True
        ... }
        >>> result = _should_include_table(table_stats, 0.05, 0.1)
        >>> print(result["include"])
        True
        >>> print(result["reason"])
        'Passed all filters'
    """
    # Initialize result
    result = {
        "include": False,
        "passes_significance": False,
        "passes_cramers_v": False,
        "passes_validity": False,
        "reason": "",
    }

    # Get values with defaults for missing fields
    p_value = table_stats.get("p_value", 1.0)  # Default to 1.0 (not significant)
    cramers_v = table_stats.get("cramers_v", 0.0)  # Default to 0.0 (no effect)
    is_valid = table_stats.get("is_valid", True)  # Default to True
    error = table_stats.get("error", "")

    # Check 1: Statistical significance
    passes_significance = p_value < significance_level
    result["passes_significance"] = passes_significance

    # Check 2: Effect size (Cramer's V)
    passes_cramers_v = cramers_v >= min_cramers_v
    result["passes_cramers_v"] = passes_cramers_v

    # Check 3: Table validity
    passes_validity = is_valid
    result["passes_validity"] = passes_validity

    # Determine overall inclusion
    if passes_significance and passes_cramers_v and passes_validity:
        result["include"] = True
        result["reason"] = "Passed all filters"
    else:
        result["include"] = False

        # Build detailed exclusion reason
        failures = []

        if not passes_validity:
            if error:
                failures.append(f"Invalid table ({error})")
            else:
                failures.append("Invalid table")
        elif not passes_significance:
            failures.append(
                f"Not statistically significant (p={p_value:.4f} >= {significance_level})"
            )
        elif not passes_cramers_v:
            failures.append(
                f"Effect size too small (Cramer's V={cramers_v:.4f} < {min_cramers_v})"
            )

        # If multiple failures, combine them
        if len(failures) > 1:
            result["reason"] = "; ".join(failures[:-1]) + ", and " + failures[-1]
        else:
            result["reason"] = failures[0] if failures else "Unknown reason"

    return result


# =============================================================================
# Validation Function
# =============================================================================

def validate_filtering_results(
    statistical_summary: Dict[str, Any],
    filter_list: Dict[str, Any],
    filtered_tables: Dict[str, Any]
) -> Tuple[bool, List[str], List[str]]:
    """
    Validate that filtering was complete and successful.

    This function performs multiple validation checks to ensure that all tables
    were properly evaluated, no tables were dropped due to errors, and filtering
    results are consistent.

    Args:
        statistical_summary: Statistical test results from Step 18 containing tables
        filter_list: Filter criteria from Step 19 containing filters
        filtered_tables: Filtered results from apply_filter_to_tables_node

    Returns:
        Tuple of (is_valid, errors, warnings):
        - is_valid: False if critical errors found, True otherwise
        - errors: List of critical error messages (must be fixed)
        - warnings: List of non-critical warnings (informational)

    Validation Checks:
        1. **All tables evaluated**: Every table in statistical_summary must have
           a corresponding filter in filter_list. Error if counts don't match.

        2. **No tables dropped due to errors**: Check all filter entries have
           a reason field and none contain "error" in the reason text.
           Error if any tables were dropped due to errors.

        3. **At least one significant table**: Check that filtered_tables contains
           at least one table. Warning only (not critical, presentation will show
           summary only).

        4. **Filter completeness**: Each table in statistical_summary must have
           a corresponding filter entry with matching table_id. Error if any
           table is missing a filter.

    Example:
        >>> statistical_summary = {
        ...     "tables": [
        ...         {"table_name": "gender_x_satisfaction", "p_value": 0.0023},
        ...         {"table_name": "age_x_brand", "p_value": 0.15}
        ...     ]
        ... }
        >>> filter_list = {
        ...     "filters": [
        ...         {"table_id": "gender_x_satisfaction", "include": True, "reason": "Passed all filters"},
        ...         {"table_id": "age_x_brand", "include": False, "reason": "Not statistically significant"}
        ...     ]
        ... }
        >>> filtered_tables = {"tables": [statistical_summary["tables"][0]]}
        >>> is_valid, errors, warnings = validate_filtering_results(
        ...     statistical_summary, filter_list, filtered_tables
        ... )
        >>> print(is_valid)
        True
        >>> print(len(warnings))
        0
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Validate inputs
    if not statistical_summary:
        errors.append("statistical_summary is empty or None")
        return False, errors, warnings

    if not filter_list:
        errors.append("filter_list is empty or None")
        return False, errors, warnings

    if not filtered_tables:
        errors.append("filtered_tables is empty or None")
        return False, errors, warnings

    # Extract data structures
    tables = statistical_summary.get("tables", [])
    filters = filter_list.get("filters", [])

    # ==========================================================================
    # Validation 1: All tables evaluated
    # ==========================================================================
    num_tables = len(tables)
    num_filters = len(filters)

    # Note: Count mismatch is checked in Validation 4 (filter completeness)
    # which distinguishes between missing filters (error) and extra filters (warning)

    # ==========================================================================
    # Validation 2: No tables dropped due to errors
    # ==========================================================================
    tables_with_errors = []
    for filter_entry in filters:
        reason = filter_entry.get("reason", "")
        if "error" in reason.lower():
            table_id = filter_entry.get("table_id", "unknown")
            tables_with_errors.append(f"{table_id}: {reason}")

    if tables_with_errors:
        errors.append(
            f"{len(tables_with_errors)} table(s) dropped due to errors: " +
            "; ".join(tables_with_errors[:3]) +
            ("..." if len(tables_with_errors) > 3 else "")
        )
        logger.error(f"Tables dropped due to errors: {tables_with_errors}")

    # ==========================================================================
    # Validation 3: At least one significant table (warning only)
    # ==========================================================================
    significant_tables = filtered_tables.get("tables", [])
    num_significant = len(significant_tables)

    if num_significant == 0:
        warning_msg = (
            f"No significant tables found after filtering. "
            f"Presentation will show summary only."
        )
        warnings.append(warning_msg)
        logger.warning(warning_msg)

    # ==========================================================================
    # Validation 4: Filter completeness
    # ==========================================================================
    # Build set of table names from statistical_summary
    table_names = {table.get("table_name", "") for table in tables}
    table_names.discard("")  # Remove empty string if any

    # Build set of table IDs from filters
    filtered_table_ids = {f.get("table_id", "") for f in filters}
    filtered_table_ids.discard("")  # Remove empty string if any

    # Check for missing filters
    missing_filters = table_names - filtered_table_ids
    if missing_filters:
        errors.append(
            f"Missing filters for {len(missing_filters)} table(s): "
            f"{', '.join(list(missing_filters)[:5])}"
            f"{'...' if len(missing_filters) > 5 else ''}"
        )
        logger.error(f"Missing filters for tables: {missing_filters}")

    # Check for extra filters (filters without corresponding tables)
    extra_filters = filtered_table_ids - table_names
    if extra_filters:
        warnings.append(
            f"Found {len(extra_filters)} filter(s) without corresponding tables: "
            f"{', '.join(list(extra_filters)[:5])}"
            f"{'...' if len(extra_filters) > 5 else ''}"
        )
        logger.warning(f"Extra filters found: {extra_filters}")

    # Determine overall validity
    is_valid = len(errors) == 0

    # Log validation summary
    logger.info(
        f"Filtering validation complete: "
        f"valid={is_valid}, errors={len(errors)}, warnings={len(warnings)}"
    )
    logger.info(
        f"Filtering summary: {num_tables} tables evaluated, "
        f"{num_significant} significant tables found"
    )

    return is_valid, errors, warnings


# =============================================================================
# Step 20: Apply Filter to Tables
# =============================================================================

def apply_filter_to_tables_node(state: WorkflowState) -> WorkflowState:
    """
    Step 20: Apply filter to cross-table data, keeping only significant tables.

    This node uses the filter list generated in Step 19 to filter the
    cross-table data, creating a new dataset containing only the tables
    that passed all filtering criteria.

    The filtered tables are saved to both CSV and JSON files and stored in
    the state for use by the PowerPoint generation node in Step 21.

    Args:
        state: Current workflow state. Must contain:
            - filter_list: Filter criteria from Step 19
            - statistical_summary: Statistical results from Step 18
            - config: Configuration dict (optional, uses DEFAULT_CONFIG)

    Returns:
        Updated workflow state with:
            - filtered_tables: Dict containing only significant tables
            - significant_tables_json_path: Path to saved significant_tables.json
            - significant_tables_csv_path: Path to saved significant_tables.csv
            - current_step: Set to 20
            - errors: List of errors (appended if any occur)
            - warnings: List of warnings (appended if any occur)

    Example:
        >>> state = {
        ...     "filter_list": {
        ...         "filters": [
        ...             {"table_id": "gender_x_satisfaction", "include": True},
        ...             {"table_id": "age_x_brand", "include": False}
        ...         ]
        ...     },
        ...         "statistical_summary": {
        ...         "tables": [...]
        ...     }
        ... }
        >>> new_state = apply_filter_to_tables_node(state)
        >>> print(new_state["filtered_tables"]["summary"]["original_count"])
        2
        >>> print(new_state["filtered_tables"]["summary"]["filtered_count"])
        1
    """
    logger.info("Step 20: Applying filter to tables")

    # Get required inputs from state
    filter_list = state.get("filter_list")
    statistical_summary = state.get("statistical_summary")
    config = state.get("config", DEFAULT_CONFIG)

    # Validate required inputs
    if not filter_list:
        error_msg = "No filter_list found in state - Step 19 must complete first"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 20,
            "errors": state.get("errors", []) + [error_msg],
        }

    if not statistical_summary:
        error_msg = "No statistical_summary found in state - Step 18 must complete first"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 20,
            "errors": state.get("errors", []) + [error_msg],
        }

    try:
        # Import pandas for CSV conversion
        import pandas as pd

        # Get filters and original tables
        filters = filter_list.get("filters", [])
        tables = statistical_summary.get("tables", [])

        if not filters:
            warning_msg = "No filters found in filter_list - creating empty filtered tables"
            logger.warning(warning_msg)
            warnings = state.get("warnings", []).copy()
            warnings.append(warning_msg)

            # Create empty filtered tables
            filtered_tables = {
                "tables": [],
                "summary": {
                    "original_count": 0,
                    "filtered_count": 0,
                    "filtering_applied": True,
                    "criteria": filter_list.get("summary", {}).get("criteria", {}),
                },
                "filtered_at": datetime.now().isoformat(),
            }

            # Create output directory and save empty files
            output_dir = Path(config.get("output_dir", "output"))
            output_dir.mkdir(parents=True, exist_ok=True)

            json_path = output_dir / "significant_tables.json"
            csv_path = output_dir / "significant_tables.csv"

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_tables, f, indent=2)

            # Create empty CSV with headers
            pd.DataFrame(columns=["table_name", "p_value", "cramers_v", "is_valid"]).to_csv(
                csv_path, index=False
            )

            return {
                **state,
                "current_step": 20,
                "filtered_tables": filtered_tables,
                "significant_tables_json_path": str(json_path),
                "significant_tables_csv_path": str(csv_path),
                "warnings": warnings,
            }

        # Extract table IDs where include=True
        included_table_ids = {
            f["table_id"] for f in filters if f.get("include", False)
        }

        logger.info(f"Found {len(included_table_ids)} tables to include from filter list")

        # Filter tables based on include flag
        filtered_tables_data = [
            table for table in tables
            if table.get("table_name", "") in included_table_ids
        ]

        # Build summary with required format
        original_count = len(tables)
        filtered_count = len(filtered_tables_data)

        summary = {
            "original_count": original_count,
            "filtered_count": filtered_count,
            "filtering_applied": True,
            "excluded_count": original_count - filtered_count,
            "inclusion_rate": round(filtered_count / original_count * 100, 2) if original_count > 0 else 0,
            "criteria": filter_list.get("summary", {}).get("criteria", {}),
        }

        # Build filtered tables structure
        filtered_tables = {
            "tables": filtered_tables_data,
            "summary": summary,
            "filtered_at": datetime.now().isoformat(),
        }

        # Create output directory
        output_dir = Path(config.get("output_dir", "output"))
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save filtered tables to JSON
        json_path = output_dir / "significant_tables.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_tables, f, indent=2)
        logger.info(f"Filtered tables saved to JSON: {json_path}")

        # Convert and save to CSV
        csv_path = output_dir / "significant_tables.csv"
        if filtered_tables_data:
            # Flatten nested dicts for CSV
            flattened_data = []
            for table in filtered_tables_data:
                row = {
                    "table_name": table.get("table_name", ""),
                    "p_value": table.get("p_value", None),
                    "cramers_v": table.get("cramers_v", None),
                    "is_valid": table.get("is_valid", True),
                    "chi_square": table.get("chi_square", None),
                    "degrees_of_freedom": table.get("degrees_of_freedom", None),
                }
                flattened_data.append(row)

            df = pd.DataFrame(flattened_data)
            df.to_csv(csv_path, index=False)
            logger.info(f"Filtered tables saved to CSV: {csv_path} ({len(df)} rows)")
        else:
            # Create empty CSV with headers
            pd.DataFrame(columns=[
                "table_name", "p_value", "cramers_v", "is_valid",
                "chi_square", "degrees_of_freedom"
            ]).to_csv(csv_path, index=False)
            logger.info(f"Empty CSV saved: {csv_path}")

        # ======================================================================
        # Validate filtering results
        # ======================================================================
        is_valid, validation_errors, validation_warnings = validate_filtering_results(
            statistical_summary, filter_list, filtered_tables
        )

        # Prepare errors and warnings from state
        errors = state.get("errors", []).copy()
        warnings = state.get("warnings", []).copy()

        # Add validation errors to state (critical)
        if not is_valid:
            errors.extend(validation_errors)
            logger.error(
                f"Filtering validation failed with {len(validation_errors)} error(s)"
            )

        # Add validation warnings to state (non-critical)
        if validation_warnings:
            warnings.extend(validation_warnings)
            logger.info(
                f"Filtering validation generated {len(validation_warnings)} warning(s)"
            )

        # ======================================================================
        # Log summary and warnings
        # ======================================================================
        logger.info(
            f"Filter application complete: "
            f"{filtered_count}/{original_count} tables included, "
            f"{summary['excluded_count']} excluded "
            f"({summary['inclusion_rate']:.1f}% inclusion rate)"
        )

        # Log validation summary to state
        logger.info(
            f"Filtering summary: "
            f"total_tables_evaluated={original_count}, "
            f"significant_tables_count={filtered_count}, "
            f"filtering_valid={is_valid}"
        )

        # Warn if no significant tables (additional to validation warning)
        if filtered_count == 0:
            warning_msg = (
                f"No significant tables found after filtering. "
                f"PowerPoint presentation will be empty. "
                f"Consider adjusting filter thresholds or data quality."
            )
            logger.warning(warning_msg)
            warnings.append(warning_msg)

        # Log table details
        if filtered_count > 0:
            logger.info("Significant tables:")
            for table in filtered_tables_data:
                table_name = table.get("table_name", "unknown")
                p_value = table.get("p_value", "N/A")
                cramers_v = table.get("cramers_v", "N/A")
                logger.info(
                    f"  - {table_name}: p={p_value:.4f}, V={cramers_v:.4f}"
                )

        # ======================================================================
        # Return new state with validation summary
        # ======================================================================
        return {
            **state,
            "current_step": 20,
            "filtered_tables": filtered_tables,
            "significant_tables_json_path": str(json_path),
            "significant_tables_csv_path": str(csv_path),
            "errors": errors,
            "warnings": warnings,
            # Add filtering summary to state for downstream nodes
            "total_tables_evaluated": original_count,
            "significant_tables_count": filtered_count,
            "filtering_valid": is_valid,
        }

    except Exception as e:
        error_msg = f"Unexpected error applying filter to tables: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": 20,
            "errors": state.get("errors", []) + [error_msg],
        }
