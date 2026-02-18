"""
Analysis Module

Core analysis functions for SPSS survey data.

Classes:
    StatisticsCalculator: Compute Chi-square and Cramer's V for cross-tables
    IndicatorGenerator: Generate indicator groupings from variables
    TransformationEngine: Apply variable recoding and transformations (replaces PSPP)
    CrossTabGenerator: Generate cross-tabs with statistics (replaces PSPP)
"""

from .statistics import StatisticsCalculator, chi_square_test
from .indicators import (
    IndicatorGenerator,
    IndicatorConfig,
    Indicator,
    IndicatorType,
    generate_indicators
)
from .transformation import (
    TransformationEngine,
    TransformationRule,
    apply_recode,
    parse_transformation_rules
)
from .crosstab import (
    CrossTabGenerator,
    CrosstabResult,
    CrosstabConfig,
    generate_crosstab,
    generate_crosstabs_with_stats
)

__all__ = [
    # Statistics
    "StatisticsCalculator",
    "chi_square_test",
    # Indicators
    "IndicatorGenerator",
    "IndicatorConfig",
    "Indicator",
    "IndicatorType",
    "generate_indicators",
    # Transformation (replaces PSPP recoding)
    "TransformationEngine",
    "TransformationRule",
    "apply_recode",
    "parse_transformation_rules",
    # Cross-tabulation (replaces PSPP CROSSTABS)
    "CrossTabGenerator",
    "CrosstabResult",
    "CrosstabConfig",
    "generate_crosstab",
    "generate_crosstabs_with_stats",
]
