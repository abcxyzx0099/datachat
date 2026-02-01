---
name: task-specification-generation
description: "Generates task specification documents from planning documents or conversation context. Creates task specs in tasks/task-specifications/ directory with direct .md generation (no .md.tmp files). Use when: converting requirements into task specifications for the task-implementation module to process."
---

# Task Specification Generation

Generate structured task specification documents for the task-implementation module.

## Overview

This skill creates task specification documents that will be processed by the `task-implementation` module. Unlike the old `task-document-writer` skill, this skill:

- **Generates .md files directly** - No `.md.tmp` intermediate files
- **Writes to `tasks/task-specifications/`** - Different directory from old system
- **No watchdog integration** - Manual loading via `task-impl load` command
- **Simpler workflow** - Focus on specification quality, not execution mechanics

## When to Use

| Scenario | Use when |
|----------|----------|
| **From Planning** | You have a `task-planning` document and want to generate multiple task specs |
| **From Conversation** | A task emerges during chat that needs to be delegated |
| **Bulk Generation** | Converting an entire planning document into task specs |

## Input Sources

**Primary Sources:**
1. **Planning documents** - `tasks/task-planning/{descriptive-name}.md`
2. **Conversation context** - Discussion between user and AI

**Auxiliary Sources:**
- Design/Project Documentation (`docs/` directory)
- Codebase investigation (Glob/Grep)

## Output Location

```
tasks/task-specifications/
└── task-YYYYMMDD-HHMMSS-{description}.md
```

## Document Template

```markdown
# Task: [One-line summary]

**Status**: pending

---

## Task
[Clear one-line description of what needs to be done]

## Context
[Relevant background - why this task exists, what problem it solves]

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

## File Naming Convention

**Format**: `task-{timestamp}-{description}.md`

| Component | Format | Example |
|-----------|--------|---------|
| Prefix | `task-` | `task-` |
| Timestamp | `YYYYMMDD-HHMMSS` | `20260202-120000` |
| Description | kebab-case | `fix-auth-timeout` |
| Extension | `.md` | `.md` |

**Full Example**: `task-20260202-120000-fix-auth-timeout.md`

## Workflow

### Scenario 1: From Conversation (Default)

**Step 1: Investigate & Understand**
- Review conversation context
- Check relevant documentation in `docs/`
- Investigate codebase with Glob/Grep
- Understand requirements fully

**Step 2: Generate Timestamp**
```python
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
```

**Step 3: Write Task Specification**
```python
# Write directly to .md file (no .md.tmp)
Write(
    file_path="tasks/task-specifications/task-{timestamp}-{description}.md",
    content=task_spec_content
)
```

**Step 4: Inform User**
```
✅ Task specification created: tasks/task-specifications/task-{timestamp}-{description}.md

To load and execute this task:
  task-impl load
```

### Scenario 2: From Planning Document (Explicit Request)

**Trigger phrases:**
- "Generate task specs from the planning document"
- "Create all task specifications from {planning-doc}.md"
- "Convert planning to task specifications"

**Step 1: Read Planning Document**
```python
Read(file_path="tasks/task-planning/{descriptive-name}.md")
```

**Step 2: Parse Tasks**
Extract all tasks from the planning document, noting:
- Subject/Title
- Description
- Phase/Module (if applicable)
- Dependencies

**Step 3: Determine Numbering**
| Task Count | Numbering Strategy |
|------------|-------------------|
| 1 task | No numbering |
| 2+ tasks | Simple sequential: 01, 02, 03... |

**Step 4: Generate All Task Specifications**
Create each file with sequential numbering:
```
task-20260202-120000-01-first-task.md
task-20260202-120001-02-second-task.md
task-20260202-120002-03-third-task.md
```

**Step 5: Inform User**
```
✅ Created N task specification(s) in tasks/task-specifications/

To load and execute these tasks:
  task-impl load

View queue status:
  task-impl queue
```

## Quality Checklist

Before creating a task specification:
- [ ] Task is clear (unambiguous summary)
- [ ] Context provided
- [ ] Scope defined
- [ ] Requirements specific
- [ ] Investigation instructions included
- [ ] Success criteria exist
- [ ] Timestamp generated correctly
- [ ] File follows naming convention

## Key Differences from Old System

| Aspect | Old (task-document-writer) | New (task-specification-generation) |
|--------|---------------------------|-------------------------------------|
| **Directory** | `tasks/task-monitor/pending/` | `tasks/task-specifications/` |
| **File creation** | `.md.tmp` → rename to `.md` | Direct `.md` creation |
| **Watchdog** | Automatic detection | Manual `task-impl load` |
| **Focus** | Execution mechanics | Specification quality |
| **CLI commands** | `task-monitor` | `task-impl` |

## Related Skills

- **task-planning**: Generates planning documents for bulk generation
- **task-implementation**: Loads and executes task specifications
- **task-worker**: Executes tasks with worker-auditor workflow

## Example Output

```markdown
# Task: Add JWT authentication to API endpoints

**Status**: pending

---

## Task
Implement JWT-based authentication for REST API endpoints

## Context
The API currently has no authentication. We need to add JWT token-based authentication to protect sensitive endpoints.

## Scope
- Directories: src/api/, src/auth/, src/middleware/
- Files: main.py, routes.py, auth.py
- Dependencies: Requires python-jose library

## Requirements
1. Implement JWT token generation on login
2. Add authentication middleware to validate tokens
3. Protect /api/* endpoints (except /api/auth/login)
4. Return 401 for unauthenticated requests
5. Implement token refresh mechanism

## Deliverables
1. JWT token generation functions
2. Authentication middleware
3. Protected route decorators
4. Login endpoint (/api/auth/login)
5. Token refresh endpoint (/api/auth/refresh)

## Constraints
1. Use HS256 algorithm for JWT signing
2. Token expiration: 15 minutes (access), 7 days (refresh)
3. Secret key from environment variable
4. Maintain backward compatibility with existing endpoints

## Success Criteria
1. Unauthenticated requests to protected endpoints return 401
2. Valid tokens allow access to protected endpoints
3. Token refresh works correctly
4. Login endpoint returns valid JWT tokens
5. All existing tests still pass

## Worker Investigation Instructions
- You MUST investigate the current API structure in src/api/
- Find ALL endpoints that need protection: grep -r "@app.route" src/api/
- Understand current authentication (if any): check src/auth/
- Identify environment variable patterns: check .env.example
- Review existing middleware: check src/middleware/
- Understand current test patterns: check tests/api/
