"""
Analysis Module

Core analysis functions for SPSS survey data.

Classes:
    StatisticsCalculator: Compute Chi-square and Cramer's V for cross-tables
    IndicatorGenerator: Generate indicator groupings from variables
"""

from .statistics import StatisticsCalculator, chi_square_test
from .indicators import (
    IndicatorGenerator,
    IndicatorConfig,
    Indicator,
    IndicatorType,
    generate_indicators
)

__all__ = [
    "StatisticsCalculator",
    "chi_square_test",
    "IndicatorGenerator",
    "IndicatorConfig",
    "Indicator",
    "IndicatorType",
    "generate_indicators",
]
