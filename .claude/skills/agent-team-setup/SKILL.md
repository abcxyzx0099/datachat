---
name: agent-team-setup
description: "Sets up AI agent teams borrowing BMAD Method's philosophy and framework. Investigates Claude Code's agent team functionality and studies BMAD Method concepts (without installation), then configures specialized agents for collaborative development using Claude Code's native capabilities. Use when establishing multi-agent coordination for complex development tasks."
---

# Agent Team Setup

Sets up AI agent teams using **BMAD Method's philosophy and framework as reference**, implementing agent roles and workflows through Claude Code's native agent team capabilities.

> **IMPORTANT**: This skill does NOT install BMAD Method. It borrows BMAD's concepts, patterns, and methodology to structure Claude Code's agent teams effectively.

## Overview

This skill establishes a multi-agent development team by:

1. **Investigating** Claude Code's agent team capabilities
2. **Studying** BMAD Method framework for agent design patterns (reference only)
3. **Configuring** specialized agents based on BMAD's philosophy (implemented via Claude Code)
4. **Establishing** team coordination protocols

**Key Principle**: We borrow BMAD's methodology and patterns, but implement everything using Claude Code's native agent team system—no BMAD installation required.

## Reference Documentation

| Resource | URL | Purpose |
|----------|-----|---------|
| **Claude Code Agent Teams** | https://code.claude.com/docs/en/agent-teams | Understanding Claude's multi-agent coordination |
| **BMAD Method** | https://github.com/bmad-code-org/bmad-method | Reference framework for agent design |
| **BMAD Documentation** | https://bmad-code-org.github.io/bmad-method/ | Complete methodology documentation |

---

## Investigation Phase

### Step 1: Study Claude Code Agent Teams

Using the `claude-code-guide` agent, investigate:

- How agent teams work in Claude Code
- Team lead vs teammate roles
- Communication patterns between agents
- Parallel execution capabilities
- Context window management

### Step 2: Study BMAD Method

Using `context7` MCP server with library ID `/bmad-code-org/bmad-method`, investigate:

- **BMAD's Four Phases**: Analysis, Planning, Solutioning, Implementation
- **Agent Types**: Simple, Expert, Module agents
- **Agent Roles**: DEV (Amelia), PM, UX-Designer, Architect, etc.
- **Workflow Patterns**: 34 workflows across 4 phases
- **Agent Compilation System**: Create, edit, validate paths

### Step 3: Cross-Reference Analysis

Map Claude Code agent team capabilities to BMAD Method concepts:

| BMAD Concept | Claude Code Equivalent |
|--------------|------------------------|
| Expert Agent | Specialized teammate with specific persona/instructions |
| Team Lead | Main Claude Code session coordinating work |
| Four Phases | Task breakdown with specialized roles |
| Workflows | Teammate collaboration patterns |

---

## BMAD Method Quick Reference

### The Four Phases

| Phase | Purpose | Key Agent |
|-------|---------|-----------|
| **Analysis** | Brainstorming, research, product brief | Analyst Agent |
| **Planning** | Requirements, PRD creation | PM Agent |
| **Solutioning** | Architecture design, technical decisions | Architect Agent |
| **Implementation** | Build epic-by-epic, story-by-story | DEV Agent (Amelia) |

### BMAD Agent Types

| Type | Structure | Use Case |
|------|-----------|----------|
| **Simple Agent** | Single YAML file | Basic tasks, single responsibility |
| **Expert Agent** | YAML + sidecars (instructions, memories, templates, knowledge) | Complex domain expertise |
| **Module Agent** | Part of complete module with shared resources | Large-scale project coordination |

---

## Team Setup Workflow

### Phase 1: Enable Agent Teams

First, enable the experimental feature flag in `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### Phase 2: Create Team Configuration

Create team configuration at `~/.claude/teams/{team-name}/config.json`:

```json
{
  "name": "bmad",
  "description": "BMAD Development Team",
  "members": [
    {
      "name": "analyst",
      "role": "Business Analyst",
      "description": "Phase 1: Research and analysis",
      "color": "blue"
    },
    {
      "name": "pm",
      "role": "Product Manager",
      "description": "Phase 2: Requirements and planning",
      "color": "green"
    },
    {
      "name": "architect",
      "role": "System Architect",
      "description": "Phase 3: Architecture and design",
      "color": "yellow"
    },
    {
      "name": "dev",
      "role": "Developer",
      "description": "Phase 4: Implementation",
      "color": "cyan"
    },
    {
      "name": "qa",
      "role": "QA Engineer",
      "description": "Phases 3-4: Quality assurance",
      "color": "magenta"
    }
  ]
}
```

### Phase 3: Create Teammate Instructions

For each teammate, create instruction files at `~/.claude/teams/{team-name}/instructions/{teammate-name}.md`:

```markdown
# Analyst Agent 🔍

## Persona
I am the Business Analyst and Research Specialist...

## Core Principles
- Evidence-based analysis
- Thorough investigation
- Clear documentation

## Key Workflows
### 1. Research & Investigation
[Process details...]
```

### Phase 4: Start Using Agent Teams

1. **Start tmux session** (for parallel teammate views):
   ```bash
   tmux new -s datachat
   ```

2. **Start Claude Code**:
   ```bash
   claude
   ```

3. **Create agent team** conversationally:
   ```
   "Create an agent team with the bmad configuration"
   ```

4. **Assign tasks** to specific teammates as needed

---

## Implementation Checklist

- [ ] Claude Code agent teams investigated and understood
- [ ] BMAD Method framework studied
- [ ] Team requirements defined with user
- [ ] Agent roles selected based on BMAD patterns
- [ ] Team configuration created in `~/.claude/teams/`
- [ ] Teammate instruction files created
- [ ] Feature flag enabled in settings.json
- [ ] tmux session started for parallel views
- [ ] Test run with sample task

---

## Example Team Configuration

### Small Project Team
- **Team Lead**: Main session (you)
- **Teammate 1**: DEV Agent - Implementation specialist
- **Teammate 2**: QA Agent - Testing and validation

### Full BMAD Development Team
- **Team Lead**: Main session (orchestration)
- **Teammate 1**: Analyst Agent - Research and analysis (Phase 1)
- **Teammate 2**: PM Agent - Requirements and planning (Phase 2)
- **Teammate 3**: Architect Agent - System design (Phase 3)
- **Teammate 4**: DEV Agent - Implementation (Phase 4)
- **Teammate 5**: QA Agent - Quality assurance (Phases 3-4)

---

## Commands and Usage

### Investigation Commands

```bash
# Study Claude Code agent teams
# (Use Task tool with claude-code-guide subagent)

# Query BMAD Method documentation
# (Use context7 MCP with /bmad-code-org/bmad-method)
```

### Team Usage

Agent teams are created conversationally within Claude Code—there is no CLI command for launching teams. Simply describe your need:

```
"Create an agent team for implementing a new feature"
```

Claude Code will then create teammates based on your team configuration.

---

## File Structure Reference

```
~/.claude/
├── settings.json              # Feature flag: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
└── teams/
    └── bmad/                  # Team name
        ├── config.json        # Team configuration
        └── instructions/      # Teammate instruction files
            ├── analyst.md
            ├── pm.md
            ├── architect.md
            ├── dev.md
            └── qa.md
```

---

## Notes

- **BMAD as Reference ONLY**: BMAD Method provides the philosophy and framework patterns—we do NOT install it
- **Claude Code Implementation**: All agents are implemented using Claude Code's native agent team system
- **Scale-Adaptive**: Team size adapts to project complexity (BMAD principle borrowed)
- **Iterative**: Team workflows follow BMAD's four-phase approach (Analysis → Planning → Solutioning → Implementation)
- **No External Dependencies**: This skill works entirely within Claude Code's capabilities
- **Team Storage**: Agent Teams are stored globally in `~/.claude/teams/`, not per-project
- **tmux Recommended**: Using tmux allows viewing all teammates simultaneously via split panes

---

## Related Skills

- **task-planning**: Generates organized task lists (BMAD Planning phase)
- **task-execution**: Executes tasks with two-agent workflow (BMAD Implementation)
- **task-documents**: Creates task specifications (BMAD Solutioning)
- **issue-fixer**: Systematic bug resolution (BMAD DEV role)

---

## BMAD Method Core Principles

1. **Scale-Adaptive Intelligence**: Processes adjust based on project complexity
2. **Specialized Agents**: Each agent has unique role, expertise, and personality
3. **Guided Workflows**: 34 workflows across 4 phases provide structure
4. **Natural Language Orchestration**: AI coordination through conversational interfaces
5. **Agentic Agile Development**: Digitizing Agile methodology with AI agents
