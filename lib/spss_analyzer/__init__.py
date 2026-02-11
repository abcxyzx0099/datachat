"""
SPSS Analyzer Library

A reusable Python library for SPSS survey data analysis.

This library extracts the core analysis functionality from the DataChat
workflow, making it available as standalone functions that can
be called from:
- Python scripts
- CLI commands
- Skills (via Claude Code)
- Other applications

Architecture:
    io/            - SPSS file I/O and metadata handling
    analysis/      - Core analysis functions (statistics, indicators)
    filtering/     - Statistical significance filtering
    reporting/     - Output generation (PowerPoint, HTML)
    pspp/          - PSPP syntax generation and execution
    specification/  - Table specification schema and validator
"""

__version__ = "0.2.0"

# Lazy imports to avoid circular dependencies
# Import modules directly when needed:
# from spss_analyzer.io import SPSSReader, MetadataTransformer
# from spss_analyzer.analysis import StatisticsCalculator
# from spss_analyzer.filtering import SignificanceFilter
# from spss_analyzer.specification import TableSpecificationValidator

__all__ = [
    # I/O
    "SPSSReader",
    "MetadataTransformer",
    # Analysis
    "StatisticsCalculator",
    "IndicatorGenerator",
    # Filtering
    "SignificanceFilter",
    # PSPP
    "RecodingSyntaxGenerator",
    "CTablesSyntaxGenerator",
    "PSPPExecutor",
    # Reporting
    "PowerPointGenerator",
    "HTMLDashboardGenerator",
    # Specification (NEW)
    "TableSpecificationDocument",
    "TableSpecification",
    "Indicator",
    "RecodingRule",
    "TableSpecificationValidator",
    "validate_specification",
    "is_valid_specification",
]

