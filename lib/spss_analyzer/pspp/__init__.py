"""
PSPP Module

PSPP syntax generation and execution.

Classes:
    RecodingSyntaxGenerator: Generate PSPP RECODE syntax
    CTablesSyntaxGenerator: Generate PSPP CTABLES syntax
    PSPPExecutor: Execute PSPP syntax files
"""

from .syntax import RecodingSyntaxGenerator, CTablesSyntaxGenerator
from .executor import PSPPExecutor

__all__ = ["RecodingSyntaxGenerator", "CTablesSyntaxGenerator", "PSPPExecutor"]
