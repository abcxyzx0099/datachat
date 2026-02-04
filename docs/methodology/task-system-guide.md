# Task System Guide

Complete guide to the asynchronous task execution system (task-queue) that enables continuous conversation while tasks execute independently.

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Architecture Diagram](#architecture-diagram)
4. [Directory Structure](#directory-structure)
5. [Task Specification Format](#task-specification-format)
6. [Skills Reference](#skills-reference)
7. [Execution Model](#execution-model)
8. [CLI Commands](#cli-commands)
9. [Service Management](#service-management)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Create and Execute a Task

```bash
# 1. Use task-specification-generation to create a task specification
# This creates: tasks/task-specifications/task-YYYYMMDD-HHMMSS-{description}.md

# 2. Load tasks using CLI
task-queue load

# 3. Task executes in background using Claude Agent SDK

# 4. Check results
cat tasks/task-queue/results/task-{timestamp}-{description}.json

# 5. View detailed worker report
ls tasks/task-worker-reports/task-{timestamp}-{description}/
```

### Common Commands

```bash
# Check daemon status
task-queue status

# Set current project path
task-queue set-project "$(pwd)"

# Load tasks from specifications directory
task-queue load

# View queue status
task-queue queue

# View live logs
journalctl --user -u task-queue -f

# Check specific task result
cat tasks/task-queue/results/task-{timestamp}-{description}.json
```

---

## System Overview

The Task System is an asynchronous, background task execution architecture that:

- **Generates** task specifications via `task-specification-generation` skill
- **Loads** tasks manually via `task-queue load` CLI command
- **Queues** tasks sequentially within each project
- **Executes** tasks using Claude Agent SDK in isolated background sessions
- **Reports** results to two separate output locations
- **Archives** completed task specifications automatically

**Key Benefit:** Continue conversation while tasks execute independently in the background.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Conversation Layer                              │
│                   (User ↔ Claude Agent)                                 │
│                    (continues uninterrupted)                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 1: Task Planning (Optional)                                        │
│                                                                          │
│   task-planning skill → tasks/task-planning/{descriptive-name}.md       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 2: Task Specification Generation                                   │
│                                                                          │
│   task-specification-generation skill                                   │
│   → tasks/task-specifications/task-{timestamp}-{description}.md        │
│                                                                          │
│   Naming: task-YYYYMMDD-HHMMSS-{kebab-description}.md                   │
│   Example: task-20260202-120000-fix-auth-timeout.md                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 3: Load Tasks (Manual CLI Command)                                 │
│                                                                          │
│   task-queue load                                                         │
│   → Scans tasks/task-specifications/ for task-*.md files                │
│   → Sorts by creation time                                              │
│   → Adds to queue                                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 4: Task Management Daemon (Background Process)                 │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  TaskExecutor (task_queue/executor.py)                      │   │
│   │                                                                  │   │
│   │  options = ClaudeAgentOptions(                                  │   │
│   │      cwd=str(project_root),        # Project context           │   │
│   │      permission_mode="bypassPermissions", # Full autonomous    │   │
│   │      setting_sources=["project"],    # Load project skills     │   │
│   │  )                                                               │   │
│   │                                                                  │   │
│   │  query("/task-worker", prompt=task_specification_path)          │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ✓ Spawns worker agent in isolated session                             │
│   ✓ Non-blocking execution                                              │
│   ✓ Conversation continues                                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 5: Task Worker Execution                                            │
│                                                                          │
│   Worker Agent executes /task-worker skill:                             │
│   ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐  │
│   │ Implementation   │───→│    Auditor       │───→│   Quality Gate  │  │
│   │    Agent         │    │    Agent         │    │                 │  │
│   └──────────────────┘    └──────────────────┘    └─────────────────┘  │
│                                                                          │
│   Automatic iteration until quality threshold met (max 3 iterations)    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 6: Dual Output System                                              │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ Output 1: Implementation Results (Execution Tracking)           │   │
│   │                                                                  │   │
│   │ Location: tasks/task-queue/results/{task_id}.json     │   │
│   │ Purpose: Task status, duration, cost, errors                    │   │
│   │ Managed by: task-queue module (task_executor.py)      │   │
│   │                                                                  │   │
│   │ { "task_id": "...", "status": "completed",                      │   │
│   │   "stdout": "...", "stderr": null,                              │   │
│   │   "duration_seconds": 123.4, "cost_usd": 0.045, ... }            │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ Output 2: Worker Reports (Detailed Workflow)                    │   │
│   │                                                                  │   │
│   │ Location: tasks/task-worker-reports/{task_id}/                  │   │
│   │ Purpose: Iteration history, audit reports, implementation       │   │
│   │ Managed by: task-worker skill                                   │   │
│   │                                                                  │   │
│   │ ├── workflow-result.json      # Complete iteration history      │   │
│   │ ├── audit-report-iteration-1.md                                │   │
│   │ ├── audit-report-iteration-2.md                                │   │
│   │ └── implementation-summary.md                                   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
{project-root}/
├── tasks/
│   ├── task-planning/              # Task planning documents
│   │   └── {descriptive-name}.md
│   ├── task-specifications/        # Task specifications (source)
│   │   ├── task-*.md
│   │   └── archive/               # Completed specs (auto-moved)
│   ├── task-queue/        # Module-managed directory
│   │   ├── state/                 # Queue state (queue_state.json)
│   │   ├── results/               # Result JSON files
│   │   └── logs/                  # Execution logs
│   ├── task-archive/               # Central archive for all tasks
│   │   └── task-*.md
│   └── task-worker-reports/        # Worker execution reports
│       └── task-{timestamp}-{description}/
│           ├── workflow-result.json
│           ├── audit-report-iteration-*.md
│           └── implementation-summary.md
└── .claude/
    └── skills/
        ├── task-planning/
        ├── task-specification-generation/
        ├── task-queue/
        ├── task-worker/
        └── task-cleanup/
```

---

## Task Specification Format

### Naming Convention

| Component | Format | Example |
|-----------|--------|---------|
| **Prefix** | `task-` | `task-` |
| **Timestamp** | `YYYYMMDD-HHMMSS` | `20260202-120000` |
| **Separator** | `-` | `-` |
| **Description** | kebab-case | `fix-auth-timeout` |
| **Extension** | `.md` | `.md` |

**Full Example:** `task-20260202-120000-fix-auth-timeout.md`

### Document Template

```markdown
# Task: [One-line summary]

**Status**: pending

---

## Task
[Clear one-line description]

## Context
[Relevant background]

## Scope
[Directories, files, dependencies]

## Requirements
1. [Specific requirement]
2. [Specific requirement]

## Deliverables
[What Worker produces]

## Constraints
[Limitations]

## Success Criteria
[How to verify completion]

## Worker Investigation Instructions
[Explicit research directives]
```

---

## Skills Reference

### 1. task-planning

**Purpose:** Generate organized task planning documents from documentation

**Input:**
- All `.md` files from `docs/` directory
- User request/requirements

**Output:**
- `tasks/task-planning/{descriptive-name}.md`

**Organization Types:**
- **FLAT_LIST** (0-10 complexity score): Simple, linear work
- **IMPLEMENTATION_PHASE** (11-25): Sequential phases
- **FEATURE_MODULE** (26+): Independent modules

### 2. task-specification-generation

**Purpose:** Generate task specification documents from planning or conversation

**Two Scenarios:**

| Scenario | Input | Output |
|----------|-------|--------|
| **Scenario 1** | Conversation context | Single task specification |
| **Scenario 2** | Planning document | Multiple task specifications (bulk) |

**Output:** `tasks/task-specifications/task-{timestamp}-{description}.md`

**Key Features:**
- Direct `.md` generation (no `.md.tmp` files)
- No watchdog integration
- Manual loading required

### 3. task-queue

**Purpose:** Coordinate task execution using CLI commands

**Workflow:**
1. Verify daemon running
2. Load task specifications (`task-queue load`)
3. Monitor queue status (`task-queue queue`)
4. Display results (check `tasks/task-queue/results/`)

**Called by:** User or AI to manage task execution

### 4. task-worker

**Purpose:** Execute tasks with worker-auditor workflow

**Workflow:**
1. Implementation Agent executes task
2. Auditor Agent reviews output
3. Automatic iteration based on feedback (max 3x)
4. Quality gate: stops when threshold met

**Called by:** task-queue module (via Claude Agent SDK)

### 5. task-cleanup

**Purpose:** Clean up the tasks directory by removing all materials while preserving directory structure

**Workflow:**
1. Verify tasks directory exists
2. Show current contents and count files to be removed
3. Confirm with user before proceeding
4. Remove all files from subdirectories (via CLI commands)
5. Verify cleanup complete

**Official Directories Cleaned:**
- `tasks/task-archive/` - Archived task specifications
- `tasks/task-queue/results/` - Result JSON files
- `tasks/task-queue/state/` - Queue state files
- `tasks/task-planning/` - Planning documents
- `tasks/task-specifications/` - Task specifications
- `tasks/task-worker-reports/` - Worker execution reports

**Preserved:**
- `docs/methodology/task-system-guide.md` - Documentation file
- All subdirectories (empty, ready for new tasks)

**Called by:** User or AI when needing a clean slate for new task work

---

## Execution Model

### Within Project (Sequential)

Tasks in the same project execute one at a time (FIFO queue) to prevent file conflicts.

```
tasks/task-specifications/:
├── task-1.md ────→ [Load] ────→ [Queue] ────→ [Executing] ────→ Done
├── task-2.md ────→ [Load] ────→ [Waiting] ──→ [Next] ────────→ Done
└── task-3.md ────→ [Load] ────→ [Waiting] ──→ [Waiting] ──────→ ...
```

### Loading Process

Tasks are loaded manually via `task-queue load`:
1. Scan `tasks/task-specifications/` for `task-*.md` files
2. Sort by creation time (oldest first)
3. Add to queue
4. Daemon processes queue sequentially

---

## CLI Commands

The `task-queue` CLI provides these commands:

```bash
# Show daemon status (Running/Stopped)
task-queue status

# Show queue state
task-queue queue

# Show current project
task-queue show-project

# Set current project
task-queue set-project /path/to/project

# Load tasks from specifications directory
task-queue load

# Show detailed status (including completed tasks)
task-queue status -v

# View task results
cat tasks/task-queue/results/task-{timestamp}-{description}.json

# View task execution logs
cat tasks/task-queue/logs/task-{timestamp}-{description}.log
```

---

## Service Management

The task-queue daemon runs as a systemd user service.

```bash
# Start service
systemctl --user start task-queue

# Stop service
systemctl --user stop task-queue

# Restart service
systemctl --user restart task-queue

# Check status
systemctl --user status task-queue

# Enable at login
systemctl --user enable task-queue

# View live logs
journalctl --user -u task-queue -f

# View last 100 log lines
journalctl --user -u task-queue -n 100
```

---

## Troubleshooting

### Service won't start

**Symptom:** `systemctl --user status task-queue` shows "failed" or "inactive"

**Solutions:**

1. **Check the logs:**
   ```bash
   journalctl --user -u task-queue -n 50
   ```

2. **Verify directory structure:**
   ```bash
   ls -la tasks/task-specifications/
   ls -la tasks/task-queue/{state,results,logs}
   ```

3. **Verify Python environment:**
   ```bash
   cd /home/admin/workspaces/task-queue
   source .venv/bin/activate
   pip install -e .
   ```

### Tasks not being loaded

**Symptom:** `task-queue load` shows no tasks

**Solutions:**

1. **Verify task files exist:**
   ```bash
   ls tasks/task-specifications/task-*.md
   ```

2. **Check naming pattern:** Task files must match `task-YYYYMMDD-HHMMSS-*.md`

3. **Check service is running:**
   ```bash
   systemctl --user status task-queue
   ```

### Task execution errors

**Symptom:** Task completes with "failed" status

**Solutions:**

1. **View error details:**
   ```bash
   cat tasks/task-queue/results/task-{id}.json
   ```

2. **Check detailed worker report:**
   ```bash
   ls tasks/task-worker-reports/task-{id}/
   cat tasks/task-worker-reports/task-{id}/audit-report-*.md
   ```

3. **Verify project context:** Task should execute with correct working directory

### Tasks not archiving

**Symptom:** Completed specs remain in `task-specifications/`

**Cause:** Archive path may be incorrect

**Solution:** Verify archive path points to correct location:
```bash
ls tasks/task-archive/
```

---

## Key Design Principles

1. **Conversation Continuity** - Tasks run in background, user keeps chatting
2. **Manual Loading** - Tasks must be explicitly loaded via CLI command
3. **Sequential Within Project** - Prevents file conflict race conditions
4. **Direct Generation** - No `.md.tmp` files, specs generated directly
5. **Traceability** - Full stdout/stderr captured in results JSON
6. **Auto-Iteration** - Worker-auditor loop until quality threshold met
7. **Project Context** - Each task runs with correct `cwd` and project settings

---

## Related Modules

### task-queue Module

**Location:** `/home/admin/workspaces/task-queue/`

**Installation:**
```bash
# Install in datachat venv
cd /home/admin/workspaces/datachat
.venv/bin/pip install -e /home/admin/workspaces/task-queue
```

**Components:**
- **daemon.py**: Background daemon process
- **executor.py**: Executes tasks via Claude Agent SDK
- **processor.py**: Loads and queues tasks
- **scanner.py**: Scans for task specification files
- **cli.py**: CLI commands (`task-queue`)
- **monitor.py**: Main queue orchestration
- **models.py**: Pydantic data models
- **config.py**: Configuration management
- **atomic.py**: Atomic file operations

**Service:** `~/.config/systemd/user/task-queue.service`
```bash
cd /home/admin/workspaces/task-queue
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Service:** `~/.config/systemd/user/task-queue.service`

---

## Migration from Old System

### Key Changes

| Aspect | Old System | New System |
|--------|-----------|------------|
| **Source Directory** | `tasks/task-monitor/pending/` | `tasks/task-specifications/` |
| **File Creation** | `.md.tmp` → rename | Direct `.md` |
| **Detection** | Watchdog (automatic) | Manual CLI load |
| **Skill** | `task-document-writer` | `task-specification-generation` |
| **Executor** | `task-queue` (skill) | `task-worker` (skill) |
| **Module** | `task-monitor` | `task-queue` |
| **CLI** | `task-monitor` | `task-queue` |
| **Worker Reports** | `tasks/task-queue/` | `tasks/task-worker-reports/` |

### Migration Steps

1. **Create new directories:**
   ```bash
   mkdir -p tasks/{task-specifications,task-queue/{state,results,logs},task-archive,task-worker-reports}
   ```

2. **Install new module:**
   ```bash
   cd /home/admin/workspaces/task-queue
   source .venv/bin/activate
   pip install -e .
   ```

3. **Set project path:**
   ```bash
   task-queue set-project "$(pwd)"
   ```

4. **Start daemon:**
   ```bash
   systemctl --user start task-queue
   ```

5. **Load tasks:**
   ```bash
   task-queue load
   ```
