---
name: results
description: "Coordinates task execution using the results module with watchdog auto-loading and per-source queue architecture. Registers Task Source Directories for monitoring and checks execution progress. Use when: you have task specifications ready; you need to register a source directory; you want to monitor task status and results."
---

# Task Queue

Coordinate task execution using the results module with watchdog auto-loading and per-source queue architecture.

## Overview

This skill bridges the gap between task specifications and execution. It uses the `results` CLI to:
1. **Initialize** the task system (one-time setup)
2. **Register** Task Source Directories for watchdog monitoring
3. **Monitor** execution status via the daemon
4. **Display** results from completed tasks

## Architecture (v2.1)

```
┌─────────────────────────────────────────────────────┐
│                    User / AI Agent                          │
│                  (invokes /results)                      │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│               Task Queue Skill                        │
│  ┌──────────────────────────────────────────────┐  │
│  │ 1. Verify daemon running                    │  │
│  │ 2. Check sources; init if needed            │  │
│  │ 3. Monitor execution status                 │  │
│  │ 4. Display results from archive             │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│       results Module (CLI: python -m task_queue.cli) │
│  ┌──────────────────────────────────────────────┐  │
│  │ Watchdog: Event-driven file system monitoring  │  │
│  │ Per-Source Workers: One thread per source    │  │
│  │ Sequential execution within each source       │  │
│  │ Lock Files: Track running tasks with metadata │  │
│  │ Executor: Calls /task-execution skill           │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│                   Task Executor Skill                       │
│           (worker-auditor workflow, auto-iteration)         │
└─────────────────────────────────────────────────────┘
```

## When to Use

Call this skill when:
- Task specifications have been created (by `pending`)
- You need to initialize or register Task Source Directories
- You want to check daemon status
- You need to monitor task execution progress

## CLI Commands Reference (v2.1)

The results module provides grouped commands:

### System Commands

| Command | Purpose |
|---------|---------|
| `init` | Initialize task system from current directory |
| `status` | Show system status (overview) |
| `status --detailed` | Show detailed status with running tasks and task lists |

### Sources Commands

| Command | Purpose |
|---------|---------|
| `sources list` | List registered Task Source Directories |
| `sources add <path> --id <id>` | Add a Task Source Directory |
| `sources rm --source-id <id>` | Remove a Task Source Directory |

### Tasks Commands

| Command | Purpose |
|---------|---------|
| `tasks show <task-id>` | Show task document path |
| `tasks logs <task-id>` | Show result JSON path |
| `tasks cancel <task-id>` | Cancel a running task |

### Workers Commands

| Command | Purpose |
|---------|---------|
| `workers status` | Show detailed worker status |
| `workers list` | List workers summary |

### Logs Command

| Command | Purpose |
|---------|---------|
| `logs` | Show daemon logs (exit with Ctrl+C) |
| `logs --follow` | Follow logs live |
| `logs --lines <n>` | Show last N lines |

## Lock File Format

When a task is running, a lock file is created:

**Location:** `{source-directory}/.task-{task-id}.lock`

**Format:**
```json
{
  "task_id": "task-20260207-123456-fix-bug",
  "worker": "ad-hoc",
  "thread_id": "140234567890123",
  "pid": 12345,
  "started_at": "2026-02-07T12:35:00.123456"
}
```

**Purpose:**
- Track which task is currently running
- Identify which worker is executing
- Enable stale lock detection (via PID check)
- Track execution start time

## Loading Methods

| Method | When to Use |
|--------|-------------|
| **Watchdog (auto)** | Production, continuous operation - tasks auto-load when files are created |
| **Interactive run** | Testing, one-off processing (`run --cycles N`) |

## Workflow

### Step 1: Initialize System (One-Time Setup)

**First, check if already initialized:**

```bash
python -m task_queue.cli sources list
```

**If empty or missing sources, initialize:**

```bash
# From your project directory
cd /home/admin/workspaces/datachat
python -m task_queue.cli init
```

This creates:
- Directory structure for ad-hoc and planned queues
- Registers both queues with watchdog monitoring

**After initialization:**
- Tasks are auto-loaded when files appear in `tasks/ad-hoc/pending/` or `tasks/planned/pending/`
- No manual loading required

### Step 2: Verify Daemon Running

**Before checking status, verify the daemon is running:**

```bash
python -m task_queue.cli status
```

**If NOT running:**

```bash
systemctl --user start results
```

### Step 3: Monitor Queue Status

```bash
# Overview mode
python -m task_queue.cli status

# Detailed mode (shows running tasks)
python -m task_queue.cli status --detailed

# Show worker details
python -m task_queue.cli workers status
```

**Expected output (overview):**
```
Project Workspace: /home/admin/workspaces/datachat
Task Source Directories: 2

📋 Overall Statistics:
   Pending:   2
   Completed: 5
   Failed:    0

📁 Per-Source Summary:

  📁 ad-hoc (✅ Idle)
      Pending: 1, Completed: 3, Failed: 0

  📁 planned (🔄 Running)
      Running: task-20260207-120000-add-feature
      Pending: 1, Completed: 2, Failed: 0
```

### Step 4: Monitor Progress (Optional)

**Only monitor when user explicitly asks to check progress.**

```bash
# Check status
python -m task_queue.cli status --detailed

# Show running task details
python -m task_queue.cli workers status

# View live logs
python -m task_queue.cli logs --follow
```

**DO NOT continuously poll during execution.** Only check when the user asks.

## Directory Structure

```
tasks/
├── ad-hoc/                           # Ad-hoc task queue
│   ├── staging/               # Staging area (atomic writes)
│   ├── pending/             # Input: Task specifications (Task Source Directory)
│   │   ├── task-YYYYMMDD-HHMMSS-{description}.md
│   │   └── .task-YYYYMMDD-HHMMSS-{description}.lock   # Lock file with metadata
│   ├── completed/                # Completed specs (auto-moved)
│   │   └── task-YYYYMMDD-HHMMSS-{description}.md
│   ├── failed/                 # Failed specs (auto-moved)
│   │   ├── task-{id}.md
│   │   └── task-{id}.error.*
│   ├── results/                  # Result JSON files
│   │   └── task-{id}.json
│   └── reports/                # Worker execution reports
│       └── task-{timestamp}-{description}/
│           ├── workflow-result.json
│           ├── audit-report-iteration-*.md
│           └── implementation-summary.md
│
└── planned/                          # Planned task queue
    └── (same structure)
```

## Per-Source Architecture (v2.1)

The results uses **per-source worker threads** with these rules:

| Rule | Description |
|------|-------------|
| **Same source** | Sequential FIFO execution (one at a time) |
| **Different sources** | Parallel execution (can run simultaneously) |
| **Worker threads** | One thread per Task Source Directory |
| **Lock files** | `.task-XXX.lock` tracks running task with metadata |

## Example Usage

### Scenario: Initialize and Execute Tasks

**User says:** "Initialize and execute the task specifications"

**Workflow:**

```bash
# 1. Check daemon status
python -m task_queue.cli status
# Output: Running or instructions to start

# 2. Check if sources are registered
python -m task_queue.cli sources list
# If empty or missing, proceed to init

# 3. Initialize system (one-time setup)
python -m task_queue.cli init
# Output:
# ✅ Initialization complete!
#   Project Workspace: /home/admin/workspaces/datachat
#   Registered Queues: 2
#
#   📁 ad-hoc
#      Path: /home/admin/workspaces/datachat/tasks/ad-hoc/pending
#
#   📁 planned
#      Path: /home/admin/workspaces/datachat/tasks/planned/pending

# 4. Check queue status
python -m task_queue.cli status --detailed
# Output: Shows pending/running/completed tasks
```

**Inform user:**
```
✅ Task system initialized successfully.

Task Source Directories are now registered for watchdog monitoring:
- Ad-hoc: tasks/ad-hoc/pending/
- Planned: tasks/planned/pending/

Tasks will be auto-loaded when files appear. The daemon processes tasks
sequentially per source. Different sources execute in parallel.
```

### Scenario: Check Progress

**User says:** "Check task progress"

**Workflow:**

```bash
# Check status with running tasks
python -m task_queue.cli status --detailed

# If task completed, check result
python -m task_queue.cli tasks logs task-20260207-120000

# View full result
cat tasks/ad-hoc/results/task-20260207-120000.json
```

### Scenario: Cancel Running Task

**User says:** "Cancel the running task"

**Workflow:**

```bash
# Check what's running
python -m task_queue.cli workers status

# Cancel the task
python -m task_queue.cli tasks cancel task-20260207-120000
# Output:
# 🛑 Cancelling task: task-20260207-120000
#    Worker: ad-hoc
# ✅ Lock file removed
# ✅ Task moved to failed directory
#    Reason: User cancelled
```

## Result Interpretation

### Check Completed Tasks

```bash
# List completed tasks
python -m task_queue.cli status --detailed
ls tasks/ad-hoc/completed/

# View completed task document
python -m task_queue.cli tasks show task-20260207-120000
cat tasks/ad-hoc/completed/task-20260207-120000.md
```

### Check Failed Tasks

```bash
# Check status for failed count
python -m task_queue.cli status

# View failed task
cat tasks/ad-hoc/failed/task-{id}.md

# Check result file
python -m task_queue.cli tasks logs task-{id}
cat tasks/ad-hoc/results/task-{id}.json
```

### Check Worker Reports

```bash
# List worker reports
ls tasks/ad-hoc/reports/

# View detailed execution report
cat tasks/ad-hoc/reports/task-{id}/workflow-result.json
cat tasks/ad-hoc/reports/task-{id}/audit-report-iteration-1.md
```

## Service Management

### Start/Stop Daemon

```bash
# Start daemon
systemctl --user start results

# Stop daemon
systemctl --user stop results

# Restart daemon
systemctl --user restart results

# Enable at login
systemctl --user enable results

# View live logs
python -m task_queue.cli logs --follow

# View last 100 log lines
python -m task_queue.cli logs --lines 100

# Or with journalctl
journalctl --user -u results -n 100
```

## Key Principles (v2.1)

1. **Event-Driven Monitoring** - Watchdog detects file changes instantly (no polling)
2. **Per-Source Worker Threads** - One worker thread per Task Source Directory
3. **Sequential Within Source** - Prevents file conflict race conditions
4. **Parallel Across Sources** - Different sources can execute simultaneously
5. **Background Processing** - Daemon runs independently with watchdog
6. **Lock File Tracking** - Running tasks tracked with metadata (worker, thread, PID)
7. **Stale Lock Detection** - Lock files with dead PIDs are automatically cleaned up
8. **Auto-Archive** - Completed specs moved to `tasks/*/completed/`
9. **Quick Start** - Use `init` command for one-time setup

## Related Skills

- **task-init**: Initializes task system with init/sources add/sources rm commands
- **pending**: Creates task specifications
- **task-execution**: Executes tasks with worker-auditor workflow
- **task-planning**: Generates planning documents

## Troubleshooting

### Daemon not running

```bash
python -m task_queue.cli status
# Output: Stopped or error message

# Start it
systemctl --user start results
```

### Tasks not being processed

```bash
# Check if sources are registered
python -m task_queue.cli sources list

# Check if task files exist
ls tasks/ad-hoc/pending/task-*.md
ls tasks/planned/pending/task-*.md

# Check if daemon is running
systemctl --user status results.service
```

### Watchdog not detecting files

```bash
# Verify Task Source Directory is configured
python -m task_queue.cli sources list

# Check daemon logs for watchdog errors
python -m task_queue.cli logs --lines 50
```

### Task stuck with lock file

```bash
# Check lock file
ls tasks/ad-hoc/pending/.task-*.lock

# View lock file contents
cat tasks/ad-hoc/pending/.task-XXX.lock

# Check if process is still running
ps aux | grep <pid-from-lock>

# If process is dead, daemon will clean up stale locks automatically
# Or manually remove the lock file
rm tasks/ad-hoc/pending/.task-XXX.lock
```

### Task failed

```bash
# Check failed task
python -m task_queue.cli tasks logs task-{id}
cat tasks/ad-hoc/failed/task-{id}.md

# Check detailed worker report
ls tasks/ad-hoc/reports/task-{id}/
cat tasks/ad-hoc/reports/task-{id}/audit-report-*.md
```
