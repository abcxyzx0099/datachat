# LLM Integration Tests Guide

This guide explains how to run LLM provider integration tests for the DataChat application.

---

## Overview

The LLM integration tests verify that all three LLM providers (Kimi, DeepSeek, Zhipu GLM) work correctly with:
- API authentication
- Request/response handling
- Error recovery (rate limits, auth failures, server errors)
- Retry logic with exponential backoff
- Provider switching

---

## Test Files

| File | Purpose |
|------|---------|
| `tests/test_llm_clients.py` | Unit tests for LLM client initialization (mocked, no API keys required) |
| `tests/test_llm_integration.py` | Integration tests for LLM workflow (mocked, no API keys required) |
| `tests/test_llm_providers_integration.py` | **Real** integration tests with actual API calls (requires API keys) |

---

## Prerequisites

### 1. Python Environment

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### 2. LLM Provider API Keys

To run real integration tests, you need API keys for one or more providers:

| Provider | Environment Variable | How to Get |
|----------|---------------------|------------|
| **Kimi (Moonshot AI)** | `KIMI_API_KEY` | https://platform.moonshot.cn/console/api-keys |
| **DeepSeek** | `DEEPSEEK_API_KEY` | https://platform.deepseek.com/api_keys |
| **Zhipu GLM** | `ZHIPU_API_KEY` | https://open.bigmodel.cn/usercenter/apikeys |

---

## Setting Up API Keys

### Option 1: Set Environment Variables Directly

```bash
export KIMI_API_KEY="your-kimi-api-key"
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export ZHIPU_API_KEY="your-zhipu-api-key"
```

### Option 2: Use .env File

Create or update `.env` file in project root:

```bash
# .env file
KIMI_API_KEY=sk-kimi-your-key-here
DEEPSEEK_API_KEY=sk-deepseek-your-key-here
ZHIPU_API_KEY=your-zhipu-key-here
```

### Verify Keys Are Set

```bash
# Check which keys are available
env | grep -E "(KIMI|DEEPSEEK|ZHIPU)_API_KEY"
```

---

## Running Tests

### Run All LLM Tests (No API Keys Required)

```bash
# Run unit tests (mocked, no API keys needed)
pytest tests/test_llm_clients.py -v

# Run integration tests (mocked, no API keys needed)
pytest tests/test_llm_integration.py -v
```

### Run Real Integration Tests (API Keys Required)

```bash
# Run all real integration tests (requires API keys)
pytest tests/test_llm_providers_integration.py -v

# Run only tests for a specific provider
pytest tests/test_llm_providers_integration.py -v -k "kimi"
pytest tests/test_llm_providers_integration.py -v -k "deepseek"
pytest tests/test_llm_providers_integration.py -v -k "zhipu"

# Run tests marked as @pytest.mark.llm
pytest tests/test_llm_providers_integration.py -v -m llm
```

### Run All Tests (Combined)

```bash
# Run all LLM-related tests
pytest tests/test_llm_*.py -v

# Run with coverage
pytest tests/test_llm_*.py -v --cov=agent/llm --cov-report=html
```

---

## Test Coverage Summary

### Unit Tests (`test_llm_clients.py`)

**133 tests** - No API keys required

- Client initialization for all providers
- Configuration validation
- Provider switching
- Error handling (mocked)
- Helper functions

### Integration Tests (`test_llm_integration.py`)

**133 tests** - No API keys required

- Prompt generation (recoding, indicators, tables)
- Response parsing (JSON extraction)
- End-to-end workflows (mocked)
- Error handling (mocked)
- Token management

### Provider Integration Tests (`test_llm_providers_integration.py`)

**23 tests** - API keys required for full coverage

| Category | Tests | API Key Required |
|----------|-------|------------------|
| API Authentication | 5 | Yes (3) |
| Request/Response | 5 | Yes (4) |
| Error Recovery | 4 | Yes (1) |
| Retry Logic | 2 | No (mocked) |
| Provider Switching | 3 | Yes (1) |
| Timeout Handling | 2 | Yes (1) |
| Concurrent Requests | 1 | Yes (1) |
| Idempotency | 1 | Yes (1) |

---

## Test Output Examples

### Successful Test Run (With API Keys)

```
============================= test session starts ==============================
platform linux -- Python 3.13.5, pytest-9.0.2
collected 23 items

tests/test_llm_providers_integration.py::TestAPIAuthentication::test_kimi_valid_api_key PASSED
tests/test_llm_providers_integration.py::TestAPIAuthentication::test_deepseek_valid_api_key SKIPPED
tests/test_llm_providers_integration.py::TestAPIAuthentication::test_zhipu_valid_api_key SKIPPED
tests/test_llm_providers_integration.py::TestProviderSwitching::test_provider_config_consistency PASSED

======================== 10 passed, 13 skipped in 1.97s =========================
```

### Test Run Without API Keys

```
======================== 10 passed, 13 skipped in 1.97s =========================
```

Tests that require API keys are skipped automatically.

---

## Troubleshooting

### Tests Are Skipped

**Problem**: All provider tests are skipped

```
SKIPPED [100%]
```

**Solution**: Set the required API key environment variable

```bash
export KIMI_API_KEY="your-key"
```

### Authentication Errors

**Problem**: Tests fail with authentication error

```
AssertionError: assert 'auth' in str(e).lower() or '401' in str(e)
```

**Solution**: Verify your API key is valid

```bash
# Test API key manually
curl -H "Authorization: Bearer $KIMI_API_KEY" https://api.moonshot.cn/v1/models
```

### Rate Limit Errors

**Problem**: Tests fail with rate limit error

```
ValueError: Rate limit exceeded (429)
```

**Solution**: Wait a few minutes and retry, or use a different API key

### Connection Timeouts

**Problem**: Tests timeout

```
socket.timeout: Request timed out
```

**Solution**: Check your internet connection and provider status

---

## Test Markers

Tests are marked with pytest markers for organization:

| Marker | Purpose |
|--------|---------|
| `@pytest.mark.llm` | Tests requiring LLM API calls |
| `@pytest.mark.integration` | Integration tests |
| `@pytest.mark.slow` | Slow tests (>1 second) |

Run tests by marker:

```bash
# Run only LLM tests
pytest -m llm

# Run only integration tests
pytest -m integration

# Run only fast tests (not slow)
pytest -m "not slow"
```

---

## Continuous Integration (CI/CD)

In CI/CD environments without API keys:

```bash
# Run only tests that don't require API keys
pytest tests/test_llm_*.py -v -m "not llm"
```

This ensures CI/CD pipelines pass without requiring secrets.

---

## Best Practices

### 1. Don't Commit API Keys

Always use environment variables or `.env` file (which is gitignored).

### 2. Test Locally Before Pushing

Run integration tests locally with your API keys before pushing changes.

### 3. Use Mocks for Unit Tests

Unit tests should use mocks to work without API keys in CI/CD.

### 4. Handle Rate Limiting

When running integration tests, add delays between requests to avoid rate limits.

### 5. Clean Up Environment

After testing, you can unset API keys:

```bash
unset KIMI_API_KEY DEEPSEEK_API_KEY ZHIPU_API_KEY
```

---

## Adding New Tests

When adding new LLM integration tests:

1. **Unit Tests**: Add to `tests/test_llm_clients.py` (mocked, no API keys)
2. **Workflow Tests**: Add to `tests/test_llm_integration.py` (mocked, no API keys)
3. **API Tests**: Add to `tests/test_llm_providers_integration.py` (requires API keys)

Example:

```python
@pytest.mark.llm
class TestMyNewFeature:
    @requires_api_key("ZHIPU")
    def test_zhipu_my_feature(self):
        """Test my new feature with Zhipu API."""
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            pytest.skip("No ZHIPU_API_KEY found")

        client = create_zhipu_client(api_key=api_key)
        # Test implementation here
```

---

## Related Documentation

- **[Technology Stack](technology-stack.md)** - LLM provider configurations
- **[Configuration](system-configuration.md)** - LLM provider settings
- **[Testing Strategy](../README.md)** - Overall testing approach
