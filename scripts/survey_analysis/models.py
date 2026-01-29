"""
Data models for the survey analysis workflow.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from enum import Enum
from datetime import datetime


class RuleType(str, Enum):
    """Types of recoding rules."""
    RANGE = "range"  # Group continuous values into ranges
    MAPPING = "mapping"  # Map specific values to new values
    DERIVED = "derived"  # Create derived variables (e.g., top-2-box)
    CATEGORY = "category"  # Category grouping/relabeling


class Transformation(BaseModel):
    """A single transformation from source values to target value."""
    source: List[int] = Field(description="Source value(s) to transform")
    target: int = Field(description="Target value to assign")
    label: str = Field(description="Human-readable label for target value")


class RecodingRule(BaseModel):
    """A recoding rule for transforming a variable."""
    source_variable: str = Field(description="Name of the source variable")
    target_variable: str = Field(description="Name of the target variable")
    rule_type: RuleType = Field(description="Type of recoding rule")
    transformations: List[Transformation] = Field(description="List of transformations")

    class Config:
        use_enum_values = True


class VariableMetadata(BaseModel):
    """Metadata for a single variable."""
    name: str
    label: str = ""
    variable_type: Literal["numeric", "string", "date"]
    value_labels: Dict[int, str] = Field(default_factory=dict)
    categories: Optional[List[str]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    missing_values: List[Any] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Results from validating recoding rules."""
    is_valid: bool = Field(description="Whether all validation checks passed")
    errors: List[str] = Field(default_factory=list, description="Critical validation errors")
    warnings: List[str] = Field(default_factory=list, description="Non-critical warnings")
    checks_performed: List[str] = Field(default_factory=list, description="List of validation checks performed")
    timestamp: datetime = Field(default_factory=datetime.now)


class WorkflowState(BaseModel):
    """State for the survey analysis workflow."""
    # Input data
    raw_metadata: List[Dict[str, Any]] = Field(default_factory=list)
    filtered_metadata: List[VariableMetadata] = Field(default_factory=list)

    # Recoding rules (with self-verification)
    recoding_rules: List[RecodingRule] = Field(default_factory=list)
    validation_result: Optional[ValidationResult] = None
    self_correction_iterations: int = Field(default=0)

    # Configuration
    max_self_correction_iterations: int = Field(default=3)

    # Execution log
    execution_log: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

    # Output paths
    output_dir: str = Field(default="output")


class RecodingRulesOutput(BaseModel):
    """Output from the recoding rules generation with verification."""
    rules: List[RecodingRule]
    validation_result: ValidationResult
    iterations_used: int
    generation_timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
