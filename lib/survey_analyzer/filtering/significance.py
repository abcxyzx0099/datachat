"""
Significance Filter

Filter cross-tabulation tables based on statistical significance criteria.

Example:
    >>> filter_criteria = FilterCriteria(
    ...     significance_level=0.05,
    ...     min_cramers_v=0.1
    ... )
    >>> filter_obj = SignificanceFilter(criteria=filter_criteria)
    >>> result = filter_obj.filter_tables(tables_with_stats)
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class FilterCriteria:
    """
    Criteria for filtering tables by statistical significance.

    Attributes:
        significance_level: Maximum p-value for inclusion (default: 0.05)
        min_cramers_v: Minimum Cramer's V for inclusion (default: 0.1)
        min_cell_count: Minimum count in any cell (default: 10)
        require_valid: Whether to exclude invalid tests (default: True)
    """
    significance_level: float = 0.05
    min_cramers_v: float = 0.1
    min_cell_count: int = 10
    require_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "significance_level": self.significance_level,
            "min_cramers_v": self.min_cramers_v,
            "min_cell_count": self.min_cell_count,
            "require_valid": self.require_valid,
        }


@dataclass
class FilterResult:
    """
    Result of filtering a single table.

    Attributes:
        table_id: Table identifier
        include: Whether table passes all criteria
        p_value: P-value from statistical test
        cramers_v: Cramer's V effect size
        is_valid: Whether test was valid
        passes_significance: Passes p-value threshold
        passes_cramers_v: Passes Cramer's V threshold
        passes_validity: Passes validity check
        reason: Explanation of inclusion/exclusion decision
    """
    table_id: str
    include: bool
    p_value: float
    cramers_v: float
    is_valid: bool
    passes_significance: bool
    passes_cramers_v: bool
    passes_validity: bool
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "table_id": self.table_id,
            "include": self.include,
            "p_value": self.p_value,
            "cramers_v": self.cramers_v,
            "is_valid": self.is_valid,
            "passes_significance": self.passes_significance,
            "passes_cramers_v": self.passes_cramers_v,
            "passes_validity": self.passes_validity,
            "reason": self.reason,
        }


@dataclass
class FilterSummary:
    """
    Summary of filtering results.

    Attributes:
        total_tables: Total number of tables evaluated
        included: Number of tables that passed filters
        excluded: Number of tables that failed filters
        inclusion_rate: Percentage of tables included
        exclusion_reasons: Count of tables by exclusion reason
        criteria: Filter criteria used
        generated_at: Timestamp of filtering
    """
    total_tables: int
    included: int
    excluded: int
    inclusion_rate: float
    exclusion_reasons: Dict[str, int] = field(default_factory=dict)
    criteria: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_tables": self.total_tables,
            "included": self.included,
            "excluded": self.excluded,
            "inclusion_rate": self.inclusion_rate,
            "exclusion_reasons": self.exclusion_reasons,
            "criteria": self.criteria,
            "generated_at": self.generated_at,
        }


class SignificanceFilter:
    """
    Filter tables by statistical significance criteria.

    Applies three filters:
    1. Statistical significance: p < significance_level
    2. Effect size: Cramer's V >= min_cramers_v
    3. Validity: Test assumptions met

    Example:
        >>> filter_obj = SignificanceFilter()
        >>> filter_list = filter_obj.filter_tables(tables_with_stats)
        >>> print(f"Included: {filter_list.summary.included}/{filter_list.summary.total_tables}")
    """

    def __init__(
        self,
        criteria: Optional[FilterCriteria] = None,
    ):
        """
        Initialize the filter.

        Args:
            criteria: Filter criteria (uses defaults if None)
        """
        self.criteria = criteria or FilterCriteria()

    def filter_tables(
        self,
        tables_with_stats: List[Dict[str, Any]],
    ) -> "FilterList":
        """
        Filter tables based on significance criteria.

        Args:
            tables_with_stats: List of table dictionaries, each containing:
                - table_name: str
                - p_value: float
                - cramers_v: float
                - is_valid: bool
                - (optional) error: str

        Returns:
            FilterList with filter results and summary

        Example:
            >>> filter_obj = SignificanceFilter()
            >>> filter_list = filter_obj.filter_tables(tables)
            >>> for table in filter_list.included_tables:
            ...     print(table["table_name"])
        """
        filter_results = []
        inclusion_reasons = {
            "not_significant": 0,
            "effect_size_too_small": 0,
            "invalid_table": 0,
            "multiple_failures": 0,
        }

        for table_stats in tables_with_stats:
            result = self._evaluate_table(table_stats)
            filter_results.append(result.to_dict())

            # Track exclusion reasons
            if not result.include:
                if "not statistically significant" in result.reason.lower():
                    inclusion_reasons["not_significant"] += 1
                elif "effect size" in result.reason.lower():
                    inclusion_reasons["effect_size_too_small"] += 1
                elif "invalid" in result.reason.lower():
                    inclusion_reasons["invalid_table"] += 1
                else:
                    inclusion_reasons["multiple_failures"] += 1

        # Build summary
        total = len(tables_with_stats)
        included = sum(1 for r in filter_results if r.get("include", False))
        excluded = total - included

        summary = FilterSummary(
            total_tables=total,
            included=included,
            excluded=excluded,
            inclusion_rate=round(included / total * 100, 2) if total > 0 else 0,
            exclusion_reasons=inclusion_reasons,
            criteria=self.criteria.to_dict(),
        )

        return FilterList(
            filters=filter_results,
            summary=summary,
        )

    def _evaluate_table(
        self,
        table_stats: Dict[str, Any],
    ) -> FilterResult:
        """
        Evaluate a single table against filter criteria.

        Args:
            table_stats: Table statistics dictionary

        Returns:
            FilterResult with pass/fail status
        """
        table_name = table_stats.get("table_name", "unknown")

        # Get values with defaults (use lenient defaults for invalid/missing data)
        p_value = table_stats.get("p_value", 1.0)
        cramers_v = table_stats.get("cramers_v", 0.0)
        is_valid = table_stats.get("is_valid", True)

        # Handle None values - treat as failing thresholds
        if p_value is None:
            p_value = 1.0  # Not significant
        if cramers_v is None:
            cramers_v = 0.0  # No effect size

        # Check each criterion
        passes_significance = p_value < self.criteria.significance_level
        passes_cramers_v = cramers_v >= self.criteria.min_cramers_v
        passes_validity = is_valid if not self.criteria.require_valid else True

        if self.criteria.require_valid:
            passes_validity = is_valid

        # Determine overall inclusion
        include = passes_significance and passes_cramers_v and passes_validity

        # Build reason
        if include:
            reason = "Passed all filters"
        else:
            failures = []

            if not passes_validity:
                error = table_stats.get("error", "")
                failures.append(f"Invalid table ({error})" if error else "Invalid table")
            elif not passes_significance:
                failures.append(
                    f"Not statistically significant "
                    f"(p={p_value:.4f} >= {self.criteria.significance_level})"
                )
            elif not passes_cramers_v:
                failures.append(
                    f"Effect size too small "
                    f"(Cramer's V={cramers_v:.4f} < {self.criteria.min_cramers_v})"
                )

            if len(failures) > 1:
                reason = "; ".join(failures[:-1]) + ", and " + failures[-1]
            else:
                reason = failures[0] if failures else "Unknown reason"

        return FilterResult(
            table_id=table_name,
            include=include,
            p_value=p_value,
            cramers_v=cramers_v,
            is_valid=is_valid,
            passes_significance=passes_significance,
            passes_cramers_v=passes_cramers_v,
            passes_validity=passes_validity,
            reason=reason,
        )

    def apply_filter(
        self,
        tables: List[Dict[str, Any]],
        filter_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Apply filter results to table list, returning only included tables.

        Args:
            tables: Original list of tables
            filter_results: Filter results from filter_tables()

        Returns:
            Filtered list containing only included tables
        """
        included_ids = {
            r["table_id"] for r in filter_results if r.get("include", False)
        }

        return [
            t for t in tables
            if t.get("table_name", "") in included_ids
        ]


@dataclass
class FilterList:
    """
    Complete filter results with summary.

    Attributes:
        filters: List of filter results for each table
        summary: Summary statistics
    """
    filters: List[Dict[str, Any]]
    summary: FilterSummary

    @property
    def included_tables(self) -> List[str]:
        """Get list of included table IDs."""
        return [
            f["table_id"] for f in self.filters
            if f.get("include", False)
        ]

    @property
    def excluded_tables(self) -> List[str]:
        """Get list of excluded table IDs."""
        return [
            f["table_id"] for f in self.filters
            if not f.get("include", False)
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "filters": self.filters,
            "summary": self.summary.to_dict(),
        }


def filter_significant(
    tables_with_stats: List[Dict[str, Any]],
    significance_level: float = 0.05,
    min_cramers_v: float = 0.1,
) -> FilterList:
    """
    Convenience function to filter tables by significance.

    Args:
        tables_with_stats: List of tables with statistics
        significance_level: Maximum p-value (default: 0.05)
        min_cramers_v: Minimum Cramer's V (default: 0.1)

    Returns:
        FilterList with results

    Example:
        >>> result = filter_significant(tables, significance_level=0.05)
        >>> print(f"Included: {result.summary.included}")
    """
    criteria = FilterCriteria(
        significance_level=significance_level,
        min_cramers_v=min_cramers_v,
    )
    filter_obj = SignificanceFilter(criteria)
    return filter_obj.filter_tables(tables_with_stats)
