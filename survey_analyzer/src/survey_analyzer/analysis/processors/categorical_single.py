"""
Categorical Single Processor

Scenario 1: Single Categorical × Single Categorical

Standard crosstab with column percentages.
Has Total column with 100% and Total row with base N.
"""

import logging
from typing import Dict, Any, Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class CategoricalSingleProcessor:
    """
    Process crosstab for single categorical indicator.

    Example:
        Row: Gender (Male, Female, Other)
        Column: Satisfaction (Very Satisfied, Satisfied, Neutral, Dissatisfied)

    Output:
        - Column percentages for each cell
        - Total column with 100%
        - Total row with base N
    """

    def generate(
        self,
        df: pd.DataFrame,
        row_indicator: Dict[str, Any],
        col_indicator: Dict[str, Any],
        weight_var: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate crosstab for single categorical indicators.

        Args:
            df: Input DataFrame
            row_indicator: Row indicator specification
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

        row_var = row_base_vars[0]["name"]
        col_var = col_base_vars[0]["name"]

        # Apply transformations if needed (from generation field)
        row_generation = row_base_vars[0].get("generation")
        if row_generation and row_generation.lower() != "null":
            from ..transformation import TransformationEngine
            engine = TransformationEngine()
            df = df.copy()
            df[row_var] = engine._apply_recode(df[row_var], row_generation)

        col_generation = col_base_vars[0].get("generation")
        if col_generation and col_generation.lower() != "null":
            from ..transformation import TransformationEngine
            engine = TransformationEngine()
            df = df.copy()
            df[col_var] = engine._apply_recode(df[col_var], col_generation)

        # Generate crosstab
        crosstab, base_n = self._generate_crosstab(df, row_var, col_var, weight_var)

        # Calculate statistics (chi-square, Cramer's V)
        statistics = self._calculate_statistics(crosstab, df, row_var, col_var, weight_var)

        # Format output
        return self._format_output(
            crosstab,
            base_n,
            row_var,
            col_var,
            statistics
        )

    def _generate_crosstab(
        self,
        df: pd.DataFrame,
        row_var: str,
        col_var: str,
        weight_var: Optional[str]
    ) -> tuple[pd.DataFrame, Dict[str, int]]:
        """
        Generate crosstab with column percentages.

        Returns:
            Tuple of (crosstab DataFrame, base_n dict)
        """
        # Calculate base N for each column
        base_n = {}
        for col_val in df[col_var].unique():
            col_data = df[df[col_var] == col_val]
            if weight_var:
                n = col_data[weight_var].sum()
            else:
                n = len(col_data)
            base_n[str(col_val)] = int(n)

        # Total base N
        if weight_var:
            base_n["Total"] = int(df[weight_var].sum())
        else:
            base_n["Total"] = len(df)

        # Generate crosstab with column percentages
        if weight_var:
            crosstab = pd.crosstab(
                index=df[row_var],
                columns=df[col_var],
                values=df[weight_var],
                aggfunc='sum',
                dropna=True,
                margins=True,
                normalize='columns'
            ) * 100
        else:
            crosstab = pd.crosstab(
                index=df[row_var],
                columns=df[col_var],
                dropna=True,
                margins=True,
                normalize='columns'
            ) * 100

        # Round to 1 decimal place
        crosstab = crosstab.round(1)

        return crosstab, base_n

    def _calculate_statistics(
        self,
        crosstab: pd.DataFrame,
        df: pd.DataFrame,
        row_var: str,
        col_var: str,
        weight_var: Optional[str]
    ) -> Dict[str, Any]:
        """Calculate chi-square test and Cramer's V."""
        try:
            from scipy.stats import chi2_contingency

            # Get observed counts (without margins)
            crosstab_counts = pd.crosstab(df[row_var], df[col_var])
            observed = crosstab_counts.values

            # Perform chi-square test
            chi2, p_value, dof, expected = chi2_contingency(observed)

            # Calculate Cramer's V
            n = observed.sum()
            min_dim = min(observed.shape[0] - 1, observed.shape[1] - 1)
            if min_dim > 0 and n > 0:
                cramers_v = np.sqrt(chi2 / (n * min_dim))
            else:
                cramers_v = 0.0

            # Interpret effect size
            if cramers_v < 0.1:
                interpretation = "negligible"
            elif cramers_v < 0.3:
                interpretation = "small"
            elif cramers_v < 0.5:
                interpretation = "medium"
            else:
                interpretation = "large"

            return {
                "chi_square": float(chi2),
                "p_value": float(p_value),
                "degrees_of_freedom": int(dof),
                "cramers_v": float(cramers_v),
                "interpretation": interpretation,
                "is_significant": p_value < 0.05
            }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {
                "chi_square": None,
                "p_value": None,
                "cramers_v": None,
                "error": str(e)
            }

    def _format_output(
        self,
        crosstab: pd.DataFrame,
        base_n: Dict[str, int],
        row_var: str,
        col_var: str,
        statistics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format output as structured dictionary."""
        rows = []

        # Process each row except "All"
        for row_label in crosstab.index:
            if row_label == "All":
                continue

            row_values = {"Total": crosstab.loc[row_label, "All"]}
            for col_label in crosstab.columns:
                if col_label != "All":
                    row_values[str(col_label)] = float(crosstab.loc[row_label, col_label])

            rows.append({
                "label": str(row_label),
                "values": row_values
            })

        # Total row
        total_row = {
            "label": "Total",
            "values": {},
            "base_n": base_n
        }
        # Add 100% for each column
        for col in crosstab.columns:
            if col != "All":
                total_row["values"][str(col)] = 100.0
        if "All" in crosstab.columns:
            total_row["values"]["Total"] = 100.0

        return {
            "row_scenario": "cat_single",
            "data": {
                "rows": rows,
                "total_row": total_row
            },
            "statistics": statistics,
            "base_n": base_n
        }
