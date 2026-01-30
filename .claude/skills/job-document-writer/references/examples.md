# Task Document Examples

Examples demonstrating good vs bad task documents.

## Bad Task Document

```markdown
## Task
Fix the bugs in the codebase

## Requirements
1. Make it work better
```

**Problems:**
- No specific task description
- Vague requirements
- No context or scope
- No success criteria

## Good Task Document

```markdown
# Task: Fix authentication timeout bug

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

**Why this works:**
- Clear, specific task description
- Provides context and scope
- Actionable requirements
- Explicit success criteria
- Investigation instructions for Worker Agent
