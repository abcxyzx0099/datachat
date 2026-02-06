---
name: task-queue
description: "Coordinates task execution using the task-queue module with watchdog auto-loading and per-source queue architecture. Registers Task Source Directories for monitoring and checks execution progress. Use when: you have task specifications ready; you need to register a source directory; you want to monitor task status and results."
---

# Task Queue

Coordinate task execution using the task-queue module with watchdog auto-loading and per-source queue architecture.

## Overview

This skill bridges the gap between task specifications and execution. It uses the `task-queue` CLI to:
1. **Register** Task Source Directories for watchdog monitoring (if not already registered)
2. **Monitor** execution status via the daemon
3. **Display** results from completed tasks

## Architecture (v2.0)

```
┌─────────────────────────────────────────────────────────────┐
│                    User / AI Agent                          │
│                  (invokes /task-queue)                      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               Task Queue Skill                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Verify daemon running                            │  │
│  │ 2. Check if registered; register if not             │  │
│  │ 3. Monitor execution status                          │  │
│  │ 4. Display results from archive                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│       task-queue Module (CLI: task-queue) v2.0              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Watchdog: Event-driven file system monitoring        │  │
│  │ Per-Source Workers: One thread per source            │  │
│  │ Sequential execution within each source              │  │
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
- Task specifications have been created (by `task-documents`)
- You need to register a Task Source Directory (one-time setup)
- You want to check daemon status
- You need to monitor task execution progress

## CLI Commands Reference (v2.0)

The task-queue module provides these commands:

| Command | Purpose |
|---------|---------|
| `task-queue register --task-source-dir <dir> --project-workspace <dir> --source-id <id>` | Register Task Source Directory for watchdog monitoring |
| `task-queue unregister --source-id <id>` | Remove Task Source Directory from monitoring |
| `task-queue list-sources` | List registered Task Source Directories |
| `task-queue status` | Show daemon and queue status |
| `task-queue run [--cycles N]` | Run interactively (for testing) |

## Loading Methods

| Method | When to Use |
|--------|-------------|
| **Watchdog (auto)** | Production, continuous operation - tasks auto-load when files are created |
| **Interactive run** | Testing, one-off processing (`task-queue run --cycles N`) |

## Workflow

### Step 1: Verify Daemon Running

**Before checking status, verify the daemon is running:**

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

### Step 2: Register Task Source Directory (One-Time Setup)

**First, check if the source is already registered:**

```bash
task-queue list-sources
```

**If the source is NOT listed (or shows "none"), register it:**

```bash
# Register Task Source Directory
task-queue register --task-source-dir tasks/task-documents --project-workspace /home/admin/workspaces/datachat --source-id main
```

**This command:**
1. Adds the directory to configuration for watchdog monitoring
2. Sets the project workspace if not already set
3. **Does NOT load tasks** - watchdog handles that automatically

**After registration:**
- Tasks are auto-loaded when files are created in `tasks/task-documents/`
- No manual loading required

### Step 3: Monitor Queue Status

```bash
task-queue status
```

**Expected output (per-source queues):**
```
Project Workspace: /home/admin/workspaces/datachat
Total Queue Size: 2

Task Source Directories: 1

📋 Overall Statistics:
   Pending:   2
   Running:   0
   Completed: 0
   Failed:    0

📁 Per-Source Details:

  📁 main
      Path: /home/admin/workspaces/datachat/tasks/task-documents
      Pending: 2, Running: 0, Completed: 0, Failed: 0
```

### Step 4: Monitor Progress (Optional)

**Only monitor when user explicitly asks to check progress.**

```bash
# Check status
task-queue status

# View live logs
journalctl --user -u task-queue -f
```

**DO NOT continuously poll during execution.** Only check when the user asks.

## Directory Structure

```
tasks/
├── task-documents/             # Input: Task specifications (Task Source Directory)
│   ├── task-YYYYMMDD-HHMMSS-{description}.md
│   └── .task-YYYYMMDD-HHMMSS-{description}.running  # Running marker
├── task-archive/               # Completed specs (auto-moved)
│   └── task-YYYYMMDD-HHMMSS-{description}.md
├── task-failed/                # Failed specs (auto-moved)
│   ├── task-YYYYMMDD-HHMMSS-{description}.md
│   └── task-YYYYMMDD-HHMMSS-{description}.error.*  # Error info
└── task-reports/               # Worker execution reports (detailed)
    └── task-{timestamp}-{description}/
        ├── workflow-result.json
        ├── audit-report-iteration-*.md
        └── implementation-summary.md
```

## Per-Source Architecture (v2.0)

The task-queue uses **per-source worker threads** with these rules:

| Rule | Description |
|------|-------------|
| **Same source** | Sequential FIFO execution (one at a time) |
| **Different sources** | Parallel execution (can run simultaneously) |
| **Worker threads** | One thread per Task Source Directory |

## Example Usage

### Scenario: Register and Execute Tasks

**User says:** "Register and execute the task specifications"

**Workflow:**

```bash
# 1. Check daemon status
task-queue status
# Output: Running

# 2. Check if source is registered
task-queue list-sources
# Output: (none) -- not registered, proceed to register

# 3. Register Task Source Directory (one-time setup)
task-queue register --task-source-dir tasks/task-documents --project-workspace /home/admin/workspaces/datachat --source-id main
# Output:
# ✅ Registered Task Source Directory 'main'
#    Path: tasks/task-documents
#    Workspace: /home/admin/workspaces/datachat
# 📋 Found N task documents in directory
#    Daemon will process them automatically

# 4. Check queue status
task-queue status
# Output: Shows pending/running/completed tasks
```

**Inform user:**
```
✅ Task Source Directory registered for watchdog monitoring.

Tasks will be auto-loaded when files appear in tasks/task-documents/
The daemon processes tasks sequentially per source. Different sources execute in parallel.
```

### Scenario: Check Progress

**User says:** "Check task progress"

**Workflow:**

```bash
# Check status
task-queue status

# If task completed, check result
cat tasks/task-archive/task-20260205-100000-fix-auth-timeout.md

# Or check the worker report
ls tasks/task-reports/
cat tasks/task-reports/task-{id}/workflow-result.json
```

## Result Interpretation

### Check Completed Tasks

```bash
# List completed tasks
ls tasks/task-archive/

# View completed task document
cat tasks/task-archive/task-20260205-100000-fix-auth-timeout.md
```

### Check Failed Tasks

```bash
# List failed tasks
ls tasks/task-failed/

# View failed task with error info
cat tasks/task-failed/task-{id}.md
cat tasks/task-failed/task-{id}.error.*
```

### Check Worker Reports

```bash
# List worker reports
ls tasks/task-reports/

# View detailed execution report
cat tasks/task-reports/task-{id}/workflow-result.json
cat tasks/task-reports/task-{id}/audit-report-iteration-1.md
```

## Service Management

### Start/Stop Daemon

```bash
# Start daemon
systemctl --user start task-queue

# Stop daemon
systemctl --user stop task-queue

# Restart daemon
systemctl --user restart task-queue

# Enable at login
systemctl --user enable task-queue

# View live logs
journalctl --user -u task-queue -f

# View last 100 log lines
journalctl --user -u task-queue -n 100
```

## Key Principles (v2.0)

1. **Event-Driven Monitoring** - Watchdog detects file changes instantly (no polling)
2. **Per-Source Worker Threads** - One worker thread per Task Source Directory
3. **Sequential Within Source** - Prevents file conflict race conditions
4. **Parallel Across Sources** - Different sources can execute simultaneously
5. **Background Processing** - Daemon runs independently with watchdog
6. **Check Before Register** - Always check `list-sources` before registering to avoid duplicates
7. **Register Once** - Use `register` command once per source, watchdog handles the rest
8. **Auto-Archive** - Completed specs moved to `tasks/task-archive/`

## Related Skills

- **task-documents**: Creates task specifications
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

### Tasks not being processed

```bash
# Check if source is registered
task-queue list-sources

# Check if task files exist
ls tasks/task-documents/task-*.md
# Ensure task-YYYYMMDD-HHMMSS-*.md files exist

# Check if daemon is running
systemctl --user status task-queue.service
```

### Watchdog not detecting files

```bash
# Check watchdog is enabled in config
cat ~/.config/task-queue/config.json | grep watch_enabled

# Verify Task Source Directory is configured
task-queue list-sources

# Check daemon logs for watchdog errors
journalctl --user -u task-queue -n 50 | grep -i watchdog
```

### Task failed

```bash
# Check failed task
cat tasks/task-failed/task-{id}.md
cat tasks/task-failed/task-{id}.error.*

# Check detailed worker report
ls tasks/task-reports/task-{id}/
cat tasks/task-reports/task-{id}/audit-report-*.md
```
