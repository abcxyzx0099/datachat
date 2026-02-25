"""
Indicators Module

Generates table specification indicators using LLM (GLM-4.7) API.
Stage 3: Indicator Generation - creates indicators without is_row/is_column fields.
These fields are added later by Stage 4: analyzer-tablespec (LLM classification).

Classes:
    IndicatorGenerator: Generate indicators for a single question using LLM
    BatchProcessor: Process questions in batch with checkpointing
"""

from .generator import IndicatorGenerator
from .batch_processor import BatchProcessor

__all__ = ["IndicatorGenerator", "BatchProcessor"]
