"""
Specification Module

Provides the table specification schema for cross-tabulation analysis.

The table specification is the primary AI-generated artifact that defines:
- Row and column indicators
- Base variables and their transformations
- Tabulation statistics (categorical/scalar)
- Filter clauses and weighting

Classes:
    TableSpecification: Root specification document
    IndicatorSpec: Indicator definition with questionnaire questions and base variables
    BaseVariable: Base variable with suffix, values, and generation rules
    QuestionRef: Reference to a questionnaire question
    TabulationStats: Statistics configuration (type, metric, explicit)
    VariableSuffix: Semantic suffix types (_raw, _bin, _cat, _t2b, _b2b, _nps, _sca, _idx, _z, _pct)
    QuestionType: Question types (Single Choice, Multiple Choice, Rating Scale, etc.)
    TabulationType: Tabulation types (categorical, scalar)
    MetricType: Metric types (column_percent, descriptive_statistics)
"""

from .schema import (
    # Enums
    VariableSuffix,
    QuestionType,
    TabulationType,
    MetricType,
    # Data classes
    QuestionRef,
    BaseVariable,
    TabulationStats,
    IndicatorSpec,
    TableSpecification,
    # Convenience functions
    create_empty_spec,
    load_from_file,
    save_to_file,
)

__all__ = [
    # Enums
    "VariableSuffix",
    "QuestionType",
    "TabulationType",
    "MetricType",
    # Data classes
    "QuestionRef",
    "BaseVariable",
    "TabulationStats",
    "IndicatorSpec",
    "TableSpecification",
    # Convenience functions
    "create_empty_spec",
    "load_from_file",
    "save_to_file",
]
