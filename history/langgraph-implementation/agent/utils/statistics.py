"""
Statistics Module

This module provides statistical computation functions for survey analysis,
including Chi-square test, Cramer's V effect size, and significance testing.

These functions are used in Phase 5 (Statistical Analysis) of the workflow.
"""

import logging
import math
from typing import Dict, Optional

import numpy as np
import pandas as pd
from scipy import stats

from agent.config import DEFAULT_CONFIG

logger = logging.getLogger(__name__)


# =============================================================================
# Cramer's V Interpretation Thresholds
# =============================================================================
# Based on Cohen's guidelines and common research practice
CRAMERS_V_THRESHOLDS = {
    "negligible": (0.00, 0.10),
    "small": (0.10, 0.30),
    "medium": (0.30, 0.50),
    "large": (0.50, 1.00),
}


def calculate_chi_square(contingency_table: pd.DataFrame) -> Dict:
    """
    Perform Chi-square test of independence on a contingency table.

    Uses scipy.stats.chi2_contingency to compute the chi-square statistic,
    p-value, and degrees of freedom.

    Args:
        contingency_table: pandas DataFrame with contingency table counts
                          (rows = categories of variable 1, columns = categories of variable 2)

    Returns:
        Dict with keys:
            - chi_square (float): Chi-square test statistic
            - p_value (float): P-value for the test
            - degrees_of_freedom (int): Degrees of freedom
            - expected_counts (np.ndarray): Expected frequencies under independence
            - is_valid (bool): Whether test assumptions are met
            - warning (str|None): Warning message if assumptions violated

    Raises:
        ValueError: If contingency table is invalid or computation fails

    Example:
        >>> import pandas as pd
        >>> table = pd.DataFrame([[10, 20], [30, 40]])
        >>> result = calculate_chi_square(table)
        >>> print(f"Chi-square: {result['chi_square']:.4f}")
        >>> print(f"p-value: {result['p_value']:.4f}")
    """
    # Validate input
    if not isinstance(contingency_table, pd.DataFrame):
        raise ValueError(
            f"Contingency table must be a pandas DataFrame, got {type(contingency_table)}"
        )

    if contingency_table.empty:
        raise ValueError("Contingency table is empty")

    # Ensure all values are numeric
    try:
        counts = contingency_table.values.astype(float)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Contingency table contains non-numeric values: {e}")

    # Get minimum expected cell count from config
    min_cell_count = DEFAULT_CONFIG.get("min_cell_count", 10)

    # Compute expected frequencies
    row_totals = counts.sum(axis=1, keepdims=True)
    col_totals = counts.sum(axis=0, keepdims=True)
    grand_total = counts.sum()

    if grand_total == 0:
        raise ValueError("Contingency table has zero total count")

    expected_counts = (row_totals @ col_totals) / grand_total

    # Check assumption: minimum expected cell count
    min_expected = expected_counts.min()
    is_valid = min_expected >= min_cell_count

    warning = None
    if not is_valid:
        warning = (
            f"Chi-square assumption violated: minimum expected count ({min_expected:.2f}) "
            f"is below threshold ({min_cell_count}). Results may be unreliable."
        )
        logger.warning(warning)

    # Perform chi-square test
    try:
        chi2, p_value, dof, _ = stats.chi2_contingency(counts)

        result = {
            "chi_square": float(chi2),
            "p_value": float(p_value),
            "degrees_of_freedom": int(dof),
            "expected_counts": expected_counts.tolist(),
            "is_valid": is_valid,
            "warning": warning,
        }

        logger.debug(
            f"Chi-square test: χ2={chi2:.4f}, p={p_value:.4f}, df={dof}, "
            f"valid={is_valid}"
        )

        return result

    except ValueError as e:
        raise ValueError(f"Chi-square test computation failed: {e}")


def calculate_cramers_v(
    contingency_table: pd.DataFrame, chi_square: Optional[float] = None
) -> float:
    """
    Calculate Cramer's V effect size for a contingency table.

    Cramer's V measures the strength of association between two categorical
    variables. Formula: V = sqrt(χ² / (n * min(r-1, c-1)))

    Args:
        contingency_table: pandas DataFrame with contingency table counts
        chi_square: Pre-computed chi-square statistic (optional, will be computed if None)

    Returns:
        Cramer's V value between 0 and 1

    Raises:
        ValueError: If computation fails or table is invalid

    Example:
        >>> import pandas as pd
        >>> table = pd.DataFrame([[10, 20], [30, 40]])
        >>> v = calculate_cramers_v(table)
        >>> print(f"Cramer's V: {v:.4f}")
    """
    # Validate input
    if not isinstance(contingency_table, pd.DataFrame):
        raise ValueError(
            f"Contingency table must be a pandas DataFrame, got {type(contingency_table)}"
        )

    if contingency_table.empty:
        raise ValueError("Contingency table is empty")

    try:
        counts = contingency_table.values.astype(float)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Contingency table contains non-numeric values: {e}")

    # Compute chi-square if not provided
    if chi_square is None:
        result = calculate_chi_square(contingency_table)
        chi_square = result["chi_square"]

    # Get table dimensions
    n_rows, n_cols = counts.shape
    min_dim = min(n_rows - 1, n_cols - 1)

    if min_dim == 0:
        # One of the dimensions has only 1 category
        # Cramer's V is not meaningful
        logger.warning("Contingency table has only 1 row or 1 column; Cramer's V is undefined")
        return 0.0

    # Calculate total sample size
    n = counts.sum()

    if n == 0:
        raise ValueError("Contingency table has zero total count")

    # Calculate Cramer's V
    try:
        cramers_v = math.sqrt(chi_square / (n * min_dim))

        # Clamp to [0, 1] range (handles floating point errors)
        cramers_v = max(0.0, min(1.0, cramers_v))

        logger.debug(f"Cramer's V: {cramers_v:.4f} (n={n}, min_dim={min_dim})")

        return cramers_v

    except (ValueError, ZeroDivisionError) as e:
        raise ValueError(f"Cramer's V computation failed: {e}")


def interpret_cramers_v(cramers_v: float) -> str:
    """
    Interpret Cramer's V effect size.

    Follows Cohen's (1988) guidelines for social science research.

    Args:
        cramers_v: Cramer's V value (0.0 to 1.0)

    Returns:
        Interpretation category: "negligible", "small", "medium", "large",
        "invalid", or "unknown"

    Example:
        >>> interpret_cramers_v(0.05)
        'negligible'
        >>> interpret_cramers_v(0.25)
        'small'
        >>> interpret_cramers_v(0.40)
        'medium'
        >>> interpret_cramers_v(0.70)
        'large'
    """
    # Handle NaN (unknown)
    if isinstance(cramers_v, float) and math.isnan(cramers_v):
        logger.warning("Cramer's V is NaN, returning 'unknown'")
        return "unknown"

    # Handle non-numeric (invalid)
    if not isinstance(cramers_v, (int, float)):
        logger.warning(f"Cramer's V is not numeric: {cramers_v}, returning 'invalid'")
        return "invalid"

    # Handle out-of-range (invalid)
    if cramers_v < 0 or cramers_v > 1.0:
        logger.warning(f"Cramer's V out of range [0,1]: {cramers_v}, returning 'invalid'")
        return "invalid"

    # Interpret based on thresholds
    if cramers_v < 0.10:
        return "negligible"
    elif cramers_v < 0.30:
        return "small"
    elif cramers_v < 0.50:
        return "medium"
    else:
        return "large"


def get_cramers_v_range(interpretation: str) -> tuple[float, float]:
    """
    Get the numeric range for a Cramer's V interpretation category.

    This is the reverse function of interpret_cramers_v().

    Args:
        interpretation: Category string ("negligible", "small", "medium", "large")

    Returns:
        Tuple of (min, max) range for the category

    Raises:
        ValueError: If interpretation category is not recognized

    Example:
        >>> get_cramers_v_range("negligible")
        (0.0, 0.1)
        >>> get_cramers_v_range("large")
        (0.5, 1.0)
    """
    if interpretation not in CRAMERS_V_THRESHOLDS:
        raise ValueError(
            f"Invalid interpretation category: {interpretation}. "
            f"Must be one of: {list(CRAMERS_V_THRESHOLDS.keys())}"
        )

    return CRAMERS_V_THRESHOLDS[interpretation]


def is_significant(p_value: float, alpha: float = 0.05) -> bool:
    """
    Determine if a p-value indicates statistical significance.

    A result is statistically significant if the p-value is less than
    the significance level (alpha). The default alpha=0.05 is the standard
    threshold used in most research.

    Args:
        p_value: P-value from a statistical test
        alpha: Significance level (default: 0.05, can be overridden by config)

    Returns:
        True if p_value < alpha (significant), False otherwise

    Example:
        >>> is_significant(0.03)
        True
        >>> is_significant(0.15)
        False
        >>> is_significant(0.03, alpha=0.01)  # More strict threshold
        False
    """
    # Validate inputs
    if not isinstance(p_value, (int, float)):
        logger.warning(f"p-value is not numeric: {p_value}, treating as not significant")
        return False

    if not isinstance(alpha, (int, float)):
        logger.warning(f"alpha is not numeric: {alpha}, using default 0.05")
        alpha = 0.05

    if p_value < 0 or p_value > 1:
        logger.warning(f"p-value out of range [0,1]: {p_value}, clamping")
        p_value = max(0.0, min(1.0, p_value))

    if alpha < 0 or alpha > 1:
        logger.warning(f"alpha out of range [0,1]: {alpha}, using default 0.05")
        alpha = 0.05

    return p_value < alpha


def calculate_all_statistics(
    contingency_table: pd.DataFrame, alpha: Optional[float] = None
) -> Dict:
    """
    Calculate all statistics for a contingency table in one call.

    This is a convenience function that computes Chi-square test,
    Cramer's V, interpretation, and significance status.

    Args:
        contingency_table: pandas DataFrame with contingency table counts
        alpha: Significance level (default: from config, usually 0.05)

    Returns:
        Dict with keys:
            - chi_square (float): Chi-square statistic
            - p_value (float): P-value
            - degrees_of_freedom (int): Degrees of freedom
            - cramers_v (float): Effect size
            - interpretation (str): Effect size category
            - is_significant (bool): Statistical significance
            - is_valid (bool): Whether test assumptions are met
            - warning (str|None): Warning message if any
            - sample_size (int): Total sample size

    Example:
        >>> import pandas as pd
        >>> table = pd.DataFrame([[10, 20], [30, 40]])
        >>> stats = calculate_all_statistics(table)
        >>> print(f"Significant: {stats['is_significant']}")
        >>> print(f"Effect size: {stats['interpretation']}")
    """
    # Get alpha from config if not provided
    if alpha is None:
        alpha = DEFAULT_CONFIG.get("significance_level", 0.05)

    # Calculate chi-square
    chi_result = calculate_chi_square(contingency_table)

    # Calculate Cramer's V
    cramers_v = calculate_cramers_v(contingency_table, chi_result["chi_square"])

    # Interpret effect size
    interpretation = interpret_cramers_v(cramers_v)

    # Check significance
    significant = is_significant(chi_result["p_value"], alpha)

    # Get sample size
    sample_size = int(contingency_table.values.sum())

    return {
        "chi_square": chi_result["chi_square"],
        "p_value": chi_result["p_value"],
        "degrees_of_freedom": chi_result["degrees_of_freedom"],
        "cramers_v": cramers_v,
        "interpretation": interpretation,
        "is_significant": significant,
        "is_valid": chi_result["is_valid"],
        "warning": chi_result["warning"],
        "sample_size": sample_size,
    }


def create_statistical_summary(table_name: str, statistics: Dict) -> Dict:
    """
    Create a standardized statistical summary entry for a table.

    This formats the statistics in the schema expected by the workflow's
    statistical_summary.json output file.

    Args:
        table_name: Name/identifier for the table
        statistics: Dict returned by calculate_all_statistics()

    Returns:
        Dict with schema matching statistical_summary.json structure

    Example:
        >>> table = pd.DataFrame([[10, 20], [30, 40]])
        >>> stats = calculate_all_statistics(table)
        >>> summary = create_statistical_summary("gender_vs_satisfaction", stats)
        >>> write_json([summary], "output/statistical_summary.json")
    """
    return {
        "table_name": table_name,
        "chi_square": statistics["chi_square"],
        "p_value": statistics["p_value"],
        "degrees_of_freedom": statistics["degrees_of_freedom"],
        "cramers_v": statistics["cramers_v"],
        "interpretation": statistics["interpretation"],
        "sample_size": statistics["sample_size"],
        "is_significant": statistics["is_significant"],
    }


# =============================================================================
# Safe Statistics Calculation with Edge Case Handling
# =============================================================================


def calculate_chi_square_safely(
    contingency_table: pd.DataFrame, min_cell_count: int = 10
) -> Dict:
    """
    Calculate Chi-square test with comprehensive error handling.

    This function performs safety checks before computing the chi-square test:
    1. Minimum cell count check (avoids unreliable results)
    2. Table structure validation (requires at least 2x2)
    3. Zero division prevention (checks row/column totals)
    4. Exception handling during computation

    Tables that fail safety checks are marked as invalid with appropriate
    error messages, allowing processing to continue for valid tables.

    Args:
        contingency_table: pandas DataFrame with contingency table counts
        min_cell_count: Minimum expected cell count threshold (default: 10)

    Returns:
        Dict with keys:
            - is_valid (bool): Whether all checks passed and calculation succeeded
            - chi_square (float|None): Chi-square statistic (None if invalid)
            - p_value (float|None): P-value (None if invalid)
            - degrees_of_freedom (int|None): Degrees of freedom (None if invalid)
            - cramers_v (float|None): Effect size (None if invalid)
            - interpretation (str|None): Effect size category (None if invalid)
            - is_significant (bool|None): Statistical significance (None if invalid)
            - error (str|None): Error message if invalid, None otherwise
            - warning (str|None): Warning message for non-critical issues

    Example:
        >>> import pandas as pd
        >>> # Valid table
        >>> table = pd.DataFrame([[10, 20], [30, 40]])
        >>> result = calculate_chi_square_safely(table)
        >>> print(result["is_valid"])
        True
        >>> print(result["chi_square"])
        0.0
        >>> # Small sample table (invalid)
        >>> small_table = pd.DataFrame([[1, 2], [3, 4]])
        >>> result = calculate_chi_square_safely(small_table, min_cell_count=10)
        >>> print(result["is_valid"])
        False
        >>> print(result["error"])
        'Minimum cell count (1.0) below threshold (10)'
    """
    # Initialize result with default values
    result = {
        "is_valid": True,
        "chi_square": None,
        "p_value": None,
        "degrees_of_freedom": None,
        "cramers_v": None,
        "interpretation": None,
        "is_significant": None,
        "error": None,
        "warning": None,
    }

    # Validate input is a DataFrame
    if not isinstance(contingency_table, pd.DataFrame):
        result["is_valid"] = False
        result["error"] = (
            f"Contingency table must be a pandas DataFrame, "
            f"got {type(contingency_table).__name__}"
        )
        logger.error(result["error"])
        return result

    # Check for empty table
    if contingency_table.empty:
        result["is_valid"] = False
        result["error"] = "Contingency table is empty"
        logger.error(result["error"])
        return result

    # Ensure all values are numeric
    try:
        counts = contingency_table.values.astype(float)
    except (ValueError, TypeError) as e:
        result["is_valid"] = False
        result["error"] = f"Contingency table contains non-numeric values: {e}"
        logger.error(result["error"])
        return result

    # Check 1: Minimum cell count (at least 2x2 structure)
    if contingency_table.shape[0] < 2 or contingency_table.shape[1] < 2:
        result["is_valid"] = False
        result["error"] = (
            f"Invalid table structure: {contingency_table.shape}. "
            f"Minimum required is 2x2 (rows x columns)."
        )
        logger.warning(result["error"])
        return result

    # Check 2: Zero total count
    grand_total = counts.sum()
    if grand_total == 0:
        result["is_valid"] = False
        result["error"] = "Contingency table has zero total count"
        logger.warning(result["error"])
        return result

    # Check 3: Row with zero total count (zero division risk)
    row_totals = counts.sum(axis=1)
    if (row_totals == 0).any():
        result["is_valid"] = False
        result["error"] = "Row with zero total count detected (zero division risk)"
        logger.warning(result["error"])
        return result

    # Check 4: Column with zero total count (zero division risk)
    col_totals = counts.sum(axis=0)
    if (col_totals == 0).any():
        result["is_valid"] = False
        result["error"] = "Column with zero total count detected (zero division risk)"
        logger.warning(result["error"])
        return result

    # Check 5: Minimum expected cell count
    # Compute expected frequencies
    row_totals_matrix = row_totals.reshape(-1, 1)
    col_totals_matrix = col_totals.reshape(1, -1)
    expected_counts = (row_totals_matrix @ col_totals_matrix) / grand_total

    min_expected = expected_counts.min()
    if min_expected < min_cell_count:
        result["is_valid"] = False
        result["error"] = (
            f"Minimum expected cell count ({min_expected:.2f}) "
            f"below threshold ({min_cell_count}). "
            f"Chi-square results may be unreliable."
        )
        logger.warning(result["error"])
        return result

    # All checks passed - calculate statistics
    try:
        # Perform chi-square test
        chi2, p_value, dof, _ = stats.chi2_contingency(counts)

        # Calculate Cramer's V
        n_rows, n_cols = counts.shape
        min_dim = min(n_rows - 1, n_cols - 1)

        # Handle edge case where min_dim is 0 (should not happen due to 2x2 check)
        if min_dim == 0:
            result["is_valid"] = False
            result["error"] = (
                f"Cannot compute Cramer's V: invalid dimension "
                f"(table shape: {counts.shape})"
            )
            logger.warning(result["error"])
            return result

        # Calculate Cramer's V with zero division protection
        try:
            cramers_v = math.sqrt(chi2 / (grand_total * min_dim))
            # Clamp to [0, 1] range
            cramers_v = max(0.0, min(1.0, cramers_v))
        except (ValueError, ZeroDivisionError) as e:
            result["is_valid"] = False
            result["error"] = f"Cramer's V computation failed: {e}"
            logger.warning(result["error"])
            return result

        # Populate result
        result["chi_square"] = float(chi2)
        result["p_value"] = float(p_value)
        result["degrees_of_freedom"] = int(dof)
        result["cramers_v"] = cramers_v
        result["interpretation"] = interpret_cramers_v(cramers_v)
        result["is_significant"] = p_value < 0.05

        logger.debug(
            f"Chi-square test completed: χ2={chi2:.4f}, p={p_value:.4f}, "
            f"df={dof}, V={cramers_v:.4f}, valid=True"
        )

    except Exception as e:
        result["is_valid"] = False
        result["error"] = f"Chi-square test computation failed: {str(e)}"
        logger.error(result["error"])

    return result
