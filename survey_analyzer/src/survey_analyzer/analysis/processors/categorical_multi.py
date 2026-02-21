"""
Categorical Multi Processor

Scenario 2: Multiple Binary (Multiple Choice) × Single Categorical

Each source variable is binary (0/1 or No/Yes).
Shows % of Yes/True for each variable.
No Total row with percentages - only base N.
"""

import logging
from typing import Dict, Any, Optional, List

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class CategoricalMultiProcessor:
    """
    Process crosstab for multiple binary variables (Multiple Choice).

    Example:
        Row: Brand Awareness (Brand A, Brand B, Brand C, Brand D)
        Column: Gender (Male, Female)

    Output:
        - Each row = one source variable
        - Shows % of Yes/True for each column
        - No Total row with percentages
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
        Generate crosstab for multiple binary variables.

        Args:
            df: Input DataFrame
            row_indicator: Row indicator with multiple binary source variables
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

        # Calculate base N for each column category
        base_n = self._calculate_base_n(df, col_var, weight_var)

        # Generate percentage for each binary variable
        rows = []
        for var in row_vars:
            row_result = self._calculate_binary_percentage(
                df, var, col_var, weight_var
            )
            rows.append(row_result)

        return self._format_output(rows, base_n, row_vars, col_var)

    def _calculate_base_n(
        self,
        df: pd.DataFrame,
        col_var: str,
        weight_var: Optional[str]
    ) -> Dict[str, int]:
        """Calculate base N for each column category."""
        base_n = {}

        for col_val in df[col_var].unique():
            col_data = df[df[col_var] == col_val]
            if weight_var:
                n = col_data[weight_var].sum()
            else:
                n = len(col_data)
            base_n[str(col_val)] = int(n)

        # Total
        if weight_var:
            base_n["Total"] = int(df[weight_var].sum())
        else:
            base_n["Total"] = len(df)

        return base_n

    def _calculate_binary_percentage(
        self,
        df: pd.DataFrame,
        binary_var: str,
        col_var: str,
        weight_var: Optional[str]
    ) -> Dict[str, Any]:
        """
        Calculate percentage of Yes/True for a binary variable by column category.

        Returns:
            Dictionary with label and values for each column category
        """
        result = {
            "label": binary_var,
            "values": {}
        }

        # Get unique column values (preserving order)
        col_values = df[col_var].unique()

        for col_val in col_values:
            subset = df[df[col_var] == col_val]

            if weight_var:
                # Weighted percentage
                yes_weight = subset[subset[binary_var].isin([1, True, "1", "Yes", "yes"])][weight_var].sum()
                total_weight = subset[weight_var].sum()
                if total_weight > 0:
                    pct = (yes_weight / total_weight) * 100
                else:
                    pct = 0.0
            else:
                # Unweighted percentage
                total_count = len(subset)
                yes_count = subset[binary_var].isin([1, True, "1", "Yes", "yes"]).sum()
                if total_count > 0:
                    pct = (yes_count / total_count) * 100
                else:
                    pct = 0.0

            result["values"][str(col_val)] = round(pct, 1)

        # Total column
        if weight_var:
            yes_weight = df[df[binary_var].isin([1, True, "1", "Yes", "yes"])][weight_var].sum()
            total_weight = df[weight_var].sum()
            if total_weight > 0:
                pct = (yes_weight / total_weight) * 100
            else:
                pct = 0.0
        else:
            yes_count = df[binary_var].isin([1, True, "1", "Yes", "yes"]).sum()
            total_count = len(df)
            if total_count > 0:
                pct = (yes_count / total_count) * 100
            else:
                pct = 0.0

        result["values"]["Total"] = round(pct, 1)

        return result

    def _format_output(
        self,
        rows: List[Dict[str, Any]],
        base_n: Dict[str, int],
        row_vars: List[str],
        col_var: str
    ) -> Dict[str, Any]:
        """Format output as structured dictionary."""
        return {
            "row_scenario": "cat_multi",
            "data": {
                "rows": rows,
                "total_row": {
                    "label": "Total",
                    "values": None,  # No percentage values for multiple choice
                    "base_n": base_n
                }
            },
            "statistics": {},  # No chi-square for multiple choice
            "base_n": base_n
        }
