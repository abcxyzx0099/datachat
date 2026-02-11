"""
DataChat SPSS Analyzer - Agent Package

This package contains the LangGraph-based workflow implementation for analyzing
SPSS survey data using PSPP and LLM-powered artifact generation.

Main Components:
- state.py: TypedDict state definitions for workflow phases
- config.py: Default configuration constants
- edges.py: Conditional routing logic for the state graph
- graph.py: LangGraph construction and execution
- nodes/: Phase-based node implementations
- utils/: Utility modules (PSPP wrapper, file I/O, statistics)
- validation/: Artifact validation functions
- llm/: LLM client initialization and prompt templates
"""

__version__ = "1.0.0"

__all__ = [
    "state",
    "config",
    "edges",
    "graph",
]
