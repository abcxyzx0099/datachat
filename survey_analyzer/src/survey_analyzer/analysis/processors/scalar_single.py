"""
Scalar Single Processor

Scenario 3: Single Scalar × Single Categorical

Shows descriptive statistics (Mean, Median, Std, Min, Max) for scalar variable
by each column category.
Total row shows base N only.
"""

import logging
from typing import Dict, Any, Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ScalarSingleProcessor:
    """
    Process crosstab for single scalar indicator.

    Example:
        Row: Overall Satisfaction (0-10 scale) - statistics as rows
        Column: Gender (Male, Female)

    Output:
        - Rows: Mean, Median, Standard Deviation, Minimum, Maximum
        - Total row with base N only
    """

    def generate(
        self,
        df: pd.DataFrame,
        row_indicator: Dict[str, Any],
        col_indicator: Dict[str, Any],
        weight_var: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate descriptive statistics for scalar variable by column categories.

        Args:
            df: Input DataFrame
            row_indicator: Row indicator with single scalar source variable
            col_indicator: Column indicator specification
            weight_var: Optional weight variable (not typically used for scalar stats)

        Returns:
            Crosstab result dictionary with statistics
        """
        from ..scenario_detector import IndicatorSpec

        row_spec = IndicatorSpec.from_dict(row_indicator)
        col_spec = IndicatorSpec.from_dict(col_indicator)

        scalar_var = row_spec.source_variables[0]
        col_var = col_spec.source_variables[0]

        # Apply column transformation if needed
        if col_spec.transformation_rules and col_spec.transformation_rules.lower() != "null":
            from ..transformation import TransformationEngine
            engine = TransformationEngine()
            df = df.copy()
            df[col_var] = engine._apply_recode(df[col_var], col_spec.transformation_rules)

        # Calculate statistics for each column category
        statistics_by_col = self._calculate_statistics_by_category(
            df, scalar_var, col_var
        )

        # Calculate base N
        base_n = self._calculate_base_n(df, col_var)

        # Format output
        return self._format_output(statistics_by_col, base_n, scalar_var, col_var)

    def _calculate_statistics_by_category(
        self,
        df: pd.DataFrame,
        scalar_var: str,
        col_var: str
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate statistics for scalar variable by each column category.

        Returns:
            Dictionary mapping statistic name to values per column category
        """
        # Get unique column values (preserving order)
        col_values = list(df[col_var].unique())

        # Initialize statistics dictionary
        stats = {
            "Mean": {},
            "Median": {},
            "Standard Deviation": {},
            "Minimum": {},
            "Maximum": {}
        }

        for col_val in col_values:
            subset = df[df[col_var] == col_val][scalar_var].dropna()

            if len(subset) > 0:
                stats["Mean"][str(col_val)] = round(float(subset.mean()), 2)
                stats["Median"][str(col_val)] = round(float(subset.median()), 2)
                stats["Standard Deviation"][str(col_val)] = round(float(subset.std()), 2)
                stats["Minimum"][str(col_val)] = round(float(subset.min()), 2)
                stats["Maximum"][str(col_val)] = round(float(subset.max()), 2)
            else:
                stats["Mean"][str(col_val)] = None
                stats["Median"][str(col_val)] = None
                stats["Standard Deviation"][str(col_val)] = None
                stats["Minimum"][str(col_val)] = None
                stats["Maximum"][str(col_val)] = None

        # Calculate total statistics
        total_data = df[scalar_var].dropna()
        if len(total_data) > 0:
            stats["Mean"]["Total"] = round(float(total_data.mean()), 2)
            stats["Median"]["Total"] = round(float(total_data.median()), 2)
            stats["Standard Deviation"]["Total"] = round(float(total_data.std()), 2)
            stats["Minimum"]["Total"] = round(float(total_data.min()), 2)
            stats["Maximum"]["Total"] = round(float(total_data.max()), 2)
        else:
            stats["Mean"]["Total"] = None
            stats["Median"]["Total"] = None
            stats["Standard Deviation"]["Total"] = None
            stats["Minimum"]["Total"] = None
            stats["Maximum"]["Total"] = None

        return stats

    def _calculate_base_n(
        self,
        df: pd.DataFrame,
        col_var: str
    ) -> Dict[str, int]:
        """Calculate base N for each column category."""
        base_n = {}

        for col_val in df[col_var].unique():
            base_n[str(col_val)] = int((df[col_var] == col_val).sum())

        base_n["Total"] = len(df)

        return base_n

    def _format_output(
        self,
        statistics_by_col: Dict[str, Dict[str, float]],
        base_n: Dict[str, int],
        scalar_var: str,
        col_var: str
    ) -> Dict[str, Any]:
        """Format output as structured dictionary."""
        rows = []

        # Create row for each statistic
        for stat_name, values in statistics_by_col.items():
            rows.append({
                "label": stat_name,
                "values": values
            })

        return {
            "row_scenario": "scalar_single",
            "data": {
                "rows": rows,
                "total_row": {
                    "label": "Total",
                    "values": None,  # No statistical aggregates for total
                    "base_n": base_n
                }
            },
            "statistics": {},  # No chi-square for scalar
            "base_n": base_n
        }
