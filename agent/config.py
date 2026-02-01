"""
Configuration Constants for Survey Analysis Workflow

This module defines the DEFAULT_CONFIG dictionary containing all configuration
options for the survey analysis workflow. Configuration values can be overridden
using environment variables.

Environment Variable Prefix: SURVEY_

Example:
    export SURVEY_LLM_PROVIDER=DEEPSEEK
    export SURVEY_LLM_TEMPERATURE=0.2
"""

from typing import Dict, Any

# =============================================================================
# DEFAULT_CONFIG
# =============================================================================

DEFAULT_CONFIG: Dict[str, Any] = {
    # ============================================
    # LLM Configuration
    # ============================================
    # LLM Provider Selection: KIMI | DEEPSEEK | ZHIPU
    "llm_provider": "ZHIPU",

    # Provider-specific model (e.g., glm-4.7 for Zhipu)
    "model": "glm-4.7",

    # LLM parameters
    "temperature": 0.1,
    "max_tokens": 4000,

    # ============================================
    # Three-Node Pattern Configuration
    # ============================================
    # Maximum validation retry iterations (self-correction)
    "max_self_correction_iterations": 3,

    # Enable human-in-the-loop review nodes
    "enable_human_review": True,

    # Auto-approval flags (override enable_human_review when True)
    "auto_approve_recoding": False,
    "auto_approve_indicators": False,
    "auto_approve_table_specs": False,

    # Review output format: markdown, html, json
    "review_output_format": "markdown",

    # ============================================
    # Step 3: Preliminary Filtering
    # ============================================
    # Maximum distinct values before filtering as high-cardinality
    "cardinality_threshold": 30,

    # Filter out binary variables (exactly 2 distinct values)
    "filter_binary": True,

    # Filter out "other" text fields (open-ended feedback)
    "filter_other_text": True,

    # ============================================
    # PSPP Configuration
    # ============================================
    # Path to PSPP executable
    "pspp_path": "pspp",

    # PSPP output log file path
    "pspp_output_path": "output/pspp_logs.txt",

    # ============================================
    # File Paths
    # ============================================
    # Output directory (relative to project root)
    "output_dir": "output",

    # Temporary files directory (relative to project root)
    "temp_dir": "temp",

    # Create timestamped subdirectories in output/
    "create_timestamp_dir": True,

    # ============================================
    # Statistical Analysis
    # ============================================
    # p-value threshold for statistical significance
    "significance_level": 0.05,

    # Minimum effect size (Cramer's V) for filtering
    "min_cramers_v": 0.1,

    # Minimum expected cell count for chi-square validity
    "min_cell_count": 10,

    # Statistical test type: chi_square, fisher_exact
    "test_type": "chi_square",

    # ============================================
    # Presentation
    # ============================================
    # PowerPoint template path (None = use default)
    "powerpoint_template": None,

    # Chart style: modern, corporate, minimal
    "chart_style": "modern",

    # Include charts in PowerPoint export
    "include_charts": True,

    # HTML dashboard theme
    "html_theme": "default",

    # Chart library: echarts, plotly, chartjs
    "chart_library": "echarts",
}


# =============================================================================
# LLM Provider Configuration
# =============================================================================

# Provider-specific default configurations
LLM_PROVIDER_CONFIGS = {
    "KIMI": {
        "base_url": "https://api.moonshot.cn/v1",
        "model": "kimi-k2-turbo-preview",
        "api_key_env": "KIMI_API_KEY",
    },
    "DEEPSEEK": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY",
    },
    "ZHIPU": {
        "base_url": "https://open.bigmodel.cn/api/coding/paas/v4",
        "model": "glm-4.7",
        "api_key_env": "ZHIPU_API_KEY",
    },
}


# =============================================================================
# Configuration Helper Functions
# =============================================================================

def load_config(env_file: str = ".env") -> Dict[str, Any]:
    """
    Load configuration from .env file and merge with DEFAULT_CONFIG.

    This function:
    1. Loads environment variables from .env file using python-dotenv
    2. Validates LLM_PROVIDER is set and valid
    3. Validates selected provider's API key is set
    4. Merges environment overrides with DEFAULT_CONFIG
    5. Returns complete configuration dict

    Args:
        env_file: Path to .env file (default: ".env")

    Returns:
        Configuration dictionary with all settings loaded

    Raises:
        ValueError: If LLM_PROVIDER is invalid or API key is missing
        FileNotFoundError: If .env file doesn't exist (only if file check requested)

    Example:
        >>> config = load_config()
        >>> print(config["llm_provider"])
        'ZHIPU'
        >>> print(get_api_key(config))
        'your-zhipu-api-key-here'
    """
    import os
    from pathlib import Path
    from dotenv import load_dotenv

    # Load .env file if it exists
    env_path = Path(env_file)
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # .env is optional for development/testing
        # Environment variables may be set via other means
        pass

    # Get LLM provider from environment (with SURVEY_ prefix for backward compatibility)
    llm_provider = os.getenv("LLM_PROVIDER") or os.getenv("SURVEY_LLM_PROVIDER")

    if not llm_provider:
        raise ValueError(
            "LLM_PROVIDER environment variable is not set. "
            "Please set LLM_PROVIDER to one of: KIMI, DEEPSEEK, ZHIPU"
        )

    # Validate provider is supported
    provider_upper = llm_provider.upper()
    if provider_upper not in LLM_PROVIDER_CONFIGS:
        raise ValueError(
            f"Invalid LLM_PROVIDER: {llm_provider}. "
            f"Supported providers: {list(LLM_PROVIDER_CONFIGS.keys())}"
        )

    # Validate API key for selected provider
    provider_config = get_provider_config(provider_upper)
    api_key_env = provider_config["api_key_env"]
    api_key = os.getenv(api_key_env)

    if not api_key:
        raise ValueError(
            f"API key for {provider_upper} provider is not set. "
            f"Please set {api_key_env} environment variable with your {provider_upper} API key."
        )

    # Start with DEFAULT_CONFIG but set the validated provider first
    # so that get_config_with_env_overrides uses the correct provider for model/base_url
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = provider_upper

    # Merge with environment overrides
    config = get_config_with_env_overrides(config)

    return config


def get_api_key(config: Dict[str, Any]) -> str:
    """
    Get API key based on selected LLM provider.

    Args:
        config: Configuration dictionary from load_config()

    Returns:
        API key for the selected provider

    Raises:
        ValueError: If API key is missing for the selected provider

    Example:
        >>> config = load_config()
        >>> api_key = get_api_key(config)
        >>> print(f"Using API key: {api_key[:10]}...")
    """
    import os

    provider = config.get("llm_provider", "ZHIPU").upper()
    provider_config = get_provider_config(provider)
    api_key_env = provider_config["api_key_env"]
    api_key = os.getenv(api_key_env)

    if not api_key:
        raise ValueError(
            f"API key for {provider} provider is not set. "
            f"Please set {api_key_env} environment variable."
        )

    return api_key


def get_model(config: Dict[str, Any]) -> str:
    """
    Get model name based on selected LLM provider.

    Returns the provider-specific model from config, or falls back to
    the provider's default model if not specified.

    Args:
        config: Configuration dictionary from load_config()

    Returns:
        Model name for the selected provider

    Example:
        >>> config = load_config()
        >>> model = get_model(config)
        >>> print(f"Using model: {model}")
    """
    provider = config.get("llm_provider", "ZHIPU").upper()

    # Return model from config if set (e.g., from environment override)
    if "model" in config:
        return config["model"]

    # Otherwise, return provider's default model
    provider_config = get_provider_config(provider)
    return provider_config["model"]


def get_provider_config(provider: str) -> Dict[str, str]:
    """
    Get provider-specific configuration.

    Args:
        provider: LLM provider name (KIMI, DEEPSEEK, ZHIPU)

    Returns:
        Dictionary with base_url, model, api_key_env

    Raises:
        ValueError: If provider is not supported
    """
    provider = provider.upper()
    if provider not in LLM_PROVIDER_CONFIGS:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: {list(LLM_PROVIDER_CONFIGS.keys())}"
        )
    return LLM_PROVIDER_CONFIGS[provider]


def get_config_with_env_overrides(
    config: Dict[str, Any] = None,
    env_prefix: str = "SURVEY_",
) -> Dict[str, Any]:
    """
    Merge DEFAULT_CONFIG with environment variable overrides.

    Args:
        config: Base configuration dict (defaults to DEFAULT_CONFIG)
        env_prefix: Environment variable prefix

    Returns:
        Configuration dictionary with environment overrides applied
    """
    import os

    if config is None:
        config = DEFAULT_CONFIG.copy()

    # Environment variable mappings
    env_mappings = {
        f"{env_prefix}LLM_PROVIDER": "llm_provider",
        f"{env_prefix}LLM_TEMPERATURE": "temperature",
        f"{env_prefix}LLM_MAX_TOKENS": "max_tokens",
        f"{env_prefix}ENABLE_HUMAN_REVIEW": "enable_human_review",
        f"{env_prefix}AUTO_APPROVE_RECODING": "auto_approve_recoding",
        f"{env_prefix}AUTO_APPROVE_INDICATORS": "auto_approve_indicators",
        f"{env_prefix}AUTO_APPROVE_TABLE_SPECS": "auto_approve_table_specs",
        f"{env_prefix}CARDINALITY_THRESHOLD": "cardinality_threshold",
        f"{env_prefix}FILTER_BINARY": "filter_binary",
        f"{env_prefix}FILTER_OTHER_TEXT": "filter_other_text",
        f"{env_prefix}SIGNIFICANCE_ALPHA": "significance_level",
        f"{env_prefix}TEST_TYPE": "test_type",
        f"{env_prefix}PSPP_PATH": "pspp_path",
        f"{env_prefix}OUTPUT_DIR": "output_dir",
        f"{env_prefix}TEMP_DIR": "temp_dir",
        f"{env_prefix}CREATE_TIMESTAMP_DIR": "create_timestamp_dir",
        f"{env_prefix}CHART_STYLE": "chart_style",
        f"{env_prefix}INCLUDE_CHARTS": "include_charts",
        f"{env_prefix}CHART_LIBRARY": "chart_library",
        f"{env_prefix}REVIEW_OUTPUT_FORMAT": "review_output_format",
    }

    # Apply environment variable overrides
    for env_var, config_key in env_mappings.items():
        value = os.getenv(env_var)
        if value is not None:
            # Type conversion based on default value type
            if config_key in config:
                default_type = type(config[config_key])

                if default_type == bool:
                    config[config_key] = value.lower() in ("true", "1", "yes", "on")
                elif default_type == int:
                    config[config_key] = int(value)
                elif default_type == float:
                    config[config_key] = float(value)
                else:
                    config[config_key] = value

    # Handle provider-specific overrides
    provider = config.get("llm_provider", "ZHIPU")
    provider_config = get_provider_config(provider)

    # Allow environment to override provider-specific settings
    if provider == "KIMI":
        config["base_url"] = os.getenv("KIMI_BASE_URL", provider_config["base_url"])
        config["model"] = os.getenv("KIMI_MODEL", provider_config["model"])
    elif provider == "DEEPSEEK":
        config["base_url"] = os.getenv("DEEPSEEK_BASE_URL", provider_config["base_url"])
        config["model"] = os.getenv("DEEPSEEK_MODEL", provider_config["model"])
    elif provider == "ZHIPU":
        config["base_url"] = os.getenv("ZHIPU_BASE_URL", provider_config["base_url"])
        config["model"] = os.getenv("ZHIPU_MODEL", provider_config["model"])

    return config
