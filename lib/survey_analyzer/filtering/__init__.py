"""
Filtering Module

Filter tables by statistical significance criteria.

Classes:
    SignificanceFilter: Filter tables based on p-value, Cramer's V, validity
"""

from .significance import SignificanceFilter, FilterCriteria

__all__ = ["SignificanceFilter", "FilterCriteria"]
