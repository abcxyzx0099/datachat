# Task Document Template

This template is used by the Task Document Writer sub-agent to generate structured task documents.

## Template Structure

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
- Directories: [list relevant directories]
- Files: [list specific files if known]
- Dependencies: [what this task depends on or affects]

## Requirements
[Specific, actionable requirements]
1. [Requirement 1 - what must be implemented]
2. [Requirement 2 - what must be implemented]
3. [Requirement 3 - constraints or edge cases]

## Deliverables
[What the Implementation Agent should produce]
1. [Deliverible 1]
2. [Deliverable 2]

## Constraints
[Limitations the Implementation Agent must respect]
1. [Constraint 1 - e.g., framework, language, compatibility]
2. [Constraint 2 - e.g., performance, security]

## Success Criteria
[How to verify the task is complete]
1. [Criterion 1]
2. [Criterion 2]

## Worker Investigation Instructions
[CRITICAL] Explicit instructions for the Implementation Agent's own investigation:
- You MUST do your own deep investigation before implementing
- Find ALL files affected: [suggest grep/find commands if applicable]
- Understand current patterns before making changes
- Identify ALL edge cases and dependencies
```

## Quality Checklist

Before finalizing the task document, ensure:

- [ ] **Task is clear** - One-line summary is unambiguous
- [ ] **Context is provided** - Implementation Agent understands why this task exists
- [ ] **Scope is defined** - Implementation Agent knows where to look
- [ ] **Requirements are specific** - Not vague like "improve code"
- [ ] **Investigation is requested** - Implementation Agent is told to do their own research
- [ ] **Success criteria exist** - Implementation Agent knows when they're done

## Examples

### Bad Task Document

```markdown
## Task
Fix the bugs in the codebase

## Requirements
1. Make it work better
```

**Problems:**
- Too vague - no specific bugs identified
- No scope - where to look?
- No investigation instructions
- No success criteria

### Good Task Document

```markdown
# Task: Fix authentication timeout bug

**Created**: 2025-01-28 14:30:52
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

## Quick Format for Simple Tasks

For very simple tasks, use this minimal structure:

```markdown
## Task
[Clear one-line description]

## Context
[Relevant background]

## Requirements
1. [Specific requirement 1]
2. [Specific requirement 2]
```
