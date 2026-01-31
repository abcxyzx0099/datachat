# Task Monitor Workflow Documentation

## Overview

The Task Monitor System is an asynchronous, background task execution architecture that enables continuous conversation while tasks execute independently. This document describes the complete workflow from task creation to completion.

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
│ │  Conversation       │    │  Task Breakdown                        │ │
│ └─────────────────────┘    └─────────────────────────────────────────┘ │
│           │                              │                             │
│           ▼                              ▼                             │
│ ┌─────────────────────┐    ┌─────────────────────────────────────────┐ │
│ │ task-document-writer│    │ task-breakdown → implementation-artifacts│ │
│ │ (single task)       │    │     /{wave-name}-tasks.md               │ │
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
│   tasks/pending/task-{timestamp}-{description}.md                        │
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
│   Location: tasks/pending/                                               │
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
│   │      permission_mode="acceptEdits", # Auto-accept file edits   │   │
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
│ Step 6: Result Storage                                                   │
│                                                                          │
│   tasks/results/{task_id}.json                                           │
│                                                                          │
│   {                                                                      │
│     "task_id": "task-20260131-204500-fix-auth-timeout",                 │
│     "status": "completed",                                               │
│     "stdout": "...",                                                     │
│     "stderr": null,                                                      │
│     "duration_seconds": 123.4,                                           │
│     "started_at": "2026-01-31T20:45:00",                                 │
│     "completed_at": "2026-01-31T20:47:03",                               │
│     "worker_output": {                                                   │
│       "summary": "Task completed successfully",                          │
│       "usage": {...},                                                    │
│       "cost_usd": 0.045                                                  │
│     },                                                                   │
│     "error": null                                                        │
│   }                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Task Document Naming Convention

| Component | Format | Example |
|-----------|--------|---------|
| **Prefix** | `task-` | `task-` |
| **Timestamp** | `YYYYMMDD-HHMMSS` | `20260131-204500` |
| **Separator** | `-` | `-` |
| **Description** | kebab-case | `fix-auth-timeout` |
| **Extension** | `.md` | `.md` |

**Full Example:** `task-20260131-204500-fix-auth-timeout.md`

**Watchdog Glob Pattern:** `task-????????-??????-*.md`

---

## Directory Structure

```
{project-root}/
├── tasks/
│   ├── pending/           # Task documents (monitored by watchdog)
│   │   └── task-*.md
│   ├── results/           # Execution results (JSON)
│   │   └── task-*.json
│   ├── logs/              # Monitor logs
│   │   └── monitor.log
│   ├── state/             # Queue state
│   │   └── queue_state.json
│   └── archive/           # Completed tasks (moved manually)
├── implementation-artifacts/
│   └── {wave-name}-tasks.md   # Task breakdown documents
└── .claude/
    └── skills/
        ├── task-breakdown/
        ├── task-document-writer/
        ├── task-implementation/
        └── task-monitor-system/
```

---

## Skills and Their Responsibilities

### 1. task-breakdown
**Purpose:** Generate organized task lists from documentation

**Input:**
- All `.md` files from `docs/` directory
- User request/requirements

**Output:**
- `implementation-artifacts/{wave-name}-tasks.md`

**Organization Types:**
- **FLAT_LIST** (0-10 complexity score): Simple, linear work
- **IMPLEMENTATION_PHASE** (11-25): Sequential phases
- **FEATURE_MODULE** (26+): Independent modules

---

### 2. task-document-writer
**Purpose:** Generate structured task documents for Worker Agents

**Two Scenarios:**

| Scenario | Input | Output |
|----------|-------|--------|
| **Scenario 1** | Conversation context | Single task document |
| **Scenario 2** | Breakdown document | Multiple task documents (bulk) |

**Output:** `tasks/pending/task-{timestamp}-{description}.md`

**Document Template:**
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

### 3. task-implementation
**Purpose:** Execute tasks with worker-auditor workflow

**Workflow:**
1. Implementation Agent executes task
2. Auditor Agent reviews output
3. Automatic iteration based on feedback (max 3x)
4. Quality gate: stops when threshold met

**Called by:** TaskExecutor via Claude Agent SDK (not directly)

---

### 4. task-monitor-system
**Purpose:** Infrastructure for task monitoring and execution

**Components:**
- **monitor_daemon.py**: Multi-project watchdog daemon
- **task_executor.py**: Executes tasks using Claude Agent SDK
- **models.py**: Pydantic data models
- **cli.py**: Status CLI tool

**System Location:** `/opt/task-monitor/`

**Service:** `task-monitor.service` (systemd)

---

## Execution Model

### Within Project (Sequential)
```
Project tasks/pending/:
├── task-1.md ────→ [Queue] ────→ [Executing] ────→ Done
├── task-2.md ────→ [Waiting] ──→ [Next] ────────→ Done
└── task-3.md ────→ [Waiting] ──→ [Waiting] ──────→ ...
```

### Across Projects (Parallel)
```
Time:  0s    10s   20s   30s   40s   50s
       │     │     │     │     │     │

datachat:   [task-1───] [task-2──────] [task-3─]

project-b:  [task-1───────────] [task-2───] [task-3]
```

---

## Why Claude Agent SDK?

| Question | Answer |
|----------|--------|
| **Why not call skill directly?** | Would block conversation |
| **Why SDK?** | Spawns isolated background session |
| **Benefit?** | Conversation continues while tasks execute |
| **Isolation?** | Each task runs independently with correct `cwd` |

---

## Key Design Principles

1. **Conversation Continuity** - Tasks run in background, user keeps chatting
2. **Event-Driven** - Watchdog detects new files, no polling
3. **Sequential Within Project** - Prevents file conflict race conditions
4. **Parallel Across Projects** - Independent codebases don't interfere
5. **Traceability** - Full stdout/stderr captured in results JSON
6. **Auto-Iteration** - Worker-auditor loop until quality threshold met
7. **Project Context** - Each task runs with correct `cwd` and project settings

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
cat tasks/results/task-20260131-204500-fix-auth-timeout.json

# View monitor logs
sudo journalctl -u task-monitor -f
```

---

## Service Management

```bash
# Start service
sudo systemctl start task-monitor

# Stop service
sudo systemctl stop task-monitor

# Restart service
sudo systemctl restart task-monitor

# Check status
sudo systemctl status task-monitor

# Enable at boot
sudo systemctl enable task-monitor
```

---

*This document describes the task monitor workflow architecture and implementation details.*
