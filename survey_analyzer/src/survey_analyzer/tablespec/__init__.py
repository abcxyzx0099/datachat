"""
Table Specification Module (Unified)

Handles the unified table specification workflow.
Single source of truth - table_specification.jsonc updated by all stages.

This module provides:
- UnifiedTableSpec: Complete unified spec management
- TableSpec: Stage 4 classification (is_row/is_column)

Stages:
    Stage 2: QuestionExtractor adds questions
    Stage 3: BatchProcessor adds indicators to questions
    Stage 4: TableSpec classifies indicators (is_row/is_column)
"""

from .unified import UnifiedTableSpec
from .tablespec import TableSpec

__all__ = ["UnifiedTableSpec", "TableSpec"]
