"""
Semantic CLI commands for SPSS survey analysis.

This module provides stage-agnostic, semantic operations for:
- Data reading and filtering
- Specification generation
- Indicator computation
- Cross-table calculation
- Statistical analysis
- Report generation

All functions are standalone and reusable. No "stage" concept at library level.
"""

from .data import (
    read_metadata,
    filter_variables,
    transform_metadata,
    save_metadata
)

from .specification import (
    generate_tables,
    generate_indicators,
    save_specification
)

from .analysis import (
    compute_indicators,
    generate_crosstabs,
    apply_recodings
)

from .statistics import (
    calculate_chi_square,
    filter_significant,
    save_statistics
)

from .reporting import (
    create_powerpoint,
    create_html_dashboard,
    save_reports
)

from . import all as workflow

__all__ = [
    # Data operations
    "read_metadata",
    "filter_variables",
    "transform_metadata",
    "save_metadata",
    # Specification operations
    "generate_tables",
    "generate_indicators",
    "save_specification",
    # Analysis operations
    "compute_indicators",
    "generate_crosstabs",
    "apply_recodings",
    # Statistics operations
    "calculate_chi_square",
    "filter_significant",
    "save_statistics",
    # Reporting operations
    "create_powerpoint",
    "create_html_dashboard",
    "save_reports",
    # Complete workflow
    "run_workflow",
]
