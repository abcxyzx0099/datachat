"""
Crosstab Processors

Specialized processors for each crosstab scenario.
"""

from .categorical_single import CategoricalSingleProcessor
from .categorical_multi import CategoricalMultiProcessor
from .scalar_single import ScalarSingleProcessor
from .scalar_multi import ScalarMultiProcessor

__all__ = [
    "CategoricalSingleProcessor",
    "CategoricalMultiProcessor",
    "ScalarSingleProcessor",
    "ScalarMultiProcessor",
]
