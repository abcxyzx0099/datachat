"""
Validation logic for recoding rules (Step 4).

Performs 7 validation checks on AI-generated recoding rules:
1. Source variables exist
2. Target variable conflicts
3. Range validity
4. No duplicate targets
5. Transformation completeness
6. Target value uniqueness
7. Source value overlap
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Results from validating AI-generated output."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    checks_performed: List[str]


class RecodingValidator:
    """Validator for recoding rules generated in Step 4."""

    def __init__(self, metadata: List[Dict[str, Any]]):
        """
        Initialize the validator with variable metadata.

        Args:
            metadata: List of variable metadata from the survey
        """
        self.metadata = {m["name"]: m for m in metadata}
        self.variable_names = set(m["name"] for m in metadata)

    def validate(self, rules: List[Dict[str, Any]]) -> ValidationResult:
        """
        Validate all recoding rules.

        Args:
            rules: List of recoding rules to validate

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        checks_performed = []

        # Check 1: Source variables exist
        check_name = "Source variables exist"
        checks_performed.append(check_name)
        for rule in rules:
            source = rule.get("source_variable")
            if source not in self.variable_names:
                errors.append(
                    f"Source variable '{source}' not found in metadata. "
                    f"Rule target: {rule.get('target_variable')}"
                )

        # Check 2: Target variables don't conflict with existing (warning)
        check_name = "Target variable conflicts"
        checks_performed.append(check_name)
        for rule in rules:
            target = rule.get("target_variable")
            if target in self.variable_names:
                warnings.append(
                    f"Target variable '{target}' already exists in metadata. "
                    f"It will be overwritten by the recoding."
                )

        # Check 3: Value ranges are valid (for range type rules)
        check_name = "Value ranges validity"
        checks_performed.append(check_name)
        for rule in rules:
            if rule.get("rule_type") == "range":
                for transform in rule.get("transformations", []):
                    source_range = transform.get("source", [])
                    if len(source_range) != 2:
                        errors.append(
                            f"Invalid range in rule {rule.get('target_variable')}: "
                            f"Range must have exactly 2 values, got {len(source_range)}"
                        )
                    elif len(source_range) == 2 and source_range[0] > source_range[1]:
                        errors.append(
                            f"Invalid range in rule {rule.get('target_variable')}: "
                            f"Range start ({source_range[0]}) > end ({source_range[1]})"
                        )

        # Check 4: No duplicate target variables
        check_name = "Duplicate target variables"
        checks_performed.append(check_name)
        targets = [r.get("target_variable") for r in rules]
        duplicates = [t for t in set(targets) if targets.count(t) > 1]
        if duplicates:
            errors.append(
                f"Duplicate target variables found: {duplicates}. "
                f"Each target variable should only be created once."
            )

        # Check 5: Transformation completeness
        check_name = "Transformation completeness"
        checks_performed.append(check_name)
        for rule in rules:
            if rule.get("rule_type") in ["range", "mapping"]:
                source_var = self.metadata.get(rule.get("source_variable"))
                if source_var and source_var.get("variable_type") == "numeric":
                    # Check if transformations cover the expected range
                    all_source_values = []
                    for transform in rule.get("transformations", []):
                        all_source_values.extend(transform.get("source", []))

                    if not all_source_values:
                        errors.append(
                            f"Rule {rule.get('target_variable')} has no source values defined"
                        )

        # Check 6: Target values are unique within each rule
        check_name = "Target value uniqueness"
        checks_performed.append(check_name)
        for rule in rules:
            target_values = [t.get("target") for t in rule.get("transformations", [])]
            if len(target_values) != len(set(target_values)):
                errors.append(
                    f"Rule {rule.get('target_variable')} has duplicate target values. "
                    f"Each transformation should map to a unique target value."
                )

        # Check 7: Source values don't overlap within a rule (for range/mapping)
        check_name = "Source value overlap"
        checks_performed.append(check_name)
        for rule in rules:
            if rule.get("rule_type") in ["range", "mapping"]:
                all_sources = []
                for transform in rule.get("transformations", []):
                    all_sources.extend(transform.get("source", []))

                if len(all_sources) != len(set(all_sources)):
                    errors.append(
                        f"Rule {rule.get('target_variable')} has overlapping source values. "
                        f"Each source value should only appear once."
                    )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checks_performed=checks_performed
        )


def validate_recoding_rules(
    rules: List[Dict[str, Any]],
    metadata: List[Dict[str, Any]]
) -> ValidationResult:
    """
    Convenience function to validate recoding rules.

    Args:
        rules: List of recoding rules to validate
        metadata: List of variable metadata

    Returns:
        ValidationResult with errors and warnings
    """
    validator = RecodingValidator(metadata)
    return validator.validate(rules)
