"""
Validation logic for table specifications (Step 9).

Performs 6 validation checks on AI-generated table specifications:
1. Indicator IDs exist
2. No overlap between rows and columns
3. Weighting variable exists
4. Sorting valid
5. Cramer's V in range [0, 1]
6. Count min > 0
"""

from typing import List, Dict, Any
from .recoding import ValidationResult


class TableSpecsValidator:
    """Validator for table specifications generated in Step 9."""

    def __init__(self, metadata: List[Dict[str, Any]], indicators: List[Dict[str, Any]]):
        """
        Initialize the validator with metadata and indicators.

        Args:
            metadata: List of variable metadata from the survey
            indicators: List of generated indicators
        """
        self.metadata = {m["name"]: m for m in metadata}
        self.variable_names = set(m["name"] for m in metadata)
        self.indicators = {ind["id"]: ind for ind in indicators}
        self.indicator_ids = set(ind["id"] for ind in indicators)

    def validate(self, table_specs: Dict[str, Any]) -> ValidationResult:
        """
        Validate table specifications.

        Args:
            table_specs: Table specifications dictionary

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        checks_performed = []

        tables = table_specs.get("tables", [])

        # Check 1: Indicator IDs exist
        check_name = "Indicator IDs exist"
        checks_performed.append(check_name)
        for table in tables:
            row_indicators = table.get("row_indicators", [])
            col_indicators = table.get("column_indicators", [])

            for ind_id in row_indicators + col_indicators:
                if ind_id not in self.indicator_ids:
                    errors.append(
                        f"Table '{table.get('id')}' references "
                        f"non-existent indicator '{ind_id}'"
                    )

        # Check 2: No overlap between rows and columns
        check_name = "No overlap between rows and columns"
        checks_performed.append(check_name)
        for table in tables:
            row_indicators = set(table.get("row_indicators", []))
            col_indicators = set(table.get("column_indicators", []))
            overlap = row_indicators & col_indicators

            if overlap:
                errors.append(
                    f"Table '{table.get('id')}' has overlapping indicators "
                    f"in rows and columns: {overlap}"
                )

        # Check 3: Weighting variable exists
        check_name = "Weighting variable exists"
        checks_performed.append(check_name)
        weighting_var = table_specs.get("weighting_variable")
        if weighting_var and weighting_var not in self.variable_names:
            errors.append(
                f"Weighting variable '{weighting_var}' not found in metadata"
            )

        # Check 4: Sorting valid
        check_name = "Sorting valid"
        checks_performed.append(check_name)
        valid_sort_options = {"none", "asc", "desc"}
        for table in tables:
            sort_rows = table.get("sort_rows")
            sort_cols = table.get("sort_columns")

            if sort_rows and sort_rows not in valid_sort_options:
                errors.append(
                    f"Table '{table.get('id')}' has invalid sort_rows value '{sort_rows}'. "
                    f"Valid options: {', '.join(sorted(valid_sort_options))}"
                )

            if sort_cols and sort_cols not in valid_sort_options:
                errors.append(
                    f"Table '{table.get('id')}' has invalid sort_columns value '{sort_cols}'. "
                    f"Valid options: {', '.join(sorted(valid_sort_options))}"
                )

        # Check 5: Cramer's V in range [0, 1]
        check_name = "Cramer's V in range"
        checks_performed.append(check_name)
        for table in tables:
            cramers_v_threshold = table.get("cramers_v_threshold")
            if cramers_v_threshold is not None:
                if not (0 <= cramers_v_threshold <= 1):
                    errors.append(
                        f"Table '{table.get('id')}' has Cramer's V threshold "
                        f"{cramers_v_threshold} which is outside valid range [0, 1]"
                    )

        # Check 6: Count min > 0
        check_name = "Count min > 0"
        checks_performed.append(check_name)
        for table in tables:
            min_count = table.get("min_count")
            if min_count is not None and min_count <= 0:
                errors.append(
                    f"Table '{table.get('id')}' has min_count {min_count} "
                    f"which must be greater than 0"
                )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            checks_performed=checks_performed
        )


def validate_table_specs(
    table_specs: Dict[str, Any],
    metadata: List[Dict[str, Any]],
    indicators: List[Dict[str, Any]]
) -> ValidationResult:
    """
    Convenience function to validate table specifications.

    Args:
        table_specs: Table specifications dictionary
        metadata: List of variable metadata
        indicators: List of indicator definitions

    Returns:
        ValidationResult with errors and warnings
    """
    validator = TableSpecsValidator(metadata, indicators)
    return validator.validate(table_specs)
