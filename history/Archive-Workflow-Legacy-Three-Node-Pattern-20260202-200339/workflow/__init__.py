"""
LangGraph workflow for survey analysis.

This package implements a LangGraph-based workflow that processes PSPP survey data
through AI-driven recoding, indicator generation, and table specification.
"""

from .state import State, create_initial_state
from .graph import create_workflow

__all__ = ["State", "create_initial_state", "create_workflow"]
