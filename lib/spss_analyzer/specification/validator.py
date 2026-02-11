"""
Table Specification Validator

Validates a consolidated table specification document against:
1. JSON schema structure
2. Variable reference validity (against metadata)
3. Logical consistency
4. PSPP syntax requirements

Used by the survey-validate skill to ensure AI-generated specifications
are valid before processing.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass

from .schema import (
    TableSpecificationDocument,
    TableSpecification,
    Indicator,
    RecodingRule,
    VariableSource,
    TableType,
    MetricType,
    AggregationType,
    RecodingType,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Validation Results
# ============================================================================

@dataclass
class ValidationError:
    """A single validation error."""
    category: str  # "structure", "reference", "logic", "syntax"
    location: str  # Path to the error (e.g., "tables[0].rows.variable")
    message: str  # Human-readable error message
    severity: str = "error"  # "error", "warning"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.location}: {self.message}"


@dataclass
class ValidationResult:
    """Result of table specification validation."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]

    @property
    def all_issues(self) -> List[ValidationError]:
        """All validation issues (errors and warnings)."""
        return self.errors + self.warnings

    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            f"Validation Result: {'✓ VALID' if self.is_valid else '✗ INVALID'}",
            f"  Errors: {len(self.errors)}",
            f"  Warnings: {len(self.warnings)}",
        ]

        if self.errors:
            lines.append("\nErrors:")
            for error in self.errors:
                lines.append(f"  - {error}")

        if self.warnings:
            lines.append("\nWarnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")

        return "\n".join(lines)


# ============================================================================
# Main Validator
# ============================================================================

class TableSpecificationValidator:
    """
    Validates a table specification document.

    Validation stages:
    1. Structure: JSON schema compliance
    2. References: Variable and indicator references exist
    3. Logic: Business rule compliance
    4. Syntax: PSPP syntax compatibility
    """

    def __init__(self, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize validator.

        Args:
            metadata: Variable metadata from .sav file for reference validation.
                      If None, reference validation is skipped.
        """
        self.metadata = metadata or {}
        self._variable_names: Set[str] = set()
        self._indicator_ids: Set[str] = set()

        # Extract variable names from metadata if provided
        if metadata:
            self._extract_variable_names()

    def _extract_variable_names(self):
        """Extract variable names from metadata."""
        if isinstance(self.metadata, dict):
            # Variable-centered format
            self._variable_names = set(self.metadata.keys())
        elif isinstance(self.metadata, list):
            # File-centered format (list of variables)
            for var in self.metadata:
                if isinstance(var, dict) and "name" in var:
                    self._variable_names.add(var["name"])

    def validate(
        self,
        spec: Dict[str, Any],
        strict: bool = True,
    ) -> ValidationResult:
        """
        Validate a table specification.

        Args:
            spec: Table specification dictionary (from JSON)
            strict: If True, fail on warnings as well as errors

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []

        # Stage 1: Structure validation
        structure_errors = self._validate_structure(spec)
        errors.extend(structure_errors)

        if structure_errors:
            # Don't continue if structure is invalid
            return ValidationResult(
                is_valid=False,
                errors=[e for e in errors if e.severity == "error"],
                warnings=[e for e in errors if e.severity == "warning"],
            )

        # Parse the specification to get internal structure
        try:
            parsed_spec = TableSpecificationDocument.from_dict(spec)
            self._extract_indicator_ids(parsed_spec)
        except Exception as e:
            errors.append(ValidationError(
                category="structure",
                location="root",
                message=f"Failed to parse specification: {e}",
                severity="error",
            ))
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
            )

        # Stage 2: Reference validation
        ref_errors, ref_warnings = self._validate_references(parsed_spec)
        errors.extend(ref_errors)
        warnings.extend(ref_warnings)

        # Stage 3: Logic validation
        logic_errors, logic_warnings = self._validate_logic(parsed_spec)
        errors.extend(logic_errors)
        warnings.extend(logic_warnings)

        # Stage 4: Syntax validation
        syntax_errors, syntax_warnings = self._validate_syntax(parsed_spec)
        errors.extend(syntax_errors)
        warnings.extend(syntax_warnings)

        is_valid = len(errors) == 0
        if strict:
            is_valid = is_valid and len(warnings) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=[e for e in errors if e.severity == "error"],
            warnings=[e for e in warnings if e.severity == "warning"] + [e for e in warnings if e.severity == "warning"],
        )

    def _extract_variable_names(self):
        """Extract variable names from metadata."""
        if isinstance(self.metadata, dict):
            # Variable-centered format
            self._variable_names = set(self.metadata.keys())
        elif isinstance(self.metadata, list):
            # File-centered format (list of variables)
            for var in self.metadata:
                if isinstance(var, dict) and "name" in var:
                    self._variable_names.add(var["name"])

    def _extract_indicator_ids(self, spec: TableSpecificationDocument):
        """Extract indicator IDs from specification."""
        self._indicator_ids = {ind.id for ind in spec.indicators}

    # ========================================================================
    # Stage 1: Structure Validation
    # ========================================================================

    def _validate_structure(self, spec: Dict[str, Any]) -> List[ValidationError]:
        """Validate JSON structure."""
        errors = []

        # Check required sections
        required_sections = ["metadata", "tables", "output_settings"]
        for section in required_sections:
            if section not in spec:
                errors.append(ValidationError(
                    category="structure",
                    location=f".{section}",
                    message=f"Missing required section: '{section}'",
                    severity="error",
                ))

        # Validate metadata
        if "metadata" in spec:
            metadata = spec["metadata"]
            if "version" not in metadata:
                errors.append(ValidationError(
                    category="structure",
                    location=".metadata",
                    message="Missing 'version' in metadata",
                    severity="error",
                ))

        # Validate tables
        if "tables" in spec:
            if not isinstance(spec["tables"], list):
                errors.append(ValidationError(
                    category="structure",
                    location=".tables",
                    message="'tables' must be a list",
                    severity="error",
                ))
            elif len(spec["tables"]) == 0:
                errors.append(ValidationError(
                    category="structure",
                    location=".tables",
                    message="At least one table must be defined",
                    severity="error",
                ))
            else:
                for i, table in enumerate(spec["tables"]):
                    table_errors = self._validate_table_structure(table, i)
                    errors.extend(table_errors)

        # Validate indicators (if present)
        if "indicators" in spec:
            if not isinstance(spec["indicators"], list):
                errors.append(ValidationError(
                    category="structure",
                    location=".indicators",
                    message="'indicators' must be a list",
                    severity="error",
                ))
            else:
                for i, indicator in enumerate(spec["indicators"]):
                    ind_errors = self._validate_indicator_structure(indicator, i)
                    errors.extend(ind_errors)

        # Validate global recodings (if present)
        if "global_recodings" in spec:
            if not isinstance(spec["global_recodings"], list):
                errors.append(ValidationError(
                    category="structure",
                    location=".global_recodings",
                    message="'global_recodings' must be a list",
                    severity="error",
                ))

        return errors

    def _validate_table_structure(self, table: Dict[str, Any], index: int) -> List[ValidationError]:
        """Validate a single table's structure."""
        errors = []
        prefix = f".tables[{index}]"
        table_id = table.get("id", f"tables[{index}]")

        # Required fields
        required_fields = ["id", "title", "type"]
        for field in required_fields:
            if field not in table:
                errors.append(ValidationError(
                    category="structure",
                    location=f"{prefix}.{field}",
                    message=f"Missing required field: '{field}'",
                    severity="error",
                ))

        # Validate table type
        if "type" in table:
            try:
                TableType(table["type"])
            except ValueError:
                errors.append(ValidationError(
                    category="structure",
                    location=f"{prefix}.type",
                    message=f"Invalid table type: '{table['type']}'. Must be one of: {[t.value for t in TableType]}",
                    severity="error",
                ))

        # For crosstabs, need dimensions
        if table.get("type") == "crosstab":
            if not table.get("rows") and not table.get("columns"):
                errors.append(ValidationError(
                    category="structure",
                    location=prefix,
                    message=f"Crosstab table '{table_id}' requires 'rows' or 'columns'",
                    severity="error",
                ))

        # Validate metrics
        if "metrics" in table:
            if not isinstance(table["metrics"], list):
                errors.append(ValidationError(
                    category="structure",
                    location=f"{prefix}.metrics",
                    message="'metrics' must be a list",
                    severity="error",
                ))
            else:
                for j, metric in enumerate(table["metrics"]):
                    if "type" not in metric:
                        errors.append(ValidationError(
                            category="structure",
                            location=f"{prefix}.metrics[{j}]",
                            message="Metric missing 'type'",
                            severity="error",
                        ))
                    else:
                        try:
                            MetricType(metric["type"])
                        except ValueError:
                            errors.append(ValidationError(
                                category="structure",
                                location=f"{prefix}.metrics[{j}].type",
                                message=f"Invalid metric type: '{metric['type']}'",
                                severity="error",
                            ))

        return errors

    def _validate_indicator_structure(self, indicator: Dict[str, Any], index: int) -> List[ValidationError]:
        """Validate an indicator's structure."""
        errors = []
        prefix = f".indicators[{index}]"
        ind_id = indicator.get("id", f"indicators[{index}]")

        # Required fields
        required_fields = ["id", "name"]
        for field in required_fields:
            if field not in indicator:
                errors.append(ValidationError(
                    category="structure",
                    location=f"{prefix}.{field}",
                    message=f"Missing required field: '{field}'",
                    severity="error",
                ))

        # Validate variables list
        if "variables" in indicator:
            if not isinstance(indicator["variables"], list):
                errors.append(ValidationError(
                    category="structure",
                    location=f"{prefix}.variables",
                    message="'variables' must be a list",
                    severity="error",
                ))
            elif len(indicator["variables"]) == 0:
                errors.append(ValidationError(
                    category="structure",
                    location=prefix,
                    message=f"Indicator '{ind_id}' has no variables",
                    severity="error",
                ))

        # Validate aggregation type
        if "aggregation" in indicator:
            try:
                AggregationType(indicator["aggregation"])
            except ValueError:
                errors.append(ValidationError(
                    category="structure",
                    location=f"{prefix}.aggregation",
                    message=f"Invalid aggregation type: '{indicator['aggregation']}'",
                    severity="error",
                ))

        return errors

    # ========================================================================
    # Stage 2: Reference Validation
    # ========================================================================

    def _validate_references(self, spec: TableSpecificationDocument) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate variable and indicator references."""
        errors = []
        warnings = []

        # Check table variable references
        for i, table in enumerate(spec.tables):
            prefix = f".tables[{i}]"

            # Check row variable
            if table.rows:
                ref_errors, ref_warnings = self._validate_variable_reference(
                    table.rows.variable,
                    f"{prefix}.rows.variable",
                    table.rows.source,
                )
                errors.extend(ref_errors)
                warnings.extend(ref_warnings)

            # Check column variable
            if table.columns:
                ref_errors, ref_warnings = self._validate_variable_reference(
                    table.columns.variable,
                    f"{prefix}.columns.variable",
                    table.columns.source,
                )
                errors.extend(ref_errors)
                warnings.extend(ref_warnings)

            # Check layer variables
            if table.layers:
                for j, layer in enumerate(table.layers):
                    ref_errors, ref_warnings = self._validate_variable_reference(
                        layer.variable,
                        f"{prefix}.layers[{j}].variable",
                        layer.source,
                    )
                    errors.extend(ref_errors)
                    warnings.extend(ref_warnings)

            # Check weight variable
            if table.weight_variable:
                if table.weight_variable not in self._variable_names:
                    errors.append(ValidationError(
                        category="reference",
                        location=f"{prefix}.weight_variable",
                        message=f"Weight variable '{table.weight_variable}' not found in data",
                        severity="error",
                    ))

            # Check indicator references
            for ind_id in table.indicator_ids:
                if ind_id not in self._indicator_ids:
                    errors.append(ValidationError(
                        category="reference",
                        location=f"{prefix}.indicator_ids",
                        message=f"Indicator '{ind_id}' not found in specification",
                        severity="error",
                    ))

        # Check indicator variable references
        for i, indicator in enumerate(spec.indicators):
            prefix = f".indicators[{i}]"
            for j, var_ref in enumerate(indicator.variables):
                ref_errors, ref_warnings = self._validate_variable_reference(
                    var_ref.name,
                    f"{prefix}.variables[{j}].name",
                    var_ref.source,
                )
                errors.extend(ref_errors)
                warnings.extend(ref_warnings)

        # Check global recoding variable references
        for i, recoding in enumerate(spec.global_recodings):
            if recoding.variable not in self._variable_names:
                errors.append(ValidationError(
                    category="reference",
                    location=f".global_recodings[{i}].variable",
                    message=f"Variable '{recoding.variable}' not found in data",
                    severity="error",
                ))

        return errors, warnings

    def _validate_variable_reference(
        self,
        var_name: str,
        location: str,
        source: VariableSource,
    ) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate a single variable reference."""
        errors = []
        warnings = []

        if source == VariableSource.RAW:
            if var_name not in self._variable_names:
                errors.append(ValidationError(
                    category="reference",
                    location=location,
                    message=f"Variable '{var_name}' not found in data",
                    severity="error",
                ))
        elif source == VariableSource.RECODED:
            # Check if recoding rule exists
            original_name = var_name.replace("_recoded", "")
            if original_name not in self._variable_names:
                errors.append(ValidationError(
                    category="reference",
                    location=location,
                    message=f"Original variable '{original_name}' for recoded '{var_name}' not found",
                    severity="error",
                ))
        elif source == VariableSource.INDICATOR:
            if var_name not in self._indicator_ids:
                errors.append(ValidationError(
                    category="reference",
                    location=location,
                    message=f"Indicator '{var_name}' not found in specification",
                    severity="error",
                ))

        return errors, warnings

    # ========================================================================
    # Stage 3: Logic Validation
    # ========================================================================

    def _validate_logic(self, spec: TableSpecificationDocument) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate business logic and consistency."""
        errors = []
        warnings = []

        # Check for duplicate table IDs
        table_ids = [t.id for t in spec.tables]
        duplicates = [tid for tid in set(table_ids) if table_ids.count(tid) > 1]
        for dup_id in duplicates:
            errors.append(ValidationError(
                category="logic",
                location=".tables",
                message=f"Duplicate table ID: '{dup_id}'",
                severity="error",
            ))

        # Check for duplicate indicator IDs
        indicator_ids = [ind.id for ind in spec.indicators]
        ind_duplicates = [iid for iid in set(indicator_ids) if indicator_ids.count(iid) > 1]
        for dup_id in ind_duplicates:
            errors.append(ValidationError(
                category="logic",
                location=".indicators",
                message=f"Duplicate indicator ID: '{dup_id}'",
                severity="error",
            ))

        # Validate output settings
        output = spec.output_settings
        if output.significance_threshold <= 0 or output.significance_threshold > 1:
            errors.append(ValidationError(
                category="logic",
                location=".output_settings.significance_threshold",
                message=f"Significance threshold must be between 0 and 1, got {output.significance_threshold}",
                severity="error",
            ))

        if output.min_cramers_v < 0 or output.min_cramers_v > 1:
            errors.append(ValidationError(
                category="logic",
                location=".output_settings.min_cramers_v",
                message=f"Cramer's V minimum must be between 0 and 1, got {output.min_cramers_v}",
                severity="error",
            ))

        # Check if max_tables_ppt is reasonable
        if output.max_tables_ppt < 1:
            errors.append(ValidationError(
                category="logic",
                location=".output_settings.max_tables_ppt",
                message=f"max_tables_ppt must be at least 1, got {output.max_tables_ppt}",
                severity="error",
            ))

        # Warn if no indicators defined
        if not spec.indicators:
            warnings.append(ValidationError(
                category="logic",
                location=".indicators",
                message="No indicators defined in specification",
                severity="warning",
            ))

        return errors, warnings

    # ========================================================================
    # Stage 4: Syntax Validation
    # ========================================================================

    def _validate_syntax(self, spec: TableSpecificationDocument) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate PSPP syntax compatibility."""
        errors = []
        warnings = []

        # Check for PSPP syntax compatibility in recodings
        for i, recoding in enumerate(spec.global_recodings):
            prefix = f".global_recodings[{i}]"

            if recoding.type == RecodingType.VALUE_MAP:
                if not recoding.value_mappings:
                    errors.append(ValidationError(
                        category="syntax",
                        location=f"{prefix}.value_mappings",
                        message=f"Recoding of type 'value_map' requires value_mappings",
                        severity="error",
                    ))
            elif recoding.type == RecodingType.RANGE_MAP:
                if not recoding.range_mappings:
                    errors.append(ValidationError(
                        category="syntax",
                        location=f"{prefix}.range_mappings",
                        message=f"Recoding of type 'range_map' requires range_mappings",
                        severity="error",
                    ))
            elif recoding.type == RecodingType.CONDITION:
                if not recoding.conditions:
                    errors.append(ValidationError(
                        category="syntax",
                        location=f"{prefix}.conditions",
                        message=f"Recoding of type 'condition' requires conditions",
                        severity="error",
                    ))

        # Check table metrics compatibility
        for i, table in enumerate(spec.tables):
            prefix = f".tables[{i}]"

            if table.type == TableType.CROSSTAB:
                # Crosstabs should have at least one dimension
                if not table.rows and not table.columns:
                    errors.append(ValidationError(
                        category="syntax",
                        location=prefix,
                        message=f"Crosstab table '{table.id}' requires rows or columns",
                        severity="error",
                    ))

            elif table.type == TableType.FREQUENCY:
                # Frequency tables should have rows only
                if table.columns:
                    warnings.append(ValidationError(
                        category="syntax",
                        location=f"{prefix}.columns",
                        message=f"Frequency table '{table.id}' typically doesn't use columns",
                        severity="warning",
                    ))

            elif table.type == TableType.SUMMARY:
                # Summary tables should use mean/median metrics
                valid_metrics = {MetricType.MEAN, MetricType.MEDIAN, MetricType.STD_DEV, MetricType.MIN, MetricType.MAX}
                for metric in table.metrics:
                    if metric.type not in valid_metrics and metric.type != MetricType.COUNT:
                        warnings.append(ValidationError(
                            category="syntax",
                            location=f"{prefix}.metrics",
                            message=f"Metric '{metric.type.value}' may not be appropriate for summary table '{table.id}'",
                            severity="warning",
                        ))

        return errors, warnings


# ============================================================================
# Convenience Functions
# ============================================================================

def validate_specification(
    spec: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    strict: bool = False,
) -> ValidationResult:
    """
    Validate a table specification document.

    Args:
        spec: Table specification dictionary (from JSON)
        metadata: Variable metadata for reference validation
        strict: If True, fail on warnings as well as errors

    Returns:
        ValidationResult with errors and warnings
    """
    validator = TableSpecificationValidator(metadata)
    return validator.validate(spec, strict=strict)


def is_valid_specification(
    spec: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Quick check if a specification is valid.

    Args:
        spec: Table specification dictionary (from JSON)
        metadata: Variable metadata for reference validation

    Returns:
        True if valid (no errors), False otherwise
    """
    result = validate_specification(spec, metadata, strict=False)
    return result.is_valid
