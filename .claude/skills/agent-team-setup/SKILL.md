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
| Expert Agent | Specialized sub-agent with specific persona |
| Module Agent | Agent with access to specific tools/knowledge |
| Team Lead | Main Claude Code session coordinating work |
| Four Phases | Task breakdown with specialized roles |
| Workflows | Skill-based task execution |

---

## BMAD Method Quick Reference

### The Four Phases

| Phase | Purpose | Key Agent |
|-------|---------|-----------|
| **Analysis** | Brainstorming, research, product brief | Innovation Agent |
| **Planning** | Requirements, PRD creation | PM Agent |
| **Solutioning** | Architecture design, technical decisions | Architect Agent |
| **Implementation** | Build epic-by-epic, story-by-story | DEV Agent (Amelia) |

### BMAD Agent Types

| Type | Structure | Use Case |
|------|-----------|----------|
| **Simple Agent** | Single YAML file | Basic tasks, single responsibility |
| **Expert Agent** | YAML + sidecars (instructions, memories, templates, knowledge) | Complex domain expertise |
| **Module Agent** | Part of complete module with shared resources | Large-scale project coordination |

### Key BMAD Modules

| Module | Description |
|--------|-------------|
| **BMM (BMad Method)** | Core agile framework - 34 workflows, 4 phases |
| **BMB (BMad Builder)** | Custom agent creation and module development |
| **CIS (Creative Intelligence Suite)** | Innovation and brainstorming workflows |

---

## Team Setup Workflow

### Phase 1: Define Team Requirements

Ask the user:

1. **Project Scope**: What is the team building?
2. **Complexity Level**: Simple feature vs enterprise platform
3. **Domain Areas**: Technical, creative, business, research?
4. **Team Size**: How many specialized roles needed?

### Phase 2: Select Agent Roles

Based on BMAD's agent roles, select appropriate specialists:

| Role | BMAD Reference | Responsibilities |
|------|----------------|------------------|
| **PM** | BMAD PM Agent | Requirements, PRD, planning |
| **Architect** | BMAD Architect | System design, ADRs, technical decisions |
| **DEV** | BMAD DEV (Amelia) | Implementation, code review, testing |
| **UX-Designer** | BMAD UX-Designer | User experience, interface design |
| **QA-Tester** | BMAD extension | Quality assurance, test coverage |
| **Innovator** | BMAD CIS module | Brainstorming, creative solutions |

### Phase 3: Configure Agent Skills

Create or configure skills for each agent role based on BMAD patterns:

```
.claude/skills/
├── pm-agent/          # Product Management
├── architect-agent/   # Architecture & Design
├── dev-agent/         # Development & Code Review
├── ux-agent/          # UX Design
├── qa-agent/          # Quality Assurance
└── innovation-agent/  # Creative Intelligence
```

### Phase 4: Establish Team Coordination

Define team coordination rules:

- **Team Lead**: Main session orchestrates work
- **Task Assignment**: Delegate to specialized agents
- **Communication**: Direct agent-to-agent coordination
- **Result Synthesis**: Team lead combines outputs
- **Iteration**: Feedback loops for quality

---

## Implementation Checklist

- [ ] Claude Code agent teams investigated and understood
- [ ] BMAD Method framework studied
- [ ] Team requirements defined with user
- [ ] Agent roles selected based on BMAD patterns
- [ ] Agent skills configured/created
- [ ] Team coordination protocols established
- [ ] Test run with sample task

---

## Example Team Configuration

### Small Project Team
- **Team Lead**: Main session (you)
- **Teammate 1**: DEV Agent - Implementation specialist
- **Teammate 2**: QA Agent - Testing and validation

### Full Development Team
- **Team Lead**: Main session (orchestration)
- **Teammate 1**: PM Agent - Requirements and planning
- **Teammate 2**: Architect Agent - System design
- **Teammate 3**: DEV Agent - Implementation
- **Teammate 4**: QA Agent - Quality assurance

---

## Commands and Usage

### Investigation Commands

```bash
# Study Claude Code agent teams
# (Use Task tool with claude-code-guide subagent)

# Query BMAD Method documentation
# (Use context7 MCP with /bmad-code-org/bmad-method)
```

### Team Launch Commands

```bash
# Launch agent team (when supported by Claude Code)
/agent-team launch --roles pm,architect,dev,qa

# Delegate task to specific agent
/agent-team delegate --role dev --task "Implement login feature"
```

---

## Notes

- **BMAD as Reference ONLY**: BMAD Method provides the philosophy and framework patterns—we do NOT install it
- **Claude Code Implementation**: All agents are implemented using Claude Code's native agent team system
- **Scale-Adaptive**: Team size adapts to project complexity (BMAD principle borrowed)
- **Iterative**: Team workflows follow BMAD's four-phase approach (Analysis → Planning → Solutioning → Implementation)
- **No External Dependencies**: This skill works entirely within Claude Code's capabilities

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
