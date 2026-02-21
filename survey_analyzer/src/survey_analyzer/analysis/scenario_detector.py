"""
Scenario Detector

Detects the type of crosstab scenario based on indicator specifications.

Scenarios:
- cat_single: Single categorical variable
- cat_multi: Multiple binary variables (Multiple Choice)
- scalar_single: Single scalar variable
- scalar_multi: Multiple scalar variables (Rating Scale)

Uses the new schema structure from survey_analyzer.specification.schema.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ScenarioDetector:
    """Detect crosstab scenario based on indicator specifications."""

    # Scenario type constants
    CAT_SINGLE = "cat_single"
    CAT_MULTI = "cat_multi"
    SCALAR_SINGLE = "scalar_single"
    SCALAR_MULTI = "scalar_multi"

    @staticmethod
    def detect(indicator: Dict[str, Any]) -> str:
        """
        Detect the scenario type for an indicator.

        Args:
            indicator: Indicator specification dictionary with new schema structure

        Returns:
            One of: "cat_single", "cat_multi", "scalar_single", "scalar_multi"

        Rules:
        - Categorical with 1 variable → cat_single
        - Categorical with multiple variables → cat_multi (Multiple Choice)
        - Scalar with 1 variable → scalar_single
        - Scalar with multiple variables → scalar_multi (Rating Scale)
        """
        # Get tabulation_statistics.type
        tab_stats = indicator.get("tabulation_statistics", {})
        stat_type = tab_stats.get("type", "categorical").lower()

        # Count base_variables
        base_vars = indicator.get("base_variables", [])
        n_vars = len(base_vars)

        if stat_type == "categorical":
            if n_vars > 1:
                return ScenarioDetector.CAT_MULTI
            return ScenarioDetector.CAT_SINGLE
        elif stat_type == "scalar":
            if n_vars > 1:
                return ScenarioDetector.SCALAR_MULTI
            return ScenarioDetector.SCALAR_SINGLE
        else:
            logger.warning(f"Unknown tabulation_statistics.type: {stat_type}, defaulting to cat_single")
            return ScenarioDetector.CAT_SINGLE

    @staticmethod
    def detect_from_dict(data: Dict[str, Any]) -> str:
        """
        Detect scenario type from dictionary.

        Args:
            data: Indicator dictionary with new schema structure

        Returns:
            Scenario type string
        """
        return ScenarioDetector.detect(data)

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


def detect_scenario(indicator: Dict[str, Any]) -> str:
    """
    Convenience function to detect scenario type.

    Args:
        indicator: Indicator dictionary with new schema structure

    Returns:
        Scenario type string
    """
    return ScenarioDetector.detect(indicator)
