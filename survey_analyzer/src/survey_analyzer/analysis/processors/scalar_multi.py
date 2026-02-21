"""
Scalar Multi Processor

Scenario 4: Multiple Scalar (Rating Scale) × Single Categorical

Each source variable is a scalar (e.g., rating for each attribute).
Shows Mean for each variable by column category.
Total row shows base N only.
"""

import logging
from typing import Dict, Any, Optional, List

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ScalarMultiProcessor:
    """
    Process crosstab for multiple scalar variables (Rating Scale).

    Example:
        Row: Attribute Ratings (Quality, Price, Service, Selection, Value)
        Column: Gender (Male, Female)

    Output:
        - Each row = one source variable
        - Shows Mean for each variable × column combination
        - Total row shows base N only
    """

    def generate(
        self,
        df: pd.DataFrame,
        row_indicator: Dict[str, Any],
        col_indicator: Dict[str, Any],
        weight_var: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate crosstab for multiple scalar variables.

        Args:
            df: Input DataFrame
            row_indicator: Row indicator with multiple scalar source variables
            col_indicator: Column indicator specification
            weight_var: Optional weight variable

        Returns:
            Crosstab result dictionary
        """
        # Get variable names from base_variables
        row_base_vars = row_indicator.get("base_variables", [])
        col_base_vars = col_indicator.get("base_variables", [])

        if not row_base_vars or not col_base_vars:
            raise ValueError("Row and column indicators must have base_variables")

        row_vars = [bv["name"] for bv in row_base_vars]
        col_var = col_base_vars[0]["name"]

        # Apply column transformation if needed (from generation field)
        col_generation = col_base_vars[0].get("generation")
        if col_generation and col_generation.lower() != "null":
            from ..transformation import TransformationEngine
            engine = TransformationEngine()
            df = df.copy()
            df[col_var] = engine._apply_recode(df[col_var], col_generation)

        # Calculate mean for each scalar variable by column category
        rows = []
        for var in row_vars:
            row_result = self._calculate_mean_by_category(
                df, var, col_var
            )
            rows.append(row_result)

        # Calculate base N
        base_n = self._calculate_base_n(df, col_var)

        return self._format_output(rows, base_n, row_vars, col_var)

    def _calculate_mean_by_category(
        self,
        df: pd.DataFrame,
        scalar_var: str,
        col_var: str
    ) -> Dict[str, Any]:
        """
        Calculate mean for a scalar variable by each column category.

        Returns:
            Dictionary with label and mean values for each column category
        """
        result = {
            "label": scalar_var,
            "values": {}
        }

        # Get unique column values (preserving order)
        col_values = df[col_var].unique()

        for col_val in col_values:
            subset = df[df[col_var] == col_val][scalar_var].dropna()

            if len(subset) > 0:
                mean_val = float(subset.mean())
                result["values"][str(col_val)] = round(mean_val, 2)
            else:
                result["values"][str(col_val)] = None

        # Total column
        total_data = df[scalar_var].dropna()
        if len(total_data) > 0:
            result["values"]["Total"] = round(float(total_data.mean()), 2)
        else:
            result["values"]["Total"] = None

        return result

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
        rows: List[Dict[str, Any]],
        base_n: Dict[str, int],
        row_vars: List[str],
        col_var: str
    ) -> Dict[str, Any]:
        """Format output as structured dictionary."""
        return {
            "row_scenario": "scalar_multi",
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
