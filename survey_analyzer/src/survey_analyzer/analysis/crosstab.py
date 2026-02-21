"""
Cross-Tabulation Generator

Generate cross-tabulation tables with statistical tests using pandas and scipy.

This module replaces PSPP CROSSTABS with pure Python implementation.
Supports weighted cross-tabs, chi-square tests, and Cramer's V calculation.

Example:
    >>> generator = CrossTabGenerator()
    >>> result = generator.generate_crosstab(df, "gender", "satisfaction")
    >>> print(f"χ² = {result['statistics']['chi_square']:.2f}")
    >>> print(f"p = {result['statistics']['p_value']:.4f}")
"""

import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

logger = logging.getLogger(__name__)


@dataclass
class CrosstabResult:
    """
    Result of cross-tabulation generation.

    Attributes:
        table_id: Unique identifier for the table
        row_var: Row variable name
        col_var: Column variable name
        crosstab: Cross-tabulation table (counts or percentages)
        row_labels: Row category labels
        col_labels: Column category labels
        statistics: Statistical test results (chi_square, p_value, cramers_v, etc.)
        is_valid: Whether the table is valid for analysis
        error: Error message if invalid
        metadata: Additional metadata about the table
    """
    table_id: str
    row_var: str
    col_var: str
    crosstab: Union[pd.DataFrame, Dict[str, Dict[str, float]]]
    row_labels: List[str]
    col_labels: List[str]
    statistics: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        crosstab_dict = self.crosstab
        if isinstance(self.crosstab, pd.DataFrame):
            crosstab_dict = self.crosstab.to_dict()

        return {
            "table_id": self.table_id,
            "row_var": self.row_var,
            "col_var": self.col_var,
            "crosstab": crosstab_dict,
            "row_labels": self.row_labels,
            "col_labels": self.col_labels,
            "statistics": self.statistics,
            "is_valid": self.is_valid,
            "error": self.error,
            "metadata": self.metadata
        }


@dataclass
class CrosstabConfig:
    """
    Configuration for cross-tabulation generation.

    Attributes:
        include_margins: Include row/column totals (default: True)
        normalize: Normalize to percentages ('index', 'columns', or None)
        dropna: Drop NaN values (default: True)
        min_count: Minimum expected count for valid chi-square (default: 5)
        significance_level: Alpha level for significance testing (default: 0.05)
        weight_var: Optional weight variable name
    """
    include_margins: bool = True
    normalize: Optional[str] = None  # 'index', 'columns', or None
    dropna: bool = True
    min_count: int = 5
    significance_level: float = 0.05
    weight_var: Optional[str] = None


class CrossTabGenerator:
    """
    Generate cross-tabulation tables with statistical tests.

    Replaces PSPP CROSSTABS functionality with pure Python:
    - Cross-tabulation with pandas.crosstab()
    - Chi-square test with scipy.stats.chi2_contingency
    - Cramer's V effect size calculation
    - Optional weight variable support

    Example:
        >>> generator = CrossTabGenerator()
        >>> result = generator.generate(
        ...     df=df,
        ...     row_var="gender",
        ...     col_var="satisfaction",
        ...     weight_var="weight"
        ... )
        >>> print(result.statistics['p_value'])
    """

    def __init__(self, config: Optional[CrosstabConfig] = None):
        """
        Initialize the cross-tabulation generator.

        Args:
            config: Configuration options (uses defaults if None)
        """
        self.config = config or CrosstabConfig()

    def generate(
        self,
        df: pd.DataFrame,
        row_var: str,
        col_var: str,
        weight_var: Optional[str] = None,
        table_id: Optional[str] = None
    ) -> CrosstabResult:
        """
        Generate cross-tabulation with statistics.

        Args:
            df: Input DataFrame
            row_var: Row variable name
            col_var: Column variable name
            weight_var: Optional weight variable
            table_id: Optional table identifier

        Returns:
            CrosstabResult with table and statistics

        Example:
            >>> generator = CrossTabGenerator()
            >>> result = generator.generate(df, "gender", "satisfaction", "weight")
        """
        # Generate table ID if not provided
        if table_id is None:
            table_id = f"{row_var}_x_{col_var}"

        # Validate inputs
        is_valid, error = self._validate_inputs(df, row_var, col_var, weight_var)
        if not is_valid:
            return CrosstabResult(
                table_id=table_id,
                row_var=row_var,
                col_var=col_var,
                crosstab={},
                row_labels=[],
                col_labels=[],
                is_valid=False,
                error=error
            )

        try:
            # Generate cross-tabulation
            crosstab_df = self._generate_crosstab(
                df, row_var, col_var, weight_var
            )

            # Extract labels
            row_labels = crosstab_df.index.tolist()
            col_labels = crosstab_df.columns.tolist()

            # Remove margins for statistical test
            crosstab_for_test = self._remove_margins(crosstab_df)

            # Calculate statistics
            statistics = self._calculate_statistics(
                crosstab_for_test, df, row_var, col_var, weight_var
            )

            return CrosstabResult(
                table_id=table_id,
                row_var=row_var,
                col_var=col_var,
                crosstab=crosstab_df,
                row_labels=row_labels,
                col_labels=col_labels,
                statistics=statistics,
                is_valid=statistics.get('is_valid', True),
                error=statistics.get('error'),
                metadata={
                    'n': len(df),
                    'rows': len(row_labels),
                    'cols': len(col_labels)
                }
            )

        except Exception as e:
            logger.error(f"Error generating crosstab for {table_id}: {e}")
            return CrosstabResult(
                table_id=table_id,
                row_var=row_var,
                col_var=col_var,
                crosstab={},
                row_labels=[],
                col_labels=[],
                is_valid=False,
                error=str(e)
            )

    def _validate_inputs(
        self,
        df: pd.DataFrame,
        row_var: str,
        col_var: str,
        weight_var: Optional[str]
    ) -> tuple[bool, Optional[str]]:
        """Validate input variables exist in DataFrame."""
        if row_var not in df.columns:
            return False, f"Row variable '{row_var}' not found in DataFrame"

        if col_var not in df.columns:
            return False, f"Column variable '{col_var}' not found in DataFrame"

        if weight_var and weight_var not in df.columns:
            return False, f"Weight variable '{weight_var}' not found in DataFrame"

        return True, None

    def _generate_crosstab(
        self,
        df: pd.DataFrame,
        row_var: str,
        col_var: str,
        weight_var: Optional[str]
    ) -> pd.DataFrame:
        """
        Generate cross-tabulation table using pandas.

        Args:
            df: Input DataFrame
            row_var: Row variable
            col_var: Column variable
            weight_var: Optional weight variable

        Returns:
            Cross-tabulation DataFrame
        """
        weight_var = weight_var or self.config.weight_var

        if weight_var:
            # Weighted cross-tabulation
            crosstab = pd.crosstab(
                index=df[row_var],
                columns=df[col_var],
                values=df[weight_var],
                aggfunc='sum',
                dropna=self.config.dropna,
                margins=self.config.include_margins,
                normalize=self.config.normalize
            )
        else:
            # Unweighted cross-tabulation
            crosstab = pd.crosstab(
                index=df[row_var],
                columns=df[col_var],
                dropna=self.config.dropna,
                margins=self.config.include_margins,
                normalize=self.config.normalize
            )

        return crosstab

    def _remove_margins(self, crosstab: pd.DataFrame) -> pd.DataFrame:
        """Remove margin rows/columns for statistical testing."""
        # Filter out 'All' rows and columns
        result = crosstab

        if 'All' in result.index:
            result = result.drop('All', axis=0)
        if 'All' in result.columns:
            result = result.drop('All', axis=1)

        # Also check for integer-indexed margins
        if result.shape[0] > 1 and result.shape[1] > 1:
            # Last row/column might be margin
            try:
                if result.index[-1] == 'All':
                    result = result.iloc[:-1, :]
                if result.columns[-1] == 'All':
                    result = result.iloc[:, :-1]
            except Exception:
                pass

        return result

    def _calculate_statistics(
        self,
        crosstab: pd.DataFrame,
        df: pd.DataFrame,
        row_var: str,
        col_var: str,
        weight_var: Optional[str]
    ) -> Dict[str, Any]:
        """
        Calculate chi-square test and Cramer's V.

        Args:
            crosstab: Cross-tabulation table (without margins)
            df: Original DataFrame
            row_var: Row variable name
            col_var: Column variable name
            weight_var: Weight variable (if used)

        Returns:
            Dictionary with statistics
        """
        try:
            # Convert to counts for chi-square test
            if self.config.normalize:
                # If normalized, we need raw counts
                weight_var = weight_var or self.config.weight_var
                if weight_var:
                    observed = pd.crosstab(
                        df[row_var],
                        df[col_var],
                        df[weight_var],
                        aggfunc='sum'
                    ).values
                else:
                    observed = pd.crosstab(df[row_var], df[col_var]).values
            else:
                observed = crosstab.values

            # Check assumptions
            n = observed.sum()
            if n == 0:
                return {
                    'is_valid': False,
                    'error': 'No observations in table'
                }

            # Perform chi-square test
            chi2, p_value, dof, expected = chi2_contingency(observed)

            # Calculate Cramer's V
            min_dim = min(observed.shape[0] - 1, observed.shape[1] - 1)
            if min_dim > 0:
                cramers_v = np.sqrt(chi2 / (n * min_dim))
            else:
                cramers_v = 0.0

            # Interpret effect size
            interpretation = self._interpret_cramers_v(cramers_v)

            return {
                'chi_square': float(chi2),
                'p_value': float(p_value),
                'degrees_of_freedom': int(dof),
                'cramers_v': float(cramers_v),
                'interpretation': interpretation,
                'is_significant': p_value < self.config.significance_level,
                'is_valid': True,
                'n': int(n)
            }

        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'chi_square': None,
                'p_value': None,
                'cramers_v': None
            }

    def _interpret_cramers_v(self, v: float) -> str:
        """
        Interpret Cramer's V effect size.

        Cohen's thresholds:
        - 0.1: small effect
        - 0.3: medium effect
        - 0.5: large effect
        """
        if v < 0.1:
            return 'negligible'
        elif v < 0.3:
            return 'small'
        elif v < 0.5:
            return 'medium'
        else:
            return 'large'

    def generate_batch(
        self,
        df: pd.DataFrame,
        table_pairs: List[Dict[str, str]],
        weight_var: Optional[str] = None
    ) -> List[CrosstabResult]:
        """
        Generate multiple cross-tabulations.

        Args:
            df: Input DataFrame
            table_pairs: List of dicts with 'row_var' and 'col_var' keys
            weight_var: Optional weight variable

        Returns:
            List of CrosstabResult objects

        Example:
            >>> pairs = [
            ...     {'row_var': 'gender', 'col_var': 'satisfaction'},
            ...     {'row_var': 'age', 'col_var': 'brand'},
            ... ]
            >>> generator = CrossTabGenerator()
            >>> results = generator.generate_batch(df, pairs)
        """
        results = []

        for pair in table_pairs:
            row_var = pair.get('row_var')
            col_var = pair.get('col_var')
            table_id = pair.get('table_id')

            if not row_var or not col_var:
                logger.warning(f"Skipping invalid pair: {pair}")
                continue

            result = self.generate(df, row_var, col_var, weight_var, table_id)
            results.append(result)

        logger.info(f"Generated {len(results)} cross-tabulations")
        return results


def generate_crosstab(
    df: pd.DataFrame,
    row_var: str,
    col_var: str,
    weight_var: Optional[str] = None,
    normalize: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate cross-tabulation with statistics.

    Args:
        df: Input DataFrame
        row_var: Row variable name
        col_var: Column variable name
        weight_var: Optional weight variable
        normalize: Normalize to percentages ('index', 'columns', or None)

    Returns:
        Dictionary with crosstab and statistics

    Example:
        >>> result = generate_crosstab(df, "gender", "satisfaction")
        >>> print(f"p-value: {result['statistics']['p_value']}")
    """
    config = CrosstabConfig(normalize=normalize)
    generator = CrossTabGenerator(config)
    result = generator.generate(df, row_var, col_var, weight_var)
    return result.to_dict()


def generate_crosstabs_with_stats(
    df: pd.DataFrame,
    row_indicators: List[Dict[str, Any]],
    column_indicators: List[Dict[str, Any]],
    weight_var: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Generate multiple cross-tabulations from indicator specifications.

    Args:
        df: Input DataFrame
        row_indicators: List of row indicator specifications
        column_indicators: List of column indicator specifications
        weight_var: Optional weight variable

    Returns:
        List of cross-tabulation results with statistics

    Example:
        >>> row_indicators = [
        ...     {
        ...         'indicator_code': 'gender',
        ...         'base_variables': [{'name': 'gender', 'suffix': '_raw'}],
        ...         'tabulation_statistics': {'type': 'categorical', 'metric': 'column_percent'}
        ...     },
        ...     {
        ...         'indicator_code': 'age',
        ...         'base_variables': [{'name': 'age', 'suffix': '_sca'}],
        ...         'tabulation_statistics': {'type': 'scalar', 'metric': 'descriptive_statistics'}
        ...     }
        ... ]
        >>> col_indicators = [
        ...     {
        ...         'indicator_code': 'sat',
        ...         'base_variables': [{'name': 'satisfaction', 'suffix': '_raw'}],
        ...         'tabulation_statistics': {'type': 'categorical', 'metric': 'column_percent'}
        ...     }
        ... ]
        >>> results = generate_crosstabs_with_stats(df, row_indicators, col_indicators)
    """
    generator = CrossTabGenerator()
    results = []

    for row_ind in row_indicators:
        for col_ind in column_indicators:
            row_var = row_ind.get('indicator_code')
            col_var = col_ind.get('indicator_code')
            table_id = f"{row_var}_x_{col_var}"

            result = generator.generate(df, row_var, col_var, weight_var, table_id)
            results.append(result.to_dict())

    return results
