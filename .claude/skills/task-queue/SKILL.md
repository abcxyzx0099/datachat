---
name: task-queue
description: "Coordinates task execution using the task-queue module. Loads task specifications from tasks/task-specifications/ directory using CLI commands and monitors execution progress. Use when: you have task specifications ready; you need to queue and execute tasks; you want to monitor task status and results."
---

# Task Queue

Coordinate task execution using the task-queue module and CLI commands.

## Overview

This skill bridges the gap between task specifications and execution. It uses the `task-queue` CLI to:
1. **Load** task specifications into the queue
2. **Monitor** execution status
3. **Display** results

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User / AI Agent                          │
│                  (invokes /task-queue)                  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               Task Queue Skill                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Verify daemon running                            │  │
│  │ 2. Load task specs (task-queue load)                 │  │
│  │ 3. Monitor status (task-queue queue/status)          │  │
│  │ 4. Display results (cat tasks/task-queue/results//history/logs)  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│          task-queue Module (CLI: task-queue)        │
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

The task-queue module provides these commands:

| Command | Purpose |
|---------|---------|
| `task-queue set-project <path>` | Set project path |
| `task-queue show-project` | Show current project path |
| `task-queue status` | Show daemon and queue status |
| `task-queue queue` | Show queue state |
| `task-queue load` | Load tasks from spec directories |
| `task-queue process` | Process pending tasks |
| `task-queue list-specs` | List spec directories |
| `task-queue run` | Run monitor interactively |

## Workflow

### Step 1: Verify Daemon Running

**Before loading tasks, check if the daemon is running:**

```bash
task-queue status
```

**Expected output:**
```
Running
```

**If NOT running:**
```
⚠️ Task management daemon is not running.

Would you like me to start the daemon now?
  systemctl --user start task-queue
```

### Step 2: Set Project Path (if needed)

```bash
# Set current project to working directory
task-queue set-project "$(pwd)"
```

### Step 3: Load Task Specifications

```bash
# Load all task-*.md files from tasks/task-specifications/
task-queue load
```

**Expected output:**
```
Loaded N task(s) from tasks/task-specifications/
  - task-20260202-120000-fix-auth-timeout.md
  - task-20260202-120500-add-user-profile.md

Added N task(s) to queue.
Total queue size: N

Use 'task-queue queue' to check the queue status
```

### Step 4: Monitor Queue Status

```bash
task-queue queue
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
cat tasks/task-queue/results/task-20260202-120000.json

# View history
task-queue status -v
```

**DO NOT continuously poll during execution.** Only check when the user asks.

## Directory Structure

```
tasks/
├── task-specifications/        # Source of task specs
│   ├── task-*.md              # Ready to load
│   └── archive/               # Completed specs (auto-moved)
├── task-queue/                # Module-managed
│   └── results/               # Result JSON files
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
task-queue status
# Output: Running

# 2. Load tasks
task-queue load
# Output:
# Loaded 2 task(s) from tasks/task-specifications/
# Added 2 task(s) to queue.
# Total queue size: 2

# 3. Verify queue
task-queue queue
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
task-queue queue

# If first task completed, check result
cat tasks/task-queue/results/ task-20260202-120000

# Show logs if needed
cat tasks/task-queue/logs/ task-20260202-120000
```

## Result Interpretation

### From `cat tasks/task-queue/results/`

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
systemctl --user start task-queue

# Stop daemon
systemctl --user stop task-queue

# Enable at login
systemctl --user enable task-queue

# View logs
journalctl --user -u task-queue -f
```

## Key Principles

1. **Manual Loading** - Tasks must be explicitly loaded via `task-queue load`
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
task-queue status
# Output: Stopped

# Start it
systemctl --user start task-queue
```

### No tasks loaded

```bash
task-queue load
# Output: No tasks to load.

# Check specifications directory
ls tasks/task-specifications/
# Ensure task-*.md files exist
```

### Task failed

```bash
# Check result
cat tasks/task-queue/results/ task-{id}

# View logs
cat tasks/task-queue/logs/ task-{id}

# Check worker reports
ls tasks/task-worker-reports/task-{id}/
```
