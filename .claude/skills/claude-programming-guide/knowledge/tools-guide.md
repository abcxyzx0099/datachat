# Tools Guide: Tools, Skills, and Tasks

**Part of**: Claude Programming Guide Skill

Complete guide for understanding and configuring tools, skills, and tasks in Claude Agent SDK.

---

## Concepts Overview

Understanding the distinction between these three concepts in Claude Code and the Agent SDK.

### Tools

Low-level functions that Claude can use directly.

| Tool | Purpose |
|------|---------|
| `Read` | Read file contents |
| `Write` | Create new files |
| `Edit` | Modify existing files |
| `Bash` | Run shell commands |
| `Grep` | Search file contents |
| `Glob` | Find files by pattern |

**Controlled by:** `tools` parameter (presets) and `allowed_tools` parameter (specific tools) in `ClaudeAgentOptions`

### Skills

Higher-level commands invoked by name in the prompt.

| Skill | Example |
|-------|---------|
| `/task-execution` | Executes task documents |
| `/commit` | Creates git commits |
| `/docs-audit` | Reviews documentation |

**NOT controlled by** `tools` parameter. Skills are enabled via `setting_sources=["project"]` + `cwd`.

**How skills work:**
1. Invoked by name in prompt text: `/task-execution`
2. Claude Code CLI intercepts and routes to skill handler
3. Skill internally uses tools to complete its work

```
Prompt: "/task-execution Execute task at: task-xxx.md"
   ↓
CLI routes to /task-execution skill
   ↓
Skill uses Read, Write, Edit tools to complete task
```

### Tasks

Markdown document files containing task specifications.

- Format: `task-YYYYMMDD-HHMMSS-description.md`
- Location: `{project_workspace}/task-monitor/ad-hoc/pending/` or `{project_workspace}/task-monitor/planned/pending/`
- Read and executed by the `/task-execution` skill

**NOT a tool** - just a data file.

### Quick Summary

| Concept | In `tools` parameter? | How invoked |
|---------|---------------------|-------------|
| **Tools** | YES | Configured in `ClaudeAgentOptions` |
| **Skills** | NO | By name in prompt (`/skill-name`) |
| **Tasks** | NO | File path passed to `/task-execution` |

**Key Point**: When using `tools={"type": "preset", "preset": "claude_code"}`:
- You enable **all low-level tools** (Read, Write, Bash, etc.)
- Skills are invoked separately via **prompt text**
- Tasks are executed by the `/task-execution` skill using those tools

---

## Tools Configuration

The Claude Agent SDK provides two parameters for controlling what tools an agent can use:

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `tools` | `list[str] \| ToolsPreset \| None` | `None` | Enable tool groups via preset |
| `allowed_tools` | `list[str]` | `[]` (empty list) | Explicitly allow specific tools |

### Default Values Explained

```python
options = ClaudeAgentOptions()  # No parameters set
```

| Parameter | Default Value | Result |
|-----------|---------------|--------|
| `tools` | `None` | No preset enabled |
| `allowed_tools` | `[]` | No tools explicitly allowed |

**Result**: Agent has **NO tool access** - can only process text (no file operations, no commands, no web access)

---

## Parameter 1: `tools` (Preset-based)

### Definition

```python
tools: list[str] | ToolsPreset | None = None
```

### Purpose

Enable groups of pre-configured tools with a single setting.

### Available Preset Values

| Preset | Description |
|--------|-------------|
| `{"type": "preset", "preset": "claude_code"}` | **All Claude Code tools** enabled |

### Example Usage

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# Enable all Claude Code tools
options = ClaudeAgentOptions(
    tools={"type": "preset", "preset": "claude_code"}
)

async for message in query(
    prompt="Analyze my codebase and fix bugs",
    options=options
):
    print(message)
```

### What `tools="claude_code"` Enables

| Category | Tools |
|----------|-------|
| **File Operations** | `Read`, `Write`, `Edit`, `Glob` |
| **Search** | `Grep` |
| **Execution** | `Bash`, `BashOutput`, `KillBash` |
| **External** | `WebSearch`, `WebFetch` |
| **Other** | `NotebookEdit`, `TodoWrite`, `ExitPlanMode`, `ListMcpResources`, `ReadMcpResource` |

**Important Notes:**
- `Task` is NOT included in the `claude_code` preset - must be added explicitly via `allowed_tools=["Task"]`
- `Skill` is NOT a tool - skills are enabled via `setting_sources=["project"]` and `cwd`, not via `allowed_tools`
- `AskUserQuestion` is NOT included in the `claude_code` preset - must be added explicitly via `allowed_tools`

---

## Parameter 2: `allowed_tools` (Whitelist-based)

### Definition

```python
allowed_tools: list[str] = field(default_factory=list)
```

### Purpose

Explicitly allow only specific tools (whitelist approach).

### Default Behavior

```python
allowed_tools = []  # Empty list = NO tools allowed
```

### Example Usage

```python
# Read-only access
options = ClaudeAgentOptions(
    allowed_tools=["Read"]
)

# File operations only (no execution)
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit"]
)

# Enable subagent launching
options = ClaudeAgentOptions(
    allowed_tools=["Task"]
)

# Enable skills (via setting_sources, NOT allowed_tools)
options = ClaudeAgentOptions(
    setting_sources=["project"],
    cwd="/path/to/project"  # Location of .claude/skills/
)
```

---

## Comparison: `tools` vs `allowed_tools`

| Aspect | `tools` (preset) | `allowed_tools` (whitelist) |
|--------|------------------|----------------------------|
| **Approach** | Enable tool groups | Explicit tool names |
| **Default** | `None` (no tools) | `[]` (no tools) |
| **Best For** | Full tool access | Restricted access |
| **Example** | `tools={"type": "preset", "preset": "claude_code"}` | `allowed_tools=["Read", "Write"]` |

---

## Common Configuration Patterns

### Pattern 1: Full Access (Recommended for Development)

```python
options = ClaudeAgentOptions(
    tools={"type": "preset", "preset": "claude_code"}
)
```

### Pattern 2: Read-Only Agent

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob"]
)
```

### Pattern 3: Subagent-Only

```python
options = ClaudeAgentOptions(
    allowed_tools=["Task"],
    agents={
        "analyzer": {
            "description": "Code analysis agent",
            "prompt": "You are a code analyzer...",
            "tools": ["Read", "Grep"]
        }
    }
)
```

### Pattern 4: Skills-Only

```python
options = ClaudeAgentOptions(
    setting_sources=["project"],  # Load skills from .claude/skills/
    cwd="/path/to/project"         # Skills directory location
)
```

### Pattern 5: Preset + Custom MCP Tools

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("my_tool", "My custom tool", {"param": str})
async def my_tool(args):
    return {"content": [{"type": "text", "text": "Result"}]}

my_server = create_sdk_mcp_server(
    name="my_server",
    tools=[my_tool]
)

options = ClaudeAgentOptions(
    tools={"type": "preset", "preset": "claude_code"},
    mcp_servers={"my_server": my_server},
    allowed_tools=["mcp__my_server__my_tool"]
)
```

---

## Complete Tool Reference

### Built-in Claude Code Tools

| Tool Name | Purpose | Input | Output |
|-----------|---------|-------|--------|
| `Read` | Read file contents | `file_path`, `offset`, `limit` | File content |
| `Write` | Create/overwrite file | `file_path`, `content` | Success message |
| `Edit` | Replace text in file | `file_path`, `old_string`, `new_string` | Replacements made |
| `Grep` | Search in files | `pattern`, `path`, `glob` | Matches found |
| `Glob` | Find files by pattern | `pattern`, `path` | Matching file paths |
| `Bash` | Run shell command | `command`, `timeout` | Command output |
| `BashOutput` | Get background process output | `bash_id` | Process output |
| `KillBash` | Stop background process | `shell_id` | Success message |
| `Task` | Launch subagent | `description`, `prompt`, `subagent_type` | Agent result |
| `AskUserQuestion` | Prompt user for input | `questions` array | User answers |
| `WebSearch` | Search the web | `query` | Search results |
| `WebFetch` | Fetch web content | `url`, `prompt` | Analyzed content |
| `NotebookEdit` | Edit Jupyter notebook | `notebook_path`, `cell_id`, `new_source` | Edit result |
| `TodoWrite` | Manage todo list | `todos` array | Todo stats |
| `ExitPlanMode` | Exit planning mode | `plan` | Approval status |
| `ListMcpResources` | List MCP resources | `server` (optional) | Resources list |
| `ReadMcpResource` | Read MCP resource | `server`, `uri` | Resource content |

---

## MCP Custom Tools

### Creating Custom Tools

```python
from claude_agent_sdk import tool, create_sdk_mcp_server
from typing import Any

@tool("tool_name", "Tool description", {"param": type})
async def my_tool(args: dict[str, Any]) -> dict[str, Any]:
    result = do_work(args.get("param"))
    return {
        "content": [{
            "type": "text",
            "text": result
        }]
    }

server = create_sdk_mcp_server(
    name="server_name",
    version="1.0.0",
    tools=[my_tool]
)
```

### Tool Naming Convention

MCP tools are automatically named:

```
mcp__{server_name}__{tool_name}
```

### Example

```python
# Server: "calculator", Tool: "add"
# Resulting name: "mcp__calculator__add"

options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator_server},
    allowed_tools=["mcp__calc__add", "mcp__calc__multiply"]
)
```

---

## Decision Flowchart

```
Need to configure agent tools?
│
├─ Want all Claude Code tools?
│  └─ YES → Use: tools={"type": "preset", "preset": "claude_code"}
│
├─ Want only specific tools?
│  └─ YES → Use: allowed_tools=["Read", "Write", ...]
│
└─ Want custom MCP tools?
   └─ YES → Use:
      1. Create server with create_sdk_mcp_server()
      2. Add to mcp_servers
      3. Add "mcp__server__tool" to allowed_tools
```

---

## Quick Reference Card

```python
from claude_agent_sdk import ClaudeAgentOptions

# NO TOOLS (default - text only)
ClaudeAgentOptions()

# ALL TOOLS (full access)
ClaudeAgentOptions(
    tools={"type": "preset", "preset": "claude_code"}
)

# SELECTIVE TOOLS (restricted)
ClaudeAgentOptions(
    allowed_tools=["Read", "Write"]
)

# SUBAGENTS ONLY
ClaudeAgentOptions(
    allowed_tools=["Task"],
    agents={...}
)

# SKILLS ONLY (skills enabled via setting_sources, not allowed_tools)
ClaudeAgentOptions(
    setting_sources=["project"],
    cwd="/path/to/project"
)

# CUSTOM MCP TOOLS
ClaudeAgentOptions(
    mcp_servers={"my_server": server},
    allowed_tools=["mcp__my_server__tool_name"]
)
```

---

## Summary

| Scenario | Use |
|----------|-----|
| Full development environment | `tools={"type": "preset", "preset": "claude_code"}` |
| Production with restrictions | `allowed_tools=["specific", "tools"]` |
| Subagent delegation | `allowed_tools=["Task"]` + `agents={...}` |
| AI-powered skills | `setting_sources=["project"]` + `cwd` (skills are NOT tools) |
| Custom operations | `mcp_servers={...}` + `allowed_tools=["mcp__*"]` |

**Key Principle**: Both parameters default to **no tools**. You must explicitly enable tools to give the agent capabilities beyond text processing.
