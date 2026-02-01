---
name: task-document-writer
description: "Generates structured task documents from conversation context for delegation to Worker Agents via the task monitoring system. Default: creates single task from conversation. Explicit request required for bulk generation from planning documents. Use when: converting user requirements into task documents; tasks should be queued for sequential processing."
---

# Task Document Writer

Generate structured task documents for Worker Agents via the task monitoring system.

## Default Behavior: Scenario 1

**Scenario 1 is the default** - this skill creates a single task document from conversation context.

To use **Scenario 2** (bulk generation from planning), you must **explicitly request it**.

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
| "Create tasks from the planning document" | Scenario 2 |
| "Generate all task documents from {wave-name}-tasks.md" | Scenario 2 |
| "Bulk generate task documents" | Scenario 2 |
| "Convert planning to task documents" | Scenario 2 |
| "Process the task planning document" | Scenario 2 |
| **(Anything else or unspecified)** | **Scenario 1 (default)** |

---

## Two Scenarios

| Scenario | Input Source | Use Case | Output | Trigger |
|----------|-------------|----------|--------|---------|
| **Scenario 1** | Conversation context | Single task identified during chat | One task document | **Default** (no explicit request) |
| **Scenario 2** | Task planning document | Bulk generation from planning | Multiple task documents | Explicit request required |

---

## Scenario 1: Single Task from Conversation (DEFAULT)

**Use when:** A task is identified during conversation that needs to be implemented by another agent.

**This is the DEFAULT behavior** - no special keywords required.

### Input Sources

**Primary Source:**
- **Conversation context** - The full discussion between user and AI

**Auxiliary Sources:**
1. **Design/Project Documentation** (`docs/` directory)
   - System architecture, data flow, business rules
   - Technology stack, configuration, deployment
   - Features, usage, project structure

2. **Codebase Investigation** (Glob/Grep)
   - Find files relevant to the task
   - Understand current implementation patterns
   - Identify files that need modification

### Workflow (5 Steps)

#### Step 1: Verify Task Monitor Service Running AND Set Project Path

**BEFORE creating any task document**, verify the service is running and set the correct project path.

```bash
# 1. Check if task monitor service is running
task-monitor status

# 2. Set current project to working directory
task-monitor use "$(pwd)"
```

**Expected output from status:**
```
Running
```

**If service is NOT running - STOP and ask the user:**
```
⚠️ Task monitor service is not running. The task document will not be processed automatically.

Would you like me to start the task monitor service now?
```

---

#### Step 2: Investigate & Understand

Before writing the task document, ensure you fully understand the context and requirements.

**2.1 Analyze Primary Source**
- **Scenario 1**: Conversation context - the original problem/request, decisions made, constraints, acceptance criteria
- **Scenario 2**: Planning document - task breakdown, organization, source documents referenced

**2.2 Review Design/Project Documentation**
- Read relevant documents from `docs/` directory
- Understand architecture, patterns, and conventions
- Extract relevant business rules and constraints

**2.3 Investigate Codebase**
- Find relevant files using Glob/Grep
- Understand current implementation patterns
- Identify files that need modification or creation

**2.4 Quality Gate**
- If anything is unclear → ask questions
- If context is missing → investigate more
- Only write document when you have complete understanding

---

#### Step 3: Write Temp File

Use the Write tool to create the task document with `.md.tmp` extension:

**Temp file pattern**: `tasks/task-monitor/pending/task-{description}.md.tmp`

**Example**: `tasks/task-monitor/pending/task-fix-auth-timeout.md.tmp`

**Why `.md.tmp` first?** The task monitor watches for `.md` files only. Writing to `.md.tmp` first ensures the document is complete before the monitor sees it.

---

#### Step 4: Rename with Timestamp

**Single file mode** (one file):
```bash
bash .claude/skills/task-document-writer/scripts/rename_task.sh /path/to/temp/file.md.tmp
```

**Batch mode** (all .md.tmp files in directory):
```bash
# Scans all .md.tmp files, sorts by creation time, renames in order
bash .claude/skills/task-document-writer/scripts/rename_task.sh
```

**Batch mode advantages:**
- Uses file creation time for timestamp (not current time)
- Maintains chronological order
- 1-second delay between files prevents timestamp collisions

**Example transformation:**
```
tasks/task-monitor/pending/task-fix-auth-timeout.md.tmp
    ↓
tasks/task-monitor/pending/task-20260129-170500-fix-auth-timeout.md
```

---

#### Step 5: Verify Task Started

```bash
# First, check queue status
task-monitor queue

# Second, check specific task status
task-monitor task-{timestamp}-{description}
```

Expected output for queue:
```
Queue size: 0
Processing: task-{timestamp}-{description}.md
```

Expected output for task status:
```
Status: processing
Task: task-{timestamp}-{description}.md
Started: [timestamp or Unknown]
```

That's it! The task is now queued and will be processed by the Worker Agent.

DO NOT continuously poll the task status during processing. Only monitor when the user explicitly asks you to check progress.

If user asks to check progress:
```bash
task-monitor task-{timestamp}-{description}
cat tasks/task-monitor/results/task-{timestamp}-{description}.json
```

---

## Scenario 2: Bulk Tasks from Planning Document (EXPLICIT REQUEST REQUIRED)

**Use when:** You have a task planning document from `task-planning` skill and want to generate all task documents in bulk.

**This requires EXPLICIT request** - see "Scenario Detection" table above for trigger phrases.

### Input Sources

**Primary Source:**
- **Planning document** - `tasks/task-planning/{descriptive-name}.md`
  - Contains task breakdown and organization
  - Lists source documents that were read

**Auxiliary Sources:**
1. **Design/Project Documentation** (`docs/` directory)
   - All documents listed in planning document under "## Source Documents"
   - System architecture, data flow, business rules
   - Technology stack, configuration, deployment
   - Features, usage, project structure

2. **Codebase Investigation** (Glob/Grep)
   - Find files relevant to each task
   - Understand current implementation patterns
   - Identify files that need modification

### Workflow (5 Steps)

#### Step 1: Verify Task Monitor Service Running AND Set Project Path

Same as Scenario 1, Step 1.

```bash
# 1. Check if task monitor service is running
task-monitor status

# 2. Set current project to working directory
task-monitor use "$(pwd)"
```

**If service is NOT running - STOP and ask user to start it.**

---

#### Step 2: Read & Parse Planning Document

**2.1 Locate and Read Planning Document**

The planning document is located at:
```
tasks/task-planning/{descriptive-name}.md
```

Use the Read tool to read the entire planning document.

**2.2 Parse Task Structure**

The planning document contains tasks organized by structure type:

| Organization | Structure |
|--------------|-----------|
| **FLAT_LIST** | Simple list of tasks |
| **IMPLEMENTATION_PHASE** | Tasks grouped by phase |
| **FEATURE_MODULE** | Tasks grouped by module |

**2.3 Extract Task Information**

For each task in the planning document, extract:
- **Subject/Title** - Brief task description
- **Description** - Detailed explanation
- **Active Form** - Present continuous form for status display
- **Phase/Module** (if applicable) - For organization

**2.4 Review Design/Project Documentation**

Read all documents listed in the planning document under "## Source Documents":
- System architecture, data flow, business rules
- Technology stack, configuration, deployment
- Features, usage, project structure

**2.5 Investigate Codebase**

For each task, find relevant files:
- Use Glob/Grep to locate files that need modification
- Understand current implementation patterns
- Identify dependencies and integration points

**2.6 Validate Breakdown**

Before proceeding:
- [ ] Document exists and is readable
- [ ] At least one task is defined
- [ ] Task information is complete
- [ ] Project context is understood

---

#### Step 3: Generate All Temp Files

**3.1 Determine Numbering Strategy**

Before creating files, assess the project structure:

| Task Count | Organization | Numbering Strategy |
|------------|--------------|-------------------|
| 1 task | Any | **No numbering** - use `task-{timestamp}-{description}.md` |
| 2+ tasks | FLAT_LIST | Simple sequential: `01`, `02`, `03`... |
| 2+ tasks | IMPLEMENTATION_PHASE | Phase-number: `1-01`, `1-02`, `2-01`... |
| 2+ tasks | FEATURE_MODULE | Module-number: `A-01`, `A-02`, `B-01`... |

**Use intelligent judgment** - add numbering when it aids clarity and referenceability.

**3.2 Create Temp Files for All Tasks**

For each task extracted from the planning document, create a temp file:

**File pattern**: `tasks/task-monitor/pending/task-{description}.md.tmp`

**3.3 Map Breakdown to Task Document Template**

Convert planning task information to the task document format:

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

Include relevant context from the planning document:
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

**4.1 Batch Rename All Temp Files** (Recommended)

Use batch mode to rename all files at once, sorted by creation time:

```bash
bash .claude/skills/task-document-writer/scripts/rename_task.sh
```

This will:
- Scan all `.md.tmp` files in the pending directory
- Sort them by file creation time
- Rename each using its original creation time as the timestamp
- Sleep 1 second between files to prevent timestamp collisions

**4.2 Alternative: Loop Individual Files** (Not recommended)

Only use if you need custom logic per file:

```bash
for file in tasks/task-monitor/pending/task-*.md.tmp; do
  bash .claude/skills/task-document-writer/scripts/rename_task.sh "$file"
done
```

**4.3 Track Created Tasks**

The batch mode outputs all created files:

**Single task (no numbering):**
```
✅ Task created: tasks/task-monitor/pending/task-20260131-204500-fix-auth-timeout.md
```

**Multiple tasks (with sequential numbering):**
```
✅ Task created: tasks/task-monitor/pending/task-20260131-204500-01-task-one.md
✅ Task created: tasks/task-monitor/pending/task-20260131-204501-02-task-two.md
✅ Task created: tasks/task-monitor/pending/task-20260131-204502-03-task-three.md
```

**Module-based organization:**
```
✅ Task created: tasks/task-monitor/pending/task-20260131-204500-A-01-set-up-structure.md
✅ Task created: tasks/task-monitor/pending/task-20260131-204501-A-02-state-definitions.md
✅ Task created: tasks/task-monitor/pending/task-20260131-204502-B-01-spss-extraction.md
```

**4.3 Verify Queue**

After creating all tasks, verify they are queued:

```bash
task-monitor queue
```

Expected output should show the number of tasks queued.

---

#### Step 5: Verify Tasks Started

5.1 Check Tasks Are Running

Verify all tasks have started processing:

```bash
# First, check queue status
task-monitor queue

# Second, check specific task status
task-monitor task-{timestamp}-{description}
```

Expected output for queue:
```
Queue size: 0
Processing: task-{timestamp}-{description}.md
```

Expected output for task status:
```
Status: processing
Task: task-{timestamp}-{description}.md
Started: [timestamp or Unknown]
```

That's it! The tasks are now queued and will be processed by Worker Agents.

DO NOT continuously poll task status during processing. Only monitor when the user explicitly asks you to check progress.

If user asks to check progress:
```bash
# Check specific task status
task-monitor task-{timestamp}-{description}

# Check result JSON (when completed)
cat tasks/task-monitor/results/task-{timestamp}-{description}.json
```

5.2 Summary Report (Only when user requests status)

When user asks for progress, provide a summary:

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

**Base Format:** `task-{timestamp}-{description}.md`

### Sequential Numbering (Multiple Tasks)

When generating **multiple task documents**, add sequential numbering after the timestamp to provide order and referenceability:

**Format:** `task-{timestamp}-{number}-{description}.md`

| Component | Format | Example |
|-----------|--------|---------|
| Prefix | `task-` | `task-` |
| Timestamp | `YYYYMMDD-HHMMSS` | `20260131-204500` |
| Number | 01, 02, 03... (only for multiple tasks) | `01` |
| Description | kebab-case | `fix-auth-timeout` |
| Extension | `.md` | `.md` |

**Single task:** `task-20260131-204500-fix-auth-timeout.md`

**Multiple tasks:**
```
task-20260131-204500-01-fix-auth-timeout.md
task-20260131-204501-02-update-password-policy.md
task-20260131-204502-03-add-rate-limiting.md
```

### Enhanced Numbering (When Organization Exists)

For projects with **modules** or **phases**, enhance the numbering to reflect structure:

| Organization | Number Format | Example |
|--------------|---------------|---------|
| **FLAT_LIST** | Simple sequential | `task-{timestamp}-01-{desc}.md` |
| **IMPLEMENTATION_PHASE** | Phase-Number | `task-{timestamp}-1-01-{desc}.md` |
| **FEATURE_MODULE** | Module-Number | `task-{timestamp}-A-01-{desc}.md` |

**Examples:**

Phase-based:
```
task-20260131-204500-1-01-analyze-schema.md
task-20260131-204501-1-02-design-new-schema.md
task-20260131-204502-2-01-create-migration-scripts.md
```

Module-based:
```
task-20260131-204500-A-01-set-up-structure.md
task-20260131-204501-A-02-state-definitions.md
task-20260131-204502-B-01-spss-extraction.md
```

### Intelligent Decision Making

| Task Count | Organization | Recommended Numbering |
|------------|--------------|----------------------|
| **1 task** | Any | No numbering needed |
| **2-9 tasks** | Flat | Simple sequential (01, 02...) |
| **10+ tasks** | Flat | Simple sequential (01, 02...) |
| **Any** | Phased | Phase-Number (1-01, 1-02...) |
| **Any** | Modular | Module-Number (A-01, B-01...) |

**Guideline:** Use intelligent judgment based on project context. Numbering should aid clarity, not add complexity.

### Watchdog Glob Pattern

`task-????????-??????-*.md`

Matches files with or without optional numbering.

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

**Verify results in `tasks/task-monitor/results/`:**

- [ ] Status is `"completed"` (not `"failed"`)
- [ ] Error field is `null`
- [ ] Summary reviewed
- [ ] Artifacts verified

---

## Full Examples

### Scenario 1 Example: Single Task from Conversation

```bash
# Step 1: Verify service running and set project path
task-monitor status
# Output: Running
task-monitor use "$(pwd)"
# Output: Current project set to: /home/admin/workspaces/datachat

# Step 2: Investigate and understand (read conversation, explore codebase)

# Step 3: Write temp file
# File: tasks/task-monitor/pending/task-fix-auth-timeout.md.tmp

# Step 4: Rename
bash .claude/skills/task-document-writer/scripts/rename_task.sh tasks/task-monitor/pending/task-fix-auth-timeout.md.tmp
# Output: ✅ Task created: tasks/task-monitor/pending/task-20260129-170500-fix-auth-timeout.md

# Step 5: Verify task started
task-monitor queue
# Output: Queue size: 0, Processing: task-20260129-170500-fix-auth-timeout.md
task-monitor task-20260129-170500-fix-auth-timeout
# Output: Status: processing (task is now being processed by Worker Agent)
```

Note: Only monitor further when user explicitly asks to check progress.

### Scenario 2 Example: Bulk Tasks from Breakdown

```bash
# Step 1: Verify service running and set project path
task-monitor status
task-monitor use "$(pwd)"

# Step 2: Read and parse planning document
# Document: tasks/task-planning/user-authentication.md
# Extract: 8 tasks across 3 modules (FEATURE_MODULE)
# AI decides: Add module-numbering (A-01, A-02, B-01, B-02, C-01, C-02, C-03, C-04)

# Step 3: Generate all temp files
# tasks/task-monitor/pending/task-user-registration.md.tmp
# tasks/task-monitor/pending/task-build-login-system.md.tmp
# tasks/task-monitor/pending/task-design-product-model.md.tmp
# ... (8 total)

# Step 4: Batch rename all files (sorted by creation time)
bash .claude/skills/task-document-writer/scripts/rename_task.sh
# Output:
# 🔍 Found 8 temp file(s) to process
# [1/8] Processing: task-user-registration.md.tmp
# ✅ Task created: tasks/task-monitor/pending/task-20260131-204500-A-01-user-registration.md
# [2/8] Processing: task-build-login-system.md.tmp
# ✅ Task created: tasks/task-monitor/pending/task-20260131-204501-A-02-build-login-system.md
# [3/8] Processing: task-design-product-model.md.tmp
# ✅ Task created: tasks/task-monitor/pending/task-20260131-204502-B-01-design-product-model.md
# ... (8 total)
# ✅ Batch processing complete: 8 file(s) renamed

# Step 5: Verify tasks are processing
task-monitor queue
# Output: Queue size: 0, Processing: task-20260131-204500-A-01-...
task-monitor task-20260131-204500-A-01-user-registration
# Output: Status: processing
```

Note: Only monitor further when user explicitly asks to check progress.

---

## Key Principles

1. **Scenario 1 is default** - Unless user explicitly requests Scenario 2, always use Scenario 1
2. **Scenario 2 requires explicit request** - Bulk operations should be intentional; detect trigger phrases
3. **Service must be running** - HARD STOP if service not running
4. **Understand first** - Investigate before writing (Scenario 1) or read planning document (Scenario 2)
5. **Be specific** - Vague tasks produce vague results
6. **Request investigation** - Worker Agents must do their own deep research
7. **Define success** - Worker needs clear completion criteria
8. **Provide context** - Worker should understand why the task exists
9. **Verify startup only** - After task is queued, just verify it started. DON'T continuously poll during processing.
10. **Monitor on request** - Only check task progress when user explicitly asks you to.
11. **Bulk awareness** - Scenario 2 creates multiple tasks; track all of them
12. **Intelligent numbering** - Add sequential numbers/codes only when multiple tasks exist. Use judgment based on project structure (flat, phased, or modular).

---

## Related Skills

- `task-planning`: Generates planning documents for Scenario 2
- `task-monitor-setup`: Creates the monitoring system that processes task documents
- `task-implementation`: Executes tasks with worker-auditor workflow (called by monitor)
