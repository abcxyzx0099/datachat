"""
Business Rules Constants

This module defines the business rule constants used across the survey analyzer package.
These values are based on market research best practices and can be adjusted as needed.

Environment Variables:
    Values can be overridden via environment variables or .env file.
    See .env.example for available options.

References:
    - docs/application-design/business-rules.md
"""

import os
from pathlib import Path
from typing import Optional

# Try to load .env file automatically
# This is optional - if dotenv is not available or .env doesn't exist, continue with defaults
try:
    from dotenv import load_dotenv

    # Load from multiple locations in order (later files override earlier ones):
    # 1. Project root (current directory) - for project-specific config
    # 2. Library root - for library defaults
    env_paths = [
        Path.cwd() / '.env',                                    # Project root
        Path(__file__).parent.parent.parent / '.env',         # Library root (3 levels up)
    ]

    # Load all existing .env files (library overrides project)
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path, verbose=False, override=True)

    # If no .env files found, try default search
    if not any(p.exists() for p in env_paths):
        load_dotenv(verbose=False)
except ImportError:
    # python-dotenv not installed - use environment variables as-is
    pass


def _get_int_env(name: str, default: int) -> int:
    """Get integer value from environment variable with fallback."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_float_env(name: str, default: float) -> float:
    """Get float value from environment variable with fallback."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_bool_env(name: str, default: bool) -> bool:
    """Get boolean value from environment variable with fallback."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')


def _get_str_env(name: str, default: Optional[str]) -> Optional[str]:
    """Get string value from environment variable with fallback."""
    value = os.getenv(name)
    if value is None or value == '':
        return default
    return value


# ============================================================================
# Filtering Rules
# ============================================================================

# Maximum number of distinct value categories for a variable to be included in analysis
# Variables with more categories are considered "high cardinality" and are excluded
# Env: SURVEY_ANALYZER_MAX_CATEGORIES
DEFAULT_MAX_CATEGORIES = _get_int_env('SURVEY_ANALYZER_MAX_CATEGORIES', 30)

# Significance level for statistical tests (p-value threshold)
# Env: SURVEY_ANALYZER_SIGNIFICANCE_LEVEL
DEFAULT_SIGNIFICANCE_LEVEL = _get_float_env('SURVEY_ANALYZER_SIGNIFICANCE_LEVEL', 0.05)

# Minimum Cramer's V effect size for inclusion
# Env: SURVEY_ANALYZER_MIN_CRAMERS_V
DEFAULT_MIN_CRAMERS_V = _get_float_env('SURVEY_ANALYZER_MIN_CRAMERS_V', 0.1)

# ============================================================================
# Variable Type Detection
# ============================================================================

# Minimum number of categories to be considered multi-categorical
MIN_CATEGORIES_FOR_MULTI = 2

# Maximum number of categories for binary variable classification
MAX_CATEGORIES_FOR_BINARY = 2

# ============================================================================
# Cross-Tabulation Limits
# ============================================================================

# Recommended maximum number of column indicators (banner variables)
# for usable cross-tabulation tables
# Env: SURVEY_ANALYZER_MAX_COLUMN_INDICATORS
MAX_RECOMMENDED_COLUMN_INDICATORS = _get_int_env('SURVEY_ANALYZER_MAX_COLUMN_INDICATORS', 30)

# Minimum number of column indicators
# Env: SURVEY_ANALYZER_MIN_COLUMN_INDICATORS
MIN_RECOMMENDED_COLUMN_INDICATORS = _get_int_env('SURVEY_ANALYZER_MIN_COLUMN_INDICATORS', 10)

# ============================================================================
# File Encoding
# ============================================================================

# Default encoding for reading SPSS files
# None means auto-detect from the SPSS file itself
# Env: SURVEY_ANALYZER_DEFAULT_ENCODING
DEFAULT_SPSS_ENCODING = _get_str_env('SURVEY_ANALYZER_DEFAULT_ENCODING', None)

# ============================================================================
# JSON Output Settings
# ============================================================================

# Whether to use ASCII encoding for JSON output
# false = Preserve Unicode characters (Chinese, etc.)
# true = Use escape sequences (\uXXXX)
# Env: SURVEY_ANALYZER_JSON_ENSURE_ASCII
JSON_ENSURE_ASCII = _get_bool_env('SURVEY_ANALYZER_JSON_ENSURE_ASCII', False)


def get_config_summary() -> dict:
    """
    Get a summary of current configuration values.

    Returns:
        Dictionary with all configuration values
    """
    return {
        'max_categories': DEFAULT_MAX_CATEGORIES,
        'significance_level': DEFAULT_SIGNIFICANCE_LEVEL,
        'min_cramers_v': DEFAULT_MIN_CRAMERS_V,
        'max_column_indicators': MAX_RECOMMENDED_COLUMN_INDICATORS,
        'min_column_indicators': MIN_RECOMMENDED_COLUMN_INDICATORS,
        'default_encoding': DEFAULT_SPSS_ENCODING,
        'json_ensure_ascii': JSON_ENSURE_ASCII,
    }
