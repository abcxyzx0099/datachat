"""
Indicators Generator

Generate indicator groupings from SPSS metadata for analysis.

Indicators are groups of related variables that measure a common concept.
For example, multiple satisfaction questions can be combined into a
"satisfaction index" indicator.

Example:
    >>> gen = IndicatorGenerator()
    >>> indicators = gen.generate_indicators(metadata, config)
    >>> for indicator in indicators:
    ...     print(f"{indicator['name']}: {indicator['variables']}")
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class IndicatorType(Enum):
    """Types of indicator generation strategies."""
    KEYWORD = "keyword"           # Group by variable name patterns
    LABEL = "label"               # Group by label text similarity
    SEMANTIC = "semantic"         # LLM-based semantic grouping
    MANUAL = "manual"             # Predefined manual groupings


@dataclass
class IndicatorConfig:
    """
    Configuration for indicator generation.

    Attributes:
        type: Strategy type (keyword, label, semantic, manual)
        keywords: List of keyword patterns for grouping
        min_variables: Minimum variables per indicator (default: 2)
        max_variables: Maximum variables per indicator (default: 10)
        prefix: Variable name prefix to match (e.g., "sat_", "q")
    """
    type: IndicatorType = IndicatorType.KEYWORD
    keywords: List[str] = field(default_factory=list)
    min_variables: int = 2
    max_variables: int = 10
    prefix: Optional[str] = None
    manual_groupings: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value,
            "keywords": self.keywords,
            "min_variables": self.min_variables,
            "max_variables": self.max_variables,
            "prefix": self.prefix,
            "manual_groupings": self.manual_groupings,
        }


@dataclass
class Indicator:
    """
    Represents an indicator grouping.

    Attributes:
        name: Indicator name
        description: Human-readable description
        variables: List of variable names in the indicator
        variable_count: Number of variables
        label: Computed label from variable labels
    """
    name: str
    description: str
    variables: List[str]
    variable_count: int
    label: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "variables": self.variables,
            "variable_count": self.variable_count,
            "label": self.label,
        }


class IndicatorGenerator:
    """
    Generate indicator groupings from SPSS metadata.

    Supports multiple strategies:
    - keyword: Group variables by name patterns (e.g., "sat_1", "sat_2" → "satisfaction")
    - label: Group by label text similarity
    - semantic: LLM-based semantic grouping
    - manual: Use predefined groupings

    Example:
        >>> gen = IndicatorGenerator()
        >>> config = IndicatorConfig(
        ...     type=IndicatorType.KEYWORD,
        ...     prefix="sat_"
        ... )
        >>> indicators = gen.generate(metadata, config)
    """

    # Common keyword patterns and their meanings
    KEYWORD_PATTERNS = {
        "sat": "satisfaction",
        "satisf": "satisfaction",
        "q": "question",
        "import": "importance",
        "like": "liking",
        "aware": "awareness",
        "prefer": "preference",
        "brand": "brand",
        "qual": "quality",
        "val": "value",
        "need": "needs",
        "expect": "expectations",
        "loyal": "loyalty",
        "recommend": "recommendation",
        "purchase": "purchase",
        "usage": "usage",
        "freq": "frequency",
    }

    def __init__(
        self,
        metadata_lookup: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """
        Initialize the generator.

        Args:
            metadata_lookup: Optional dict mapping variable names to metadata
        """
        self.metadata_lookup = metadata_lookup or {}

    def generate(
        self,
        metadata: Dict[str, Any],
        config: Optional[IndicatorConfig] = None,
    ) -> List[Indicator]:
        """
        Generate indicators from SPSS metadata.

        Args:
            metadata: Variable-centered metadata dictionary
            config: Generation configuration (uses defaults if None)

        Returns:
            List of Indicator objects

        Example:
            >>> gen = IndicatorGenerator()
            >>> indicators = gen.generate(metadata)
            >>> for ind in indicators:
            ...     print(f"{ind.name}: {ind.variable_count} variables")
        """
        config = config or IndicatorConfig()

        if config.type == IndicatorType.KEYWORD:
            return self._generate_by_keywords(metadata, config)
        elif config.type == IndicatorType.LABEL:
            return self._generate_by_labels(metadata, config)
        elif config.type == IndicatorType.MANUAL:
            return self._generate_manual(config)
        elif config.type == IndicatorType.SEMANTIC:
            return self._generate_semantic(metadata, config)
        else:
            logger.warning(f"Unknown indicator type: {config.type}")
            return []

    def _generate_by_keywords(
        self,
        metadata: Dict[str, Any],
        config: IndicatorConfig,
    ) -> List[Indicator]:
        """
        Generate indicators by grouping variables with similar name patterns.

        Example:
            sat_1, sat_2, sat_3 → "satisfaction" indicator
            q1a, q1b, q1c → "q1" indicator
        """
        indicators = []

        # Group variables by prefix pattern
        if config.prefix:
            variables = [
                v for v in metadata.keys()
                if v.startswith(config.prefix)
            ]
            if variables:
                indicators.append(self._create_indicator_from_variables(
                    variables,
                    config.prefix,
                    metadata
                ))
            return indicators

        # Auto-detect patterns
        groups = self._detect_variable_groups(metadata)

        # Create indicators from groups
        for group_name, variables in groups.items():
            if config.min_variables <= len(variables) <= config.max_variables:
                indicators.append(self._create_indicator_from_variables(
                    variables,
                    group_name,
                    metadata
                ))

        logger.info(f"Generated {len(indicators)} keyword-based indicators")
        return indicators

    def _detect_variable_groups(
        self,
        metadata: Dict[str, Any],
    ) -> Dict[str, List[str]]:
        """
        Detect groups of variables with similar naming patterns.

        Looks for patterns like:
        - sat_1, sat_2, sat_3 → "sat"
        - q1a, q1b, q1c → "q1"
        - brand_a, brand_b, brand_c → "brand"
        """
        groups = {}

        for var_name in metadata.keys():
            # Extract base name (remove numeric suffixes)
            base = self._extract_base_name(var_name)

            if base not in groups:
                groups[base] = []
            groups[base].append(var_name)

        # Filter out single-variable groups
        return {
            name: vars for name, vars in groups.items()
            if len(vars) >= 2
        }

    def _extract_base_name(self, var_name: str) -> str:
        """
        Extract the base name from a variable name.

        Examples:
            sat_1 → sat
            q1a → q1
            brand_pref → brand
        """
        import re

        # Remove trailing numbers
        base = re.sub(r'_?\d+$', '', var_name)

        # Remove single trailing letters (a, b, c)
        base = re.sub(r'_?[a-z]$', '', base)

        # Remove common suffixes
        for suffix in ['_val', '_score', '_ind', '_idx']:
            if base.endswith(suffix):
                base = base[:-len(suffix)]
                break

        return base

    def _create_indicator_from_variables(
        self,
        variables: List[str],
        base_name: str,
        metadata: Dict[str, Any],
    ) -> Indicator:
        """Create an Indicator from a list of variables."""
        # Get label from first variable
        label = ""
        if variables:
            first_var = variables[0]
            if first_var in metadata:
                label = metadata[first_var].get("label", first_var)

        # Expand base name to full concept name
        concept = self._expand_concept_name(base_name)

        return Indicator(
            name=f"{concept}_indicator",
            description=f"Combined indicator from {len(variables)} variables",
            variables=variables,
            variable_count=len(variables),
            label=label,
        )

    def _expand_concept_name(self, base: str) -> str:
        """Expand abbreviated base name to full concept."""
        base_lower = base.lower()

        for pattern, concept in self.KEYWORD_PATTERNS.items():
            if pattern in base_lower:
                return concept

        return base

    def _generate_by_labels(
        self,
        metadata: Dict[str, Any],
        config: IndicatorConfig,
    ) -> List[Indicator]:
        """
        Generate indicators by grouping variables with similar label text.

        Uses text similarity to find variables measuring the same concept.
        """
        indicators = []

        # Group by label keywords
        label_groups: Dict[str, List[str]] = {}

        for var_name, var_info in metadata.items():
            label = var_info.get("label", "").lower()

            # Check for keywords in label
            for keyword in config.keywords or self.KEYWORD_PATTERNS.keys():
                if keyword in label:
                    if keyword not in label_groups:
                        label_groups[keyword] = []
                    label_groups[keyword].append(var_name)
                    break

        # Create indicators
        for keyword, variables in label_groups.items():
            if config.min_variables <= len(variables) <= config.max_variables:
                concept = self.KEYWORD_PATTERNS.get(keyword, keyword)
                indicators.append(Indicator(
                    name=f"{concept}_indicator",
                    description=f"Variables related to {concept}",
                    variables=variables,
                    variable_count=len(variables),
                ))

        logger.info(f"Generated {len(indicators)} label-based indicators")
        return indicators

    def _generate_manual(
        self,
        config: IndicatorConfig,
    ) -> List[Indicator]:
        """
        Generate indicators from predefined manual groupings.

        Example:
            config.manual_groupings = {
                "satisfaction": ["sat_1", "sat_2", "sat_3"],
                "loyalty": ["rec_1", "rep_1", "rep_2"]
            }
        """
        indicators = []

        for name, variables in config.manual_groupings.items():
            indicators.append(Indicator(
                name=f"{name}_indicator",
                description=f"Manual grouping: {name}",
                variables=variables,
                variable_count=len(variables),
            ))

        logger.info(f"Generated {len(indicators)} manual indicators")
        return indicators

    def _generate_semantic(
        self,
        metadata: Dict[str, Any],
        config: IndicatorConfig,
    ) -> List[Indicator]:
        """
        Generate indicators using semantic analysis.

        This method uses text embeddings to group semantically similar
        variables. Requires sentence-transformers or similar.

        Note: This is a placeholder for LLM-based grouping.
        """
        # Placeholder for semantic grouping
        # In production, this would:
        # 1. Get embeddings for variable labels
        # 2. Cluster by similarity
        # 3. Return clusters as indicators

        logger.warning("Semantic grouping not implemented, falling back to keyword")
        return self._generate_by_keywords(metadata, config)

    def validate_indicator(
        self,
        indicator: Indicator,
        metadata: Dict[str, Any],
    ) -> tuple[bool, Optional[str]]:
        """
        Validate that an indicator meets requirements.

        Args:
            indicator: Indicator to validate
            metadata: Variable metadata for lookup

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check all variables exist in metadata
        for var in indicator.variables:
            if var not in metadata:
                return False, f"Variable '{var}' not found in metadata"

        # Check minimum variables
        if indicator.variable_count < 2:
            return False, f"Indicator has only {indicator.variable_count} variable(s)"

        return True, None

    def get_indicator_variables(
        self,
        metadata: Dict[str, Any],
        indicator_names: List[str],
    ) -> Dict[str, List[str]]:
        """
        Get the variable lists for specified indicators.

        Args:
            metadata: Variable metadata
            indicator_names: List of indicator names to extract

        Returns:
            Dict mapping indicator names to variable lists
        """
        config = IndicatorConfig(type=IndicatorType.KEYWORD)
        all_indicators = self.generate(metadata, config)

        result = {}
        for ind in all_indicators:
            if ind.name in indicator_names:
                result[ind.name] = ind.variables

        return result


def generate_indicators(
    metadata: Dict[str, Any],
    strategy: str = "keyword",
    prefix: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Convenience function to generate indicators.

    Args:
        metadata: Variable-centered metadata
        strategy: Generation strategy (keyword, label, manual, semantic)
        prefix: Variable name prefix for keyword grouping

    Returns:
        List of indicator dictionaries

    Example:
        >>> indicators = generate_indicators(
        ...     metadata,
        ...     strategy="keyword",
        ...     prefix="sat_"
        ... )
    """
    gen = IndicatorGenerator()

    try:
        ind_type = IndicatorType(strategy)
    except ValueError:
        ind_type = IndicatorType.KEYWORD

    config = IndicatorConfig(type=ind_type, prefix=prefix)
    indicators = gen.generate(metadata, config)

    return [ind.to_dict() for ind in indicators]
