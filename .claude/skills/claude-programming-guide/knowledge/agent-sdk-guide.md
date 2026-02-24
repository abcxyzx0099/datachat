# Agent SDK Guide

**Part of**: Claude Programming Guide Skill

Complete guide for using the Claude Agent SDK to build AI agent applications in Python.

---

## Overview

The Claude Agent SDK is designed for building AI agent applications with conversations, tools, and skills. It manages state, handles streaming, and provides a Pythonic interface for agent development.

## Installation

```bash
pip install claude-agent-sdk
```

---

## Basic Usage

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant."
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("Hello, Claude!")

        async for message in client.receive_response():
            print(message)

asyncio.run(main())
```

---

## Configuration

### ClaudeAgentOptions

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `system_prompt` | string | - | System prompt for the agent |
| `tools` | `ToolsPreset \| None` | `None` | Enable tool groups via preset |
| `allowed_tools` | list | `[]` | Tools agent can use |
| `mcp_servers` | dict | `{}` | MCP servers with tools |
| `setting_sources` | list | `[]` | Sources for settings (e.g., `["project"]`) |
| `cwd` | string | `.` | Current working directory for skills |
| `permission_mode` | string | - | Tool permission mode |
| `interrupts` | bool | `false` | Enable interrupts |
| `hooks` | object | - | Lifecycle hooks |
| `agents` | dict | `{}` | Subagent configurations |

### Example Configuration

```python
options = ClaudeAgentOptions(
    system_prompt="You are a data analyst assistant.",
    tools={"type": "preset", "preset": "claude_code"},  # All Claude Code tools
    setting_sources=["project"],  # For skills
    cwd="/path/to/project",  # Skills directory
    permission_mode="auto"
)
```

---

## Extending Capabilities

The Claude Agent SDK supports two distinct patterns for extending Claude's capabilities:

| Pattern | Purpose | Control | Invocation | Use Case |
|---------|---------|---------|------------|----------|
| **MCP Tools** | Deterministic operations | Application | Tool calls | Data processing, API calls |
| **Skills** | AI-powered capabilities | Model | Autonomous | Configuration generation, complex reasoning |

---

## MCP Tools (Deterministic)

### Definition

MCP (Model Context Protocol) Tools are programmatic functions defined with the `@tool` decorator. They provide **deterministic** operations that the application controls directly.

### Characteristics

- **Application-controlled**: Your code decides when to execute
- **Deterministic**: Same input always produces same output
- **Programmatic**: Defined in Python code, not filesystem
- **Direct return**: Values returned directly to caller

### Code Example

```python
from claude_agent_sdk import tool, create_sdk_mcp_server
from typing import Any

@tool("calculate", "Perform a calculation", {"expression": str})
async def calculate(args: dict[str, Any]) -> dict[str, Any]:
    """Perform a mathematical calculation."""
    expr = args.get("expression")
    result = eval(expr)
    return {
        "content": [{
            "type": "text",
            "text": str(result)
        }]
    }

# Create MCP server
CALC_SERVER = create_sdk_mcp_server(
    name="calculator",
    version="1.0.0",
    tools=[calculate]
)

# Configure agent to use tools
options = ClaudeAgentOptions(
    mcp_servers={"calc": CALC_SERVER},
    allowed_tools=["mcp__calc__calculate"]
)
```

### Tool Naming Convention

Tools are automatically named: `mcp__{server_name}__{tool_name}`

- `mcp__calculator__add`
- `mcp__spss__load_file`
- `mcp__database__query`

### When to Use MCP Tools

Use MCP Tools when:
- ✅ Operation requires **deterministic** execution
- ✅ You need **direct control** over when code runs
- ✅ Operation doesn't require AI reasoning
- ✅ You want to wrap existing Python functions

Examples:
- Database operations
- API calls
- File I/O operations
- Data processing
- Mathematical calculations

---

## Skills (AI-Powered)

### Definition

Skills are filesystem-based capabilities defined as `SKILL.md` files. Claude **autonomously** decides when to use them based on context and task requirements.

### Characteristics

- **Model-controlled**: Claude decides when to invoke
- **Contextual**: Triggered by task description match
- **Filesystem-based**: Stored as markdown files
- **AI-powered**: Can handle complex reasoning

### File Structure

```
.claude/skills/
└── config-generator/
    └── SKILL.md
```

### SKILL.md Example

```markdown
---
name: config-generator
description: Generate configuration YAML for analysis. Use when user needs to create configurations.
---

# Configuration Generator Skill

You are a specialized agent for generating configuration YAML files.

## Output Structure

Generate ONLY valid YAML in this format:

```yaml
items:
  - id: item-001
    code: variable_name
    label: Variable Label
```

## Output Rules

1. **YAML only**: No markdown code blocks, no explanations
2. **Valid syntax**: Proper indentation, no trailing spaces
```

### Code Configuration

```python
options = ClaudeAgentOptions(
    cwd="/path/to/project",  # Skills location
    setting_sources=["project"]  # Load from .claude/skills/
)
```

### When to Use Skills

Use Skills when:
- ✅ Task requires **AI reasoning** and interpretation
- ✅ You want Claude to **autonomously** decide when to use capability
- ✅ Logic is **complex** and benefits from LLM understanding
- ✅ You want **separation** between code and prompts

Examples:
- Configuration generation (YAML, JSON)
- Code generation from natural language
- Complex data transformations
- Report generation
- Natural language to structured output

**Important**: Skills are NOT tools - they don't go in `allowed_tools`. Enable via `setting_sources=["project"]` + `cwd`.

---

## MCP Tools vs Skills Comparison

| Aspect | MCP Tools | Skills |
|--------|-----------|--------|
| **Invocation** | Application-controlled (deterministic) | Model-controlled (autonomous) |
| **Definition** | Python code with `@tool` | Markdown `SKILL.md` files |
| **Location** | In Python modules | `.claude/skills/` |
| **Return** | Direct return values | Via agent response stream |
| **Use Case** | Data processing, API calls | Configuration, code generation |

---

## Streaming

The SDK supports streaming responses:

```python
async with ClaudeSDKClient(options) as client:
    await client.query("Tell me a story")

    async for message in client.receive_response():
        if message.type == "content":
            print(message.content, end="", flush=True)
```

### Important: Asyncio Cleanup Caution

When iterating messages, **avoid using `break`** to prevent asyncio cleanup issues including resource leaks and hanging connections.

```python
# ❌ WRONG - Causes asyncio cleanup issues
async for message in client.receive_response():
    if some_condition:
        break  # Don't do this!

# ✅ CORRECT - Uses flag pattern
task_complete = False

async for message in client.receive_response():
    if task_complete:
        continue  # Skip but don't break

    if message.type == "success":
        result = message.result
        task_complete = True  # Set flag, let loop continue
```

---

## Conversation History

The SDK automatically manages conversation history:

```python
async with ClaudeSDKClient(options) as client:
    # First message
    await client.query("What is Python?")
    async for message in client.receive_response():
        print(message)

    # Follow-up message with context
    await client.query("Show me an example")
    async for message in client.receive_response():
        print(message)
```

---

## Error Handling

```python
from claude_agent_sdk import ClaudeAgentError

async with ClaudeSDKClient(options) as client:
    try:
        await client.query("Help me")
        async for message in client.receive_response():
            print(message)
    except ClaudeAgentError as e:
        print(f"Agent error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

---

## Advanced Features

### Hooks

Define lifecycle hooks:

```python
from claude_agent_sdk import HookConfig

hooks = HookConfig(
    on_before_tool_call=lambda tool_name, args: print(f"Calling {tool_name}"),
    on_after_tool_call=lambda tool_name, result: print(f"{tool_name} returned")
)

options = ClaudeAgentOptions(hooks=hooks)
```

### Interrupts

Enable user interrupts during tool execution:

```python
options = ClaudeAgentOptions(
    interrupts=True,
    permission_mode="manual"
)
```

### Subagents

Enable task delegation:

```python
options = ClaudeAgentOptions(
    allowed_tools=["Task"],
    agents={
        "researcher": ClaudeAgentOptions(
            system_prompt="You are a researcher..."
        ),
        "writer": ClaudeAgentOptions(
            system_prompt="You are a writer..."
        )
    }
)
```

---

## Comparison: query() vs ClaudeSDKClient

| Feature | `query()` | `ClaudeSDKClient` |
|---------|-----------|-------------------|
| Session | New each time | Reuses same session |
| Conversation | Single exchange | Multiple exchanges |
| Connection | Auto-managed | Manual control |
| Streaming | ✅ | ✅ |
| Interrupts | ❌ | ✅ |
| Hooks | ❌ | ✅ |
| Custom Tools | ❌ | ✅ |
| Use Case | One-off tasks | Continuous conversations |

### Using query()

```python
from claude_agent_sdk import query

response = await query(
    system_prompt="You are a helpful assistant.",
    message="Hello!",
    options=ClaudeAgentOptions()
)
```

---

## Decision Tree

```
Need to extend Claude's capabilities?
│
├─ Requires deterministic execution?
│  └─ YES → Use MCP Tools
│     - API calls
│     - Data processing
│     - Database queries
│
└─ Requires AI reasoning/interpretation?
   └─ YES → Use Skills
      - Configuration generation
      - Natural language → structured output
      - Complex decision-making
```

---

## Quick Reference

### Creating a New MCP Tool

```python
@tool("tool_name", "Description", {"param": type})
async def my_tool(args: dict[str, Any]) -> dict[str, Any]:
    result = do_something(args.get("param"))
    return {"content": [{"type": "text", "text": json.dumps(result)}]}
```

### Creating a New Skill

1. Create directory: `.claude/skills/my-skill/`
2. Create `SKILL.md` with:
   - YAML frontmatter (name, description)
   - Markdown instructions for Claude
3. Set `cwd` to project directory
4. Set `setting_sources=["project"]`

**Note**: Skills are NOT tools - they don't go in `allowed_tools`

---

## Best Practices

1. **Use async context managers** - `async with ClaudeSDKClient(...)`
2. **Set appropriate allowed_tools** - Only enable needed tools
3. **Configure permission_mode** - Based on your security needs
4. **Handle cleanup properly** - Avoid `break` in message iteration
5. **Use hooks for logging** - Track tool calls and responses
