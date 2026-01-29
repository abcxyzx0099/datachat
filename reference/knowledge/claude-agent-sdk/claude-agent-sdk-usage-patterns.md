# Claude Agent SDK Usage Patterns

**Category**: Guide
**Layer**: Agent
**Granularity**: Low
**Stage**: Development
**Runtime**: Backend

**Note**: This document covers MCP Tools and Skills patterns for extending Claude Agent SDK capabilities.

---

## Architecture

dataflow uses a two-runtime, two-agent, two-paradigm architecture. See [System Architecture Overview](../system-docs/system-architecture-overview.md) for details.

---

## Overview

The Claude Agent SDK supports two distinct patterns for extending Claude's capabilities:

| Pattern | Purpose | Control | Invocation | Use Case |
|---------|---------|---------|------------|----------|
| **MCP Tools** | Deterministic operations | Application | Tool calls | SPSS analysis, data processing |
| **Skills** | AI-powered capabilities | Model | Autonomous | Configuration generation, complex reasoning |

---

## Pattern 1: MCP Tools (Deterministic)

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

@tool("load_spss_file", "Load an SPSS .sav file for analysis", {
    "file_path": str
})
async def load_spss_file(args: dict[str, Any]) -> dict[str, Any]:
    """Load an SPSS file and return metadata."""
    file_path = args.get("file_path")

    # Direct SPSS processing
    data = load_spss_data(file_path)
    variables = extract_variables(data)

    return {
        "content": [{
            "type": "text",
            "text": json.dumps({
                "success": True,
                "variable_count": len(variables),
                "variables": variables
            })
        }]
    }

# Create MCP server
SPSS_MCP_SERVER = create_sdk_mcp_server(
    name="spss",
    version="1.0.0",
    tools=[load_spss_file, ...]
)

# Configure agent to use tools
options = ClaudeAgentOptions(
    mcp_servers={"spss": SPSS_MCP_SERVER},
    allowed_tools=["mcp__spss__load_spss_file", ...]
)
```

### Tool Naming Convention

Tools are automatically named: `mcp__{server_name}__{tool_name}`

- `mcp__spss__load_spss_file`
- `mcp__spss__frequency_analysis`
- `mcp__spss__crosstab_analysis`

### When to Use MCP Tools

Use MCP Tools when:
- ✅ Operation requires **deterministic** execution
- ✅ You need **direct control** over when code runs
- ✅ Operation doesn't require AI reasoning
- ✅ You want to wrap existing Python functions

Examples:
- Loading SPSS files
- Running frequency analysis
- Generating charts
- Database operations
- File I/O operations

---

## Pattern 2: Skills (AI-Powered)

### Definition

Skills are filesystem-based capabilities defined as `SKILL.md` files. Claude **autonomously** decides when to use them based on context and task requirements.

### Characteristics

- **Model-controlled**: Claude decides when to invoke
- **Contextual**: Triggered by task description match
- **Filesystem-based**: Stored as markdown files
- **AI-powered**: Can handle complex reasoning

### File Structure

```
production/.claude/skills/config-generator/
└── SKILL.md
```

### SKILL.md Example

```markdown
---
name: config-generator
description: Generate row/column configuration YAML for SPSS crosstab analysis. Use when user needs to create row configurations, column configurations, or variable groupings.
---

# Configuration Generator Skill

You are a specialized agent for generating SPSS/PSPP crosstab configuration YAML files.

## Output Structure

Generate ONLY valid YAML in this format:

```yaml
row_items:
  - id: ri-001
    code: age_groups
    label: Age Groups
    child_variables:
      - age
    is_multiple_response: false
    statistic: percentage
```

## Output Rules

1. **YAML only**: No markdown code blocks, no explanations
2. **Valid syntax**: Proper indentation, no trailing spaces
3. **Existing variables only**: Only use variables provided in context
```

### Code Configuration

```python
from claude_agent_sdk import ClaudeAgentOptions

def get_production_cwd() -> str:
    """Get production directory for skills."""
    backend_dir = Path(__file__).parent.resolve()
    project_root = backend_dir.parent.parent
    production_dir = project_root / "production"
    return str(production_dir)

options = ClaudeAgentOptions(
    cwd=get_production_cwd(),          # Skills location
    setting_sources=["project"],        # Load from .claude/skills/
    allowed_tools=["Skill"],            # Enable skill invocation
    system_prompt="You are a SPSS analyst..."
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

---

## Comparison Summary

| Aspect | MCP Tools | Skills |
|--------|-----------|--------|
| **Invocation** | Application-controlled (deterministic) | Model-controlled (autonomous) |
| **Definition** | Python code with `@tool` | Markdown `SKILL.md` files |
| **Location** | In Python modules | `production/.claude/skills/` |
| **Return** | Direct return values | Via agent response stream |
| **Use Case** | Data processing, SPSS operations | Configuration, code generation |

---

## Architecture in dataflow

### Current Implementation

```
Development Environment                    Production Environment
-----------------------                    ---------------------
.claude/skills/                           production/.claude/skills/
├── developer/                            ├── config-generator/     ← Skill
├── pspp-teacher/                         └── skill-creator/
└── git-helper/

web/backend/
├── claude_tools.py                       ← MCP Tools (@tool decorator)
├── claude_agent.py                       ← Agent configuration
└── analysis/                             ← Analysis logic
```

### Agent Configuration

```python
# Main SPSS Analyst Agent
options = ClaudeAgentOptions(
    cwd=get_production_cwd(),              # Production skills
    setting_sources=["project"],            # Load skills
    mcp_servers={"spss": SPSS_MCP_SERVER}, # MCP tools
    allowed_tools=list(SPSS_TOOL_NAMES) + ["Skill"],  # Both!
    system_prompt=SPSS_SYSTEM_PROMPT
)
```

### User Request Flow

```
User: "Generate row config for age groups"
    ↓
Main Agent recognizes config request (from system prompt)
    ↓
Main Agent autonomously invokes config-generator skill
    ↓
Skill generates YAML configuration
    ↓
Main Agent presents result to user
```

```
User: "Show frequency table for gender"
    ↓
Main Agent recognizes frequency analysis request
    ↓
Main Agent calls mcp__spss__frequency_analysis tool
    ↓
Tool executes SPSS processing
    ↓
Main Agent presents result to user
```

---

## Decision Tree

```
Need to extend Claude's capabilities?
│
├─ Requires deterministic execution?
│  └─ YES → Use MCP Tools
│     - SPSS operations
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

## Migration from Agno

When migrating from Agno to Claude Agent SDK:

| Agno Concept | Claude SDK Equivalent |
|--------------|----------------------|
| `@tool` decorator (direct return) | MCP Tool with `{"content": [{"type": "text", "text": "..."}]}` |
| `@tool` with nested agent call | Skill (filesystem-based) |
| Agent subprocess | `ClaudeSDKClient` with tools/skills |
| Tool permissions | `allowed_tools` + `permission_mode` |

---

## References

- [System Architecture Overview](../system-docs/system-architecture-overview.md) - Overall architecture
- **Official Docs**: `/home/admin/workspaces/dataflow/docs/external-official-manual/claude-agent-sdk/`
  - `custom-tools.md` - MCP Tools documentation
  - `agent-skills-in-the-sdk.md` - Skills documentation
- **Examples**: `/home/admin/workspaces/claude-agent-sdk-python/examples/`
  - `mcp_calculator.py` - Tool pattern
  - `streaming_mode.py` - Agent usage
- **Production Skills**: `/home/admin/workspaces/dataflow/agent/.claude/skills/`
  - `config-generator/SKILL.md` - Example skill
- **Tools Code**: `/home/admin/workspaces/dataflow/web/backend/claude_tools.py`

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

1. Create directory: `production/.claude/skills/my-skill/`
2. Create `SKILL.md` with:
   - YAML frontmatter (name, description)
   - Markdown instructions for Claude
3. Add `"Skill"` to `allowed_tools`
4. Set `cwd` to production directory
5. Set `setting_sources=["project"]`

---

**Document Version**: 1.0
**Last Updated**: 2025-12-31
**Related**: Agno to Claude SDK Migration Plan
