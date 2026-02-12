"""
Statistics Calculator

Compute statistical tests for cross-tabulation tables:
- Chi-square test of independence
- Cramer's V effect size
- Expected frequencies
- Residuals

Example:
    >>> calc = StatisticsCalculator()
    >>> result = calc.chi_square_test(table_data)
    >>> print(f"Chi-square: {result['chi_square']:.4f}")
    >>> print(f"p-value: {result['p_value']:.4f}")
    >>> print(f"Cramer's V: {result['cramers_v']:.4f}")
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ChiSquareResult:
    """
    Result of a Chi-square test.

    Attributes:
        chi_square: Chi-square test statistic
        degrees_of_freedom: Degrees of freedom
        p_value: P-value (probability under null hypothesis)
        cramers_v: Cramer's V effect size (0-1)
        interpretation: Effect size interpretation ('negligible', 'small', 'medium', 'large')
        is_significant: Whether p < significance_level (default 0.05)
        is_valid: Whether test assumptions were met
        error: Error message if assumptions violated
        expected_frequencies: Expected counts under independence
        residuals: Standardized residuals
    """
    chi_square: float
    degrees_of_freedom: int
    p_value: float
    cramers_v: float
    interpretation: str
    is_significant: bool
    is_valid: bool
    error: Optional[str] = None
    expected_frequencies: Optional[np.ndarray] = None
    residuals: Optional[np.ndarray] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "chi_square": self.chi_square,
            "degrees_of_freedom": self.degrees_of_freedom,
            "p_value": self.p_value,
            "cramers_v": self.cramers_v,
            "interpretation": self.interpretation,
            "is_significant": self.is_significant,
            "is_valid": self.is_valid,
            "error": self.error,
        }


class StatisticsCalculator:
    """
    Calculator for statistical tests on cross-tabulation tables.

    Provides methods for:
    - Chi-square test of independence
    - Cramer's V effect size
    - Expected frequencies
    - Standardized residuals

    Example:
        >>> calc = StatisticsCalculator(significance_level=0.05)
        >>> result = calc.analyze_table(counts, row_labels, col_labels)
        >>> if result.is_significant:
        ...     print(f"Significant association found (p={result.p_value:.4f})")
    """

    # Cramer's V interpretation thresholds (Cohen, 1988)
    CRAMERS_V_THRESHOLDS = {
        "negligible": 0.0,
        "small": 0.1,
        "medium": 0.3,
        "large": 0.5,
    }

    def __init__(
        self,
        significance_level: float = 0.05,
        min_expected_frequency: float = 5.0,
        min_cell_count: int = 10,
    ):
        """
        Initialize the calculator.

        Args:
            significance_level: Alpha level for significance testing (default: 0.05)
            min_expected_frequency: Minimum expected frequency for valid test (default: 5)
            min_cell_count: Minimum count in any cell for valid test (default: 10)
        """
        self.significance_level = significance_level
        self.min_expected_frequency = min_expected_frequency
        self.min_cell_count = min_cell_count

    def analyze_table(
        self,
        counts: List[List[int]],
        row_labels: List[str],
        column_labels: List[str],
    ) -> ChiSquareResult:
        """
        Perform complete statistical analysis on a cross-tabulation table.

        Args:
            counts: 2D array of counts (rows x columns)
            row_labels: Labels for row categories
            column_labels: Labels for column categories

        Returns:
            ChiSquareResult with all test statistics

        Example:
            >>> calc = StatisticsCalculator()
            >>> counts = [[45, 32], [52, 28]]
            >>> result = calc.analyze_table(counts, ["Male", "Female"], ["Yes", "No"])
            >>> print(f"χ² = {result.chi_square:.2f}, p = {result.p_value:.4f}")
        """
        # Validate input
        is_valid, error = self._validate_table(counts)

        if not is_valid:
            return ChiSquareResult(
                chi_square=0.0,
                degrees_of_freedom=0,
                p_value=1.0,
                cramers_v=0.0,
                interpretation="invalid",
                is_significant=False,
                is_valid=False,
                error=error,
            )

        # Convert to numpy array
        observed = np.array(counts, dtype=float)

        # Perform chi-square test
        chi_square, dof, p_value, expected = self._chi_square_test(observed)

        # Calculate Cramer's V
        cramers_v = self._cramers_v(chi_square, observed)

        # Interpret effect size
        interpretation = self._interpret_cramers_v(cramers_v)

        # Check significance
        is_significant = p_value < self.significance_level

        # Calculate residuals
        residuals = self._standardized_residuals(observed, expected)

        return ChiSquareResult(
            chi_square=float(chi_square),
            degrees_of_freedom=int(dof),
            p_value=float(p_value),
            cramers_v=float(cramers_v),
            interpretation=interpretation,
            is_significant=is_significant,
            is_valid=True,
            expected_frequencies=expected,
            residuals=residuals,
        )

    def _validate_table(self, counts: List[List[int]]) -> Tuple[bool, Optional[str]]:
        """
        Validate that table meets test assumptions.

        Args:
            counts: 2D array of counts

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not counts or not counts[0]:
            return False, "Table is empty"

        observed = np.array(counts)

        # Check for negative values
        if np.any(observed < 0):
            return False, "Table contains negative values"

        # Check for minimum cell count
        if np.any(observed < self.min_cell_count):
            return False, (
                f"Cell count below minimum ({self.min_cell_count}). "
                "Consider combining categories."
            )

        return True, None

    def _chi_square_test(
        self,
        observed: np.ndarray,
    ) -> Tuple[float, int, float, np.ndarray]:
        """
        Perform Chi-square test of independence.

        Args:
            observed: Observed frequency table

        Returns:
            Tuple of (chi_square, dof, p_value, expected)
        """
        from scipy.stats import chi2_contingency

        # Compute chi-square test
        chi_square, p_value, dof, expected = chi2_contingency(
            observed,
            correction=False,  # No Yates' correction for 2x2
        )

        return chi_square, dof, p_value, expected

    def _cramers_v(
        self,
        chi_square: float,
        observed: np.ndarray,
    ) -> float:
        """
        Calculate Cramer's V effect size.

        Formula: V = sqrt(χ² / (n * min(r-1, c-1)))

        Args:
            chi_square: Chi-square test statistic
            observed: Observed frequency table

        Returns:
            Cramer's V (0-1)
        """
        n = observed.sum()
        min_dim = min(observed.shape) - 1

        if min_dim == 0:
            return 0.0

        cramers_v = np.sqrt(chi_square / (n * min_dim))

        # Clamp to [0, 1]
        return min(1.0, max(0.0, cramers_v))

    def _interpret_cramers_v(self, cramers_v: float) -> str:
        """
        Interpret Cramer's V effect size.

        Args:
            cramers_v: Cramer's V value

        Returns:
            Interpretation string: 'negligible', 'small', 'medium', or 'large'
        """
        thresholds = self.CRAMERS_V_THRESHOLDS

        if cramers_v >= thresholds["large"]:
            return "large"
        elif cramers_v >= thresholds["medium"]:
            return "medium"
        elif cramers_v >= thresholds["small"]:
            return "small"
        else:
            return "negligible"

    def _standardized_residuals(
        self,
        observed: np.ndarray,
        expected: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate standardized residuals.

        Formula: (O - E) / sqrt(E)

        Args:
            observed: Observed frequencies
            expected: Expected frequencies

        Returns:
            Array of standardized residuals
        """
        # Avoid division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            residuals = (observed - expected) / np.sqrt(expected)
            residuals[np.isnan(residuals)] = 0

        return residuals


def chi_square_test(
    counts: List[List[int]],
    row_labels: List[str],
    column_labels: List[str],
    significance_level: float = 0.05,
) -> Dict[str, Any]:
    """
    Convenience function to perform chi-square test.

    Args:
        counts: 2D array of counts
        row_labels: Row category labels
        column_labels: Column category labels
        significance_level: Alpha level (default: 0.05)

    Returns:
        Dictionary with test results

    Example:
        >>> result = chi_square_test([[45, 32], [52, 28]], ["M", "F"], ["Y", "N"])
        >>> print(result["interpretation"])
        'small'
    """
    calc = StatisticsCalculator(significance_level=significance_level)
    chi_result = calc.analyze_table(counts, row_labels, column_labels)
    return chi_result.to_dict()
