"""
SPSS Analyzer Library

A reusable Python library for SPSS survey data analysis.

This library extracts the core analysis functionality from the DataChat
workflow, making it available as standalone functions that can
be called from:
- Python scripts
- CLI commands
- Skills (via Claude Code)
- Web applications (FastAPI, LangGraph)
- Other applications

Architecture:
    io/            - SPSS file I/O and metadata handling
    analysis/      - Core analysis (statistics, transformation, crosstabs)
    filtering/     - Statistical significance filtering
    reporting/     - Output generation (PowerPoint, HTML)
    specification/ - Table specification schema and validator
    pspp/          - [DEPRECATED] PSPP syntax (to be removed - use analysis/)
"""

__version__ = "0.3.0"

# Lazy imports to avoid circular dependencies
# Import modules directly when needed:
# from survey_analyzer.io import SPSSReader, MetadataTransformer
# from survey_analyzer.analysis import TransformationEngine, CrossTabGenerator
# from survey_analyzer.filtering import SignificanceFilter
# from survey_analyzer.specification import TableSpecificationValidator

__all__ = [
    # I/O
    "SPSSReader",
    "MetadataTransformer",
    # Analysis - Core Statistics
    "StatisticsCalculator",
    "chi_square_test",
    # Analysis - Transformation (replaces PSPP)
    "TransformationEngine",
    "TransformationRule",
    "apply_recode",
    "parse_transformation_rules",
    # Analysis - Cross-Tabulation (replaces PSPP)
    "CrossTabGenerator",
    "CrosstabResult",
    "CrosstabConfig",
    "generate_crosstab",
    "generate_crosstabs_with_stats",
    # Analysis - Indicators
    "IndicatorGenerator",
    "IndicatorConfig",
    "Indicator",
    "IndicatorType",
    "generate_indicators",
    # Filtering
    "SignificanceFilter",
    "FilterCriteria",
    "filter_significant",
    # Reporting
    "PowerPointGenerator",
    "ChartType",
    "create_powerpoint",
    "HTMLDashboardGenerator",
    "DashboardConfig",
    "create_dashboard",
    # Specification
    "TableSpecificationDocument",
    "TableSpecification",
    "OutputSettings",
    "Indicator",
    "RecodingRule",
    "TableSpecificationValidator",
    "validate_specification",
    "is_valid_specification",
    # PSPP [DEPRECATED - use TransformationEngine, CrossTabGenerator instead]
    "RecodingSyntaxGenerator",
    "CTablesSyntaxGenerator",
    "PSPPExecutor",
]

