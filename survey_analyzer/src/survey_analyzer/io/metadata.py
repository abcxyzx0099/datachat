"""
Metadata Transformer

Transforms SPSS metadata between different formats:
- File-centered (from pyreadstat)
- Variable-centered (for easier lookup)
- Filtered (for business rules)

Example:
    >>> transformer = MetadataTransformer()
    >>> variable_metadata = transformer.to_variable_centered(pyreadstat_metadata)
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MetadataTransformer:
    """
    Transform SPSS metadata between different formats.

    The original pyreadstat metadata is "file-centered" - value_labels
    is a dict where keys are variable names. For easier use in analysis,
    we provide a "variable-centered" format where each variable has all
    its information in one place.

    Example:
        >>> transformer = MetadataTransformer()
        >>> new_metadata = transformer.to_variable_centered(metadata)
        >>> print(new_metadata["q1"]["label"])
        'Question 1: Satisfaction'
    """

    def to_variable_centered(
        self,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert metadata to variable-centered format.

        Input format (from pyreadstat):
            {
                "variable_labels": {"q1": "Satisfaction", "q2": "Brand"},
                "value_labels": {"q1": {"1": "Yes", "2": "No"}}
            }

        Output format (variable-centered):
            {
                "q1": {
                    "label": "Satisfaction",
                    "value_labels": {"1": "Yes", "2": "No"},
                    "variable_type": "numeric"
                },
                "q2": {...}
            }

        Args:
            metadata: Original metadata from SPSSReader

        Returns:
            Variable-centered metadata dictionary

        Example:
            >>> transformer = MetadataTransformer()
            >>> new_metadata = transformer.to_variable_centered(metadata)
            >>> for var_name, var_info in new_metadata.items():
            ...     print(f"{var_name}: {var_info['label']}")
        """
        new_metadata = {}
        variable_labels = metadata.get("variable_labels", {})
        value_labels = metadata.get("value_labels", {})

        # Process each variable
        for var_name, label in variable_labels.items():
            new_metadata[var_name] = {
                "label": label,
                "value_labels": value_labels.get(var_name, {}),
                "variable_type": self._infer_variable_type(
                    var_name, value_labels.get(var_name, {})
                ),
            }

        # Add variables without labels (unlabeled numeric columns)
        for var_name in metadata.get("variable_types", {}):
            if var_name not in new_metadata:
                new_metadata[var_name] = {
                    "label": var_name,  # Use variable name as label
                    "value_labels": {},
                    "variable_type": "numeric",
                }

        logger.info(
            f"Transformed metadata to variable-centered format: "
            f"{len(new_metadata)} variables"
        )

        return new_metadata

    def filter_variables(
        self,
        metadata: Dict[str, Any],
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        max_categories: int = 30,
        filter_other_text: bool = True,
    ) -> Dict[str, Any]:
        """
        Filter metadata variables based on business rules.

        Filtering Rules:
        1. High Cardinality: DROP variables with > max_categories distinct values
        2. Other Text Fields: DROP variables where name contains "other" AND type is string
        3. Binary Variables: KEEP (2 categories are preserved for analysis)

        Args:
            metadata: Variable-centered metadata
            include_patterns: List of regex patterns - variables must match one
            exclude_patterns: List of regex patterns - exclude if matched
            max_categories: Maximum number of value categories (default: 30 per business rules)
            filter_other_text: Whether to filter "other" text fields (default: True)

        Returns:
            Filtered metadata dictionary

        Example:
            >>> transformer = MetadataTransformer()
            >>> filtered = transformer.filter_variables(
            ...     metadata,
            ...     include_patterns=[r"^q[0-9]+"],  # Questions only
            ...     max_categories=30
            ... )
        """
        import re

        filtered = {}
        dropped = {}
        include_regexes = [
            re.compile(p) for p in (include_patterns or [])
        ]
        exclude_regexes = [
            re.compile(p) for p in (exclude_patterns or [])
        ]

        for var_name, var_info in metadata.items():
            # Check include patterns
            if include_regexes:
                if not any(r.match(var_name) for r in include_regexes):
                    continue

            # Check exclude patterns
            if exclude_regexes:
                if any(r.match(var_name) for r in exclude_regexes):
                    continue

            # Get category count
            value_labels = var_info.get("value_labels", {})
            num_categories = len(value_labels)
            variable_type = var_info.get("variable_type", "unknown")

            # Rule 1: High Cardinality - DROP if > max_categories
            if num_categories > max_categories:
                dropped[var_name] = {
                    "reason": "high_cardinality",
                    "cardinality": num_categories
                }
                logger.debug(
                    f"Excluding {var_name}: high cardinality ({num_categories} > {max_categories})"
                )
                continue

            # Rule 2: Other Text Fields - DROP if name contains "other" AND type is string
            if filter_other_text and "other" in var_name.lower() and variable_type == "string":
                dropped[var_name] = {
                    "reason": "other_text_field",
                    "type": variable_type
                }
                logger.debug(
                    f"Excluding {var_name}: other text field"
                )
                continue

            # Rule 3: Single/Empty variables - DROP if < 1 category (no data)
            # Note: Binary variables (2 categories) are KEPT
            if num_categories < 1:
                dropped[var_name] = {
                    "reason": "no_categories",
                    "cardinality": num_categories
                }
                logger.debug(
                    f"Excluding {var_name}: no categories ({num_categories})"
                )
                continue

            # Variable passed all filters
            filtered[var_name] = var_info

        logger.info(
            f"Filtered variables: {len(filtered)}/{len(metadata)} remaining, "
            f"{len(dropped)} dropped"
        )

        return filtered

    def get_analysis_variables(
        self,
        metadata: Dict[str, Any],
        exclude_metadata_fields: bool = True,
    ) -> List[str]:
        """
        Get list of variables suitable for cross-tabulation analysis.

        Note: Binary variables (2 categories) are INCLUDED for analysis.
        Only variables without value labels (open-ended text) are excluded.

        Args:
            metadata: Variable-centered metadata
            exclude_metadata_fields: Exclude common metadata field names

        Returns:
            List of variable names

        Example:
            >>> transformer = MetadataTransformer()
            >>> vars = transformer.get_analysis_variables(metadata)
            >>> print(vars[:5])
            ['q1', 'q2', 'q3', 'q4', 'q5']
        """
        # Common metadata field names to exclude
        metadata_fields = {
            "resp_id", "responseid", "respondent_id", "id",
            "start_date", "end_date", "duration", "status",
            "ip_address", "user_agent", "language",
            "weight", "sample_weight",
        }

        analysis_vars = []

        for var_name, var_info in metadata.items():
            # Skip metadata fields
            if exclude_metadata_fields and var_name.lower() in metadata_fields:
                continue

            # Skip variables without value labels (likely open-ended text)
            if not var_info.get("value_labels"):
                continue

            # Skip empty variables (0 categories)
            # Note: Binary variables (2 categories) are KEPT
            if len(var_info["value_labels"]) < 1:
                continue

            analysis_vars.append(var_name)

        logger.info(
            f"Found {len(analysis_vars)} variables suitable for analysis"
        )

        return analysis_vars

    def _infer_variable_type(
        self,
        var_name: str,
        value_labels: Dict[str, str],
    ) -> str:
        """
        Infer variable type from name and value labels.

        Returns:
            'categorical', 'ordinal', or 'numeric'
        """
        if not value_labels:
            return "numeric"

        # Check if values are numeric (suggests ordinal)
        try:
            values = [int(v) for v in value_labels.keys()]
        except ValueError:
            return "categorical"

        # Check if labels suggest ordinal nature
        ordinal_keywords = [
            "scale", "rank", "rating", "agree", "satisfy",
            "likely", "often", "frequency", "level"
        ]

        label_text = " ".join(value_labels.values()).lower()
        if any(kw in label_text for kw in ordinal_keywords):
            return "ordinal"

        return "categorical"


def transform_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to transform metadata to variable-centered format.

    Args:
        metadata: Original metadata from SPSSReader

    Returns:
        Variable-centered metadata

    Example:
        >>> new_metadata = transform_metadata(metadata)
    """
    transformer = MetadataTransformer()
    return transformer.to_variable_centered(metadata)
