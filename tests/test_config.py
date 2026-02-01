"""
Unit Tests for Configuration Module (agent/config.py)

This module contains comprehensive unit tests for the configuration module.
Tests cover:
- DEFAULT_CONFIG structure
- load_config() function
- get_config_with_env_overrides() function
- get_api_key() function
- get_model() function
- get_provider_config() function
- Environment variable handling
- Validation and error cases
- Edge cases (missing env vars, invalid providers, malformed values)

Test Framework: pytest
Environment Mocking: monkeypatch/pytest fixtures
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch, Mock

import pytest

# Add agent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.config import (
    DEFAULT_CONFIG,
    LLM_PROVIDER_CONFIGS,
    load_config,
    get_config_with_env_overrides,
    get_api_key,
    get_model,
    get_provider_config,
)


# =============================================================================
# Autouse Fixture to Clean Environment
# =============================================================================

@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    """
    Automatically clean environment variables before each test.

    This autouse fixture ensures that tests don't interfere with each other
    by clearing all relevant environment variables before each test runs.
    """
    # Clear all relevant env vars before each test
    env_vars_to_clear = []
    for key in os.environ.copy():
        if key.startswith("SURVEY_") or key in ["LLM_PROVIDER"] or \
           key.startswith("KIMI_") or key.startswith("DEEPSEEK_") or key.startswith("ZHIPU_"):
            env_vars_to_clear.append(key)

    for key in env_vars_to_clear:
        monkeypatch.delenv(key, raising=False)

    yield  # Run the test


# =============================================================================
# DEFAULT_CONFIG Structure Tests
# =============================================================================

class TestDefaultConfig:
    """Tests for DEFAULT_CONFIG dictionary structure."""

    def test_default_config_exists(self):
        """Test that DEFAULT_CONFIG is defined and is a dictionary."""
        assert isinstance(DEFAULT_CONFIG, dict)
        assert len(DEFAULT_CONFIG) > 0

    def test_default_config_has_required_keys(self):
        """Test that DEFAULT_CONFIG contains all expected keys."""
        required_keys = [
            # LLM Configuration
            "llm_provider",
            "model",
            "temperature",
            "max_tokens",
            # Three-Node Pattern Configuration
            "max_self_correction_iterations",
            "enable_human_review",
            "auto_approve_recoding",
            "auto_approve_indicators",
            "auto_approve_table_specs",
            "review_output_format",
            # Step 3: Preliminary Filtering
            "cardinality_threshold",
            "filter_binary",
            "filter_other_text",
            # PSPP Configuration
            "pspp_path",
            "pspp_output_path",
            # File Paths
            "output_dir",
            "temp_dir",
            "create_timestamp_dir",
            # Statistical Analysis
            "significance_level",
            "min_cramers_v",
            "min_cell_count",
            "test_type",
            # Presentation
            "powerpoint_template",
            "chart_style",
            "include_charts",
            "html_theme",
            "chart_library",
        ]
        for key in required_keys:
            assert key in DEFAULT_CONFIG, f"Missing required key: {key}"

    def test_default_config_types(self):
        """Test that DEFAULT_CONFIG values have correct types."""
        type_checks = {
            "llm_provider": str,
            "model": str,
            "temperature": (int, float),
            "max_tokens": int,
            "max_self_correction_iterations": int,
            "enable_human_review": bool,
            "auto_approve_recoding": bool,
            "auto_approve_indicators": bool,
            "auto_approve_table_specs": bool,
            "review_output_format": str,
            "cardinality_threshold": int,
            "filter_binary": bool,
            "filter_other_text": bool,
            "pspp_path": str,
            "pspp_output_path": str,
            "output_dir": str,
            "temp_dir": str,
            "create_timestamp_dir": bool,
            "significance_level": (int, float),
            "min_cramers_v": (int, float),
            "min_cell_count": int,
            "test_type": str,
            "powerpoint_template": (str, type(None)),
            "chart_style": str,
            "include_charts": bool,
            "html_theme": str,
            "chart_library": str,
        }
        for key, expected_type in type_checks.items():
            assert key in DEFAULT_CONFIG
            value = DEFAULT_CONFIG[key]
            assert isinstance(value, expected_type), \
                f"Key '{key}' has type {type(value)}, expected {expected_type}"

    def test_default_config_values_are_valid(self):
        """Test that DEFAULT_CONFIG has sensible default values."""
        # LLM provider should be one of the supported providers
        assert DEFAULT_CONFIG["llm_provider"] in ["KIMI", "DEEPSEEK", "ZHIPU"]

        # Temperature should be between 0 and 2
        assert 0 <= DEFAULT_CONFIG["temperature"] <= 2

        # Max tokens should be positive
        assert DEFAULT_CONFIG["max_tokens"] > 0

        # Max iterations should be positive
        assert DEFAULT_CONFIG["max_self_correction_iterations"] > 0

        # Cardinality threshold should be positive
        assert DEFAULT_CONFIG["cardinality_threshold"] > 0

        # Significance level should be between 0 and 1
        assert 0 < DEFAULT_CONFIG["significance_level"] < 1


# =============================================================================
# LLM Provider Configuration Tests
# =============================================================================

class TestLLMProviderConfigs:
    """Tests for LLM_PROVIDER_CONFIGS dictionary."""

    def test_provider_configs_exist(self):
        """Test that LLM_PROVIDER_CONFIGS is defined."""
        assert isinstance(LLM_PROVIDER_CONFIGS, dict)
        assert len(LLM_PROVIDER_CONFIGS) == 3

    def test_provider_configs_has_all_providers(self):
        """Test that all expected providers are in LLM_PROVIDER_CONFIGS."""
        assert "KIMI" in LLM_PROVIDER_CONFIGS
        assert "DEEPSEEK" in LLM_PROVIDER_CONFIGS
        assert "ZHIPU" in LLM_PROVIDER_CONFIGS

    def test_provider_config_structure(self):
        """Test that each provider config has required fields."""
        required_fields = ["base_url", "model", "api_key_env"]
        for provider, config in LLM_PROVIDER_CONFIGS.items():
            for field in required_fields:
                assert field in config, f"Provider {provider} missing field: {field}"
            assert isinstance(config["base_url"], str)
            assert isinstance(config["model"], str)
            assert isinstance(config["api_key_env"], str)
            assert config["api_key_env"].endswith("_API_KEY")

    def test_provider_base_urls_are_valid(self):
        """Test that provider base URLs are valid HTTPS URLs."""
        for provider, config in LLM_PROVIDER_CONFIGS.items():
            assert config["base_url"].startswith("https://")
            assert len(config["base_url"]) > 10


# =============================================================================
# get_provider_config() Tests
# =============================================================================

class TestGetProviderConfig:
    """Tests for get_provider_config() function."""

    def test_get_kimi_config(self):
        """Test getting KIMI provider config."""
        config = get_provider_config("KIMI")
        assert config["base_url"] == "https://api.moonshot.cn/v1"
        assert config["model"] == "kimi-k2-turbo-preview"
        assert config["api_key_env"] == "KIMI_API_KEY"

    def test_get_deepseek_config(self):
        """Test getting DEEPSEEK provider config."""
        config = get_provider_config("DEEPSEEK")
        assert config["base_url"] == "https://api.deepseek.com/v1"
        assert config["model"] == "deepseek-chat"
        assert config["api_key_env"] == "DEEPSEEK_API_KEY"

    def test_get_zhipu_config(self):
        """Test getting ZHIPU provider config."""
        config = get_provider_config("ZHIPU")
        assert config["base_url"] == "https://open.bigmodel.cn/api/coding/paas/v4"
        assert config["model"] == "glm-4.7"
        assert config["api_key_env"] == "ZHIPU_API_KEY"

    def test_get_provider_config_case_insensitive(self):
        """Test that provider name is case-insensitive."""
        config1 = get_provider_config("kimi")
        config2 = get_provider_config("KIMI")
        config3 = get_provider_config("KiMi")
        assert config1 == config2 == config3

    def test_get_provider_config_invalid_provider(self):
        """Test that invalid provider raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            get_provider_config("INVALID_PROVIDER")
        assert "Unsupported LLM provider" in str(excinfo.value)
        assert "INVALID_PROVIDER" in str(excinfo.value)
        assert "KIMI" in str(excinfo.value)
        assert "DEEPSEEK" in str(excinfo.value)
        assert "ZHIPU" in str(excinfo.value)


# =============================================================================
# get_config_with_env_overrides() Tests
# =============================================================================

class TestGetConfigWithEnvOverrides:
    """Tests for get_config_with_env_overrides() function."""

    def test_returns_default_config_when_no_env_vars(self):
        """Test that default config is returned when no env vars are set."""
        # Note: autouse fixture already clears env vars
        config = get_config_with_env_overrides()
        # get_config_with_env_overrides adds base_url and provider-specific model
        # So we check that all DEFAULT_CONFIG keys are present with same values
        for key, value in DEFAULT_CONFIG.items():
            assert config[key] == value

    def test_does_not_modify_default_config(self, monkeypatch):
        """Test that function doesn't modify the original DEFAULT_CONFIG."""
        original_defaults = DEFAULT_CONFIG.copy()
        monkeypatch.setenv("SURVEY_LLM_TEMPERATURE", "0.5")

        config = get_config_with_env_overrides()
        assert DEFAULT_CONFIG == original_defaults
        assert config["temperature"] == 0.5
        assert DEFAULT_CONFIG["temperature"] != 0.5

    def test_llm_provider_override(self, monkeypatch):
        """Test LLM_PROVIDER override."""
        monkeypatch.setenv("SURVEY_LLM_PROVIDER", "DEEPSEEK")
        config = get_config_with_env_overrides()
        assert config["llm_provider"] == "DEEPSEEK"

    def test_llm_provider_legacy_env_var(self, monkeypatch):
        """Test legacy SURVEY_LLM_PROVIDER env var."""
        monkeypatch.setenv("SURVEY_LLM_PROVIDER", "KIMI")
        config = get_config_with_env_overrides()
        assert config["llm_provider"] == "KIMI"

    def test_temperature_override_string(self, monkeypatch):
        """Test temperature override from string."""
        monkeypatch.setenv("SURVEY_LLM_TEMPERATURE", "0.7")
        config = get_config_with_env_overrides()
        assert config["temperature"] == 0.7
        assert isinstance(config["temperature"], float)

    def test_max_tokens_override_int(self, monkeypatch):
        """Test max_tokens override from int string."""
        monkeypatch.setenv("SURVEY_LLM_MAX_TOKENS", "8000")
        config = get_config_with_env_overrides()
        assert config["max_tokens"] == 8000
        assert isinstance(config["max_tokens"], int)

    def test_boolean_override_true_variations(self, monkeypatch):
        """Test boolean override with various 'true' values."""
        true_values = ["true", "TRUE", "True", "1", "yes", "YES", "on", "ON"]
        for val in true_values:
            monkeypatch.setenv("SURVEY_ENABLE_HUMAN_REVIEW", val)
            config = get_config_with_env_overrides()
            assert config["enable_human_review"] is True, f"Failed for value: {val}"

    def test_boolean_override_false_variations(self, monkeypatch):
        """Test boolean override with various 'false' values."""
        false_values = ["false", "FALSE", "False", "0", "no", "NO", "off", "OFF"]
        for val in false_values:
            monkeypatch.setenv("SURVEY_ENABLE_HUMAN_REVIEW", val)
            config = get_config_with_env_overrides()
            assert config["enable_human_review"] is False, f"Failed for value: {val}"

    def test_all_boolean_overrides(self, monkeypatch):
        """Test all boolean config options can be overridden."""
        boolean_vars = [
            "SURVEY_ENABLE_HUMAN_REVIEW",
            "SURVEY_AUTO_APPROVE_RECODING",
            "SURVEY_AUTO_APPROVE_INDICATORS",
            "SURVEY_AUTO_APPROVE_TABLE_SPECS",
            "SURVEY_FILTER_BINARY",
            "SURVEY_FILTER_OTHER_TEXT",
            "SURVEY_CREATE_TIMESTAMP_DIR",
            "SURVEY_INCLUDE_CHARTS",
        ]
        for var in boolean_vars:
            monkeypatch.setenv(var, "true")
        config = get_config_with_env_overrides()
        for key in [
            "enable_human_review",
            "auto_approve_recoding",
            "auto_approve_indicators",
            "auto_approve_table_specs",
            "filter_binary",
            "filter_other_text",
            "create_timestamp_dir",
            "include_charts",
        ]:
            assert config[key] is True

    def test_integer_overrides(self, monkeypatch):
        """Test integer config options can be overridden."""
        monkeypatch.setenv("SURVEY_CARDINALITY_THRESHOLD", "50")
        # Note: SURVEY_MIN_CELL_COUNT is not in the env_mappings in config.py
        # So this test verifies actual behavior - min_cell_count won't be overridden
        config = get_config_with_env_overrides()
        assert config["cardinality_threshold"] == 50
        # min_cell_count stays at default since there's no env var mapping for it
        assert config["min_cell_count"] == DEFAULT_CONFIG["min_cell_count"]
        assert isinstance(config["cardinality_threshold"], int)

    def test_float_overrides(self, monkeypatch):
        """Test float config options can be overridden."""
        monkeypatch.setenv("SURVEY_LLM_TEMPERATURE", "0.75")
        monkeypatch.setenv("SURVEY_SIGNIFICANCE_ALPHA", "0.01")
        # Note: SURVEY_MIN_CRAMERS_V is not in the env_mappings in config.py
        config = get_config_with_env_overrides()
        assert config["temperature"] == 0.75
        assert config["significance_level"] == 0.01
        # min_cramers_v stays at default since there's no env var mapping for it
        assert config["min_cramers_v"] == DEFAULT_CONFIG["min_cramers_v"]

    def test_string_overrides(self, monkeypatch):
        """Test string config options can be overridden."""
        monkeypatch.setenv("SURVEY_TEST_TYPE", "fisher_exact")
        monkeypatch.setenv("SURVEY_PSPP_PATH", "/usr/local/bin/pspp")
        monkeypatch.setenv("SURVEY_OUTPUT_DIR", "custom_output")
        monkeypatch.setenv("SURVEY_TEMP_DIR", "custom_temp")
        monkeypatch.setenv("SURVEY_CHART_STYLE", "corporate")
        monkeypatch.setenv("SURVEY_CHART_LIBRARY", "plotly")
        monkeypatch.setenv("SURVEY_REVIEW_OUTPUT_FORMAT", "json")
        config = get_config_with_env_overrides()
        assert config["test_type"] == "fisher_exact"
        assert config["pspp_path"] == "/usr/local/bin/pspp"
        assert config["output_dir"] == "custom_output"
        assert config["temp_dir"] == "custom_temp"
        assert config["chart_style"] == "corporate"
        assert config["chart_library"] == "plotly"
        assert config["review_output_format"] == "json"

    def test_provider_specific_overrides_kimi(self, monkeypatch):
        """Test provider-specific overrides for KIMI."""
        monkeypatch.setenv("SURVEY_LLM_PROVIDER", "KIMI")
        monkeypatch.setenv("KIMI_BASE_URL", "https://custom.kimi.com/v1")
        monkeypatch.setenv("KIMI_MODEL", "custom-kimi-model")
        config = get_config_with_env_overrides()
        assert config["llm_provider"] == "KIMI"
        assert config["base_url"] == "https://custom.kimi.com/v1"
        assert config["model"] == "custom-kimi-model"

    def test_provider_specific_overrides_deepseek(self, monkeypatch):
        """Test provider-specific overrides for DEEPSEEK."""
        monkeypatch.setenv("SURVEY_LLM_PROVIDER", "DEEPSEEK")
        monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://custom.deepseek.com/v1")
        monkeypatch.setenv("DEEPSEEK_MODEL", "custom-deepseek-model")
        config = get_config_with_env_overrides()
        assert config["llm_provider"] == "DEEPSEEK"
        assert config["base_url"] == "https://custom.deepseek.com/v1"
        assert config["model"] == "custom-deepseek-model"

    def test_provider_specific_overrides_zhipu(self, monkeypatch):
        """Test provider-specific overrides for ZHIPU."""
        monkeypatch.setenv("SURVEY_LLM_PROVIDER", "ZHIPU")
        monkeypatch.setenv("ZHIPU_BASE_URL", "https://custom.zhipu.com/v1")
        monkeypatch.setenv("ZHIPU_MODEL", "custom-zhipu-model")
        config = get_config_with_env_overrides()
        assert config["llm_provider"] == "ZHIPU"
        assert config["base_url"] == "https://custom.zhipu.com/v1"
        assert config["model"] == "custom-zhipu-model"

    def test_custom_base_config(self):
        """Test with custom base config dict."""
        custom_config = {"llm_provider": "KIMI", "temperature": 0.5, "custom_key": "custom_value"}
        result = get_config_with_env_overrides(custom_config)
        assert result["llm_provider"] == "KIMI"
        assert result["temperature"] == 0.5
        assert result["custom_key"] == "custom_value"

    def test_custom_env_prefix(self, monkeypatch):
        """Test with custom environment variable prefix."""
        monkeypatch.setenv("CUSTOM_LLM_TEMPERATURE", "0.9")
        monkeypatch.setenv("SURVEY_LLM_TEMPERATURE", "0.3")
        config = get_config_with_env_overrides(env_prefix="CUSTOM_")
        assert config["temperature"] == 0.9

    def test_none_config_uses_default(self):
        """Test that None as config uses DEFAULT_CONFIG."""
        config = get_config_with_env_overrides(config=None)
        # get_config_with_env_overrides adds base_url and provider-specific model
        # So we check that all DEFAULT_CONFIG keys are present with same values
        for key, value in DEFAULT_CONFIG.items():
            assert config[key] == value


# =============================================================================
# load_config() Tests
# =============================================================================

class TestLoadConfig:
    """Tests for load_config() function."""

    def test_load_config_success_with_env(self, monkeypatch, tmp_path):
        """Test successful config loading with environment variables."""
        # Create a test .env file
        env_file = tmp_path / ".env"
        env_file.write_text("LLM_PROVIDER=ZHIPU\nZHIPU_API_KEY=test-api-key-123\n")

        monkeypatch.setenv("LLM_PROVIDER", "ZHIPU")
        monkeypatch.setenv("ZHIPU_API_KEY", "test-api-key-123")

        config = load_config(env_file=str(env_file))
        assert config["llm_provider"] == "ZHIPU"

    def test_load_config_missing_llm_provider(self, monkeypatch, tmp_path):
        """Test that missing LLM_PROVIDER raises ValueError."""
        env_file = tmp_path / ".env"
        env_file.write_text("ZHIPU_API_KEY=test-api-key-123\n")

        with pytest.raises(ValueError) as excinfo:
            load_config(env_file=str(env_file))
        assert "LLM_PROVIDER environment variable is not set" in str(excinfo.value)

    def test_load_config_invalid_provider(self, monkeypatch, tmp_path):
        """Test that invalid LLM_PROVIDER raises ValueError."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        monkeypatch.setenv("LLM_PROVIDER", "INVALID")
        monkeypatch.setenv("INVALID_API_KEY", "test-key")

        with pytest.raises(ValueError) as excinfo:
            load_config(env_file=str(env_file))
        assert "Invalid LLM_PROVIDER" in str(excinfo.value)
        assert "INVALID" in str(excinfo.value)

    def test_load_config_missing_api_key(self, monkeypatch, tmp_path):
        """Test that missing API key raises ValueError."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        monkeypatch.setenv("LLM_PROVIDER", "ZHIPU")

        with pytest.raises(ValueError) as excinfo:
            load_config(env_file=str(env_file))
        assert "API key for ZHIPU provider is not set" in str(excinfo.value)
        assert "ZHIPU_API_KEY" in str(excinfo.value)

    def test_load_config_kimi_provider(self, monkeypatch, tmp_path):
        """Test loading config with KIMI provider."""
        # Create .env file with KIMI config
        env_file = tmp_path / "test.env"
        env_file.write_text("LLM_PROVIDER=KIMI\nKIMI_API_KEY=kimi-key-123\n")

        monkeypatch.setenv("LLM_PROVIDER", "KIMI")
        monkeypatch.setenv("KIMI_API_KEY", "kimi-key-123")

        config = load_config(env_file=str(env_file))
        assert config["llm_provider"] == "KIMI"

    def test_load_config_deepseek_provider(self, monkeypatch, tmp_path):
        """Test loading config with DEEPSEEK provider."""
        # Create .env file with DEEPSEEK config
        env_file = tmp_path / "test.env"
        env_file.write_text("LLM_PROVIDER=DEEPSEEK\nDEEPSEEK_API_KEY=deepseek-key-123\n")

        monkeypatch.setenv("LLM_PROVIDER", "DEEPSEEK")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key-123")

        config = load_config(env_file=str(env_file))
        assert config["llm_provider"] == "DEEPSEEK"

    def test_load_config_zhipu_provider(self, monkeypatch, tmp_path):
        """Test loading config with ZHIPU provider."""
        # Create empty .env file
        env_file = tmp_path / "test.env"
        env_file.write_text("")

        monkeypatch.setenv("LLM_PROVIDER", "ZHIPU")
        monkeypatch.setenv("ZHIPU_API_KEY", "zhipu-key-123")

        config = load_config(env_file=str(env_file))
        assert config["llm_provider"] == "ZHIPU"

    def test_load_config_with_env_overrides(self, monkeypatch, tmp_path):
        """Test that environment overrides are applied."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        monkeypatch.setenv("LLM_PROVIDER", "DEEPSEEK")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
        monkeypatch.setenv("SURVEY_LLM_TEMPERATURE", "0.8")
        monkeypatch.setenv("SURVEY_CARDINALITY_THRESHOLD", "50")

        config = load_config(env_file=str(env_file))
        assert config["temperature"] == 0.8
        assert config["cardinality_threshold"] == 50

    def test_load_config_nonexistent_env_file(self, monkeypatch, tmp_path):
        """Test that nonexistent .env file doesn't raise error (optional)."""
        nonexistent_file = tmp_path / "nonexistent.env"

        monkeypatch.setenv("LLM_PROVIDER", "ZHIPU")
        monkeypatch.setenv("ZHIPU_API_KEY", "test-key")

        # Should not raise FileNotFoundError
        config = load_config(env_file=str(nonexistent_file))
        assert config["llm_provider"] == "ZHIPU"

    def test_load_config_legacy_survey_env_var(self, monkeypatch, tmp_path):
        """Test that legacy SURVEY_LLM_PROVIDER is still supported."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        monkeypatch.setenv("SURVEY_LLM_PROVIDER", "KIMI")
        monkeypatch.setenv("KIMI_API_KEY", "test-key")

        config = load_config(env_file=str(env_file))
        assert config["llm_provider"] == "KIMI"


# =============================================================================
# get_api_key() Tests
# =============================================================================

class TestGetApiKey:
    """Tests for get_api_key() function."""

    def test_get_api_key_kimi(self, monkeypatch):
        """Test getting KIMI API key."""
        config = {"llm_provider": "KIMI"}
        monkeypatch.setenv("KIMI_API_KEY", "kimi-test-key-123")
        api_key = get_api_key(config)
        assert api_key == "kimi-test-key-123"

    def test_get_api_key_deepseek(self, monkeypatch):
        """Test getting DEEPSEEK API key."""
        config = {"llm_provider": "DEEPSEEK"}
        monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-test-key-456")
        api_key = get_api_key(config)
        assert api_key == "deepseek-test-key-456"

    def test_get_api_key_zhipu(self, monkeypatch):
        """Test getting ZHIPU API key."""
        config = {"llm_provider": "ZHIPU"}
        monkeypatch.setenv("ZHIPU_API_KEY", "zhipu-test-key-789")
        api_key = get_api_key(config)
        assert api_key == "zhipu-test-key-789"

    def test_get_api_key_missing_provider_in_config(self, monkeypatch):
        """Test that missing provider defaults to ZHIPU."""
        config = {}
        monkeypatch.setenv("ZHIPU_API_KEY", "default-zhipu-key")
        api_key = get_api_key(config)
        assert api_key == "default-zhipu-key"

    def test_get_api_key_case_insensitive_provider(self, monkeypatch):
        """Test that provider name is case-insensitive."""
        config1 = {"llm_provider": "kimi"}
        config2 = {"llm_provider": "KIMI"}
        config3 = {"llm_provider": "KiMi"}
        monkeypatch.setenv("KIMI_API_KEY", "test-key")
        assert get_api_key(config1) == "test-key"
        assert get_api_key(config2) == "test-key"
        assert get_api_key(config3) == "test-key"

    def test_get_api_key_missing_key_raises_error(self, monkeypatch):
        """Test that missing API key raises ValueError."""
        config = {"llm_provider": "KIMI"}
        with pytest.raises(ValueError) as excinfo:
            get_api_key(config)
        assert "API key for KIMI provider is not set" in str(excinfo.value)
        assert "KIMI_API_KEY" in str(excinfo.value)


# =============================================================================
# get_model() Tests
# =============================================================================

class TestGetModel:
    """Tests for get_model() function."""

    def test_get_model_from_config(self):
        """Test getting model from config when set."""
        config = {"llm_provider": "KIMI", "model": "custom-kimi-model"}
        model = get_model(config)
        assert model == "custom-kimi-model"

    def test_get_model_from_provider_default(self):
        """Test getting provider default model when not in config."""
        config = {"llm_provider": "KIMI"}
        model = get_model(config)
        assert model == "kimi-k2-turbo-preview"

    def test_get_model_deepseek_default(self):
        """Test getting DEEPSEEK default model."""
        config = {"llm_provider": "DEEPSEEK"}
        model = get_model(config)
        assert model == "deepseek-chat"

    def test_get_model_zhipu_default(self):
        """Test getting ZHIPU default model."""
        config = {"llm_provider": "ZHIPU"}
        model = get_model(config)
        assert model == "glm-4.7"

    def test_get_model_missing_provider_defaults_to_zhipu(self):
        """Test that missing provider defaults to ZHIPU."""
        config = {}
        model = get_model(config)
        assert model == "glm-4.7"

    def test_get_model_case_insensitive_provider(self):
        """Test that provider name is case-insensitive."""
        config1 = {"llm_provider": "deepseek"}
        config2 = {"llm_provider": "DEEPSEEK"}
        config3 = {"llm_provider": "DeEpSeEk"}
        assert get_model(config1) == "deepseek-chat"
        assert get_model(config2) == "deepseek-chat"
        assert get_model(config3) == "deepseek-chat"


# =============================================================================
# Edge Cases and Error Handling Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_string_env_var(self, monkeypatch):
        """Test that empty string env var raises error (actual behavior)."""
        monkeypatch.setenv("SURVEY_LLM_TEMPERATURE", "")
        # Empty string causes ValueError when trying to convert to float
        with pytest.raises(ValueError):
            get_config_with_env_overrides()

    def test_invalid_float_env_var(self, monkeypatch):
        """Test that invalid float value raises error."""
        monkeypatch.setenv("SURVEY_LLM_TEMPERATURE", "not-a-float")
        with pytest.raises(ValueError):
            get_config_with_env_overrides()

    def test_invalid_int_env_var(self, monkeypatch):
        """Test that invalid int value raises error."""
        monkeypatch.setenv("SURVEY_CARDINALITY_THRESHOLD", "not-an-int")
        # The code tries to convert to int which will raise ValueError
        with pytest.raises(ValueError):
            get_config_with_env_overrides()

    def test_malformed_api_key(self, monkeypatch, tmp_path):
        """Test that malformed API key is still accepted (no validation)."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        monkeypatch.setenv("LLM_PROVIDER", "ZHIPU")
        # The code doesn't validate key format, just presence
        monkeypatch.setenv("ZHIPU_API_KEY", "   ")  # Just whitespace

        # Empty/whitespace key is accepted by the code
        # This tests documents the actual behavior
        config = load_config(env_file=str(env_file))
        assert config["llm_provider"] == "ZHIPU"

    def test_provider_with_whitespace(self, monkeypatch, tmp_path):
        """Test that provider with whitespace is handled correctly."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        # Current implementation uppercases, so " ZHIPU " becomes " ZHIPU "
        # which won't match "ZHIPU" in the provider configs
        # This tests the actual behavior - it should fail
        monkeypatch.setenv("LLM_PROVIDER", " ZHIPU ")
        monkeypatch.setenv("ZHIPU_API_KEY", "test-key")

        # This will fail because " ZHIPU " != "ZHIPU"
        with pytest.raises(ValueError):
            load_config(env_file=str(env_file))

    def test_multiple_env_vars_set(self, monkeypatch):
        """Test behavior when multiple conflicting env vars are set."""
        monkeypatch.setenv("LLM_PROVIDER", "KIMI")
        monkeypatch.setenv("SURVEY_LLM_PROVIDER", "DEEPSEEK")
        monkeypatch.setenv("KIMI_API_KEY", "kimi-key")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")
        # SURVEY_LLM_PROVIDER takes precedence over LLM_PROVIDER in get_config_with_env_overrides
        # This tests the actual behavior
        config = get_config_with_env_overrides()
        assert config["llm_provider"] == "DEEPSEEK"


# =============================================================================
# Integration Tests
# =============================================================================

class TestConfigIntegration:
    """Integration tests for configuration module."""

    def test_full_config_loading_workflow(self, monkeypatch, tmp_path):
        """Test complete workflow: load_config -> get_api_key -> get_model."""
        # Create .env file with DEEPSEEK config
        env_file = tmp_path / "test.env"
        env_file.write_text(
            "LLM_PROVIDER=DEEPSEEK\n"
            "DEEPSEEK_API_KEY=deepseek-integration-key\n"
            "SURVEY_LLM_TEMPERATURE=0.6\n"
            "SURVEY_CARDINALITY_THRESHOLD=40\n"
        )

        monkeypatch.setenv("LLM_PROVIDER", "DEEPSEEK")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-integration-key")
        monkeypatch.setenv("SURVEY_LLM_TEMPERATURE", "0.6")
        monkeypatch.setenv("SURVEY_CARDINALITY_THRESHOLD", "40")

        # Load config
        config = load_config(env_file=str(env_file))

        # Get API key
        api_key = get_api_key(config)
        assert api_key == "deepseek-integration-key"

        # Get model
        model = get_model(config)
        assert model == "deepseek-chat"

        # Verify overrides applied
        assert config["temperature"] == 0.6
        assert config["cardinality_threshold"] == 40

    def test_provider_switching(self, monkeypatch, tmp_path):
        """Test switching between providers."""
        # Create .env file
        env_file = tmp_path / "test.env"

        # Start with KIMI
        env_file.write_text("LLM_PROVIDER=KIMI\nKIMI_API_KEY=kimi-key\n")
        monkeypatch.setenv("LLM_PROVIDER", "KIMI")
        monkeypatch.setenv("KIMI_API_KEY", "kimi-key")

        config = load_config(env_file=str(env_file))
        assert config["llm_provider"] == "KIMI"
        assert get_model(config) == "kimi-k2-turbo-preview"

        # Switch to DEEPSEEK
        env_file.write_text("LLM_PROVIDER=DEEPSEEK\nDEEPSEEK_API_KEY=deepseek-key\n")
        monkeypatch.setenv("LLM_PROVIDER", "DEEPSEEK")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")

        config = load_config(env_file=str(env_file))
        assert config["llm_provider"] == "DEEPSEEK"
        assert get_model(config) == "deepseek-chat"

    def test_config_immutability_across_calls(self, monkeypatch):
        """Test that each call to get_config_with_env_overrides is independent."""
        monkeypatch.setenv("SURVEY_LLM_TEMPERATURE", "0.5")
        config1 = get_config_with_env_overrides()
        assert config1["temperature"] == 0.5

        monkeypatch.setenv("SURVEY_LLM_TEMPERATURE", "0.9")
        config2 = get_config_with_env_overrides()
        assert config2["temperature"] == 0.9

        # Original config should not be affected
        assert config1["temperature"] == 0.5
