# Skills Guide: Messages API vs Agent SDK

**Part of**: Claude Programming Guide Skill

Complete guide for using Claude Agent Skills with both Messages API and Claude Agent SDK.

---

## Overview

Claude Agent Skills can be used in two different ways with different formats and purposes:

| Aspect | Messages API | Agent SDK |
|--------|--------------|-----------|
| **SDK** | `anthropic` (Python/TypeScript) | `claude_agent_sdk` (Python only) |
| **Purpose** | Direct API calls to Claude | Building AI agent applications |
| **Parameter** | `container.skills[]` | `setting_sources=["project"]` + `cwd` |
| **Skill Storage** | Cloud-hosted (Anthropic or Custom) | Local filesystem (`.claude/skills/`) |
| **Skill Format** | Uploaded via Skills API | `SKILL.md` files |
| **Code Execution** | Required (`code_execution_20250825`) | Built-in |
| **Use Case** | Quick integration, one-off tasks | Long-running agent applications |

---

## Method 1: Messages API (Cloud Skills)

### Description

Use Anthropic's Messages API directly with Agent Skills. Skills are specified in the `container` parameter and execute in a cloud code execution environment.

### Prerequisites

```bash
pip install anthropic
```

### Beta Headers Required

- `code-execution-2025-08-25` - Enables code execution
- `skills-2025-10-02` - Enables Skills API
- `files-api-2025-04-14` - For file uploads/downloads

### Code Example

```python
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [
            {"type": "anthropic", "skill_id": "xlsx", "version": "latest"},
            {"type": "custom", "skill_id": "skill_01AbCd...", "version": "latest"}
        ]
    },
    messages=[{"role": "user", "content": "Create an Excel report"}],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}]
)
```

### Skill Types

| Type | Description | Example IDs |
|------|-------------|-------------|
| **anthropic** | Pre-built by Anthropic | `xlsx`, `pptx`, `docx`, `pdf` |
| **custom** | Uploaded via Skills API | `skill_01AbCdEfGhIjKlMnOpQrStUv` |

### Managing Custom Skills

```python
# Create a skill
skill = client.beta.skills.create(
    name="my-skill",
    description="My custom skill",
    # ... skill configuration
)

# Use the skill
response = client.beta.messages.create(
    container={
        "skills": [{"type": "custom", "skill_id": skill.id, "version": "latest"}]
    },
    ...
)
```

### When to Use Messages API

- ✅ Using pre-built skills (xlsx, pptx, docx, pdf)
- ✅ Quick one-off tasks
- ✅ Direct API integration
- ✅ Simple automation scripts
- ✅ Skills are simple and self-contained
- ✅ Building stateless applications

---

## Method 2: Agent SDK (Local Skills)

### Description

Use the Claude Agent SDK to build AI agent applications with filesystem-based skills stored locally as `SKILL.md` files.

### Prerequisites

```bash
pip install claude-agent-sdk
```

### Code Example

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
import asyncio

async def main():
    options = ClaudeAgentOptions(
        setting_sources=["project"],  # Load from .claude/skills/
        cwd="/path/to/project",       # Skills directory location
        system_prompt="You are a helpful assistant..."
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("Help me with a task")

        async for message in client.receive_response():
            print(message)

asyncio.run(main())
```

### Skill Storage

Skills are stored as markdown files:

```
.claude/skills/
├── my-skill/
│   └── SKILL.md
└── another-skill/
    ├── SKILL.md
    ├── references/      # Documentation
    ├── scripts/         # Executable code
    └── assets/          # Templates, files
```

### SKILL.md Format

```markdown
---
name: my-skill
description: Description of when to use this skill
---

# My Skill

Instructions for Claude...
```

### When to Use Agent SDK

- ✅ Building AI agent applications
- ✅ Long-running conversations
- ✅ Custom domain-specific skills
- ✅ Require frequent skill updates
- ✅ Need full control over skill content
- ✅ Skills need to access local resources
- ✅ Building stateful conversational agents

---

## Feature Comparison

### Skill Management

| Feature | Messages API | Agent SDK |
|---------|--------------|-----------|
| Create skills | Via Skills API | Create files |
| Update skills | Via Skills API | Edit files |
| Delete skills | Via Skills API | Delete files |
| Version skills | Automatic | Git/version control |

### Execution

| Feature | Messages API | Agent SDK |
|---------|--------------|-----------|
| Environment | Cloud code execution | Local execution |
| File access | Via Files API | Direct filesystem access |
| Network access | Restricted | Full access |
| Dependencies | Pre-installed | User-controlled |

### Cost

| Aspect | Messages API | Agent SDK |
|--------|--------------|-----------|
| Token cost | Per token | Per token |
| Execution cost | Code execution time | None (local) |
| Storage | Cloud storage | Local disk |

---

## Decision Tree

```
Need to use Claude Agent Skills?
│
├─ Quick one-off task?
│  └─ YES → Messages API
│     - Direct API call
│     - Pre-built skills (xlsx, pptx, etc.)
│
└─ Building an agent application?
   └─ YES → Agent SDK
      - Long-running conversations
      - Custom filesystem-based skills
      - Full control over skills
```

---

## Migration Path

### Starting with Messages API

Use the Messages API when:
- Prototyping a use case
- Need quick results
- Using pre-built skills only

### Moving to Agent SDK

Migrate to Agent SDK when:
- Building production agent applications
- Need custom skills
- Require stateful conversations

### Migration Example

```python
# Messages API (initial prototype)
response = client.beta.messages.create(
    container={"skills": [{"type": "anthropic", "skill_id": "xlsx"}]},
    messages=[{"role": "user", "content": "..."}],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}]
)

# → Agent SDK (production)

# 1. Create local skill directory
# .claude/skills/excel-processor/SKILL.md

# 2. Configure SDK
options = ClaudeAgentOptions(
    setting_sources=["project"],
    cwd="/path/to/project"  # Contains local SKILL.md files
)

# 3. Use in agent
async with ClaudeSDKClient(options) as client:
    await client.query("Process this Excel file")

    async for message in client.receive_response():
        print(message)
```

---

## Summary

| Aspect | Messages API | Agent SDK |
|--------|--------------|-----------|
| **Setup** | API keys + SDK | Local files + SDK |
| **Skills** | Cloud-hosted | Local files |
| **Best for** | Quick integration | Agent applications |
| **Control** | Limited | Full |
| **Cost** | Higher (execution) | Lower (local) |
