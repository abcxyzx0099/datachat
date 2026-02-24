---
name: claude-programming-guide
description: 'Comprehensive guide for using Claude programmatically - covering both Messages API method and Claude Agent SDK method. Use when users need to: (1) Integrate Claude into Python/TypeScript applications via API, (2) Build AI agent applications using Claude Agent SDK, (3) Understand the difference between API and SDK approaches, (4) Implement Agent Skills in either method, (5) Choose the right method for their use case.'
license: Apache-2.0
---

# Claude Programming Guide

Complete guide for using Claude AI capabilities programmatically in your applications.

## Overview

This skill covers two primary methods for integrating Claude into your applications:

| Method | SDK | Purpose | Best For |
|--------|-----|---------|----------|
| **Messages API** | `anthropic` (Python/TS) | Direct API calls | One-off tasks, quick integration |
| **Agent SDK** | `claude_agent_sdk` (Python) | Build AI agents | Agent applications, long-running conversations |

---

## Quick Start: Choose Your Method

### Method 1: Messages API (Quick Integration)

Use when you need direct API access to Claude with minimal setup.

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude!"}]
)
```

**Reference**: See `knowledge/messages-api-guide.md` for complete Messages API documentation.

### Method 2: Agent SDK (Build AI Agents)

Use when building AI agent applications with conversations and tools.

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

options = ClaudeAgentOptions(
    system_prompt="You are a helpful assistant..."
)

async with ClaudeSDKClient(options) as client:
    await client.query("Hello!")

    async for message in client.receive_response():
        print(message)
```

**Reference**: See `knowledge/agent-sdk-guide.md` for complete Agent SDK documentation.

---

## Decision Tree

```
Need to integrate Claude into your application?
│
├─ Simple request/response?
│  └─ YES → Messages API
│     - Stateless calls
│     - Any language (Python, TypeScript, etc.)
│     - Quick integration
│
└─ Building an AI agent?
   └─ YES → Agent SDK (Python only)
      - Conversational agents
      - Tool integration
      - Skills support
```

---

## Key Differences

| Feature | Messages API | Agent SDK |
|---------|--------------|-----------|
| **State** | Stateless (manage history yourself) | Stateful (automatic) |
| **Tools** | Via API parameters | Via Python configuration |
| **Skills** | `container.skills[]` (cloud) | `setting_sources=["project"]` + `cwd` (local) |
| **Language** | Python, TypeScript, cURL | Python only |
| **Streaming** | Supported | Supported |
| **Cost** | Per token | Per token |

---

## Knowledge Documents

For detailed information, load these documents when needed:

| Topic | Document |
|-------|----------|
| **Messages API** | `knowledge/messages-api-guide.md` |
| **Agent SDK** | `knowledge/agent-sdk-guide.md` |
| **Skills Guide** | `knowledge/skills-guide.md` |
| **Tools Guide** | `knowledge/tools-guide.md` |
| **Code Examples** | `knowledge/code-examples.md` |

---

## Official Manual References

For the complete official documentation, refer to the `official-manual/` directory:

| Document | Description |
|----------|-------------|
| `official-manual/claude-agent-sdk-python.md` | Complete Python SDK API reference |
| `official-manual/using-agent-skills-with-api.md` | Agent Skills with Messages API |

---

## Common Use Cases

### 1. Simple Chat Completion

**Method**: Messages API

```python
response = client.messages.create(
    model="claude-opus-4-6",
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)
```

### 2. Conversational Agent

**Method**: Agent SDK

```python
options = ClaudeAgentOptions(
    system_prompt="You are a customer service agent..."
)

async with ClaudeSDKClient(options) as client:
    # Maintains conversation history automatically
    await client.query("I need help")
    async for message in client.receive_response():
        print(message)

    await client.query("What about my refund?")
    async for message in client.receive_response():
        print(message)
```

### 3. Agent with Tools

**Method**: Agent SDK

```python
options = ClaudeAgentOptions(
    allowed_tools=["Task"],  # Optional: Task is a tool (not in preset)
    setting_sources=["project"]  # For skills (not in allowed_tools)
)
```

### 4. Agent with Cloud Skills

**Method**: Messages API

```python
response = client.beta.messages.create(
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [{"type": "anthropic", "skill_id": "xlsx"}]
    },
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}]
)
```

---

## When to Use Each Method

### Use Messages API when:

- ✅ Making one-off requests
- ✅ Building simple integrations
- ✅ Using languages other than Python
- ✅ Need minimal setup
- ✅ Using pre-built Agent Skills (xlsx, pptx, etc.)

### Use Agent SDK when:

- ✅ Building AI agent applications
- ✅ Need conversational state management
- ✅ Integrating custom tools
- ✅ Using filesystem-based skills
- ✅ Building long-running agent processes

---

## Installation

### Messages API

```bash
pip install anthropic
# or
npm install @anthropic-ai/sdk
```

### Agent SDK

```bash
pip install claude-agent-sdk
```

---

## Next Steps

1. **Choose your method** based on your use case (see Decision Tree above)
2. **Read the appropriate knowledge document**:
   - `knowledge/messages-api-guide.md` for Messages API
   - `knowledge/agent-sdk-guide.md` for Agent SDK
3. **Check official manuals** in `official-manual/` for complete API reference
4. **See code examples** in `knowledge/code-examples.md`

---

## Error Handling

Both methods include comprehensive error handling:

```python
# Messages API
try:
    response = client.messages.create(...)
except anthropic.APIClientError as e:
    print(f"API Error: {e}")

# Agent SDK
async with ClaudeSDKClient(options) as client:
    try:
        await client.query("...")
        async for message in client.receive_response():
            print(message)
    except Exception as e:
        print(f"Agent Error: {e}")
```

---

## Advanced Topics

For advanced usage patterns, see the respective guides:

- **Streaming responses**: `knowledge/agent-sdk-guide.md` - Streaming section
- **Tool integration**: `knowledge/tools-guide.md` - MCP Custom Tools section
- **Skills implementation**: `knowledge/skills-guide.md` - Agent SDK section
- **Error handling**: `knowledge/agent-sdk-guide.md` - Error Handling section
