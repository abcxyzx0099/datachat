"""
Validation logic for indicators (Step 8).

Performs 5 validation checks on AI-generated indicators:
1. Variables exist
2. Metric valid
3. No duplicate IDs
4. Variables not empty
5. Variable type matches metric
"""

from typing import List, Dict, Any
from .recoding import ValidationResult


class IndicatorValidator:
    """Validator for indicators generated in Step 8."""

    VALID_METRICS = {"average", "percentage", "distribution"}

    def __init__(self, metadata: List[Dict[str, Any]]):
        """
        Initialize the validator with variable metadata.

        Args:
            metadata: List of variable metadata from the survey
        """
        self.metadata = {m["name"]: m for m in metadata}
        self.variable_names = set(m["name"] for m in metadata)

    def validate(self, indicators: List[Dict[str, Any]]) -> ValidationResult:
        """
        Validate all indicators.

        Args:
            indicators: List of indicators to validate

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        checks_performed = []

        # Check 1: Variables exist
        check_name = "Variables exist"
        checks_performed.append(check_name)
        for indicator in indicators:
            for var in indicator.get("underlying_variables", []):
                if var not in self.variable_names:
                    errors.append(
                        f"Indicator '{indicator.get('id')}' references "
                        f"non-existent variable '{var}'"
                    )

        # Check 2: Metric valid
        check_name = "Metric valid"
        checks_performed.append(check_name)
        for indicator in indicators:
            metric = indicator.get("metric")
            if metric not in self.VALID_METRICS:
                errors.append(
                    f"Indicator '{indicator.get('id')}' has invalid metric '{metric}'. "
                    f"Valid metrics: {', '.join(sorted(self.VALID_METRICS))}"
                )

        # Check 3: No duplicate IDs
        check_name = "No duplicate IDs"
        checks_performed.append(check_name)
        indicator_ids = [ind.get("id") for ind in indicators]
        duplicates = [id for id in set(indicator_ids) if indicator_ids.count(id) > 1]
        if duplicates:
            errors.append(
                f"Duplicate indicator IDs found: {duplicates}. "
                f"Each indicator ID must be unique."
            )

        # Check 4: Variables not empty
        check_name = "Variables not empty"
        checks_performed.append(check_name)
        for indicator in indicators:
            vars_list = indicator.get("underlying_variables", [])
            if not vars_list:
                errors.append(
                    f"Indicator '{indicator.get('id')}' has no underlying variables. "
                    f"Each indicator must have at least one variable."
                )

        # Check 5: Variable type matches metric
        check_name = "Variable type matches metric"
        checks_performed.append(check_name)
        for indicator in indicators:
            metric = indicator.get("metric")
            vars_list = indicator.get("underlying_variables", [])

            for var in vars_list:
                var_meta = self.metadata.get(var)
                if not var_meta:
                    continue  # Already caught by check 1

                var_type = var_meta.get("variable_type")

                # Average requires numeric variables
                if metric == "average" and var_type != "numeric":
                    errors.append(
                        f"Indicator '{indicator.get('id')}' uses metric 'average' "
                        f"with non-numeric variable '{var}' (type: {var_type})"
                    )

                # Percentage works with binary variables
                if metric == "percentage" and var_type not in ["numeric"]:
                    warnings.append(
                        f"Indicator '{indicator.get('id')}' uses metric 'percentage' "
                        f"with variable '{var}' (type: {var_type}). "
                        f"Percentage typically uses binary (0/1) variables."
                    )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checks_performed=checks_performed
        )


def validate_indicators(
    indicators: List[Dict[str, Any]],
    metadata: List[Dict[str, Any]]
) -> ValidationResult:
    """
    Convenience function to validate indicators.

    Args:
        indicators: List of indicators to validate
        metadata: List of variable metadata

    Returns:
        ValidationResult with errors and warnings
    """
    validator = IndicatorValidator(metadata)
    return validator.validate(indicators)
