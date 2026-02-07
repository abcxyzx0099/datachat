# Tools, Skills, and Tasks in Claude Code

Understanding the distinction between these three concepts in Claude Code and the Agent SDK.

---

## Tools

Low-level functions that Claude can use directly.

| Tool | Purpose |
|------|---------|
| `Read` | Read file contents |
| `Write` | Create new files |
| `Edit` | Modify existing files |
| `Bash` | Run shell commands |
| `Grep` | Search file contents |
| `Glob` | Find files by pattern |

**Controlled by:** `tools` parameter in `ClaudeAgentOptions`

```python
tools={"type": "preset", "preset": "claude_code"}  # All Claude Code tools
tools=["Read", "Write", "Edit"]  # Specific tools only
```

---

## Skills

Higher-level commands invoked by name in the prompt.

| Skill | Example |
|-------|---------|
| `/task-execution` | Executes task documents |
| `/commit` | Creates git commits |
| `/docs-audit` | Reviews documentation |

**NOT controlled by** `tools` parameter.

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

---

## Tasks

Markdown document files containing task specifications.

- Format: `task-YYYYMMDD-HHMMSS-description.md`
- Location: `{project_workspace}/tasks/ad-hoc/pending/` or `{project_workspace}/tasks/planned/pending/`
- Read and executed by the `/task-execution` skill

**NOT a tool** - just a data file.

---

## Summary

| Concept | In `tools` parameter? | How invoked |
|---------|---------------------|-------------|
| **Tools** | YES | Configured in `ClaudeAgentOptions` |
| **Skills** | NO | By name in prompt (`/skill-name`) |
| **Tasks** | NO | File path passed to `/task-execution` |

---

## Key Point

When using `tools={"type": "preset", "preset": "claude_code"}`:
- You enable **all low-level tools** (Read, Write, Bash, etc.)
- Skills are invoked separately via **prompt text**
- Tasks are executed by the `/task-execution` skill using those tools
