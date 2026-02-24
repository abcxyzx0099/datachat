# Messages API Guide

**Part of**: Claude Programming Guide Skill

Complete guide for using Anthropic's Messages API to integrate Claude into your applications.

---

## Overview

The Messages API provides direct access to Claude's capabilities via HTTP requests. It's the most straightforward way to integrate Claude into any application.

## Installation

```bash
# Python
pip install anthropic

# Node.js/TypeScript
npm install @anthropic-ai/sdk
```

## Basic Usage

### Python

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ]
)

print(response.content[0].text)
```

### TypeScript

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({ apiKey: 'your-api-key' });

const response = await client.messages.create({
  model: 'claude-opus-4-6',
  maxTokens: 1024,
  messages: [{ role: 'user', content: 'Hello, Claude!' }]
});

console.log(response.content[0].text);
```

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model ID (e.g., `claude-opus-4-6`, `claude-sonnet-4-6`) |
| `messages` | array | Yes | Conversation messages |
| `max_tokens` | integer | Yes | Maximum tokens to generate |
| `temperature` | float | No | Randomness (0-1, default: depends on model) |
| `top_p` | float | No | Nucleus sampling (0-1, default: depends on model) |
| `stop_sequences` | array | No | Sequences that stop generation |
| `stream` | boolean | No | Enable streaming (default: false) |
| `tools` | array | No | Tools for Claude to use |
| `system` | string | No | System prompt |

## Conversation Management

The Messages API is stateless - you must manage conversation history yourself.

```python
conversation = [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language..."},
    {"role": "user", "content": "Show me an example"}
]

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=conversation
)
```

## Streaming

Enable streaming for real-time responses:

```python
with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me a story"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

## Using Tools

Define tools that Claude can use:

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
]

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools
)

# Handle tool use
if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            # Execute tool and send result back
            tool_result = execute_tool(block.name, block.input)
            ...
```

## Using Agent Skills (Beta)

See the main skill document or `official-manual/using-agent-skills-with-api.md` for complete documentation on using Agent Skills with the Messages API.

```python
response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [
            {"type": "anthropic", "skill_id": "xlsx", "version": "latest"}
        ]
    },
    messages=[{"role": "user", "content": "Create an Excel report"}],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}]
)
```

## Error Handling

```python
from anthropic import APIClientError, RateLimitError

try:
    response = client.messages.create(...)
except RateLimitError as e:
    print(f"Rate limited: {e}")
except APIClientError as e:
    print(f"API error: {e}")
```

## Models

| Model | Context | Best For |
|-------|---------|----------|
| `claude-opus-4-6` | 200K | Complex reasoning, analysis |
| `claude-sonnet-4-6` | 200K | Balanced performance/cost |
| `claude-haiku-4-5-20251001` | 200K | Fast, cost-effective tasks |

## Cost Optimization

1. **Use the right model** - Haiku for simple tasks, Sonnet for balance, Opus for complexity
2. **Set appropriate `max_tokens`** - Don't over-allocate
3. **Cache system prompts** - Use prompt caching for repeated prompts
4. **Stream when possible** - Reduces latency perception

## Best Practices

1. **Always set `max_tokens`** - Required parameter
2. **Use system prompts for context** - More efficient than in messages
3. **Handle stop_reason** - Check if response was complete
4. **Implement retry logic** - For transient failures
5. **Monitor token usage** - Check `response.usage` for costs
