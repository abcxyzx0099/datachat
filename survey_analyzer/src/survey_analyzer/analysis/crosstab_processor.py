"""
Crosstab Processor

Main processor that routes to the appropriate scenario-specific processor
based on indicator types.

Handles all 4 scenarios:
1. Single Categorical × Single Categorical
2. Multiple Binary (Multiple Choice) × Single Categorical
3. Single Scalar × Single Categorical
4. Multiple Scalar (Rating Scale) × Single Categorical
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

import pandas as pd

from .scenario_detector import ScenarioDetector
from .processors import (
    CategoricalSingleProcessor,
    CategoricalMultiProcessor,
    ScalarSingleProcessor,
    ScalarMultiProcessor
)

logger = logging.getLogger(__name__)


@dataclass
class CrosstabResult:
    """
    Result of cross-tabulation generation.

    Attributes:
        table_id: Unique identifier for the table
        row_indicator: Row indicator specification (dict with new schema)
        column_indicator: Column indicator specification (dict with new schema)
        row_scenario: Detected row scenario type
        col_scenario: Detected column scenario type
        data: Formatted crosstab data
        has_total_column: Whether total column exists
        has_total_row: Whether total row exists
        total_row_type: Type of total row ("full", "base_only", "none")
        base_n: Sample sizes for each column
        statistics: Statistical test results (chi-square, p-value, etc.)
        is_valid: Whether the table is valid
        error: Error message if invalid
    """
    table_id: str
    row_indicator: Dict[str, Any]
    column_indicator: Dict[str, Any]
    row_scenario: str
    col_scenario: str
    data: Dict[str, Any]
    has_total_column: bool
    has_total_row: bool
    total_row_type: str
    base_n: Dict[str, int]
    statistics: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "table_id": self.table_id,
            "row_indicator": self.row_indicator,
            "column_indicator": self.column_indicator,
            "row_scenario": self.row_scenario,
            "col_scenario": self.col_scenario,
            "data": self.data,
            "has_total_column": self.has_total_column,
            "has_total_row": self.has_total_row,
            "total_row_type": self.total_row_type,
            "base_n": self.base_n,
            "statistics": self.statistics,
            "is_valid": self.is_valid,
            "error": self.error
        }


class CrosstabProcessor:
    """
    Main crosstab processor that handles all 4 scenarios.

    Uses scenario detection to route to the appropriate specialized processor.
    """

    def __init__(self):
        """Initialize the processor with scenario-specific processors."""
        self.cat_single_proc = CategoricalSingleProcessor()
        self.cat_multi_proc = CategoricalMultiProcessor()
        self.scalar_single_proc = ScalarSingleProcessor()
        self.scalar_multi_proc = ScalarMultiProcessor()

    def generate(
        self,
        df: pd.DataFrame,
        row_indicator: Dict[str, Any],
        col_indicator: Dict[str, Any],
        weight_var: Optional[str] = None,
        table_id: Optional[str] = None
    ) -> CrosstabResult:
        """
        Generate cross-tabulation for given indicators.

        Args:
            df: Input DataFrame
            row_indicator: Row indicator specification
            col_indicator: Column indicator specification
            weight_var: Optional weight variable
            table_id: Optional table identifier

        Returns:
            CrosstabResult with formatted data
        """
        # Generate table ID if not provided
        if table_id is None:
            row_code = row_indicator.get("indicator_code", "row")
            col_code = col_indicator.get("indicator_code", "col")
            table_id = f"{row_code}_x_{col_code}"

        # Detect scenarios
        row_scenario = ScenarioDetector.detect(row_indicator)
        col_scenario = ScenarioDetector.detect(col_indicator)

        logger.info(f"Generating crosstab: {table_id}")
        logger.info(f"  Row scenario: {row_scenario}, Column scenario: {col_scenario}")

        try:
            # Route to appropriate processor based on row scenario
            if row_scenario == ScenarioDetector.CAT_SINGLE:
                result_data = self.cat_single_proc.generate(
                    df, row_indicator, col_indicator, weight_var
                )
            elif row_scenario == ScenarioDetector.CAT_MULTI:
                result_data = self.cat_multi_proc.generate(
                    df, row_indicator, col_indicator, weight_var
                )
            elif row_scenario == ScenarioDetector.SCALAR_SINGLE:
                result_data = self.scalar_single_proc.generate(
                    df, row_indicator, col_indicator, weight_var
                )
            elif row_scenario == ScenarioDetector.SCALAR_MULTI:
                result_data = self.scalar_multi_proc.generate(
                    df, row_indicator, col_indicator, weight_var
                )
            else:
                return CrosstabResult(
                    table_id=table_id,
                    row_indicator=row_indicator,
                    column_indicator=col_indicator,
                    row_scenario=row_scenario,
                    col_scenario=col_scenario,
                    data={},
                    has_total_column=False,
                    has_total_row=False,
                    total_row_type="none",
                    base_n={},
                    is_valid=False,
                    error=f"Unknown row scenario: {row_scenario}"
                )

            # Determine formatting flags
            has_total_column = True  # Always have total column
            has_total_row = ScenarioDetector.has_total_row(row_scenario)
            total_row_type = ScenarioDetector.get_total_row_type(row_scenario)

            return CrosstabResult(
                table_id=table_id,
                row_indicator=row_indicator,
                column_indicator=col_indicator,
                row_scenario=row_scenario,
                col_scenario=col_scenario,
                data=result_data["data"],
                has_total_column=has_total_column,
                has_total_row=has_total_row,
                total_row_type=total_row_type,
                base_n=result_data.get("base_n", {}),
                statistics=result_data.get("statistics", {}),
                is_valid=True
            )

        except Exception as e:
            logger.error(f"Error generating crosstab for {table_id}: {e}")
            return CrosstabResult(
                table_id=table_id,
                row_indicator=row_indicator,
                column_indicator=col_indicator,
                row_scenario=row_scenario,
                col_scenario=col_scenario,
                data={},
                has_total_column=False,
                has_total_row=False,
                total_row_type="none",
                base_n={},
                is_valid=False,
                error=str(e)
            )

    def generate_batch(
        self,
        df: pd.DataFrame,
        row_indicators: List[Dict[str, Any]],
        col_indicators: List[Dict[str, Any]],
        weight_var: Optional[str] = None
    ) -> List[CrosstabResult]:
        """
        Generate multiple cross-tabulations.

        Creates all combinations of row × column indicators.

        Args:
            df: Input DataFrame
            row_indicators: List of row indicator specifications
            col_indicators: List of column indicator specifications
            weight_var: Optional weight variable

        Returns:
            List of CrosstabResult objects
        """
        results = []

        for row_ind in row_indicators:
            for col_ind in col_indicators:
                row_code = row_ind.get("indicator_code", "row")
                col_code = col_ind.get("indicator_code", "col")
                table_id = f"{row_code}_x_{col_code}"

                result = self.generate(df, row_ind, col_ind, weight_var, table_id)
                results.append(result)

        logger.info(f"Generated {len(results)} cross-tabulations")
        return results


def generate_crosstab(
    df: pd.DataFrame,
    row_indicator: Dict[str, Any],
    col_indicator: Dict[str, Any],
    weight_var: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate cross-tabulation.

    Args:
        df: Input DataFrame
        row_indicator: Row indicator specification
        col_indicator: Column indicator specification
        weight_var: Optional weight variable

    Returns:
        Dictionary with crosstab result
    """
    processor = CrosstabProcessor()
    result = processor.generate(df, row_indicator, col_indicator, weight_var)
    return result.to_dict()


def generate_crosstabs_batch(
    df: pd.DataFrame,
    row_indicators: List[Dict[str, Any]],
    col_indicators: List[Dict[str, Any]],
    weight_var: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to generate multiple cross-tabulations.

    Args:
        df: Input DataFrame
        row_indicators: List of row indicator specifications
        col_indicators: List of column indicator specifications
        weight_var: Optional weight variable

    Returns:
        List of crosstab result dictionaries
    """
    processor = CrosstabProcessor()
    results = processor.generate_batch(df, row_indicators, col_indicators, weight_var)
    return [r.to_dict() for r in results]
