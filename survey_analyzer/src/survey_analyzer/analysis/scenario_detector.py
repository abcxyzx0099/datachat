"""
Scenario Detector

Detects the type of crosstab scenario based on indicator specifications.

Scenarios:
- cat_single: Single categorical variable
- cat_multi: Multiple binary variables (Multiple Choice)
- scalar_single: Single scalar variable
- scalar_multi: Multiple scalar variables (Rating Scale)
"""

import logging
from typing import Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class IndicatorSpec:
    """Indicator specification for crosstab generation."""
    indicator_code: str
    statistic_type: str  # "categorical" or "scalar"
    source_variables: list[str]
    question_type: str  # "Single Choice", "Multiple Choice", "Rating Scale", "Numeric Input"
    transformation_rules: str | None
    question_label: str = ""
    question_description: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IndicatorSpec":
        """Create IndicatorSpec from dictionary."""
        return cls(
            indicator_code=data.get("indicator_code", ""),
            statistic_type=data.get("statistic_type", "categorical"),
            source_variables=data.get("source_variables", []),
            question_type=data.get("question_type", ""),
            transformation_rules=data.get("transformation_rules"),
            question_label=data.get("question_label", ""),
            question_description=data.get("question_description", "")
        )


class ScenarioDetector:
    """Detect crosstab scenario based on indicator specifications."""

    # Scenario type constants
    CAT_SINGLE = "cat_single"
    CAT_MULTI = "cat_multi"
    SCALAR_SINGLE = "scalar_single"
    SCALAR_MULTI = "scalar_multi"

    @staticmethod
    def detect(indicator: IndicatorSpec) -> str:
        """
        Detect the scenario type for an indicator.

        Args:
            indicator: Indicator specification

        Returns:
            One of: "cat_single", "cat_multi", "scalar_single", "scalar_multi"

        Rules:
        - Categorical with 1 variable → cat_single
        - Categorical with multiple variables → cat_multi (Multiple Choice)
        - Scalar with 1 variable → scalar_single
        - Scalar with multiple variables → scalar_multi (Rating Scale)
        """
        n_vars = len(indicator.source_variables)
        stat_type = indicator.statistic_type.lower()

        if stat_type == "categorical":
            if n_vars > 1:
                return ScenarioDetector.CAT_MULTI
            return ScenarioDetector.CAT_SINGLE
        elif stat_type == "scalar":
            if n_vars > 1:
                return ScenarioDetector.SCALAR_MULTI
            return ScenarioDetector.SCALAR_SINGLE
        else:
            logger.warning(f"Unknown statistic_type: {stat_type}, defaulting to cat_single")
            return ScenarioDetector.CAT_SINGLE

    @staticmethod
    def detect_from_dict(data: Dict[str, Any]) -> str:
        """
        Detect scenario type from dictionary.

        Args:
            data: Indicator dictionary

        Returns:
            Scenario type string
        """
        indicator = IndicatorSpec.from_dict(data)
        return ScenarioDetector.detect(indicator)

    @staticmethod
    def has_total_row(row_scenario: str) -> bool:
        """
        Check if scenario has a total row.

        Args:
            row_scenario: Scenario type

        Returns:
            True if scenario should have a total row
        """
        # Only cat_single has full total row with percentages
        # cat_multi has total row with base N only
        # scalar scenarios have total row with base N only
        return row_scenario in [ScenarioDetector.CAT_SINGLE, ScenarioDetector.CAT_MULTI,
                               ScenarioDetector.SCALAR_SINGLE, ScenarioDetector.SCALAR_MULTI]

    @staticmethod
    def get_total_row_type(row_scenario: str) -> str:
        """
        Get the type of total row for a scenario.

        Args:
            row_scenario: Scenario type

        Returns:
            "full" - Total row with percentages (cat_single)
            "base_only" - Total row with base N only (all others)
            "none" - No total row
        """
        if row_scenario == ScenarioDetector.CAT_SINGLE:
            return "full"
        elif row_scenario in [ScenarioDetector.CAT_MULTI, ScenarioDetector.SCALAR_SINGLE,
                             ScenarioDetector.SCALAR_MULTI]:
            return "base_only"
        return "none"


def detect_scenario(indicator: IndicatorSpec | Dict[str, Any]) -> str:
    """
    Convenience function to detect scenario type.

    Args:
        indicator: IndicatorSpec or dictionary

    Returns:
        Scenario type string
    """
    if isinstance(indicator, dict):
        return ScenarioDetector.detect_from_dict(indicator)
    return ScenarioDetector.detect(indicator)
