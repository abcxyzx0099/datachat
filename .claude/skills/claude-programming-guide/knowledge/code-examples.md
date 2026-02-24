# Code Examples

**Part of**: Claude Programming Guide Skill

Practical code examples for using Claude programmatically.

---

## Table of Contents

1. [Messages API Examples](#messages-api-examples)
2. [Agent SDK Examples](#agent-sdk-examples)
3. [Common Patterns](#common-patterns)

---

## Messages API Examples

### Simple Chat

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.content[0].text)
```

### With System Prompt

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    system="You are a helpful customer service agent.",
    messages=[{"role": "user", "content": "I need help with my order"}]
)
```

### Multi-turn Conversation

```python
conversation = [
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."},
    {"role": "user", "content": "What's the population?"}
]

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=conversation
)
```

### Streaming Response

```python
with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me a joke"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### With Image

```python
import base64

with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image:"},
            {"type": "image", "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": image_data
            }}
        ]
    }]
)
```

### With Tools

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get weather for a location",
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
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools
)

# Handle tool use
for block in response.content:
    if block.type == "tool_use":
        # Execute the tool
        result = get_weather(block.input["location"])

        # Send result back
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": "What's the weather in Tokyo?"},
                {"role": "assistant", "content": response.content},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result)
                        }
                    ]
                }
            ]
        )
```

### With Agent Skills (Beta)

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
    messages=[{"role": "user", "content": "Create a sales report in Excel"}],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}]
)

# Download generated file
if hasattr(response, 'file_id'):
    file_content = client.files.content(response.file_id)
    with open("report.xlsx", "wb") as f:
        f.write(file_content.content)
```

---

## Agent SDK Examples

### Basic Agent

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant."
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("Hello!")
        async for message in client.receive_response():
            print(message)

asyncio.run(main())
```

### Agent with Skills

```python
options = ClaudeAgentOptions(
    system_prompt="You are a data analyst.",
    setting_sources=["project"],  # Load skills from .claude/skills/
    cwd="/path/to/project"         # Skills directory location
)

async with ClaudeSDKClient(options) as client:
    await client.query("Analyze the data")

    async for message in client.receive_response():
        print(message)
```

### Agent with MCP Tools

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("calculate", "Perform calculations", {"expression": str})
async def calculate(args: dict) -> dict:
    expr = args.get("expression")
    result = eval(expr)
    return {"content": [{"type": "text", "text": str(result)}]}

server = create_sdk_mcp_server(
    name="calculator",
    version="1.0.0",
    tools=[calculate]
)

options = ClaudeAgentOptions(
    mcp_servers={"calc": server},
    allowed_tools=["mcp__calc__calculate"]
)

async with ClaudeSDKClient(options) as client:
    await client.query("What is 2 + 2?")

    async for message in client.receive_response():
        print(message)
```

### Streaming with Agent SDK

```python
async with ClaudeSDKClient(options) as client:
    await client.query("Tell me a story")

    task_complete = False
    async for message in client.receive_response():
        if task_complete:
            continue
        if message.type == "content":
            print(message.content, end="", flush=True)
        elif message.type == "end":
            task_complete = True
```

### Using query() Helper

```python
from claude_agent_sdk import query

response = await query(
    system_prompt="You are a translator.",
    message="Translate 'Hello' to Spanish.",
    options=ClaudeAgentOptions()
)

print(response)
```

---

## Common Patterns

### Retry Logic

```python
import time
from anthropic import APIClientError

def create_with_retry(client, **kwargs):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return client.messages.create(**kwargs)
        except APIClientError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Rate Limit Handling

```python
from anthropic import RateLimitError

try:
    response = client.messages.create(...)
except RateLimitError:
    # Wait and retry
    time.sleep(60)
    response = client.messages.create(...)
```

### Token Counting

```python
response = client.messages.create(...)

usage = response.usage
print(f"Input tokens: {usage.input_tokens}")
print(f"Output tokens: {usage.output_tokens}")
print(f"Total tokens: {usage.input_tokens + usage.output_tokens}")
```

### Structured Output

```python
import json

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Return data as JSON with keys: name, age, city"
    }]
)

# Parse JSON from response
data = json.loads(response.content[0].text)
```

### Multi-Agent Orchestration

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

# Define agents
researcher_opts = ClaudeAgentOptions(
    system_prompt="You are a researcher. Find information."
)

writer_opts = ClaudeAgentOptions(
    system_prompt="You are a writer. Create content."
)

async def research_and_write(topic):
    # Research
    async with ClaudeSDKClient(researcher_opts) as researcher:
        research = await researcher.query(f"Research: {topic}")

    # Write
    async with ClaudeSDKClient(writer_opts) as writer:
        article = await writer.query(f"Write article based on: {research}")

    return article
```

### Conversation State Management (Messages API)

```python
class ConversationManager:
    def __init__(self, system_prompt=None):
        self.messages = []
        if system_prompt:
            self.system = system_prompt

    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content):
        self.messages.append({"role": "assistant", "content": content})

    def chat(self, user_message, client):
        self.add_user_message(user_message)

        kwargs = {"messages": self.messages}
        if hasattr(self, 'system'):
            kwargs["system"] = self.system

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            **kwargs
        )

        assistant_message = response.content[0].text
        self.add_assistant_message(assistant_message)

        return assistant_message

# Usage
conv = ConversationManager(system_prompt="You are a helpful assistant.")
response1 = conv.chat("Hello!", client)
response2 = conv.chat("Tell me more", client)
```

---

## TypeScript Examples

### Basic Request

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

const response = await client.messages.create({
  model: 'claude-opus-4-6',
  maxTokens: 1024,
  messages: [{ role: 'user', content: 'Hello!' }]
});

console.log(response.content[0].text);
```

### Streaming

```typescript
const stream = await client.messages.create({
  model: 'claude-opus-4-6',
  maxTokens: 1024,
  messages: [{ role: 'user', content: 'Tell me a story' }],
  stream: true
});

for await (const event of stream) {
  if (event.type === 'content_block_delta') {
    process.stdout.write(event.delta.text);
  }
}
```

---

## cURL Examples

### Basic Request

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### With Streaming

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```
