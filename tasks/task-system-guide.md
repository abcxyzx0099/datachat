# Task Monitor System Guide

Complete guide to the asynchronous task execution system that enables continuous conversation while tasks execute independently.

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Architecture Diagram](#architecture-diagram)
4. [Directory Structure](#directory-structure)
5. [Task Document Format](#task-document-format)
6. [Dual Output System](#dual-output-system)
7. [Skills Reference](#skills-reference)
8. [Execution Model](#execution-model)
9. [CLI Commands](#cli-commands)
10. [Service Management](#service-management)
11. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Create and Execute a Task

```bash
# 1. Use task-document-writer to create a task document
# This creates: tasks/task-monitor/pending/task-YYYYMMDD-HHMMSS-{description}.md

# 2. Watchdog automatically detects and queues the task

# 3. Task executes in background using Claude Agent SDK

# 4. Check results
cat tasks/task-monitor/results/task-*.json

# 5. View detailed implementation report
ls tasks/task-implementation/task-*/
```

### Common Commands

```bash
# Check service status
systemctl --user status task-monitor

# View queue status
task-monitor queue

# View live logs
journalctl --user -u task-monitor -f

# Check specific task result
cat tasks/task-monitor/results/task-*.json
```

---

## System Overview

The Task Monitor System is an asynchronous, background task execution architecture that:

- **Detects** new task documents via file system monitoring (watchdog)
- **Queues** tasks sequentially within each project (parallel across projects)
- **Executes** tasks using Claude Agent SDK in isolated background sessions
- **Reports** results to two separate output locations
- **Archives** completed task documents automatically

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
│ Step 1: Task Definition                                                  │
│ ┌─────────────────────┐    ┌─────────────────────────────────────────┐ │
│ │   Scenario 1        │    │   Scenario 2                            │ │
│ │  Conversation       │    │  Task Planning                        │ │
│ └─────────────────────┘    └─────────────────────────────────────────┘ │
│           │                              │                             │
│           ▼                              ▼                             │
│ ┌─────────────────────┐    ┌─────────────────────────────────────────┐ │
│ │ task-document-writer│    │ task-planning → tasks/task-planning│ │
│ │ (single task)       │    │     /{descriptive-name}.md               │ │
│ └─────────────────────┘    │              │                          │ │
│                            │              ▼                          │ │
│                            │   task-document-writer                   │ │
│                            │   (bulk task generation)                 │ │
│                            └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 2: Task Document Creation                                           │
│                                                                          │
│   tasks/task-monitor/pending/task-{timestamp}-{description}.md          │
│                                                                          │
│   Naming: task-YYYYMMDD-HHMMSS-{kebab-description}.md                   │
│   Example: task-20260131-204500-fix-auth-timeout.md                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 3: Watchdog Detection (Python watchdog library)                    │
│                                                                          │
│   Pattern: task-????????-??????-*.md                                     │
│   Location: tasks/task-monitor/pending/                                 │
│   Action: On file creation → Queue to project's FIFO queue             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 4: Claude Agent SDK (Background Process)                            │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  TaskExecutor (task_executor.py)                               │   │
│   │                                                                  │   │
│   │  options = ClaudeAgentOptions(                                  │   │
│   │      cwd=str(project_root),        # Project context           │   │
│   │      permission_mode="bypassPermissions", # Full autonomous    │   │
│   │      setting_sources=["project"],    # Load project skills     │   │
│   │  )                                                               │   │
│   │                                                                  │   │
│   │  query("/task-implementation", prompt=task_content)             │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ✓ Spawns worker agent in isolated session                             │
│   ✓ Non-blocking execution                                              │
│   ✓ Conversation continues                                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 5: Task Implementation                                               │
│                                                                          │
│   Worker Agent executes /task-implementation skill:                      │
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
│   │ Output 1: Monitor Results (Execution Tracking)                  │   │
│   │                                                                  │   │
│   │ Location: tasks/task-monitor/results/{task_id}.json            │   │
│   │ Purpose: Task status, duration, cost, errors                    │   │
│   │ Managed by: Monitor daemon (task_executor.py)                  │   │
│   │                                                                  │   │
│   │ { "task_id": "...", "status": "completed",                      │   │
│   │   "stdout": "...", "stderr": null,                              │   │
│   │   "duration_seconds": 123.4, "cost_usd": 0.045, ... }            │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ Output 2: Skill Reports (Detailed Workflow)                     │   │
│   │                                                                  │   │
│   │ Location: tasks/task-implementation/{task_id}/                  │   │
│   │ Purpose: Iteration history, audit reports, implementation       │   │
│   │ Managed by: task-implementation skill                           │   │
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
│   ├── task-planning/      # Task planning documents
│   │   └── {descriptive-name}.md
│   ├── task-monitor/       # Task monitoring system
│   │   ├── pending/        # Task documents (monitored by watchdog)
│   │   │   └── task-*.md
│   │   ├── results/        # Output 1: Execution results (JSON)
│   │   │   └── task-*.json
│   │   ├── logs/           # Monitor logs
│   │   │   └── monitor.log
│   │   ├── state/          # Queue state
│   │   │   └── queue_state.json
│   │   └── archive/        # Completed tasks (auto-archived)
│   ├── task-implementation/ # Output 2: Detailed workflow reports
│   │   └── task-{timestamp}-{description}/
│   │       ├── workflow-result.json
│   │       ├── audit-report-iteration-*.md
│   │       └── implementation-summary.md
│   └── task-monitor-guide.md  # This document
└── .claude/
    └── skills/
        ├── task-planning/
        ├── task-document-writer/
        ├── task-implementation/
        └── task-monitor-setup/
```

---

## Task Document Format

### Naming Convention

| Component | Format | Example |
|-----------|--------|---------|
| **Prefix** | `task-` | `task-` |
| **Timestamp** | `YYYYMMDD-HHMMSS` | `20260131-204500` |
| **Separator** | `-` | `-` |
| **Description** | kebab-case | `fix-auth-timeout` |
| **Extension** | `.md` | `.md` |

**Full Example:** `task-20260131-204500-fix-auth-timeout.md`

**Watchdog Glob Pattern:** `task-????????-??????-*.md`

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

## Dual Output System

The task monitoring system uses **two separate output locations** with distinct purposes:

### Output 1: Monitor Results (`tasks/task-monitor/results/`)

**Purpose:** Execution tracking and system-level monitoring

| Aspect | Description |
|--------|-------------|
| **Location** | `tasks/task-monitor/results/{task_id}.json` |
| **Managed by** | Monitor daemon (`task_executor.py`) |
| **Audience** | CLI tools, status queries, system monitoring |
| **Content** | Status, duration, cost, stdout/stderr, error info |

**Example questions answered:**
- Did the task complete successfully?
- How long did execution take?
- How much did it cost?
- Were there any errors or crashes?

**Format:**
```json
{
  "task_id": "task-20260131-204500-fix-auth-timeout",
  "status": "completed",
  "stdout": "...",
  "stderr": null,
  "duration_seconds": 123.4,
  "started_at": "2026-01-31T20:45:00",
  "completed_at": "2026-01-31T20:47:03",
  "worker_output": {
    "summary": "Task completed successfully",
    "usage": {...},
    "cost_usd": 0.045
  },
  "error": null
}
```

### Output 2: Skill Reports (`tasks/task-implementation/`)

**Purpose:** Detailed workflow results and implementation audit

| Aspect | Description |
|--------|-------------|
| **Location** | `tasks/task-implementation/{task_id}/` |
| **Managed by** | `task-implementation` skill |
| **Audience** | Developers reviewing implementation work |
| **Content** | Iteration history, audit reports, implementation details |

**Example questions answered:**
- What was actually implemented?
- How many iterations were needed?
- What was the audit feedback?
- What files were changed?
- Why did certain decisions get made?

**Directory structure:**
```
tasks/task-implementation/task-{timestamp}-{description}/
├── workflow-result.json           # Complete iteration history
├── audit-report-iteration-1.md    # Auditor feedback from round 1
├── audit-report-iteration-2.md    # Auditor feedback from round 2
└── implementation-summary.md      # What was implemented
```

### Separation of Concerns

| Concern | Monitor Results | Skill Reports |
|---------|----------------|---------------|
| **Focus** | Execution mechanics | Implementation details |
| **Creator** | Monitor daemon | Task skill |
| **Consumer** | System tools | Human developers |
| **Lifetime** | Short-term (status) | Long-term (reference) |

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

### 2. task-document-writer

**Purpose:** Generate structured task documents for Worker Agents

**Two Scenarios:**

| Scenario | Input | Output |
|----------|-------|--------|
| **Scenario 1** | Conversation context | Single task document |
| **Scenario 2** | Planning document | Multiple task documents (bulk) |

**Output:** `tasks/task-monitor/pending/task-{timestamp}-{description}.md`

### 3. task-implementation

**Purpose:** Execute tasks with worker-auditor workflow

**Workflow:**
1. Implementation Agent executes task
2. Auditor Agent reviews output
3. Automatic iteration based on feedback (max 3x)
4. Quality gate: stops when threshold met

**Called by:** TaskExecutor via Claude Agent SDK (not directly)

### 4. task-monitor-setup

**Purpose:** Infrastructure for task monitoring and execution

**Components:**
- **monitor_daemon.py**: Multi-project watchdog daemon
- **task_executor.py**: Executes tasks using Claude Agent SDK
- **models.py**: Pydantic data models
- **cli.py**: Status CLI tool

**System Location:** `/home/admin/workspaces/task-monitor/` (editable install)

**CLI:** `/home/admin/workspaces/task-monitor/.venv/bin/task-monitor`

**Service:** `~/.config/systemd/user/task-monitor.service` (user systemd service)

---

## Execution Model

### Within Project (Sequential)

Tasks in the same project execute one at a time (FIFO queue) to prevent file conflicts.

```
Project tasks/task-monitor/pending/:
├── task-1.md ────→ [Queue] ────→ [Executing] ────→ Done
├── task-2.md ────→ [Waiting] ──→ [Next] ────────→ Done
└── task-3.md ────→ [Waiting] ──→ [Waiting] ──────→ ...
```

### Across Projects (Parallel)

Different projects execute independently and simultaneously.

```
Time:  0s    10s   20s   30s   40s   50s
       │     │     │     │     │     │

datachat:   [task-1───] [task-2──────] [task-3─]

project-b:  [task-1───────────] [task-2───] [task-3]
```

---

## CLI Commands

```bash
# Check queue status
task-monitor queue

# View specific task
task-monitor task-20260131-204500-fix-auth-timeout

# List all tasks
task-monitor

# View result JSON
cat tasks/task-monitor/results/task-20260131-204500-fix-auth-timeout.json
```

---

## Service Management

```bash
# Start service
systemctl --user start task-monitor

# Stop service
systemctl --user stop task-monitor

# Restart service
systemctl --user restart task-monitor

# Check status
systemctl --user status task-monitor

# Enable at login
systemctl --user enable task-monitor

# View live logs
journalctl --user -u task-monitor -f

# View last 100 log lines
journalctl --user -u task-monitor -n 100

# View logs since 1 hour ago
journalctl --user -u task-monitor --since "1 hour ago"
```

---

## Troubleshooting

### Service won't start

**Symptom:** `systemctl --user status task-monitor` shows "failed" or "inactive"

**Solutions:**

1. **Check the logs:**
   ```bash
   journalctl --user -u task-monitor -n 50
   ```

2. **Verify directory structure:**
   ```bash
   ls -la tasks/task-monitor/{pending,results,logs,state,archive}
   ```

3. **Check project registry:**
   ```bash
   cat ~/.config/task-monitor/registered.json
   ```

4. **Verify Python environment:**
   ```bash
   cd /home/admin/workspaces/task-monitor
   source .venv/bin/activate
   pip install -e .
   ```

### Tasks not being detected

**Symptom:** Task files in `pending/` but not executing

**Solutions:**

1. **Verify watchdog pattern:** Task files must match `task-????????-??????-*.md`

2. **Check service is running:**
   ```bash
   systemctl --user status task-monitor
   ```

3. **Review logs for errors:**
   ```bash
   journalctl --user -u task-monitor -f | grep -E "(File event|error|failed)"
   ```

4. **Manually trigger queue check:** Restart the service
   ```bash
   systemctl --user restart task-monitor
   ```

### Task execution errors

**Symptom:** Task completes with "failed" status

**Solutions:**

1. **View error details:**
   ```bash
   cat tasks/task-monitor/results/task-{id}.json
   ```

2. **Check detailed implementation report:**
   ```bash
   ls tasks/task-implementation/task-{id}/
   cat tasks/task-implementation/task-{id}/audit-report-*.md
   ```

3. **Verify project context:** Task should execute with correct working directory

### FileNotFoundError in watchdog

**Symptom:** Logs show `FileNotFoundError: [Errno 2] No such file or directory`

**Cause:** Directory paths in code don't match actual directory structure

**Solution:**

1. **Verify paths in monitor_daemon.py:**
   ```python
   tasks_dir = project_path / "tasks" / "task-monitor" / "pending"
   ```

2. **Clear Python cache and reinstall:**
   ```bash
   cd /home/admin/workspaces/task-monitor
   find . -type d -name __pycache__ -exec rm -rf {} +
   find . -name "*.pyc" -delete
   pip install -e .
   systemctl --user restart task-monitor
   ```

### Tasks not archiving

**Symptom:** Completed tasks remain in `pending/`

**Cause:** Archive path in task_executor.py may be incorrect

**Solution:** Verify archive path points to correct location:
```python
self.archive_dir = self.project_root / 'tasks' / 'task-monitor' / 'archive'
```

---

## Key Design Principles

1. **Conversation Continuity** - Tasks run in background, user keeps chatting
2. **Event-Driven** - Watchdog detects new files, no polling
3. **Sequential Within Project** - Prevents file conflict race conditions
4. **Parallel Across Projects** - Independent codebases don't interfere
5. **Traceability** - Full stdout/stderr captured in results JSON
6. **Auto-Iteration** - Worker-auditor loop until quality threshold met
7. **Project Context** - Each task runs with correct `cwd` and project settings
