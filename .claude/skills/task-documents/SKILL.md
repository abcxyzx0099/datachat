---
name: pending
description: "Generates task document specifications from planning documents or conversation context. Creates task specs using staging pattern: write to staging/ first, then atomically move to pending/. Ad-hoc tasks go to tasks/ad-hoc/, planned tasks go to tasks/planned/. Each queue processes independently via watchdog."
---

# Task Documents Generation

Generate structured task document specifications for the task-queue module.

## Overview

This skill creates task document specifications that serve as the single source of truth for task execution. Each specification includes:

- **Clear task definition** with context and scope
- **Specific requirements** that must be implemented
- **Testing requirements** with coverage targets and test scenarios
- **Success criteria** to verify completion
- **Worker investigation instructions** for autonomous execution

The specifications are consumed by the `task-queue` module, which loads them via CLI and executes them using the `task-worker` skill.

---

## Two Queue System

The task system supports two independent queues:

| Queue | Target Directory | Source | Use When |
|-------|------------------|--------|----------|
| **ad-hoc** | `tasks/ad-hoc/pending/` | Conversation context | Quick, spontaneous tasks from chat |
| **planned** | `tasks/planned/pending/` | Planning documents | Organized, sequential tasks from planning |

**Both queues process independently in parallel.**

---

## When to Use

| Scenario | Queue | Use when |
|----------|-------|----------|
| **Scenario 1: Ad-hoc** | ad-hoc | A task emerges during chat that needs to be delegated |
| **Scenario 2: Planned** | planned | You have a `task-planning` document and want to generate multiple task specs |

## Input Sources

**Primary Sources:**
1. **Planning documents** - `tasks/planned/planning/{descriptive-name}.md` → planned queue
2. **Conversation context** - Discussion between user and AI → ad-hoc queue

**Auxiliary Sources:**
- Design/Project Documentation (`docs/application-design/` directory)
- Codebase investigation (Glob/Grep)

## Output Location

Task specifications use a **staging pattern** to ensure atomic writes:

### Ad-hoc Queue (Conversation-based)

```
tasks/ad-hoc/staging/              # Write complete file here first
└── task-YYYYMMDD-HHMMSS-{description}.md

tasks/ad-hoc/pending/            # Then atomically move here (watchdog monitors)
└── task-YYYYMMDD-HHMMSS-{description}.md
```

### Planned Queue (Planning-based)

```
tasks/planned/staging/             # Write complete file here first
└── task-YYYYMMDD-HHMMSS-{description}.md

tasks/planned/pending/           # Then atomically move here (watchdog monitors)
└── task-YYYYMMDD-HHMMSS-{description}.md
```

**Why Staging?** The watchdog monitors each queue's `pending/`. Writing to `staging/` first ensures the file is fully written before the watchdog detects and processes it. This prevents race conditions where incomplete files are processed.

**Note:** Each `pending/` is a Task Source Directory monitored by the watchdog. New files are auto-loaded into the task-queue after the atomic move from staging.

---

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

## Testing Requirements
[CRITICAL] Testing expectations for this task:

### Test Type
- [ ] **Unit Tests** - Required for new functions/classes
- [ ] **Integration Tests** - Required for API/database/service changes
- [ ] **E2E Tests** - Required for user workflow changes
- [ ] **No Tests** - Only for documentation/configuration changes

### Coverage Target
- **Minimum**: 80% code coverage for modified/new files
- **Test File**: tests/ [path to test file]

### Test Scenarios
1. [Happy path - normal operation]
2. [Error cases - edge conditions]
3. [Boundary values - limits]
4. [Integration points - external dependencies]

### Verification Commands
```bash
# Run tests
pytest tests/[test-file].py -v

# Check coverage
coverage run -m pytest tests/[test-file].py
coverage report --include='[modified-files]'
```

## Deliverables
[What the Worker Agent should produce]
1. [Implementation code]
2. [Test files]
3. [Documentation if applicable]

## Constraints
[Limitations the Worker must respect]
1. [Constraint 1 - e.g., framework, language, compatibility]
2. [Constraint 2 - e.g., performance, security]

## Success Criteria
[How to verify the task is complete]
1. [All requirements implemented]
2. [All tests pass (100% pass rate)]
3. [Coverage threshold met (80%+)]
4. [No regressions in existing tests]
5. [Code follows existing patterns]

## Worker Investigation Instructions
[CRITICAL] Explicit instructions for the Worker Agent's own investigation:
- You MUST do your own deep investigation before implementing
- Find ALL files affected: [suggest grep/find commands if applicable]
- Understand current patterns before making changes
- Identify ALL edge cases and dependencies
- Review existing test patterns: check tests/ directory for similar test patterns
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

---

## Workflow

### Scenario 1: Ad-hoc Task (From Conversation)

**Use when:** A task emerges during chat that needs to be delegated

**Target Queue:** `tasks/ad-hoc/`

**Step 1: Investigate & Understand**
- Review conversation context
- Check relevant documentation in `docs/application-design/`
- Investigate codebase with Glob/Grep
- Understand requirements fully

**Step 2: Generate Timestamp**
```python
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
```

**Step 3: Write Task Document to Staging**
```python
Write(
    file_path="tasks/ad-hoc/staging/task-{timestamp}-{description}.md",
    content=task_spec_content
)
```

**Step 4: Atomically Move to Task Documents**
```python
# Atomic move ensures watchdog detects complete file
import os
os.rename(
    "tasks/ad-hoc/staging/task-{timestamp}-{description}.md",
    "tasks/ad-hoc/pending/task-{timestamp}-{description}.md"
)
```

**Step 5: Inform User**
```
Ad-hoc task created: tasks/ad-hoc/pending/task-{timestamp}-{description}.md

The ad-hoc queue watchdog will auto-load this task. View queue status:
  python -m task_queue.cli status
```

### Scenario 2: Planned Tasks (From Planning Document)

**Use when:** You have a `task-planning` document and want to generate multiple task specs

**Target Queue:** `tasks/planned/`

**Trigger phrases:**
- "Generate task specs from the planning document"
- "Create all task specifications from {planning-doc}.md"
- "Convert planning to task specifications"

**Step 1: Read Planning Document**
```python
Read(file_path="tasks/planned/planning/{descriptive-name}.md")
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

**Step 4: Generate All Task Documents to Staging (Write All First)**
```python
# PHASE 1: Write all files to staging first (no watchdog detection)
staging_files = []
for i, task in enumerate(tasks, start=1):
    staging_path = f"tasks/planned/staging/task-{timestamp}-{i:02d}-{description}.md"
    Write(file_path=staging_path, content=task_content)
    staging_files.append(staging_path)
```

Resulting files in staging:
```
tasks/planned/staging/
├── task-20260202-120000-01-first-task.md
├── task-20260202-120001-02-second-task.md
└── task-20260202-120002-03-third-task.md
```

**Step 5: Show User What Was Generated**
```
Generated N task document(s) in planned staging:
  - task-20260202-120000-01-first-task.md
  - task-20260202-120001-02-second-task.md
  - task-20260202-120002-03-third-task.md

Ready to move to planned/pending/ (will trigger watchdog execution).
```

**Step 6: Atomically Move All Files (Triggers Watchdog)**
```python
# PHASE 2: Move all files at once (atomic batch operation)
for staging_path in staging_files:
    filename = os.path.basename(staging_path)
    final_path = f"tasks/planned/pending/{filename}"
    os.rename(staging_path, final_path)
```

**Step 7: Inform User**
```
Moved N task document(s) to tasks/planned/pending/

The planned queue watchdog will auto-load these tasks. View queue status:
  python -m task_queue.cli status
```

**Why Write All First?**
- Review all generated tasks before execution starts
- If generation fails, no partial work is executed
- Cleaner batch operation with predictable timing

## Quality Checklist

Before creating a task document:
- [ ] Task is clear (unambiguous summary)
- [ ] Context provided
- [ ] Scope defined
- [ ] Requirements specific
- [ ] **Testing requirements included**
- [ ] **Test type specified (Unit/Integration/E2E/None)**
- [ ] **Coverage target set (80% minimum)**
- [ ] Investigation instructions included
- [ ] Success criteria exist (including tests)
- [ ] Timestamp generated correctly
- [ ] File follows naming convention
- [ ] Correct queue selected (ad-hoc vs planned)

---

## Key Principles

1. **Atomic Write Pattern** - Write to `staging/` first, then atomically move to `pending/`. This prevents the watchdog from detecting incomplete files.

2. **Batch Generation for Multiple Tasks** - When generating multiple tasks: write ALL to staging first, review, then move ALL at once. This allows review before execution starts and prevents partial execution on errors.

3. **Queue Selection** - Ad-hoc tasks from conversation go to `tasks/ad-hoc/`. Planned tasks from planning documents go to `tasks/planned/`. Each queue processes independently.

4. **Watchdog Integration** - Task specifications are moved to `pending/` as complete `.md` files; the watchdog auto-loads them when the atomic move completes.

5. **Testing is Mandatory** - Every code task must include testing requirements. Only documentation/configuration tasks may use "No Tests."

6. **80% Coverage Minimum** - All code changes must achieve at least 80% test coverage for modified/new files.

7. **Clear Success Criteria** - Success criteria must include test pass rate and coverage thresholds.

8. **Worker Autonomy** - Worker agents do their own investigation. Provide clear investigation instructions.

9. **Specific Requirements** - Requirements must be actionable, not vague. Avoid "improve code" - specify what must be done.

---

## Related Skills

- **task-init**: Initializes the task system with ad-hoc and planned queues
- **task-planning**: Generates planning documents for bulk generation
- **task-queue**: Loads and executes task documents
- **task-worker**: Executes tasks with worker-auditor workflow

---

## Example Usage

```markdown
# Task: Add JWT authentication to API endpoints

**Status**: pending

---

## Task
Implement JWT-based authentication for REST API endpoints

## Context
The API currently has no authentication. We need to add JWT token-based authentication to protect sensitive endpoints.

## Scope
- Directories: agent/, tests/
- Files: agent/server.py, agent/auth.py
- Dependencies: Requires python-jose library

## Requirements
1. Implement JWT token generation on login
2. Add authentication middleware to validate tokens
3. Protect /api/* endpoints (except /api/auth/login)
4. Return 401 for unauthenticated requests
5. Implement token refresh mechanism

## Testing Requirements

### Test Type
- [x] **Unit Tests** - Required for auth functions
- [x] **Integration Tests** - Required for API endpoints
- [ ] **E2E Tests** - Not required for this task

### Coverage Target
- **Minimum**: 80% code coverage for agent/auth.py
- **Test Files**:
  - tests/test_auth.py (unit tests)
  - tests/test_api_auth.py (integration tests)

### Test Scenarios
1. Valid login returns JWT token
2. Invalid credentials return 401
3. Protected endpoint with valid token returns 200
4. Protected endpoint without token returns 401
5. Expired token returns 401
6. Token refresh works correctly

### Verification Commands
```bash
# Run tests
pytest tests/test_auth.py tests/test_api_auth.py -v

# Check coverage
coverage run -m pytest tests/test_auth.py tests/test_api_auth.py
coverage report --include='agent/auth.py'
```

## Deliverables
1. JWT token generation functions (agent/auth.py)
2. Authentication middleware (agent/middleware.py)
3. Protected route decorators
4. Login endpoint (/api/auth/login)
5. Token refresh endpoint (/api/auth/refresh)
6. Unit tests (tests/test_auth.py)
7. Integration tests (tests/test_api_auth.py)

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
5. All tests pass (100% pass rate)
6. Coverage >= 80% for agent/auth.py
7. No regressions in existing tests

## Worker Investigation Instructions
- You MUST investigate the current API structure in agent/
- Find ALL endpoints that need protection: grep -r "@app.route" agent/
- Understand current authentication (if any): check agent/auth/
- Identify environment variable patterns: check .env.example
- Review existing middleware: check agent/middleware/
- Review existing test patterns: check tests/test_*.py
```
