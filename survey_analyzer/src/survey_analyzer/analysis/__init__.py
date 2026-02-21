"""
Analysis Module

Core analysis functions for SPSS survey data.

Classes:
    StatisticsCalculator: Compute Chi-square and Cramer's V for cross-tables
    IndicatorGenerator: Generate indicator groupings from variables
    TransformationEngine: Apply variable recoding and transformations (replaces PSPP)
    CrossTabGenerator: Generate cross-tabs with statistics (replaces PSPP)
    CrosstabProcessor: Enhanced crosstab processor for all 4 scenarios
    ScenarioDetector: Detect crosstab scenario type
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
    CrosstabResult as LegacyCrosstabResult,
    CrosstabConfig,
    generate_crosstab as legacy_generate_crosstab,
    generate_crosstabs_with_stats
)
from .scenario_detector import (
    ScenarioDetector,
    detect_scenario
)
from .crosstab_processor import (
    CrosstabProcessor,
    CrosstabResult,
    generate_crosstab,
    generate_crosstabs_batch
)
from . import processors

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
    # Cross-tabulation (replaces PSPP CROSSTABS) - Legacy
    "CrossTabGenerator",
    "LegacyCrosstabResult",
    "CrosstabConfig",
    "legacy_generate_crosstab",
    "generate_crosstabs_with_stats",
    # Enhanced crosstab processor - New
    "CrosstabProcessor",
    "CrosstabResult",
    "ScenarioDetector",
    "detect_scenario",
    "generate_crosstab",
    "generate_crosstabs_batch",
    "processors",
]
