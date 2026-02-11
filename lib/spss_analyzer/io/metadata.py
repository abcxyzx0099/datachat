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
        min_categories: int = 2,
        max_categories: int = 50,
    ) -> Dict[str, Any]:
        """
        Filter metadata variables based on business rules.

        Args:
            metadata: Variable-centered metadata
            include_patterns: List of regex patterns - variables must match one
            exclude_patterns: List of regex patterns - exclude if matched
            min_categories: Minimum number of value categories
            max_categories: Maximum number of value categories

        Returns:
            Filtered metadata dictionary

        Example:
            >>> transformer = MetadataTransformer()
            >>> filtered = transformer.filter_variables(
            ...     metadata,
            ...     include_patterns=[r"^q[0-9]+"],  # Questions only
            ...     min_categories=2,
            ...     max_categories=10
            ... )
        """
        import re

        filtered = {}
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

            # Check category count
            value_labels = var_info.get("value_labels", {})
            num_categories = len(value_labels)

            if num_categories < min_categories:
                logger.debug(
                    f"Excluding {var_name}: too few categories ({num_categories})"
                )
                continue

            if num_categories > max_categories:
                logger.debug(
                    f"Excluding {var_name}: too many categories ({num_categories})"
                )
                continue

            filtered[var_name] = var_info

        logger.info(
            f"Filtered variables: {len(filtered)}/{len(metadata)} remaining"
        )

        return filtered

    def get_analysis_variables(
        self,
        metadata: Dict[str, Any],
        exclude_metadata_fields: bool = True,
    ) -> List[str]:
        """
        Get list of variables suitable for cross-tabulation analysis.

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

            # Skip variables without value labels (likely open-ended)
            if not var_info.get("value_labels"):
                continue

            # Skip single-value variables
            if len(var_info["value_labels"]) < 2:
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
