---
name: task-document-generator
description: "Generates structured task documents from conversation context for delegation to Worker Agents via the task monitoring system. Use when: a task identified in conversation needs to be implemented by another agent; you need to convert user requirements into a clear, actionable task document; the task should be queued for sequential processing."
---

# Task Document Generator

## Workflow

Convert conversation context and user requirements into a structured task document, then save it to the `tasks/` directory for pickup by the task monitoring system.

### Input

- **Conversation history** - The full discussion between user and AI; read all history but focus especially on the recent conversation
- **Context** - Project context (codebase, architecture, current state)
- **Task intent** - What needs to be done (may be implied from conversation)

## File Generation (5 Steps)

### Step 1: Verify Task Monitor Service Running

**BEFORE creating any task document**, verify that the task monitoring service is running. If the service is not running, the task document will never be processed and will sit idle in the `tasks/` directory.

**1.1 Check Service Status**

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

**1.2 If Service Is Running**

✅ Continue to Step 2.

**1.3 If Service Is NOT Running - STOP**

⚠️ **STOP and ask the user**:

```
⚠️ Task monitor service is not running. The task document will not be processed automatically.

Would you like me to start the task monitor service now? Please confirm, and I will start it before continuing with task creation.
```

- If user confirms → Start the service using `task-monitor start` or appropriate command, then verify it's running
- Only proceed to Step 2 **after** the service is confirmed running

**1.4 Quality Gate**

- **MUST NOT proceed** to Step 2 until the service is confirmed running
- This is a hard stop - no "create anyway" option

---

### Step 2: Investigate & Understand (Before Writing)

Before writing the task document, ensure you fully understand the context and requirements.

**2.1 Analyze Conversation**

Re-read the discussion to identify:
- The original problem/request
- Decisions made during discussion
- Constraints mentioned
- Acceptance criteria discussed
- Any assumptions that need clarification

**2.2 Clarify Task Intent**

Define what needs to be done:
- Specific outcome required
- Boundaries of the task (what's included/excluded)
- Success metrics

**2.3 Investigate Codebase**

Use tools to gather technical context:

```bash
# Find relevant files
glob "**/*.py"           # or appropriate pattern
grep "keyword" --include="*.py"    # search for related code

# Read key files to understand patterns
```

**2.4 Identify Technical Context**

Determine:
- Current architecture/patterns used
- Dependencies and their locations
- Potential edge cases
- Integration points

**2.5 Quality Gate**

Before proceeding to write:
- If anything is unclear → ask questions
- If context is missing → investigate more
- Only write document when you have complete understanding

---

### Step 3: Write Temp File (AI Agent)

Once you fully understand the task, use the Write tool to create the task document with `.md.tmp` extension:

**Temp file pattern**: `tasks/task-{description}.md.tmp`

**Example**: `tasks/task-fix-auth-timeout.md.tmp`

- Simple filename with description only
- The `.tmp` extension prevents monitor from picking it up prematurely
- Timestamp will be added to filename in Step 4

**Why `.md.tmp` first?** The task monitor watches for `.md` files only. By writing to `.md.tmp` first, we ensure the document is complete before the monitor sees it. This prevents race conditions where an incomplete file gets executed.

---

### Step 4: Rename with Timestamp (Bash Script)

Run the rename script to atomically rename the temp file:

```bash
bash .claude/skills/task-document-generator/scripts/rename_task.sh /path/to/temp/file.md.tmp
```

**What the script does:**
1. Extracts description from temp filename
2. Gets current timestamp: `YYYYMMDD-HHMMSS`
3. Renames `task-{description}.md.tmp` → `task-{description}-{TIMESTAMP}.md`
4. Outputs the final file path

**Example transformation:**
```
tasks/task-fix-auth-timeout.md.tmp
    ↓
tasks/task-fix-auth-timeout-20260129-170500.md
```

**Capture the output** - The script outputs the final file path, which can be captured and passed to Step 5:

```bash
# Capture final file path
FINAL_FILE=$(bash .claude/skills/task-document-generator/scripts/rename_task.sh tasks/task-xxx.md.tmp)
```

---

### Step 5: Monitor Status (CLI - Enhanced)

Use the task-monitor CLI to check the task processing status with detailed information:

```bash
# Check full status (waiting + running tasks)
task-monitor queue

# Check specific task details (if task file exists)
task-monitor task-xxx-20260130-hhmmss.md
```

**What the CLI does:**
1. Checks the queue state file (`state/queue_state.json`)
2. Displays current task being processed
3. Shows tasks waiting in queue
4. Shows process information

**Output you'll see:**

```
┌─────────────────────────────────────────────┐
│  Task Monitor Status                         │
├─────────────────────────────────────────────┤
│  Service: ✅ Running                         │
│                                              │
│  Currently Processing:                       │
│  → task-refactor-phase2-20260130-110940.md  │
│                                              │
│  Waiting in Queue:                           │
│  → task-another-task-20260130-111500.md     │
│  → task-third-task-20260130-111600.md       │
│                                              │
│  Queue Size: 2                               │
└─────────────────────────────────────────────┘
```

**Interpreting the output:**

| Field | Meaning |
|-------|---------|
| **Currently Processing** | Task that was dequeued and is being executed by Worker Agent |
| **Waiting in Queue** | Tasks that have been created but not yet started |
| **Queue Size** | Number of tasks waiting (not including the one being processed) |

**Note**: The task-monitor CLI requires `~/.local/bin` to be in your PATH (already configured in `~/.bashrc`). If the command is not found, run `source ~/.bashrc` or open a new terminal.

## Full Example

```bash
# Step 1: Verify task monitor service is running
task-monitor queue

# IF RUNNING:
# Output: Service is running, proceed to Step 2

# IF NOT RUNNING:
# ⚠️ Task monitor service is not running. The task document will not be processed automatically.
# Would you like me to start the task monitor service now?
# (After user confirms and service starts)
# Output: Service is running, proceed to Step 2

# Step 2: Investigate and understand (read conversation, explore codebase)

# Step 3: Write temp file using Write tool
# File: tasks/task-fix-auth-timeout.md.tmp
# Content: (full task document)

# Step 4: Rename with timestamp
FINAL_FILE=$(bash .claude/skills/task-document-generator/scripts/rename_task.sh tasks/task-fix-auth-timeout.md.tmp)
# Output: ✅ Task created: tasks/task-fix-auth-timeout-20260129-170500.md
#         tasks/task-fix-auth-timeout-20260129-170500.md

# Step 5: Monitor status (shows both waiting and running)
task-monitor queue
# Output: Shows your task in "Currently Processing" or "Waiting in Queue"
```

## Document Structure

Use the template in [references/task-template.md](references/task-template.md) for the document structure.

**Required sections**:
- Task (one-line summary)
- Context (why this task exists)
- Scope (directories, files, dependencies)
- Requirements (specific, actionable)
- Deliverables (what Worker produces)
- Constraints (limitations)
- Success Criteria (how to verify completion)
- Worker Investigation Instructions (explicit research directives)

## Quality Checklist

Before running the rename script (Step 4), ensure:

- [ ] **Service verified and running** - Task monitor is running (Step 1 - HARD REQUIREMENT)
- [ ] **Task is clear** - One-line summary is unambiguous
- [ ] **Context is provided** - Worker understands why this task exists
- [ ] **Scope is defined** - Worker knows where to look
- [ ] **Requirements are specific** - Not vague like "improve code"
- [ ] **Investigation is requested** - Worker is told to do their own research
- [ ] **Success criteria exist** - Worker knows when they're done

## Examples

See [references/examples.md](references/examples.md) for good vs bad task document examples.

## Key Principles

1. **Service must be running** - HARD STOP if service not running; ask user to start it before proceeding
2. **Understand first** - Investigate before writing
3. **Be specific** - Vague tasks produce vague results
4. **Request investigation** - Worker Agents must do their own deep research before implementing
5. **Define success** - Worker needs clear completion criteria
6. **Provide context** - Worker should understand why the task exists
7. **Monitor visibility** - Show both waiting and running tasks for complete status

## Related Skills

- `task-monitor-system`: Creates the task monitoring system that processes these task documents
- `task-coordination`: Executes tasks with worker-auditor workflow (called by monitor)
