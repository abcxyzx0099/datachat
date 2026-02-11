"""
LLM Client Initialization for Survey Analysis Workflow

This module provides a unified interface for initializing ChatOpenAI-compatible
clients for multiple LLM providers (Kimi, DeepSeek, Zhipu GLM).

Provider selection is determined by the LLM_PROVIDER configuration value,
and each provider uses provider-specific base URLs, API keys, and models.

Example:
    >>> from agent.config import load_config
    >>> from agent.llm.clients import get_llm_client
    >>> config = load_config()
    >>> llm = get_llm_client(config)
    >>> response = llm.invoke("Hello, world!")
"""

import os
import logging
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

from agent.config import (
    LLM_PROVIDER_CONFIGS,
    get_provider_config,
    get_api_key,
    get_model,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Provider Constants
# =============================================================================

PROVIDER_KIMI = "KIMI"
PROVIDER_DEEPSEEK = "DEEPSEEK"
PROVIDER_ZHIPU = "ZHIPU"

ALL_PROVIDERS = [PROVIDER_KIMI, PROVIDER_DEEPSEEK, PROVIDER_ZHIPU]


# =============================================================================
# LLM Client Initialization
# =============================================================================

def get_llm_client(config: Dict[str, Any]) -> BaseChatModel:
    """
    Initialize a ChatOpenAI-compatible LLM client based on provider configuration.

    This function reads the LLM_PROVIDER from config and initializes the
    appropriate ChatOpenAI client with provider-specific base URLs and models.

    Args:
        config: Configuration dictionary from load_config()

    Returns:
        BaseChatModel: Initialized ChatOpenAI instance for the selected provider

    Raises:
        ValueError: If provider is unknown or API key is missing

    Example:
        >>> from agent.config import load_config
        >>> from agent.llm.clients import get_llm_client
        >>> config = load_config()
        >>> llm = get_llm_client(config)
        >>> print(f"Using model: {llm.model_name}")
    """
    # Get provider from config
    provider = config.get("llm_provider", "ZHIPU").upper()
    provider_config = get_provider_config(provider)

    # Get API key for selected provider
    api_key = get_api_key(config)

    # Get model name (from config or provider default)
    model = get_model(config)

    # Get LLM parameters with defaults
    temperature = config.get("temperature", 0.1)
    max_tokens = config.get("max_tokens", 4000)

    # Initialize ChatOpenAI with provider-specific configuration
    logger.info(
        f"Initializing LLM client: provider={provider}, "
        f"model={model}, temperature={temperature}, max_tokens={max_tokens}"
    )

    client = ChatOpenAI(
        base_url=provider_config["base_url"],
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    logger.info(f"LLM client initialized successfully for {provider}")
    return client


# =============================================================================
# Helper Functions
# =============================================================================

def get_model_name(config: Dict[str, Any]) -> str:
    """
    Get the model name for the selected LLM provider.

    This helper function returns the model name that will be used by
    get_llm_client(), useful for logging and debugging.

    Args:
        config: Configuration dictionary from load_config()

    Returns:
        Model name for the selected provider

    Example:
        >>> from agent.config import load_config
        >>> from agent.llm.clients import get_model_name
        >>> config = load_config()
        >>> model = get_model_name(config)
        >>> print(f"Using model: {model}")
    """
    return get_model(config)


def get_provider_name(config: Dict[str, Any]) -> str:
    """
    Get the provider name from configuration.

    Args:
        config: Configuration dictionary from load_config()

    Returns:
        Provider name (KIMI, DEEPSEEK, or ZHIPU)

    Example:
        >>> from agent.config import load_config
        >>> from agent.llm.clients import get_provider_name
        >>> config = load_config()
        >>> provider = get_provider_name(config)
        >>> print(f"Using provider: {provider}")
    """
    return config.get("llm_provider", "ZHIPU").upper()


def get_base_url(config: Dict[str, Any]) -> str:
    """
    Get the base URL for the selected LLM provider.

    Args:
        config: Configuration dictionary from load_config()

    Returns:
        Base URL for the selected provider's API

    Example:
        >>> from agent.config import load_config
        >>> from agent.llm.clients import get_base_url
        >>> config = load_config()
        >>> url = get_base_url(config)
        >>> print(f"API endpoint: {url}")
    """
    provider = config.get("llm_provider", "ZHIPU").upper()
    provider_config = get_provider_config(provider)
    return provider_config["base_url"]


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate LLM configuration before client initialization.

    This helper checks that:
    1. LLM_PROVIDER is valid (KIMI, DEEPSEEK, or ZHIPU)
    2. API key exists for the selected provider

    Args:
        config: Configuration dictionary from load_config()

    Returns:
        True if configuration is valid

    Raises:
        ValueError: If provider is invalid or API key is missing

    Example:
        >>> from agent.config import load_config
        >>> from agent.llm.clients import validate_config
        >>> config = load_config()
        >>> if validate_config(config):
        ...     print("Configuration is valid")
    """
    provider = config.get("llm_provider", "ZHIPU").upper()

    # Validate provider
    if provider not in ALL_PROVIDERS:
        raise ValueError(
            f"Invalid LLM_PROVIDER: {provider}. "
            f"Supported providers: {ALL_PROVIDERS}"
        )

    # Validate API key exists
    try:
        api_key = get_api_key(config)
        if not api_key:
            raise ValueError(
                f"API key for {provider} provider is not set or is empty. "
                f"Please set the appropriate environment variable."
            )
    except ValueError as e:
        raise ValueError(
            f"Configuration validation failed: {e}"
        ) from e

    logger.info(f"Configuration validation passed for provider: {provider}")
    return True


def get_provider_info(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Get comprehensive provider information for logging/debugging.

    Returns a dictionary with provider, model, and base URL (excluding API key).

    Args:
        config: Configuration dictionary from load_config()

    Returns:
        Dictionary with provider information

    Example:
        >>> from agent.config import load_config
        >>> from agent.llm.clients import get_provider_info
        >>> config = load_config()
        >>> info = get_provider_info(config)
        >>> print(f"Provider: {info['provider']}")
        >>> print(f"Model: {info['model']}")
        >>> print(f"Base URL: {info['base_url']}")
    """
    provider = config.get("llm_provider", "ZHIPU").upper()
    provider_config = get_provider_config(provider)

    return {
        "provider": provider,
        "model": get_model(config),
        "base_url": provider_config["base_url"],
    }


# =============================================================================
# Convenience Functions
# =============================================================================

def create_kimi_client(
    api_key: str,
    model: str = "kimi-k2-turbo-preview",
    temperature: float = 0.1,
    max_tokens: int = 4000,
) -> ChatOpenAI:
    """
    Create a Kimi (Moonshot AI) LLM client directly.

    This is a convenience function for creating a Kimi client without
    going through the full config loading process.

    Args:
        api_key: Kimi API key
        model: Model name (default: kimi-k2-turbo-preview)
        temperature: LLM temperature (default: 0.1)
        max_tokens: Maximum tokens (default: 4000)

    Returns:
        ChatOpenAI instance configured for Kimi

    Example:
        >>> from agent.llm.clients import create_kimi_client
        >>> llm = create_kimi_client(api_key="your-key")
        >>> response = llm.invoke("Hello")
    """
    logger.info(f"Creating Kimi client with model: {model}")
    return ChatOpenAI(
        base_url="https://api.moonshot.cn/v1",
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def create_deepseek_client(
    api_key: str,
    model: str = "deepseek-chat",
    temperature: float = 0.1,
    max_tokens: int = 4000,
) -> ChatOpenAI:
    """
    Create a DeepSeek LLM client directly.

    This is a convenience function for creating a DeepSeek client without
    going through the full config loading process.

    Args:
        api_key: DeepSeek API key
        model: Model name (default: deepseek-chat)
        temperature: LLM temperature (default: 0.1)
        max_tokens: Maximum tokens (default: 4000)

    Returns:
        ChatOpenAI instance configured for DeepSeek

    Example:
        >>> from agent.llm.clients import create_deepseek_client
        >>> llm = create_deepseek_client(api_key="your-key")
        >>> response = llm.invoke("Hello")
    """
    logger.info(f"Creating DeepSeek client with model: {model}")
    return ChatOpenAI(
        base_url="https://api.deepseek.com/v1",
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def create_zhipu_client(
    api_key: str,
    model: str = "glm-4.7",
    temperature: float = 0.1,
    max_tokens: int = 4000,
) -> ChatOpenAI:
    """
    Create a Zhipu GLM LLM client directly.

    This is a convenience function for creating a Zhipu client without
    going through the full config loading process.

    Args:
        api_key: Zhipu API key
        model: Model name (default: glm-4.7)
        temperature: LLM temperature (default: 0.1)
        max_tokens: Maximum tokens (default: 4000)

    Returns:
        ChatOpenAI instance configured for Zhipu GLM

    Example:
        >>> from agent.llm.clients import create_zhipu_client
        >>> llm = create_zhipu_client(api_key="your-key")
        >>> response = llm.invoke("Hello")
    """
    logger.info(f"Creating Zhipu GLM client with model: {model}")
    return ChatOpenAI(
        base_url="https://open.bigmodel.cn/api/coding/paas/v4",
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
