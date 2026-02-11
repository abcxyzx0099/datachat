"""
Phase 5: Statistics Nodes (Direct Library Call)

This module contains a simplified statistics computation node that directly calls
the StatisticsCalculator library, replacing the over-engineered script generation
and subprocess execution pattern of nodes 17-18.

Node:
- Step 17-18 (NEW): compute_statistics_node - Direct library call for Chi-square

Architecture:
- OLD: Node 17 (generate script) → Node 18 (execute script) → StatisticsCalculator
- NEW: Node 17-18 (compute_statistics_node) → StatisticsCalculator

Benefits:
- Single node instead of two
- No subprocess overhead
- Direct Python call, easier to debug
- Cleaner separation of concerns (orchestration vs. computation)
"""

import logging
import json
from typing import Dict, Any
from pathlib import Path

from agent.state import WorkflowState, STEP_17_GENERATE_STATS_SCRIPT, STEP_18_EXECUTE_STATS_SCRIPT
from agent.utils.tracing import trace_node
from agent.config import DEFAULT_CONFIG

logger = logging.getLogger(__name__)


@trace_node("Step 17-18: Compute Statistics (Direct Library Call)")
def compute_statistics_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Step 17-18 (NEW): Compute statistics using library directly.

    This node replaces the over-engineered script generation and subprocess
    execution pattern. It directly calls the StatisticsCalculator
    from the library, avoiding unnecessary subprocess overhead and complexity.

    This is a BUSINESS LOGIC node - it performs statistical computation
    using the spss_analyzer library. The node itself only handles
    orchestration: reading input, calling the library, formatting output.

    Args:
        state: Current workflow state. Must contain:
            - cross_table_file: Path to JSON file with cross-table data
            - config: Optional configuration dict

    Returns:
        Updated workflow state with:
            - statistics_results: Dict with Chi-square and Cramer's V results
            - current_step: Set to STEP_18_EXECUTE_STATS_SCRIPT
            - errors: List of errors (appended if any occur)
            - warnings: List of warnings (appended if any occur)

    Raises:
        FileNotFoundError: If cross_table JSON file doesn't exist
        ValueError: If cross_table JSON is malformed
        Exception: For unexpected errors during computation

    Example:
        >>> state = {
        ...     "cross_table_file": "output/cross_table.json",
        ... }
        >>> new_state = compute_statistics_node(state)
        >>> results = new_state["statistics_results"]
        >>> print(results["tables"][0]["chi_square"])
        15.23
    """
    logger.info("Step 17-18 (NEW): Computing statistics using direct library call")

    # Get cross table file path from state
    cross_table_file = state.get("cross_table_file")

    if not cross_table_file:
        error_msg = "No cross_table_file available in state. Step 16 must complete first."
        logger.error(error_msg)
        return {
            "current_step": STEP_18_EXECUTE_STATS_SCRIPT,
            "errors": [error_msg],
        }

    # Get config
    config = state.get("config", DEFAULT_CONFIG)
    significance_level = config.get("significance_level", 0.05)

    logger.info(f"Loading cross-table data from: {cross_table_file}")

    # Load cross-table JSON
    try:
        with open(cross_table_file, 'r', encoding='utf-8') as f:
            cross_table_data = json.load(f)
    except FileNotFoundError:
        error_msg = f"Cross-table file not found: {cross_table_file}"
        logger.error(error_msg)
        return {
            "current_step": STEP_18_EXECUTE_STATS_SCRIPT,
            "errors": [error_msg],
        }
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in cross-table file: {cross_table_file} - {str(e)}"
        logger.error(error_msg)
        return {
            "current_step": STEP_18_EXECUTE_STATS_SCRIPT,
            "errors": [error_msg],
        }
    except Exception as e:
        error_msg = f"Unexpected error loading cross-table file: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "current_step": STEP_18_EXECUTE_STATS_SCRIPT,
            "errors": [error_msg],
        }

    # Validate cross table data structure
    tables = cross_table_data.get("tables", [])

    if not tables:
        error_msg = f"No tables found in cross-table file: {cross_table_file}"
        logger.error(error_msg)
        return {
            "current_step": STEP_18_EXECUTE_STATS_SCRIPT,
            "errors": [error_msg],
        }

    logger.info(f"Processing {len(tables)} cross-tables for statistical analysis")

    # Import StatisticsCalculator from library
    try:
        from lib.spss_analyzer.analysis.statistics import StatisticsCalculator

        calculator = StatisticsCalculator(significance_level=significance_level)

    except ImportError as e:
        error_msg = f"Failed to import StatisticsCalculator: {str(e)}"
        logger.error(error_msg)
        return {
            "current_step": STEP_18_EXECUTE_STATS_SCRIPT,
            "errors": [error_msg],
        }

    # Compute statistics for each table
    results = []
    processed_count = 0
    skipped_count = 0

    for table in tables:
        try:
            # Extract table data
            table_id = table.get("table_id", f"table_{processed_count + 1}")
            row_labels = table.get("row_labels", [])
            column_labels = table.get("column_labels", [])
            counts = table.get("counts", [])

            # Validate required fields
            if not row_labels or not column_labels or not counts:
                logger.warning(f"Table {table_id}: Missing required fields, skipping")
                skipped_count += 1
                continue

            # Validate counts dimensions
            if not counts or len(counts) == 0:
                logger.warning(f"Table {table_id}: Empty counts data, skipping")
                skipped_count += 1
                continue

            # Call StatisticsCalculator.analyze_table()
            result = calculator.analyze_table(
                counts=counts,
                row_labels=row_labels,
                column_labels=column_labels
            )

            # Format result for state
            table_result = {
                "table_name": table_id,
                "row_variable": table.get("row_variable", ""),
                "column_variable": table.get("column_variable", ""),
                "chi_square": result.get("chi_square"),
                "degrees_of_freedom": result.get("degrees_of_freedom"),
                "p_value": result.get("p_value"),
                "cramers_v": result.get("cramers_v"),
                "interpretation": result.get("interpretation"),
                "is_significant": result.get("is_significant"),
                "is_valid": result.get("is_valid"),
            }

            results.append(table_result)
            processed_count += 1

            logger.debug(
                f"Table {table_id}: χ²={result.get('chi_square', 'N/A'):.4f}, "
                f"p={result.get('p_value', 'N/A'):.4f}, "
                f"V={result.get('cramers_v', 'N/A'):.4f}"
            )

        except Exception as e:
            logger.error(f"Error computing statistics for table {table_id}: {str(e)}")
            # Continue with other tables instead of failing completely
            continue

    # Build results structure
    statistics_summary = {
        "significance_level": significance_level,
        "total_tables": len(tables),
        "processed_tables": processed_count,
        "skipped_tables": skipped_count,
        "tables": results,
    }

    # Log summary
    logger.info(
        f"Statistics computation complete: "
        f"{processed_count} processed, {skipped_count} skipped, "
        f"{len(results)} results returned"
    )

    # Prepare warnings
    warnings = state.get("warnings", []).copy()

    if skipped_count > 0:
        warning_msg = f"{skipped_count} tables skipped due to missing or invalid data"
        logger.warning(warning_msg)
        warnings.append(warning_msg)

    return {
        "current_step": STEP_18_EXECUTE_STATS_SCRIPT,
        "statistics_results": statistics_summary,
        "warnings": warnings,
    }
