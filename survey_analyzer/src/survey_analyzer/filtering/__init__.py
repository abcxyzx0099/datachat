"""
Filtering Module

Filter tables by statistical significance criteria.

Classes:
    SignificanceFilter: Filter tables based on p-value, Cramer's V, validity
    FilterCriteria: Criteria for filtering
    filter_significant: Convenience function to filter tables by significance
"""
from .significance import SignificanceFilter, FilterCriteria, filter_significant

__all__ = [
    "SignificanceFilter",
    "FilterCriteria",
    "filter_significant",
]