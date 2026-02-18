"""
Transformation Engine

Apply variable recoding and transformations using pandas.

This module replaces PSPP RECODE syntax with pure Python pandas operations.
Supports value recoding, range mapping, and computed variables.

Example:
    >>> engine = TransformationEngine()
    >>> df_transformed = engine.apply_transformations(df, indicators)
    >>> # Recoded: "(1 THRU 2=1) (3=2) (4 THRU 5=3)" applied
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TransformationRule:
    """
    Represents a single transformation rule.

    Attributes:
        source: Source variable name
        target: Target variable name
        rules: Recoding rules (e.g., "(1 THRU 2=1) (3=2)")
        mapping: Explicit value mapping dict
        compute: Computation expression (e.g., "var1 + var2")
    """
    source: str
    target: str
    rules: Optional[str] = None
    mapping: Optional[Dict[Any, Any]] = None
    compute: Optional[str] = None

    def has_rules(self) -> bool:
        """Check if any transformation is defined."""
        return bool(self.rules or self.mapping or self.compute)


class TransformationEngine:
    """
    Apply variable transformations using pandas.

    Supports:
    - Value recoding: "(1=2) (3 THRU 5=99)"
    - Range mapping: "(1 THRU 3=1) (4 THRU 6=2)"
    - Explicit mapping: {1: "A", 2: "B", 3: "C"}
    - Computed variables: "var_a + var_b"

    Example:
        >>> engine = TransformationEngine()
        >>> df = pd.DataFrame({"age": [25, 35, 45, 55, 65]})
        >>> engine.apply_recode(df, "age", "age_group", "(1 THRU 2=1) (3=2) (4 THRU 5=3)")
        >>> df["age_group"]
        0    1
        1    1
        2    2
        3    2
        4    3
    """

    # Regex patterns for parsing transformation rules
    RULE_PATTERN = re.compile(r'\(([^)]+)\)')
    RANGE_PATTERN = re.compile(r'(\d+)\s+THRU\s+(\d+)\s*=\s*(.+)')
    SINGLE_PATTERN = re.compile(r'(\d+)\s*=\s*(.+)')

    def __init__(self, copy: bool = True):
        """
        Initialize the transformation engine.

        Args:
            copy: If True, create a copy of the DataFrame (default: True)
        """
        self.copy = copy

    def apply_transformations(
        self,
        df: pd.DataFrame,
        indicators: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """
        Apply all transformations from indicator specifications.

        Args:
            df: Input DataFrame
            indicators: List of indicator dicts with transformation_rules

        Returns:
            DataFrame with transformed variables

        Example:
            >>> indicators = [
            ...     {
            ...         "indicator_code": "age_recoded",
            ...         "source_variables": ["age"],
            ...         "transformation_rules": "(1 THRU 2=1) (3=2)"
            ...     }
            ... ]
            >>> engine = TransformationEngine()
            >>> df_transformed = engine.apply_transformations(df, indicators)
        """
        if self.copy:
            df = df.copy()

        for indicator in indicators:
            code = indicator.get('indicator_code')
            source_vars = indicator.get('source_variables', [])
            rules = indicator.get('transformation_rules')

            if not rules or rules.lower() == 'null':
                # No transformation - use source as-is
                if source_vars and len(source_vars) == 1:
                    if code not in df.columns:
                        df[code] = df[source_vars[0]]
                continue

            # Parse and apply transformation
            if source_vars:
                source = source_vars[0]
                target = code

                if rules.startswith('COMPUTE'):
                    # Computed variable
                    df[target] = self._apply_compute(df, rules, source)
                else:
                    # Recoding rules
                    df[target] = self._apply_recode(df[source], rules)

                logger.debug(f"Applied transformation: {source} -> {target} ({rules})")

        return df

    def apply_recode(
        self,
        df: pd.DataFrame,
        source_column: str,
        target_column: str,
        rules: str
    ) -> pd.Series:
        """
        Apply recoding rules to a column.

        Args:
            df: Input DataFrame
            source_column: Source column name
            target_column: Target column name
            rules: Recoding rules (e.g., "(1 THRU 2=1) (3=2)")

        Returns:
            Series with recoded values

        Example:
            >>> df = pd.DataFrame({"q1": [1, 2, 3, 4, 5]})
            >>> engine = TransformationEngine()
            >>> df["q1_recoded"] = engine.apply_recode(df, "q1", "q1_recoded", "(1 THRU 2=1) (3=2)")
        """
        return self._apply_recode(df[source_column], rules)

    def _apply_recode(self, series: pd.Series, rules: str) -> pd.Series:
        """
        Apply recoding rules to a series.

        Args:
            series: Input series
            rules: Recoding rules string

        Returns:
            Recoded series
        """
        # Parse rules into mapping
        mapping = self._parse_rules(rules)

        # Apply mapping with default = original value
        return series.map(mapping).fillna(series)

    def _parse_rules(self, rules: str) -> Dict[Any, Any]:
        """
        Parse recoding rules into a value mapping dictionary.

        Supports:
        - Single values: "(3=2)" -> {3: 2}
        - Ranges: "(1 THRU 3=99)" -> {1: 99, 2: 99, 3: 99}

        Args:
            rules: Rules string (e.g., "(1 THRU 3=1) (4=2) (5 THRU 6=99)")

        Returns:
            Dictionary mapping source values to target values
        """
        mapping = {}

        # Extract all rule groups
        rule_groups = self.RULE_PATTERN.findall(rules)

        for rule_group in rule_groups:
            # Try range pattern first
            range_match = self.RANGE_PATTERN.match(rule_group.strip())
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                target = self._parse_value(range_match.group(3))

                # Map all values in range to target
                for value in range(start, end + 1):
                    mapping[value] = target
                continue

            # Try single value pattern
            single_match = self.SINGLE_PATTERN.match(rule_group.strip())
            if single_match:
                source = self._parse_value(single_match.group(1))
                target = self._parse_value(single_match.group(2))
                mapping[source] = target
                continue

            logger.warning(f"Could not parse rule: {rule_group}")

        return mapping

    def _parse_value(self, value_str: str) -> Union[int, float, str]:
        """
        Parse a value string to int, float, or str.

        Args:
            value_str: String representation of value

        Returns:
            Parsed value (int, float, or str)
        """
        value_str = value_str.strip()

        # Try integer
        try:
            return int(value_str)
        except ValueError:
            pass

        # Try float
        try:
            return float(value_str)
        except ValueError:
            pass

        # Return as string
        return value_str

    def _apply_compute(
        self,
        df: pd.DataFrame,
        compute_expr: str,
        default_column: str
    ) -> pd.Series:
        """
        Apply a COMPUTE transformation.

        Args:
            df: Input DataFrame
            compute_expr: COMPUTE expression (e.g., "COMPUTE new = a + b")
            default_column: Default column if target not specified

        Returns:
            Computed series
        """
        # Parse COMPUTE statement
        # Format: "COMPUTE target = expression"
        match = re.match(r'COMPUTE\s+(\w+)\s*=\s*(.+)', compute_expr, re.IGNORECASE)

        if match:
            target = match.group(1)
            expr = match.group(2)
        else:
            # Assume expression only, use default target
            target = default_column
            expr = compute_expr.replace('COMPUTE', '', 1).strip()

        # Evaluate expression safely
        try:
            # Create safe evaluation context
            context = {col: df[col] for col in df.columns if col.isidentifier()}
            context['np'] = np

            result = eval(expr, {"__builtins__": {}}, context)

            # Handle scalar results
            if not isinstance(result, pd.Series):
                result = pd.Series(result, index=df.index)

            return result
        except Exception as e:
            logger.error(f"Error evaluating compute expression '{expr}': {e}")
            return pd.Series(np.nan, index=df.index)

    def create_mapping_from_rules(self, rules: str) -> Dict[Any, Any]:
        """
        Create a value mapping dictionary from recoding rules.

        Useful for documentation and validation.

        Args:
            rules: Recoding rules string

        Returns:
            Dictionary mapping source values to target values

        Example:
            >>> engine = TransformationEngine()
            >>> mapping = engine.create_mapping_from_rules("(1 THRU 2=1) (3=2)")
            >>> print(mapping)
            {1: 1, 2: 1, 3: 2}
        """
        return self._parse_rules(rules)

    def validate_rules(self, rules: str) -> tuple[bool, Optional[str]]:
        """
        Validate that recoding rules are well-formed.

        Args:
            rules: Rules string to validate

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            >>> engine = TransformationEngine()
            >>> engine.validate_rules("(1 THRU 2=1) (3=2)")
            (True, None)
            >>> engine.validate_rules("invalid rules")
            (False, "Could not parse rule: invalid rules")
        """
        try:
            mapping = self._parse_rules(rules)
            if not mapping:
                return False, "No valid rules found"
            return True, None
        except Exception as e:
            return False, str(e)


def apply_recode(
    series: pd.Series,
    rules: str,
    target_column: Optional[str] = None
) -> pd.Series:
    """
    Convenience function to apply recoding rules.

    Args:
        series: Input series
        rules: Recoding rules (e.g., "(1 THRU 2=1) (3=2)")
        target_column: Optional target column name (for logging)

    Returns:
        Recoded series

    Example:
        >>> df = pd.DataFrame({"q1": [1, 2, 3, 4, 5]})
        >>> df["q1_recoded"] = apply_recode(df["q1"], "(1 THRU 2=1) (3=2) (4 THRU 5=3)")
    """
    engine = TransformationEngine()
    return engine._apply_recode(series, rules)


def parse_transformation_rules(rules: str) -> Dict[Any, Any]:
    """
    Parse transformation rules into a value mapping.

    Args:
        rules: Rules string

    Returns:
        Dictionary mapping source values to target values

    Example:
        >>> mapping = parse_transformation_rules("(1=2) (3 THRU 5=99)")
        >>> print(mapping)
        {1: 2, 3: 99, 4: 99, 5: 99}
    """
    engine = TransformationEngine()
    return engine._parse_rules(rules)
