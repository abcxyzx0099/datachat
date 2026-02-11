"""
Specification Module

Provides the consolidated table specification schema and validator.

The table specification is the primary AI-generated artifact that combines:
- Indicator definitions
- Recoding rules
- Table specifications (dimensions, metrics, grouping rules)
- Output settings

Classes:
    TableSpecificationDocument: Root specification document
    TableSpecification: Single table definition
    Indicator: Indicator definition
    RecodingRule: Variable recoding rules
    TableSpecificationValidator: Validates specifications
"""

from .schema import (
    # Enums
    MetricType,
    AggregationType,
    RecodingType,
    TableType,
    VariableSource,
    # Data classes
    ValueMapping,
    RangeMapping,
    RecodingRule,
    VariableRef,
    Indicator,
    TableDimension,
    TableMetric,
    TableSpecification,
    OutputSettings,
    TableSpecificationDocument,
    # Convenience functions
    create_empty_spec,
    validate_spec_structure,
)

from .validator import (
    ValidationError,
    ValidationResult,
    TableSpecificationValidator,
    validate_specification,
    is_valid_specification,
)

__all__ = [
    # Enums
    "MetricType",
    "AggregationType",
    "RecodingType",
    "TableType",
    "VariableSource",
    # Data classes
    "ValueMapping",
    "RangeMapping",
    "RecodingRule",
    "VariableRef",
    "Indicator",
    "TableDimension",
    "TableMetric",
    "TableSpecification",
    "OutputSettings",
    "TableSpecificationDocument",
    # Schema functions
    "create_empty_spec",
    "validate_spec_structure",
    # Validator
    "ValidationError",
    "ValidationResult",
    "TableSpecificationValidator",
    "validate_specification",
    "is_valid_specification",
]
