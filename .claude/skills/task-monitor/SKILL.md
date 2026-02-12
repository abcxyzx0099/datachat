---
name: task-monitor
description: "Monitors task execution status and checks results using the task-monitor CLI. Use when: you need to check task status; view execution progress; display completed or failed task results; cancel running tasks."
---

# Task Monitor

Monitor task execution status and check results using the task-monitor CLI.

## Overview

This skill focuses on monitoring and checking results after the task system has been initialized (by `task-init` skill).

| Purpose | Command |
|---------|---------|
| **Check status** | `task-monitor status` |
| **View detailed status** | `task-monitor status --detailed` |
| **Check task results** | `task-monitor tasks result <task-id>` |
| **View worker status** | `task-monitor workers status` |
| **Cancel running task** | `task-monitor tasks cancel <task-id>` |

## When to Use

Call this skill when:
- You need to check task execution status
- You want to monitor task progress
- You need to view completed or failed task results
- You want to cancel a running task
- You need to check worker status or daemon logs

## CLI Commands Reference

### Status Commands

| Command | Purpose |
|---------|---------|
| `status` | Show system status (overview) |
| `status --detailed` | Show detailed status with running tasks and task lists |

**Usage:**
```bash
task-monitor status
task-monitor status --detailed
```

**Expected output (overview):**
```
============================================================
📊 Task Monitor Status
============================================================

Project Workspace: /home/admin/workspaces/datachat
Task Source Directories: 2

📋 Overall Statistics:
   Pending:   1
   Completed: 2
   Failed:    0

📁 Per-Source Summary:

  📁 ad-hoc (✅ Idle)
      Path: /home/admin/workspaces/datachat/task-monitor/ad-hoc
      Pending: 1, Completed: 2, Failed: 0

  📁 planned (✅ Idle)
      Path: /home/admin/workspaces/datachat/task-monitor/planned
      Pending: 0, Completed: 0, Failed: 0
```

**Note:** The overview counts files in `pending/` - tasks that are currently running will still appear as "Pending" because the task file remains in `pending/` during execution. Use `--detailed` to see running tasks separately.

### Tasks Commands

| Command | Purpose |
|---------|---------|
| `tasks show <task-id>` | Show task document path |
| `tasks result <task-id>` | Show task result |
| `tasks cancel <task-id>` | Cancel a running task |

**Usage:**
```bash
task-monitor tasks show task-20260208-091827-refactor-current-step-to-string
task-monitor tasks result task-20260208-091827-refactor-current-step-to-string
task-monitor tasks cancel task-20260208-091827-refactor-current-step-to-string
```

### Workers Commands

| Command | Purpose |
|---------|---------|
| `workers status` | Show detailed worker status |
| `workers list` | List workers summary |

**Usage:**
```bash
task-monitor workers status
task-monitor workers list
```

## Task ID Format

**Full Task ID**: `task-{timestamp}-{description}`

| Component | Format | Example |
|-----------|--------|---------|
| Prefix | `task-` | `task-` |
| Timestamp | `YYYYMMDD-HHMMSS` | `20260208-091827` |
| Description | kebab-case | `refactor-current-step-to-string` |

**Example:**
- Filename: `task-20260208-091827-refactor-current-step-to-string.md`
- Task ID: `task-20260208-091827-refactor-current-step-to-string`

## Workflow Examples

### Check Current Status

```bash
# Overview
task-monitor status

# Detailed (shows running tasks)
task-monitor status --detailed
```

### View Completed Task Results

```bash
# List completed tasks
ls task-monitor/ad-hoc/completed/

# View result for specific task
task-monitor tasks result task-20260208-090033-fix-langgraph-json-docs

# Or read directly
cat task-monitor/ad-hoc/results/task-20260208-090033-fix-langgraph-json-docs.json
cat task-monitor/ad-hoc/reports/task-20260208-090033-fix-langgraph-json-docs.md
```

### View Failed Task Details

```bash
# List failed tasks
ls task-monitor/ad-hoc/failed/

# View result for failed task
task-monitor tasks result task-20260208-091827-refactor-current-step-to-string

# Check error file
cat task-monitor/ad-hoc/failed/task-20260208-091827-refactor-current-step-to-string.error.*
```

### Monitor Running Task

```bash
# Check if anything is running
task-monitor status --detailed

# Show worker status
task-monitor workers status

# View daemon logs (via journalctl)
journalctl --user -u task-monitor -f
```

### Cancel Running Task

```bash
# Check what's running
task-monitor workers status

# Cancel the task
task-monitor tasks cancel task-20260208-091827-refactor-current-step-to-string
```

## Directory Structure Reference

```
task-monitor/
├── ad-hoc/
│   ├── pending/          # Tasks waiting to be processed
│   ├── completed/        # Successfully completed tasks
│   ├── failed/           # Failed tasks (with .error files)
│   ├── results/          # JSON result files
│   └── reports/          # Execution reports
└── planned/
    ├── pending/
    ├── completed/
    ├── failed/
    ├── results/
    └── reports/
```

## Service Management

Start/Stop the daemon (when needed):

```bash
# Start daemon
systemctl --user start task-monitor

# Stop daemon
systemctl --user stop task-monitor

# Restart daemon
systemctl --user restart task-monitor

# View daemon logs (use journalctl)
journalctl --user -u task-monitor -f    # Follow live logs
journalctl --user -u task-monitor -n 50 # Show last 50 lines
```

## Result Interpretation

### Check Completed Tasks

```bash
# List completed tasks
ls task-monitor/ad-hoc/completed/

# View completed task report
cat task-monitor/ad-hoc/reports/task-{id}.md

# Check result JSON
task-monitor tasks result task-{id}
cat task-monitor/ad-hoc/results/task-{id}.json
```

**Successful completion indicators:**
- Task moved to `completed/` directory
- Result JSON shows `"success": true`
- Report shows `Final Verdict: PASS`

### Check Failed Tasks

```bash
# Check failed count
task-monitor status

# View failed task
cat task-monitor/ad-hoc/failed/task-{id}.md

# Check error file
cat task-monitor/ad-hoc/failed/task-{id}.error.*

# Check result for error details
task-monitor tasks result task-{id}
```

**Failure indicators:**
- Task moved to `failed/` directory
- Error file present (`.error.*`)
- Result JSON shows error details

## Finding Task IDs

```bash
# List all tasks
find task-monitor/ad-hoc -name "task-*.md"

# Find recent tasks
ls -lt task-monitor/ad-hoc/completed/ | head -10

# Find tasks by pattern
ls task-monitor/ad-hoc/*/task-*refactor*.md
```

## In-Memory Task Tracking

The daemon tracks currently running tasks using **in-memory tracking** (not lock files).

**How it works:**
- The daemon maintains a `current_tasks` dictionary: `queue_id -> task_id`
- When a task starts, it's tracked in memory
- The task file stays in `pending/` during execution
- When complete, the file moves to `completed/` or `failed/`
- No lock files are created

**Status Command Behavior:**
- **Overview** (`task-monitor status`): Counts files in `pending/` - includes running tasks
- **Detailed** (`task-monitor status --detailed`): Shows running task separately from pending

```bash
# Check for running tasks (uses in-memory tracking)
task-monitor status --detailed

# The daemon logs show when tasks start/complete
journalctl --user -u task-monitor -f
```

## Related Skills

- **task-init**: Initializes task system, adds queues, installs CLI
- **task-documents**: Creates task specifications
- **task-execution**: Executes tasks with worker-auditor workflow
- **task-planning**: Generates planning documents

## Troubleshooting

### Daemon not running

```bash
task-monitor status
# If not running, start it:
systemctl --user start task-monitor
```

### Tasks not being processed

```bash
# Check if daemon is running
systemctl --user status task-monitor.service

# Check daemon logs (via journalctl)
journalctl --user -u task-monitor -n 50
```

### Task stuck in "running" state

If a task appears to be stuck running:

```bash
# Check daemon logs to see what's happening
journalctl --user -u task-monitor -n 50

# Restart the daemon to clear in-memory state
systemctl --user restart task-monitor

# After restart, the task will be re-queued in pending/
```

**Note:** In-memory tracking is cleared when the daemon restarts. Tasks in `pending/` will be re-processed from the beginning.
