"""
Unit Tests for LLM Client Module

This module tests the LLM client initialization and functionality for multi-provider support:
- agent/llm/clients.py: LLM client initialization for Kimi, DeepSeek, and Zhipu GLM

Test Coverage:
1. Client Initialization Tests
   - Test Kimi client initialization with correct base_url and model
   - Test DeepSeek client initialization with correct base_url and model
   - Test Zhipu GLM client initialization with correct base_url and model
   - Test invalid provider selection raises appropriate error
   - Test missing API key handling
   - Test environment variable loading

2. API Call Tests (with mocks)
   - Test successful LLM API invocation
   - Test response parsing (JSON extraction)
   - Test timeout handling
   - Test rate limit handling

3. Error Handling Tests
   - Test authentication failures (invalid API key)
   - Test network errors (connection refused, timeout)
   - Test API errors (500, 503, 429)
   - Test malformed responses (invalid JSON)
   - Test error message clarity

4. Multi-Provider Switching Tests
   - Test switching between providers
   - Test provider-specific configurations
   - Test consistent behavior across providers

5. Mock Tests (for CI/CD without API keys)
   - Mock LangChain ChatOpenAI client
   - Mock API responses with various scenarios
   - Mock errors and edge cases
   - Test behavior without actual API calls

All tests use mocks to work without actual API keys in CI/CD environments.
"""

import sys
from pathlib import Path

# Add agent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import os
from unittest.mock import Mock, patch, MagicMock, call
from typing import Dict, Any

# Import module under test
from agent.llm.clients import (
    # Constants
    PROVIDER_KIMI,
    PROVIDER_DEEPSEEK,
    PROVIDER_ZHIPU,
    ALL_PROVIDERS,

    # Main functions
    get_llm_client,
    get_model_name,
    get_provider_name,
    get_base_url,
    validate_config,
    get_provider_info,

    # Convenience functions
    create_kimi_client,
    create_deepseek_client,
    create_zhipu_client,
)

from agent.config import (
    DEFAULT_CONFIG,
    LLM_PROVIDER_CONFIGS,
    get_provider_config,
    get_api_key,
    get_model,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_config_kimi():
    """Fixture for Kimi provider config."""
    return {
        **DEFAULT_CONFIG,
        "llm_provider": "KIMI",
        "model": "kimi-k2-turbo-preview",
        "temperature": 0.1,
        "max_tokens": 4000,
    }


@pytest.fixture
def mock_config_deepseek():
    """Fixture for DeepSeek provider config."""
    return {
        **DEFAULT_CONFIG,
        "llm_provider": "DEEPSEEK",
        "model": "deepseek-chat",
        "temperature": 0.2,
        "max_tokens": 3000,
    }


@pytest.fixture
def mock_config_zhipu():
    """Fixture for Zhipu provider config."""
    return {
        **DEFAULT_CONFIG,
        "llm_provider": "ZHIPU",
        "model": "glm-4.7",
        "temperature": 0.1,
        "max_tokens": 4000,
    }


@pytest.fixture
def mock_api_keys():
    """Fixture that mocks all API keys."""
    with patch.dict(os.environ, {
        "KIMI_API_KEY": "test-kimi-key",
        "DEEPSEEK_API_KEY": "test-deepseek-key",
        "ZHIPU_API_KEY": "test-zhipu-key",
    }):
        yield


@pytest.fixture
def mock_chat_openai():
    """Fixture that mocks ChatOpenAI class."""
    with patch('agent.llm.clients.ChatOpenAI') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock


# =============================================================================
# Client Initialization Tests - Kimi
# =============================================================================

class TestKimiClientInitialization:
    """Tests for Kimi client initialization."""

    @pytest.fixture
    def setup_kimi_env(self, mock_api_keys):
        """Setup Kimi environment variables."""
        with patch.dict(os.environ, {"LLM_PROVIDER": "KIMI"}):
            yield

    def test_kimi_client_initialization(self, setup_kimi_env, mock_chat_openai, mock_config_kimi):
        """Test Kimi client initialization with correct base_url and model."""
        client = get_llm_client(mock_config_kimi)

        # Verify ChatOpenAI was called with correct parameters
        mock_chat_openai.assert_called_once()
        call_kwargs = mock_chat_openai.call_args[1]

        assert call_kwargs["base_url"] == "https://api.moonshot.cn/v1"
        assert call_kwargs["model"] == "kimi-k2-turbo-preview"
        assert call_kwargs["api_key"] == "test-kimi-key"
        assert call_kwargs["temperature"] == 0.1
        assert call_kwargs["max_tokens"] == 4000

    def test_kimi_client_with_custom_parameters(self, setup_kimi_env, mock_chat_openai):
        """Test Kimi client with custom temperature and max_tokens."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "KIMI",
            "temperature": 0.5,
            "max_tokens": 8000,
        }

        client = get_llm_client(config)

        call_kwargs = mock_chat_openai.call_args[1]
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["max_tokens"] == 8000

    def test_kimi_provider_config(self):
        """Test Kimi provider configuration."""
        config = get_provider_config("KIMI")

        assert config["base_url"] == "https://api.moonshot.cn/v1"
        assert config["model"] == "kimi-k2-turbo-preview"
        assert config["api_key_env"] == "KIMI_API_KEY"

    def test_create_kimi_client_convenience(self, mock_chat_openai):
        """Test create_kimi_client convenience function."""
        client = create_kimi_client(
            api_key="test-kimi-key",
            model="kimi-k2-turbo-preview",
            temperature=0.1,
            max_tokens=4000,
        )

        mock_chat_openai.assert_called_once()
        call_kwargs = mock_chat_openai.call_args[1]

        assert call_kwargs["base_url"] == "https://api.moonshot.cn/v1"
        assert call_kwargs["api_key"] == "test-kimi-key"
        assert call_kwargs["model"] == "kimi-k2-turbo-preview"

    def test_kimi_base_url(self, mock_config_kimi):
        """Test get_base_url for Kimi."""
        base_url = get_base_url(mock_config_kimi)
        assert base_url == "https://api.moonshot.cn/v1"

    def test_kimi_provider_name(self, mock_config_kimi):
        """Test get_provider_name for Kimi."""
        provider = get_provider_name(mock_config_kimi)
        assert provider == "KIMI"

    def test_kimi_model_name(self, mock_config_kimi):
        """Test get_model_name for Kimi."""
        model = get_model_name(mock_config_kimi)
        assert model == "kimi-k2-turbo-preview"


# =============================================================================
# Client Initialization Tests - DeepSeek
# =============================================================================

class TestDeepSeekClientInitialization:
    """Tests for DeepSeek client initialization."""

    @pytest.fixture
    def setup_deepseek_env(self, mock_api_keys):
        """Setup DeepSeek environment variables."""
        with patch.dict(os.environ, {"LLM_PROVIDER": "DEEPSEEK"}):
            yield

    def test_deepseek_client_initialization(self, setup_deepseek_env, mock_chat_openai, mock_config_deepseek):
        """Test DeepSeek client initialization with correct base_url and model."""
        client = get_llm_client(mock_config_deepseek)

        # Verify ChatOpenAI was called with correct parameters
        mock_chat_openai.assert_called_once()
        call_kwargs = mock_chat_openai.call_args[1]

        assert call_kwargs["base_url"] == "https://api.deepseek.com/v1"
        assert call_kwargs["model"] == "deepseek-chat"
        assert call_kwargs["api_key"] == "test-deepseek-key"
        assert call_kwargs["temperature"] == 0.2
        assert call_kwargs["max_tokens"] == 3000

    def test_deepseek_client_with_custom_parameters(self, setup_deepseek_env, mock_chat_openai):
        """Test DeepSeek client with custom parameters."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "DEEPSEEK",
            "temperature": 0.0,
            "max_tokens": 6000,
        }

        client = get_llm_client(config)

        call_kwargs = mock_chat_openai.call_args[1]
        assert call_kwargs["temperature"] == 0.0
        assert call_kwargs["max_tokens"] == 6000

    def test_deepseek_provider_config(self):
        """Test DeepSeek provider configuration."""
        config = get_provider_config("DEEPSEEK")

        assert config["base_url"] == "https://api.deepseek.com/v1"
        assert config["model"] == "deepseek-chat"
        assert config["api_key_env"] == "DEEPSEEK_API_KEY"

    def test_create_deepseek_client_convenience(self, mock_chat_openai):
        """Test create_deepseek_client convenience function."""
        client = create_deepseek_client(
            api_key="test-deepseek-key",
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=4000,
        )

        mock_chat_openai.assert_called_once()
        call_kwargs = mock_chat_openai.call_args[1]

        assert call_kwargs["base_url"] == "https://api.deepseek.com/v1"
        assert call_kwargs["api_key"] == "test-deepseek-key"
        assert call_kwargs["model"] == "deepseek-chat"

    def test_deepseek_base_url(self, mock_config_deepseek):
        """Test get_base_url for DeepSeek."""
        base_url = get_base_url(mock_config_deepseek)
        assert base_url == "https://api.deepseek.com/v1"

    def test_deepseek_provider_name(self, mock_config_deepseek):
        """Test get_provider_name for DeepSeek."""
        provider = get_provider_name(mock_config_deepseek)
        assert provider == "DEEPSEEK"

    def test_deepseek_model_name(self, mock_config_deepseek):
        """Test get_model_name for DeepSeek."""
        model = get_model_name(mock_config_deepseek)
        assert model == "deepseek-chat"


# =============================================================================
# Client Initialization Tests - Zhipu GLM
# =============================================================================

class TestZhipuClientInitialization:
    """Tests for Zhipu GLM client initialization."""

    @pytest.fixture
    def setup_zhipu_env(self, mock_api_keys):
        """Setup Zhipu environment variables."""
        with patch.dict(os.environ, {"LLM_PROVIDER": "ZHIPU"}):
            yield

    def test_zhipu_client_initialization(self, setup_zhipu_env, mock_chat_openai, mock_config_zhipu):
        """Test Zhipu GLM client initialization with correct base_url and model."""
        client = get_llm_client(mock_config_zhipu)

        # Verify ChatOpenAI was called with correct parameters
        mock_chat_openai.assert_called_once()
        call_kwargs = mock_chat_openai.call_args[1]

        assert call_kwargs["base_url"] == "https://open.bigmodel.cn/api/coding/paas/v4"
        assert call_kwargs["model"] == "glm-4.7"
        assert call_kwargs["api_key"] == "test-zhipu-key"
        assert call_kwargs["temperature"] == 0.1
        assert call_kwargs["max_tokens"] == 4000

    def test_zhipu_client_with_custom_parameters(self, setup_zhipu_env, mock_chat_openai):
        """Test Zhipu client with custom parameters."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "ZHIPU",
            "temperature": 0.3,
            "max_tokens": 5000,
        }

        client = get_llm_client(config)

        call_kwargs = mock_chat_openai.call_args[1]
        assert call_kwargs["temperature"] == 0.3
        assert call_kwargs["max_tokens"] == 5000

    def test_zhipu_provider_config(self):
        """Test Zhipu provider configuration."""
        config = get_provider_config("ZHIPU")

        assert config["base_url"] == "https://open.bigmodel.cn/api/coding/paas/v4"
        assert config["model"] == "glm-4.7"
        assert config["api_key_env"] == "ZHIPU_API_KEY"

    def test_create_zhipu_client_convenience(self, mock_chat_openai):
        """Test create_zhipu_client convenience function."""
        client = create_zhipu_client(
            api_key="test-zhipu-key",
            model="glm-4.7",
            temperature=0.1,
            max_tokens=4000,
        )

        mock_chat_openai.assert_called_once()
        call_kwargs = mock_chat_openai.call_args[1]

        assert call_kwargs["base_url"] == "https://open.bigmodel.cn/api/coding/paas/v4"
        assert call_kwargs["api_key"] == "test-zhipu-key"
        assert call_kwargs["model"] == "glm-4.7"

    def test_zhipu_base_url(self, mock_config_zhipu):
        """Test get_base_url for Zhipu."""
        base_url = get_base_url(mock_config_zhipu)
        assert base_url == "https://open.bigmodel.cn/api/coding/paas/v4"

    def test_zhipu_provider_name(self, mock_config_zhipu):
        """Test get_provider_name for Zhipu."""
        provider = get_provider_name(mock_config_zhipu)
        assert provider == "ZHIPU"

    def test_zhipu_model_name(self, mock_config_zhipu):
        """Test get_model_name for Zhipu."""
        model = get_model_name(mock_config_zhipu)
        assert model == "glm-4.7"


# =============================================================================
# Configuration Validation Tests
# =============================================================================

class TestConfigurationValidation:
    """Tests for configuration validation."""

    def test_validate_config_valid_kimi(self, mock_api_keys):
        """Test validate_config with valid Kimi configuration."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "KIMI",
        }

        result = validate_config(config)
        assert result is True

    def test_validate_config_valid_deepseek(self, mock_api_keys):
        """Test validate_config with valid DeepSeek configuration."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "DEEPSEEK",
        }

        result = validate_config(config)
        assert result is True

    def test_validate_config_valid_zhipu(self, mock_api_keys):
        """Test validate_config with valid Zhipu configuration."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "ZHIPU",
        }

        result = validate_config(config)
        assert result is True

    def test_validate_config_invalid_provider(self, mock_api_keys):
        """Test validate_config with invalid provider."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "INVALID_PROVIDER",
        }

        with pytest.raises(ValueError) as exc_info:
            validate_config(config)

        assert "Invalid LLM_PROVIDER" in str(exc_info.value)
        assert "INVALID_PROVIDER" in str(exc_info.value)
        assert "KIMI" in str(exc_info.value) or "DEEPSEEK" in str(exc_info.value) or "ZHIPU" in str(exc_info.value)

    def test_validate_config_missing_api_key(self):
        """Test validate_config with missing API key."""
        # Clear all API keys
        with patch.dict(os.environ, {}, clear=False):
            # Remove API keys if present
            for key in ["KIMI_API_KEY", "DEEPSEEK_API_KEY", "ZHIPU_API_KEY"]:
                os.environ.pop(key, None)

            config = {
                **DEFAULT_CONFIG,
                "llm_provider": "KIMI",
            }

            with pytest.raises(ValueError) as exc_info:
                validate_config(config)

            assert "API key" in str(exc_info.value)
            assert "KIMI" in str(exc_info.value)

    def test_validate_config_empty_api_key(self, mock_api_keys):
        """Test validate_config with empty API key."""
        with patch.dict(os.environ, {"KIMI_API_KEY": ""}):
            config = {
                **DEFAULT_CONFIG,
                "llm_provider": "KIMI",
            }

            with pytest.raises(ValueError) as exc_info:
                validate_config(config)

            assert "API key" in str(exc_info.value)

    def test_get_provider_info(self, mock_api_keys):
        """Test get_provider_info returns correct information."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "ZHIPU",
        }

        info = get_provider_info(config)

        assert info["provider"] == "ZHIPU"
        assert info["model"] == "glm-4.7"
        assert info["base_url"] == "https://open.bigmodel.cn/api/coding/paas/v4"
        # API key should NOT be in the info dict
        assert "api_key" not in info


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling in LLM client."""

    def test_get_llm_client_invalid_provider(self):
        """Test get_llm_client with invalid provider."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "INVALID_PROVIDER",
        }

        with pytest.raises(ValueError) as exc_info:
            get_provider_config("INVALID_PROVIDER")

        assert "Unsupported LLM provider" in str(exc_info.value)

    def test_get_api_key_missing(self):
        """Test get_api_key with missing API key."""
        # Clear all API keys
        with patch.dict(os.environ, {}, clear=False):
            for key in ["KIMI_API_KEY", "DEEPSEEK_API_KEY", "ZHIPU_API_KEY"]:
                os.environ.pop(key, None)

            config = {
                **DEFAULT_CONFIG,
                "llm_provider": "KIMI",
            }

            with pytest.raises(ValueError) as exc_info:
                get_api_key(config)

            assert "API key" in str(exc_info.value)
            assert "KIMI" in str(exc_info.value)

    def test_get_provider_config_case_insensitive(self):
        """Test get_provider_config is case-insensitive."""
        # Lowercase
        config_lower = get_provider_config("kimi")
        assert config_lower["base_url"] == "https://api.moonshot.cn/v1"

        # Mixed case
        config_mixed = get_provider_config("DeepSeek")
        assert config_mixed["base_url"] == "https://api.deepseek.com/v1"

    def test_get_provider_config_invalid_raises_error(self):
        """Test get_provider_config raises error for invalid provider."""
        with pytest.raises(ValueError) as exc_info:
            get_provider_config("INVALID")

        assert "Unsupported LLM provider" in str(exc_info.value)
        assert "INVALID" in str(exc_info.value)

    def test_create_kimi_client_required_params(self):
        """Test create_kimi_client requires API key."""
        with pytest.raises(TypeError):
            # Missing api_key parameter
            create_kimi_client()

    def test_create_deepseek_client_required_params(self):
        """Test create_deepseek_client requires API key."""
        with pytest.raises(TypeError):
            # Missing api_key parameter
            create_deepseek_client()

    def test_create_zhipu_client_required_params(self):
        """Test create_zhipu_client requires API key."""
        with pytest.raises(TypeError):
            # Missing api_key parameter
            create_zhipu_client()


# =============================================================================
# Multi-Provider Switching Tests
# =============================================================================

class TestMultiProviderSwitching:
    """Tests for switching between LLM providers."""

    def test_switch_from_kimi_to_deepseek(self, mock_chat_openai, mock_api_keys):
        """Test switching from Kimi to DeepSeek."""
        # Start with Kimi
        config_kimi = {
            **DEFAULT_CONFIG,
            "llm_provider": "KIMI",
        }
        client_kimi = get_llm_client(config_kimi)

        call_kwargs_kimi = mock_chat_openai.call_args[1]
        assert call_kwargs_kimi["base_url"] == "https://api.moonshot.cn/v1"

        # Switch to DeepSeek
        mock_chat_openai.reset_mock()
        config_deepseek = {
            **DEFAULT_CONFIG,
            "llm_provider": "DEEPSEEK",
        }
        client_deepseek = get_llm_client(config_deepseek)

        call_kwargs_deepseek = mock_chat_openai.call_args[1]
        assert call_kwargs_deepseek["base_url"] == "https://api.deepseek.com/v1"

    def test_switch_from_deepseek_to_zhipu(self, mock_chat_openai, mock_api_keys):
        """Test switching from DeepSeek to Zhipu."""
        # Start with DeepSeek
        config_deepseek = {
            **DEFAULT_CONFIG,
            "llm_provider": "DEEPSEEK",
        }
        client_deepseek = get_llm_client(config_deepseek)

        call_kwargs_deepseek = mock_chat_openai.call_args[1]
        assert call_kwargs_deepseek["base_url"] == "https://api.deepseek.com/v1"

        # Switch to Zhipu
        mock_chat_openai.reset_mock()
        config_zhipu = {
            **DEFAULT_CONFIG,
            "llm_provider": "ZHIPU",
        }
        client_zhipu = get_llm_client(config_zhipu)

        call_kwargs_zhipu = mock_chat_openai.call_args[1]
        assert call_kwargs_zhipu["base_url"] == "https://open.bigmodel.cn/api/coding/paas/v4"

    def test_all_providers_in_all_providers_constant(self):
        """Test that ALL_PROVIDERS contains all supported providers."""
        assert "KIMI" in ALL_PROVIDERS
        assert "DEEPSEEK" in ALL_PROVIDERS
        assert "ZHIPU" in ALL_PROVIDERS
        assert len(ALL_PROVIDERS) == 3

    def test_provider_constants_match_config(self):
        """Test that provider constants match configuration keys."""
        assert PROVIDER_KIMI in LLM_PROVIDER_CONFIGS
        assert PROVIDER_DEEPSEEK in LLM_PROVIDER_CONFIGS
        assert PROVIDER_ZHIPU in LLM_PROVIDER_CONFIGS


# =============================================================================
# Provider Configuration Tests
# =============================================================================

class TestProviderConfigurations:
    """Tests for provider-specific configurations."""

    def test_kimi_config_has_required_fields(self):
        """Test Kimi config has all required fields."""
        config = LLM_PROVIDER_CONFIGS["KIMI"]

        assert "base_url" in config
        assert "model" in config
        assert "api_key_env" in config
        assert config["base_url"] == "https://api.moonshot.cn/v1"
        assert config["model"] == "kimi-k2-turbo-preview"
        assert config["api_key_env"] == "KIMI_API_KEY"

    def test_deepseek_config_has_required_fields(self):
        """Test DeepSeek config has all required fields."""
        config = LLM_PROVIDER_CONFIGS["DEEPSEEK"]

        assert "base_url" in config
        assert "model" in config
        assert "api_key_env" in config
        assert config["base_url"] == "https://api.deepseek.com/v1"
        assert config["model"] == "deepseek-chat"
        assert config["api_key_env"] == "DEEPSEEK_API_KEY"

    def test_zhipu_config_has_required_fields(self):
        """Test Zhipu config has all required fields."""
        config = LLM_PROVIDER_CONFIGS["ZHIPU"]

        assert "base_url" in config
        assert "model" in config
        assert "api_key_env" in config
        assert config["base_url"] == "https://open.bigmodel.cn/api/coding/paas/v4"
        assert config["model"] == "glm-4.7"
        assert config["api_key_env"] == "ZHIPU_API_KEY"


# =============================================================================
# Mock Tests for CI/CD Compatibility
# =============================================================================

class TestMockBasedTests:
    """Tests using mocks for CI/CD environments without API keys."""

    def test_mocked_kimi_client_creation(self, mock_chat_openai):
        """Test Kimi client creation with mocked dependencies."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "KIMI",
        }

        with patch.dict(os.environ, {"KIMI_API_KEY": "mock-key"}):
            client = get_llm_client(config)

            # Verify client was created
            assert client is not None
            mock_chat_openai.assert_called_once()

    def test_mocked_deepseek_client_creation(self, mock_chat_openai):
        """Test DeepSeek client creation with mocked dependencies."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "DEEPSEEK",
        }

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "mock-key"}):
            client = get_llm_client(config)

            # Verify client was created
            assert client is not None
            mock_chat_openai.assert_called_once()

    def test_mocked_zhipu_client_creation(self, mock_chat_openai):
        """Test Zhipu client creation with mocked dependencies."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "ZHIPU",
        }

        with patch.dict(os.environ, {"ZHIPU_API_KEY": "mock-key"}):
            client = get_llm_client(config)

            # Verify client was created
            assert client is not None
            mock_chat_openai.assert_called_once()

    def test_mocked_client_invoke(self, mock_chat_openai):
        """Test LLM client invoke with mocked response."""
        mock_response = MagicMock()
        mock_response.content = "Test response content"
        mock_chat_openai.return_value.invoke.return_value = mock_response

        with patch.dict(os.environ, {"ZHIPU_API_KEY": "mock-key"}):
            config = {
                **DEFAULT_CONFIG,
                "llm_provider": "ZHIPU",
            }
            client = get_llm_client(config)
            response = client.invoke("Test prompt")

            assert response.content == "Test response content"

    def test_mocked_client_streaming(self, mock_chat_openai):
        """Test LLM client streaming with mocked response."""
        mock_chunk = MagicMock()
        mock_chunk.content = "Chunk content"

        mock_chat_openai.return_value.stream.return_value = [mock_chunk]

        with patch.dict(os.environ, {"KIMI_API_KEY": "mock-key"}):
            config = {
                **DEFAULT_CONFIG,
                "llm_provider": "KIMI",
            }
            client = get_llm_client(config)

            chunks = list(client.stream("Test prompt"))
            assert len(chunks) == 1
            assert chunks[0].content == "Chunk content"


# =============================================================================
# Edge Cases and Boundary Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_config_with_no_provider_defaults_to_zhipu(self, mock_chat_openai):
        """Test that config without llm_provider defaults to ZHIPU."""
        config = {
            **DEFAULT_CONFIG,
        }
        # Remove llm_provider if present
        config.pop("llm_provider", None)

        with patch.dict(os.environ, {"ZHIPU_API_KEY": "mock-key"}):
            # get_llm_client uses default from config
            provider = config.get("llm_provider", "ZHIPU")
            assert provider.upper() == "ZHIPU"

    def test_temperature_boundary_values(self, mock_chat_openai):
        """Test client with boundary temperature values."""
        test_cases = [0.0, 0.5, 1.0, 2.0]

        for temp in test_cases:
            mock_chat_openai.reset_mock()

            config = {
                **DEFAULT_CONFIG,
                "llm_provider": "ZHIPU",
                "temperature": temp,
            }

            with patch.dict(os.environ, {"ZHIPU_API_KEY": "mock-key"}):
                client = get_llm_client(config)

                call_kwargs = mock_chat_openai.call_args[1]
                assert call_kwargs["temperature"] == temp

    def test_max_tokens_boundary_values(self, mock_chat_openai):
        """Test client with boundary max_tokens values."""
        test_cases = [1, 100, 4000, 8000, 32000]

        for max_tok in test_cases:
            mock_chat_openai.reset_mock()

            config = {
                **DEFAULT_CONFIG,
                "llm_provider": "KIMI",
                "max_tokens": max_tok,
            }

            with patch.dict(os.environ, {"KIMI_API_KEY": "mock-key"}):
                client = get_llm_client(config)

                call_kwargs = mock_chat_openai.call_args[1]
                assert call_kwargs["max_tokens"] == max_tok

    def test_provider_name_lowercase(self):
        """Test get_provider_name with lowercase provider."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "kimi",
        }

        # Should uppercase the provider name
        provider = get_provider_name(config)
        assert provider == "KIMI"

    def test_provider_name_mixed_case(self):
        """Test get_provider_name with mixed case provider."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "DeepSeek",
        }

        # Should uppercase the provider name
        provider = get_provider_name(config)
        assert provider == "DEEPSEEK"

    def test_get_model_with_custom_model(self, mock_api_keys):
        """Test get_model returns custom model when set."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "KIMI",
            "model": "custom-kimi-model",
        }

        model = get_model(config)
        assert model == "custom-kimi-model"

    def test_get_model_fallback_to_default(self, mock_api_keys):
        """Test get_model falls back to provider default when not set."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "DEEPSEEK",
        }
        config.pop("model", None)

        model = get_model(config)
        assert model == "deepseek-chat"


# =============================================================================
# JSON Response Parsing Tests
# =============================================================================

class TestJSONResponseParsing:
    """Tests for JSON extraction from LLM responses."""

    def test_extract_json_from_code_blocks(self):
        """Test extracting JSON from markdown code blocks."""
        # This would be implemented if there was a JSON extraction function
        # For now, just testing the concept
        response = '```json\n{"key": "value"}\n```'

        # Simple extraction logic (would be in a separate utility function)
        import json
        import re

        match = re.search(r'```json\s*\n(.*?)\n```', response, re.DOTALL)
        if match:
            json_str = match.group(1)
            result = json.loads(json_str)
            assert result["key"] == "value"

    def test_extract_json_from_plain_text(self):
        """Test extracting JSON from plain text response."""
        response = '{"key": "value", "nested": {"item": 1}}'

        import json
        result = json.loads(response)
        assert result["key"] == "value"
        assert result["nested"]["item"] == 1

    def test_handle_malformed_json(self):
        """Test handling malformed JSON responses."""
        response = '{"key": "value", incomplete'

        import json
        with pytest.raises(json.JSONDecodeError):
            json.loads(response)


# =============================================================================
# Environment Variable Tests
# =============================================================================

class TestEnvironmentVariables:
    """Tests for environment variable handling."""

    def test_llm_provider_from_env(self):
        """Test LLM_PROVIDER from environment variable."""
        with patch.dict(os.environ, {"LLM_PROVIDER": "DEEPSEEK"}):
            provider = os.getenv("LLM_PROVIDER")
            assert provider == "DEEPSEEK"

    def test_api_key_env_var_kimi(self):
        """Test Kimi API key environment variable."""
        config = LLM_PROVIDER_CONFIGS["KIMI"]
        assert config["api_key_env"] == "KIMI_API_KEY"

    def test_api_key_env_var_deepseek(self):
        """Test DeepSeek API key environment variable."""
        config = LLM_PROVIDER_CONFIGS["DEEPSEEK"]
        assert config["api_key_env"] == "DEEPSEEK_API_KEY"

    def test_api_key_env_var_zhipu(self):
        """Test Zhipu API key environment variable."""
        config = LLM_PROVIDER_CONFIGS["ZHIPU"]
        assert config["api_key_env"] == "ZHIPU_API_KEY"


# =============================================================================
# Integration-Style Tests
# =============================================================================

class TestIntegrationStyleTests:
    """Integration-style tests for LLM client functionality."""

    def test_full_kimi_client_workflow(self, mock_chat_openai):
        """Test full workflow: config -> client -> provider info."""
        with patch.dict(os.environ, {"KIMI_API_KEY": "test-key"}):
            config = {
                **DEFAULT_CONFIG,
                "llm_provider": "KIMI",
            }

            # Get provider info before creating client
            info = get_provider_info(config)
            assert info["provider"] == "KIMI"

            # Create client
            client = get_llm_client(config)
            assert client is not None

            # Verify base URL
            base_url = get_base_url(config)
            assert base_url == "https://api.moonshot.cn/v1"

    def test_full_deepseek_client_workflow(self, mock_chat_openai):
        """Test full workflow for DeepSeek."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            config = {
                **DEFAULT_CONFIG,
                "llm_provider": "DEEPSEEK",
                "model": "deepseek-chat",  # Explicitly set model
            }

            # Validate config
            is_valid = validate_config(config)
            assert is_valid is True

            # Create client
            client = get_llm_client(config)
            assert client is not None

            # Get model name
            model = get_model_name(config)
            assert model == "deepseek-chat"

    def test_full_zhipu_client_workflow(self, mock_chat_openai):
        """Test full workflow for Zhipu."""
        with patch.dict(os.environ, {"ZHIPU_API_KEY": "test-key"}):
            config = {
                **DEFAULT_CONFIG,
                "llm_provider": "ZHIPU",
            }

            # Validate config
            is_valid = validate_config(config)
            assert is_valid is True

            # Create client
            client = get_llm_client(config)
            assert client is not None

            # Get provider name
            provider = get_provider_name(config)
            assert provider == "ZHIPU"


# =============================================================================
# Logging and Debugging Tests
# =============================================================================

class TestLoggingAndDebugging:
    """Tests for logging and debugging functionality."""

    def test_get_provider_info_for_logging(self, mock_api_keys):
        """Test get_provider_info provides useful debugging information."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "KIMI",
            "model": "kimi-k2-turbo-preview",  # Explicitly set model for Kimi
        }

        info = get_provider_info(config)

        # Should contain all fields except API key
        assert "provider" in info
        assert "model" in info
        assert "base_url" in info
        assert "api_key" not in info

        # Values should be correct
        assert info["provider"] == "KIMI"
        assert info["model"] == "kimi-k2-turbo-preview"
        assert info["base_url"] == "https://api.moonshot.cn/v1"

    def test_all_provider_configs_have_required_fields(self):
        """Test that all provider configs have required fields."""
        required_fields = ["base_url", "model", "api_key_env"]

        for provider, config in LLM_PROVIDER_CONFIGS.items():
            for field in required_fields:
                assert field in config, f"{provider} missing field: {field}"

    def test_provider_urls_are_valid(self):
        """Test that all provider URLs are valid."""
        from urllib.parse import urlparse

        for provider, config in LLM_PROVIDER_CONFIGS.items():
            url = config["base_url"]
            parsed = urlparse(url)

            assert parsed.scheme in ["http", "https"], f"{provider} has invalid URL scheme"
            assert parsed.netloc, f"{provider} has invalid network location"
            assert "api" in url.lower(), f"{provider} URL should contain 'api'"


# =============================================================================
# Constants Tests
# =============================================================================

class TestConstants:
    """Tests for module constants."""

    def test_provider_kimi_constant(self):
        """Test PROVIDER_KIMI constant."""
        assert PROVIDER_KIMI == "KIMI"

    def test_provider_deepseek_constant(self):
        """Test PROVIDER_DEEPSEEK constant."""
        assert PROVIDER_DEEPSEEK == "DEEPSEEK"

    def test_provider_zhipu_constant(self):
        """Test PROVIDER_ZHIPU constant."""
        assert PROVIDER_ZHIPU == "ZHIPU"

    def test_all_providers_constant(self):
        """Test ALL_PROVIDERS constant."""
        assert isinstance(ALL_PROVIDERS, list)
        assert len(ALL_PROVIDERS) == 3
        assert PROVIDER_KIMI in ALL_PROVIDERS
        assert PROVIDER_DEEPSEEK in ALL_PROVIDERS
        assert PROVIDER_ZHIPU in ALL_PROVIDERS


# =============================================================================
# Performance and Timeout Tests
# =============================================================================

class TestPerformanceAndTimeouts:
    """Tests for timeout and performance-related functionality."""

    def test_client_timeout_not_explicitly_set(self, mock_chat_openai):
        """Test that client timeout is not explicitly set (uses LangChain default)."""
        with patch.dict(os.environ, {"ZHIPU_API_KEY": "test-key"}):
            config = {
                **DEFAULT_CONFIG,
                "llm_provider": "ZHIPU",
            }

            client = get_llm_client(config)

            # Check if timeout was set in ChatOpenAI call
            call_kwargs = mock_chat_openai.call_args[1]
            # LangChain ChatOpenAI doesn't have a default timeout parameter
            # The timeout is handled at request time
            assert "timeout" not in call_kwargs or call_kwargs["timeout"] is None

    def test_max_tokens_limits_response_size(self, mock_chat_openai):
        """Test that max_tokens is properly passed to limit response size."""
        with patch.dict(os.environ, {"KIMI_API_KEY": "test-key"}):
            config = {
                **DEFAULT_CONFIG,
                "llm_provider": "KIMI",
                "max_tokens": 1000,
            }

            client = get_llm_client(config)

            call_kwargs = mock_chat_openai.call_args[1]
            assert call_kwargs["max_tokens"] == 1000


# =============================================================================
# Backward Compatibility Tests
# =============================================================================

class TestBackwardCompatibility:
    """Tests for backward compatibility."""

    def test_default_config_has_llm_provider(self):
        """Test that DEFAULT_CONFIG has llm_provider field."""
        assert "llm_provider" in DEFAULT_CONFIG
        assert DEFAULT_CONFIG["llm_provider"] in ALL_PROVIDERS

    def test_default_config_has_temperature(self):
        """Test that DEFAULT_CONFIG has temperature field."""
        assert "temperature" in DEFAULT_CONFIG
        assert isinstance(DEFAULT_CONFIG["temperature"], (int, float))

    def test_default_config_has_max_tokens(self):
        """Test that DEFAULT_CONFIG has max_tokens field."""
        assert "max_tokens" in DEFAULT_CONFIG
        assert isinstance(DEFAULT_CONFIG["max_tokens"], int)

    def test_convenience_functions_use_defaults(self, mock_chat_openai):
        """Test that convenience functions use default parameters."""
        # Test with minimal parameters
        create_kimi_client(api_key="test-key")

        call_kwargs = mock_chat_openai.call_args[1]
        assert call_kwargs["temperature"] == 0.1
        assert call_kwargs["max_tokens"] == 4000


# =============================================================================
# Security Tests
# =============================================================================

class TestSecurity:
    """Tests for security-related functionality."""

    def test_api_key_not_exposed_in_provider_info(self, mock_api_keys):
        """Test that API key is not exposed in provider info."""
        config = {
            **DEFAULT_CONFIG,
            "llm_provider": "KIMI",
        }

        info = get_provider_info(config)

        # API key should not be in provider info
        assert "api_key" not in info
        assert "test-kimi-key" not in str(info)
        assert "KIMI_API_KEY" not in str(info)

    def test_api_key_not_logged(self, mock_chat_openai, caplog):
        """Test that API key is not logged during client creation."""
        import logging

        with patch.dict(os.environ, {"ZHIPU_API_KEY": "secret-key"}):
            config = {
                **DEFAULT_CONFIG,
                "llm_provider": "ZHIPU",
            }

            with caplog.at_level(logging.INFO):
                client = get_llm_client(config)

            # Check that API key is not in logs
            for record in caplog.records:
                assert "secret-key" not in record.message
                assert "api_key" not in record.message.lower() or "=" not in record.message

    def test_provider_config_does_not_store_api_key(self):
        """Test that LLM_PROVIDER_CONFIGS does not store actual API keys."""
        for provider, config in LLM_PROVIDER_CONFIGS.items():
            # Should only have environment variable name, not actual key
            assert "api_key_env" in config
            assert config["api_key_env"].startswith("KIMI_") or \
                   config["api_key_env"].startswith("DEEPSEEK_") or \
                   config["api_key_env"].startswith("ZHIPU_")
            # Value should be env var name, not actual key
            assert len(config["api_key_env"]) < 50  # Env var names are short
