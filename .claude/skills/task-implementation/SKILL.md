---
name: task-implementation
description: "Coordinates task execution using the task-implementation module. Loads task specifications from tasks/task-specifications/ directory using CLI commands and monitors execution progress. Use when: you have task specifications ready; you need to queue and execute tasks; you want to monitor task status and results."
---

# Task Implementation

Coordinate task execution using the task-implementation module and CLI commands.

## Overview

This skill bridges the gap between task specifications and execution. It uses the `task-impl` CLI to:
1. **Load** task specifications into the queue
2. **Monitor** execution status
3. **Display** results

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User / AI Agent                          │
│                 (invokes /task-implementation)              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Task Implementation Skill                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Verify daemon running                            │  │
│  │ 2. Load task specs (task-impl load)                 │  │
│  │ 3. Monitor status (task-impl queue/status)          │  │
│  │ 4. Display results (task-impl result/history/logs)  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│          task-implementation Module (CLI: task-impl)        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Daemon: Background process that manages queue        │  │
│  │ Executor: Calls /task-worker skill for each task     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Task Worker Skill                         │
│           (worker-auditor workflow, auto-iteration)         │
└─────────────────────────────────────────────────────────────┘
```

## When to Use

Call this skill when:
- Task specifications have been created (by `task-specification-generation`)
- You want to load and queue tasks for execution
- You need to monitor task execution progress
- You want to view task results

## CLI Commands Reference

The task-implementation module provides these commands:

| Command | Purpose |
|---------|---------|
| `task-impl use <path>` | Set current project path |
| `task-impl status` | Show daemon status |
| `task-impl queue` | Show queue state |
| `task-impl load` | Load tasks from specifications directory |
| `task-impl result <id>` | Show task result details |
| `task-impl history` | List completed tasks |
| `task-impl logs <id>` | Show task execution logs |

## Workflow

### Step 1: Verify Daemon Running

**Before loading tasks, check if the daemon is running:**

```bash
task-impl status
```

**Expected output:**
```
Running
```

**If NOT running:**
```
⚠️ Task implementation daemon is not running.

Would you like me to start the daemon now?
  systemctl --user start task-implementation
```

### Step 2: Set Project Path (if needed)

```bash
# Set current project to working directory
task-impl use "$(pwd)"
```

### Step 3: Load Task Specifications

```bash
# Load all task-*.md files from tasks/task-specifications/
task-impl load
```

**Expected output:**
```
Loaded N task(s) from tasks/task-specifications/
  - task-20260202-120000-fix-auth-timeout.md
  - task-20260202-120500-add-user-profile.md

Added N task(s) to queue.
Total queue size: N

Use 'task-impl queue' to check the queue status
```

### Step 4: Monitor Queue Status

```bash
task-impl queue
```

**Expected output:**
```
Project: /home/admin/workspaces/datachat
Queue size: 1
Processing: task-20260202-120000-fix-auth-timeout.md
Queued tasks:
  1. task-20260202-120500-add-user-profile.md
```

### Step 5: Monitor Progress (Optional)

**Only monitor when user explicitly asks to check progress.**

```bash
# Check specific task status
task-impl result task-20260202-120000

# View execution logs
task-impl logs task-20260202-120000

# View history
task-impl history
```

**DO NOT continuously poll during execution.** Only check when the user asks.

## Directory Structure

```
tasks/
├── task-specifications/        # Source of task specs
│   ├── task-*.md              # Ready to load
│   └── archive/               # Completed specs (auto-moved)
├── task-implementation/        # Module-managed
│   ├── state/                 # queue_state.json
│   ├── results/               # Result JSON files
│   └── logs/                  # Execution logs
├── task-archive/               # Central archive
└── task-worker-reports/        # Worker execution reports
    └── task-{timestamp}-{description}/
        ├── workflow-result.json
        ├── audit-report-iteration-*.md
        └── implementation-summary.md
```

## Example Usage

### Scenario: Load and Execute Tasks

**User says:** "Load and execute the task specifications"

**Workflow:**

```bash
# 1. Check daemon status
task-impl status
# Output: Running

# 2. Load tasks
task-impl load
# Output:
# Loaded 2 task(s) from tasks/task-specifications/
# Added 2 task(s) to queue.
# Total queue size: 2

# 3. Verify queue
task-impl queue
# Output:
# Queue size: 2
# Processing: task-20260202-120000-fix-auth-timeout.md
# Queued tasks:
#   1. task-20260202-120500-add-user-profile.md
```

**Inform user:**
```
✅ Tasks loaded and queued for execution.

Current status:
- Queue size: 2
- Processing: task-20260202-120000-fix-auth-timeout.md

The daemon will process tasks sequentially. I can check progress when you ask.
```

### Scenario: Check Progress

**User says:** "Check task progress"

**Workflow:**

```bash
# Check queue status
task-impl queue

# If first task completed, check result
task-impl result task-20260202-120000

# Show logs if needed
task-impl logs task-20260202-120000
```

## Result Interpretation

### From `task-impl result`

```
Task ID: task-20260202-120000-fix-auth-timeout
Status: completed
Created: 2026-02-02 12:00:00
Started: 2026-02-02 12:00:05
Completed: 2026-02-02 12:05:30
Duration: 325.42 seconds

Summary:
  Task completed successfully

Usage:
  Tokens: 45,230
  Cost: $0.1234
```

### Status Values

| Status | Meaning |
|--------|---------|
| `queued` | Waiting in queue |
| `running` | Currently executing |
| `completed` | Finished successfully |
| `failed` | Failed with error |

## Service Management

### Start/Stop Daemon

```bash
# Start daemon
systemctl --user start task-implementation

# Stop daemon
systemctl --user stop task-implementation

# Enable at login
systemctl --user enable task-implementation

# View logs
journalctl --user -u task-implementation -f
```

## Key Principles

1. **Manual Loading** - Tasks must be explicitly loaded via `task-impl load`
2. **Sequential Execution** - Tasks execute one at a time (FIFO)
3. **Background Processing** - Daemon runs independently
4. **Status on Request** - Only check progress when user asks
5. **Auto-Archive** - Completed specs moved to `tasks/task-specifications/archive/`

## Related Skills

- **task-specification-generation**: Creates task specifications
- **task-worker**: Executes tasks with worker-auditor workflow
- **task-planning**: Generates planning documents

## Troubleshooting

### Daemon not running

```bash
task-impl status
# Output: Stopped

# Start it
systemctl --user start task-implementation
```

### No tasks loaded

```bash
task-impl load
# Output: No tasks to load.

# Check specifications directory
ls tasks/task-specifications/
# Ensure task-*.md files exist
```

### Task failed

```bash
# Check result
task-impl result task-{id}

# View logs
task-impl logs task-{id}

# Check worker reports
ls tasks/task-worker-reports/task-{id}/
```
