---
name: task-document-writer
description: "Generates structured task documents from conversation context for delegation to Worker Agents via the task monitoring system. Default: creates single task from conversation. Explicit request required for bulk generation from breakdown documents. Use when: converting user requirements into task documents; tasks should be queued for sequential processing."
---

# Task Document Writer

Generate structured task documents for Worker Agents via the task monitoring system.

## Default Behavior: Scenario 1

**Scenario 1 is the default** - this skill creates a single task document from conversation context.

To use **Scenario 2** (bulk generation from breakdown), you must **explicitly request it**.

---

## How It Determines Which Scenario

```
┌─────────────────────────────────────────────────────────────┐
│ User invokes: /task-document-writer                          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Explicit Scenario 2   │
              │  request detected?      │
              └────────────────────────┘
                    │              │
                   Yes            No
                    │              │
                    ▼              ▼
            ┌───────────┐    ┌─────────────┐
            │ Scenario 2│    │ Scenario 1  │
            │ (bulk)    │    │ (default)   │
            └───────────┘    └─────────────┘
```

## Scenario Detection

| User Says | Scenario |
|-----------|----------|
| "Create tasks from the breakdown" | Scenario 2 |
| "Generate all task documents from {wave-name}-tasks.md" | Scenario 2 |
| "Bulk generate task documents" | Scenario 2 |
| "Convert breakdown to task documents" | Scenario 2 |
| "Process the task breakdown document" | Scenario 2 |
| **(Anything else or unspecified)** | **Scenario 1 (default)** |

---

## Two Scenarios

| Scenario | Input Source | Use Case | Output | Trigger |
|----------|-------------|----------|--------|---------|
| **Scenario 1** | Conversation context | Single task identified during chat | One task document | **Default** (no explicit request) |
| **Scenario 2** | Task breakdown document | Bulk generation from breakdown | Multiple task documents | Explicit request required |

---

## Scenario 1: Single Task from Conversation (DEFAULT)

**Use when:** A task is identified during conversation that needs to be implemented by another agent.

**This is the DEFAULT behavior** - no special keywords required.

### Input

- **Conversation history** - The full discussion between user and AI
- **Context** - Project context (codebase, architecture, current state)
- **Task intent** - What needs to be done

### Workflow (5 Steps)

#### Step 1: Verify Task Monitor Service Running

**BEFORE creating any task document**, verify that the task monitoring service is running.

```bash
# Check if task monitor service is running
task-monitor queue
```

**Expected output if running:**
```
Queue size: 0
Processing: (task name or empty)
```

**Expected output if NOT running:**
```
Error: Task monitor service is not running
```

**If service is NOT running - STOP and ask the user:**
```
⚠️ Task monitor service is not running. The task document will not be processed automatically.

Would you like me to start the task monitor service now?
```

---

#### Step 2: Investigate & Understand

Before writing the task document, ensure you fully understand the context and requirements.

**2.1 Analyze Conversation**
- The original problem/request
- Decisions made during discussion
- Constraints mentioned
- Acceptance criteria discussed

**2.2 Clarify Task Intent**
- Specific outcome required
- Boundaries of the task (what's included/excluded)
- Success metrics

**2.3 Investigate Codebase**
```bash
# Find relevant files
glob "**/*.py"
grep "keyword" --include="*.py"

# Read key files to understand patterns
```

**2.4 Quality Gate**
- If anything is unclear → ask questions
- If context is missing → investigate more
- Only write document when you have complete understanding

---

#### Step 3: Write Temp File

Use the Write tool to create the task document with `.md.tmp` extension:

**Temp file pattern**: `tasks/pending/task-{description}.md.tmp`

**Example**: `tasks/pending/task-fix-auth-timeout.md.tmp`

**Why `.md.tmp` first?** The task monitor watches for `.md` files only. Writing to `.md.tmp` first ensures the document is complete before the monitor sees it.

---

#### Step 4: Rename with Timestamp

```bash
bash .claude/skills/task-document-writer/scripts/rename_task.sh /path/to/temp/file.md.tmp
```

**Example transformation:**
```
tasks/pending/task-fix-auth-timeout.md.tmp
    ↓
tasks/pending/task-20260129-170500-fix-auth-timeout.md
```

---

#### Step 5: Monitor & Verify Results

```bash
# Poll task status until "completed"
task-monitor task-{timestamp}-{description}

# Verify results
cat tasks/results/task-{timestamp}-{description}.json
```

---

## Scenario 2: Bulk Tasks from Breakdown Document (EXPLICIT REQUEST REQUIRED)

**Use when:** You have a task breakdown document from `task-breakdown` skill and want to generate all task documents in bulk.

**This requires EXPLICIT request** - see "Scenario Detection" table above for trigger phrases.

### Input

- **Breakdown document** - `implementation-artifacts/{wave-name}-tasks.md`
- **Project context** - Codebase, architecture, current state

### Workflow (5 Steps)

#### Step 1: Verify Task Monitor Service Running

Same as Scenario 1, Step 1.

```bash
task-monitor queue
```

**If service is NOT running - STOP and ask user to start it.**

---

#### Step 2: Read & Parse Breakdown Document

**2.1 Locate the Breakdown Document**

The breakdown document is located at:
```
implementation-artifacts/{wave-name}-tasks.md
```

**2.2 Read the Document**

Use the Read tool to read the entire breakdown document.

**2.3 Parse Task Structure**

The breakdown document contains tasks organized by structure type:

| Organization | Structure |
|--------------|-----------|
| **FLAT_LIST** | Simple list of tasks |
| **IMPLEMENTATION_PHASE** | Tasks grouped by phase |
| **FEATURE_MODULE** | Tasks grouped by module |

**2.4 Extract Task Information**

For each task in the breakdown, extract:
- **Subject/Title** - Brief task description
- **Description** - Detailed explanation
- **Active Form** - Present continuous form for status display
- **Phase/Module** (if applicable) - For organization

**2.5 Validate Breakdown**

Before proceeding:
- [ ] Document exists and is readable
- [ ] At least one task is defined
- [ ] Task information is complete
- [ ] Project context is understood

---

#### Step 3: Generate All Temp Files

**3.1 Create Temp Files for All Tasks**

For each task extracted from the breakdown, create a temp file:

**File pattern**: `tasks/pending/task-{description}.md.tmp`

**3.2 Map Breakdown to Task Document Template**

Convert breakdown task information to the task document format:

| Breakdown Field | Task Document Section |
|-----------------|----------------------|
| Subject | ## Task |
| Description | ## Context + expanded details |
| (Derived) | ## Scope |
| (Derived) | ## Requirements |
| (Derived) | ## Deliverables |
| (Derived) | ## Constraints |
| (Derived) | ## Success Criteria |
| (Derived) | ## Worker Investigation Instructions |

**3.3 Add Context from Breakdown**

Include relevant context from the breakdown document:
- Source documents read
- Project context summary
- Overall project goals

**3.4 Quality Gate**

Before proceeding to Step 4:
- [ ] All temp files created successfully
- [ ] Each task document follows the template
- [ ] Worker Investigation Instructions included
- [ ] Success Criteria defined

---

#### Step 4: Rename All Files with Timestamps

**4.1 Rename Each Temp File**

For each temp file, run the rename script:

```bash
bash .claude/skills/task-document-writer/scripts/rename_task.sh tasks/pending/task-{description}.md.tmp
```

**4.2 Track Created Tasks**

Maintain a list of all task files created with their timestamps:

```
✅ Task created: tasks/pending/task-20260131-204500-task-one.md
✅ Task created: tasks/pending/task-20260131-204501-task-two.md
✅ Task created: tasks/pending/task-20260131-204502-task-three.md
```

**4.3 Verify Queue**

After creating all tasks, verify they are queued:

```bash
task-monitor queue
```

Expected output should show the number of tasks queued.

---

#### Step 5: Monitor All Tasks

**5.1 Track All Task Status**

Monitor all created tasks:

```bash
# List all tasks
task-monitor

# Check specific task
task-monitor task-{timestamp}-{description}
```

**5.2 Verify Each Task Result**

As tasks complete, verify each one:

```bash
# Check result JSON
cat tasks/results/task-{timestamp}-{description}.json
```

**5.3 Summary Report**

After all tasks complete, provide a summary:

| Task ID | Status | Duration | Summary |
|---------|--------|----------|---------|
| task-xxx-xxx | completed | 45s | ... |
| task-xxx-xyy | completed | 120s | ... |
| task-xxx-xzz | failed | - | (error details) |

---

## Document Template

All task documents must follow this structure (from `references/task-template.md`):

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

---

## Task File Naming Convention

**Format:** `task-{timestamp}-{description}.md`

| Component | Format | Example |
|-----------|--------|---------|
| Prefix | `task-` | `task-` |
| Timestamp | `YYYYMMDD-HHMMSS` | `20260131-204500` |
| Separator | `-` | `-` |
| Description | kebab-case | `fix-auth-timeout` |
| Extension | `.md` | `.md` |

**Full Example:** `task-20260131-204500-fix-auth-timeout.md`

**Watchdog Glob Pattern:** `task-????????-??????-*.md`

---

## Quality Checklist

### Before Task Creation (Both Scenarios)

- [ ] Service running (HARD REQUIREMENT)
- [ ] Task is clear (unambiguous summary)
- [ ] Context provided
- [ ] Scope defined
- [ ] Requirements specific
- [ ] Investigation requested
- [ ] Success criteria exist

### Scenario 2 Additional Checks

- [ ] Breakdown document parsed correctly
- [ ] All tasks extracted
- [ ] Organization structure preserved
- [ ] All temp files created
- [ ] All files renamed with timestamps

### After Task Completes

**Verify results in `tasks/results/`:**

- [ ] Status is `"completed"` (not `"failed"`)
- [ ] Error field is `null`
- [ ] Summary reviewed
- [ ] Artifacts verified

---

## Full Examples

### Scenario 1 Example: Single Task from Conversation

```bash
# Step 1: Verify service running
task-monitor queue
# Output: Queue size: 0, Processing: none

# Step 2: Investigate and understand (read conversation, explore codebase)

# Step 3: Write temp file
# File: tasks/pending/task-fix-auth-timeout.md.tmp

# Step 4: Rename
bash .claude/skills/task-document-writer/scripts/rename_task.sh tasks/pending/task-fix-auth-timeout.md.tmp
# Output: ✅ Task created: tasks/pending/task-20260129-170500-fix-auth-timeout.md

# Step 5: Monitor and verify
task-monitor task-20260129-170500-fix-auth-timeout
cat tasks/results/task-20260129-170500-fix-auth-timeout.json
```

### Scenario 2 Example: Bulk Tasks from Breakdown

```bash
# Step 1: Verify service running
task-monitor queue

# Step 2: Read and parse breakdown
# Document: implementation-artifacts/authentication-tasks.md
# Extract: 8 tasks across 3 modules

# Step 3: Generate all temp files
# tasks/pending/task-user-registration.md.tmp
# tasks/pending/task-build-login-system.md.tmp
# tasks/pending/task-design-product-model.md.tmp
# ... (8 total)

# Step 4: Rename all files
for file in tasks/pending/task-*.md.tmp; do
  bash .claude/skills/task-document-writer/scripts/rename_task.sh "$file"
done
# Output:
# ✅ Task created: tasks/pending/task-20260131-204500-user-registration.md
# ✅ Task created: tasks/pending/task-20260131-204501-build-login-system.md
# ✅ Task created: tasks/pending/task-20260131-204502-design-product-model.md
# ... (8 total)

# Step 5: Monitor all tasks
task-monitor queue
# Output: Queue size: 8

# Track progress and verify results as tasks complete
```

---

## Key Principles

1. **Scenario 1 is default** - Unless user explicitly requests Scenario 2, always use Scenario 1
2. **Scenario 2 requires explicit request** - Bulk operations should be intentional; detect trigger phrases
3. **Service must be running** - HARD STOP if service not running
4. **Understand first** - Investigate before writing (Scenario 1) or read breakdown (Scenario 2)
5. **Be specific** - Vague tasks produce vague results
6. **Request investigation** - Worker Agents must do their own deep research
7. **Define success** - Worker needs clear completion criteria
8. **Provide context** - Worker should understand why the task exists
9. **Verify results** - ALWAYS check `tasks/results/` after completion
10. **Bulk awareness** - Scenario 2 creates multiple tasks; track all of them

---

## Related Skills

- `task-breakdown`: Generates breakdown documents for Scenario 2
- `task-monitor-system`: Creates the monitoring system that processes task documents
- `task-implementation`: Executes tasks with worker-auditor workflow (called by monitor)
