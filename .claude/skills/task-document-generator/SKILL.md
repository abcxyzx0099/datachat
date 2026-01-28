---
name: task-document-generator
description: "Generates structured task documents from conversation context for delegation to Worker Agents. Use when: a task identified in conversation needs to be implemented by another agent; you need to convert user requirements into a clear, actionable task document; the task is complex enough to require independent verification through the agent-delegation-auditor skill."
---

# Task Document Generator

## Purpose

Convert conversation context and user requirements into a structured task document that can be passed to the `agent-delegation-auditor` skill.

## When to Use

Call this skill when:
- A conversation has identified a task that needs implementation
- The task is complex enough to benefit from a Worker Agent + Auditor workflow
- You need to transform discussion into clear, actionable requirements

## Input

You will receive:
- **Conversation history** - The discussion between user and AI
- **Context** - Project context (codebase, architecture, current state)
- **Task intent** - What needs to be done (may be implied from conversation)

## Output

Generate a structured task document in the following format AND save it to a file.

### File Location

**Directory**: `temp/tasks/` (project root)

**Naming Convention**: `{YYYYMMDD}-{HHMMSS}-{slug}.md`

**Example file paths**:
- `temp/tasks/20250113-143052-fix-auth-timeout.md`
- `temp/tasks/20250113-150230-indicator-manager-two-page-design.md`
- `temp/tasks/20250113-161045-crosstab-specs-sidebar-layout.md`

### Return Format

Return BOTH the task document content AND the file path:

```json
{
  "task_document": "[Full markdown content]",
  "file_path": "temp/tasks/20250113-143052-fix-auth-timeout.md",
  "task_summary": "Fix authentication timeout bug"
}
```

### Task Document Template

```markdown
# Task: [One-line summary]

**Created**: [YYYY-MM-DD HH:MM:SS]
**Status**: pending

---

## Task
[Clear one-line description of what needs to be done]

## Context
[Relevant background from the conversation - why this task exists, what problem it solves]

## Scope
[Directories, files, or areas affected]
- Directories: [list relevant directories]
- Files: [list specific files if known]
- Dependencies: [what this task depends on or affects]

## Requirements
[Specific, actionable requirements]
1. [Requirement 1 - what must be implemented]
2. [Requirement 2 - what must be implemented]
3. [Requirement 3 - constraints or edge cases]

## Deliverables
[What the Worker Agent should produce]
1. [Deliverable 1]
2. [Deliverable 2]

## Constraints
[Limitations the Worker must respect]
1. [Constraint 1 - e.g., framework, language, compatibility]
2. [Constraint 2 - e.g., performance, security]

## Success Criteria
[How to verify the task is complete]
1. [Criterion 1]
2. [Criterion 2]

## Worker Investigation Instructions
[CRITICAL] Explicit instructions for the Worker Agent's own investigation:
- You MUST do your own deep investigation before implementing
- Find ALL files affected: [suggest grep/find commands if applicable]
- Understand current patterns before making changes
- Identify ALL edge cases and dependencies
```

## Task Document Quality Checklist

Before returning the task document, ensure:

- [ ] **Task is clear** - One-line summary is unambiguous
- [ ] **Context is provided** - Worker understands why this task exists
- [ ] **Scope is defined** - Worker knows where to look
- [ ] **Requirements are specific** - Not vague like "improve code"
- [ ] **Investigation is requested** - Worker is told to do their own research
- [ ] **Success criteria exist** - Worker knows when they're done

## Example: Good vs Bad

### Bad Task Document
```markdown
## Task
Fix the bugs in the codebase

## Requirements
1. Make it work better
```

### Good Task Document
```markdown
# Task: Fix authentication timeout bug

**Created**: 2025-01-12 14:30:52
**Status**: pending

---

## Task
Fix the authentication bug where users are incorrectly logged out after 5 minutes

## Context
Users report being logged out even when active. Session timeout is set to 24 hours but appears to be expiring at 5 minutes. Affects user experience significantly.

## Scope
- Directories: frontend/src/auth/, backend/src/middleware/
- Files: session_manager.py, auth_store.ts

## Requirements
1. Identify why session expires at 5 minutes instead of 24 hours
2. Fix the session timeout configuration
3. Ensure session refresh works properly during active use
4. Add logging for session lifecycle events

## Deliverables
1. Fixed session timeout code
2. Explanation of root cause
3. Test cases verifying 24-hour timeout works

## Constraints
1. Must not break existing active sessions
2. Must maintain backward compatibility
3. Use existing session management infrastructure

## Success Criteria
1. Sessions last 24 hours of inactivity
2. Active sessions refresh properly
3. No existing functionality broken

## Worker Investigation Instructions
[CRITICAL] You MUST do your own deep investigation:
- Find ALL session-related configuration: grep -r "timeout\|expir" --include="*.py" --include="*.ts"
- Check frontend and backend timeout settings
- Identify where session refresh logic lives
- Review any recent changes to auth code
```

## What This Skill Does

- ✅ Generate structured task document from conversation
- ✅ Save task document to `tasks/` directory
- ✅ Return file path for downstream skills
- ✅ Extract context and requirements from discussion

## What This Skill Does NOT Do

- ❌ Execute the task
- ❌ Review or audit implementation
- ❌ Make assumptions - extract from conversation context
- ❌ Create vague tasks - be specific

## Workflow After This Skill

Once the task document is generated and saved:

```
┌─────────────────────────────────────────────────────────────────┐
│  task-document-generator SKILL                                  │
│  1. Generate task document from conversation                    │
│  2. Save to: temp/tasks/{YYYYMMDD}-{HHMMSS}-{slug}.md   │
│  3. Return: document content + file_path                        │
└────────────────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  agent-delegation-auditor SKILL                                 │
│  1. Receives task document (or file_path)                       │
│  2. Delegates to Worker Agent                                   │
│  3. Auditor Agent reviews and rates                             │
│  4. Returns: implementation + quality rating                    │
└─────────────────────────────────────────────────────────────────┘
```

Your job ends when:
1. Task document is generated
2. File is saved to `temp/tasks/`
3. File path is returned to caller
