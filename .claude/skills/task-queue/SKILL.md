---
name: task-queue
description: "Coordinates task execution using the task-queue module with watchdog auto-loading and per-source queue architecture. Loads task specifications from Task Source Directories using CLI commands and monitors execution progress. Use when: you have task specifications ready; you need to queue and execute tasks; you want to monitor task status and results."
---

# Task Queue

Coordinate task execution using the task-queue module with watchdog auto-loading and per-source queue architecture.

## Overview

This skill bridges the gap between task specifications and execution. It uses the `task-queue` CLI to:
1. **Auto-load** task specifications via watchdog when files are created/modified
2. **Manually load** tasks via CLI commands
3. **Monitor** execution status across per-source queues
4. **Display** results

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
│  │ 2. Load task specs OR rely on watchdog auto-load     │  │
│  │ 3. Monitor queue status (per-source)                 │  │
│  │ 4. Display results (cat tasks/task-queue/task-{id}.json) │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│       task-queue Module (CLI: task-queue) v2.0              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Watchdog: Event-driven file system monitoring        │  │
│  │ Per-Source Queues: Independent queues per source     │  │
│  │ Coordinator: Round-robin scheduling                  │  │
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
- You want to load and queue tasks for execution
- You need to monitor task execution progress
- You want to view task results

## CLI Commands Reference (v2.0)

The task-queue module provides these commands:

| Command | Purpose |
|---------|---------|
| `task-queue load --task-source-dir <dir> --project-workspace <dir> --source-id <id>` | Load tasks from Task Source Directory |
| `task-queue reload --task-source-dir <id-or-path> --project-workspace <dir>` | Force re-scan a Task Source Directory |
| `task-queue unload --source-id <id>` | Remove all tasks from a source |
| `task-queue list-sources` | List Task Source Directories |
| `task-queue status` | Show daemon and queue status |
| `task-queue queue` | Show per-source queue state |
| `task-queue process [--max-tasks N]` | Process pending tasks |
| `task-queue run [--cycles N]` | Run monitor interactively |

## Loading Methods

| Method | When to Use |
|--------|-------------|
| **Watchdog (auto)** | Production, continuous operation - tasks auto-load when files are created |
| **Manual Load** | One-off processing, testing, specific files |

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

### Step 2: Load Task Specifications (Manual OR Watchdog)

**Option A: Manual Load**

```bash
# Load from Task Source Directory
task-queue load --task-source-dir tasks/task-documents --project-workspace /home/admin/workspaces/datachat --source-id main
```

**Option B: Watchdog (Automatic)**

Tasks are automatically loaded when files are created in `tasks/task-documents/`. No manual loading required.

**Expected output:**
```
Loaded N task(s) from tasks/task-documents/
  - task-20260205-100000-fix-auth-timeout.md
  - task-20260205-100500-add-feature.md

Added N task(s) to queue.
Total queue size: N

Use 'task-queue queue' to check the queue status
```

### Step 3: Monitor Queue Status

```bash
task-queue queue
```

**Expected output (per-source queues):**
```
Project Workspace: /home/admin/workspaces/datachat
Total Queue Size: 2

Source: main (tasks/task-documents)
  Queue Size: 2
  Processing: task-20260205-100000-fix-auth-timeout.md
  Queued:
    1. task-20260205-100500-add-feature.md
```

### Step 4: Monitor Progress (Optional)

**Only monitor when user explicitly asks to check progress.**

```bash
# Check specific task status
cat tasks/task-queue/task-20260205-100000-fix-auth-timeout.json

# View live logs
journalctl --user -u task-queue -f
```

**DO NOT continuously poll during execution.** Only check when the user asks.

## Directory Structure

```
tasks/
├── task-documents/             # Input: Task specifications (Task Source Directory)
│   └── task-YYYYMMDD-HHMMSS-{description}.md
├── task-queue/                 # Execution tracking JSONs (flat)
│   └── task-YYYYMMDD-HHMMSS-{description}.json
├── task-archive/               # Completed specs (auto-moved)
│   └── task-YYYYMMDD-HHMMSS-{description}.md
└── task-reports/               # Worker execution reports (detailed)
    └── task-{timestamp}-{description}/
        ├── workflow-result.json
        ├── audit-report-iteration-*.md
        └── implementation-summary.md
```

## Per-Source Architecture (v2.0)

The task-queue uses **per-source queues** with these rules:

| Rule | Description |
|------|-------------|
| **Same source** | Sequential FIFO execution (one at a time) |
| **Different sources** | Parallel execution (can run simultaneously) |
| **Scheduling** | Round-robin coordinator for fair scheduling |

## Example Usage

### Scenario: Load and Execute Tasks

**User says:** "Load and execute the task specifications"

**Workflow:**

```bash
# 1. Check daemon status
task-queue status
# Output: Running

# 2. Load tasks (or rely on watchdog)
task-queue load --task-source-dir tasks/task-documents --project-workspace /home/admin/workspaces/datachat --source-id main
# Output:
# Loaded 2 task(s) from tasks/task-documents/
# Added 2 task(s) to queue.
# Total queue size: 2

# 3. Verify queue
task-queue queue
```

**Inform user:**
```
✅ Tasks loaded and queued for execution.

Current status:
- Source: main
- Queue size: 2
- Processing: task-20260205-100000-fix-auth-timeout.md

The daemon processes tasks sequentially per source. Different sources execute in parallel.
```

### Scenario: Check Progress

**User says:** "Check task progress"

**Workflow:**

```bash
# Check queue status
task-queue queue

# If task completed, check result
cat tasks/task-queue/task-20260205-100000-fix-auth-timeout.json
```

## Result Interpretation

### From `cat tasks/task-queue/task-{id}.json`

```json
{
  "task_id": "task-20260205-100000-fix-auth-timeout",
  "status": "completed",
  "stdout": "...",
  "stderr": null,
  "duration_seconds": 123.4,
  "cost_usd": 0.045,
  "created": "2026-02-05T10:00:00",
  "started": "2026-02-05T10:00:05",
  "completed": "2026-02-05T10:02:08"
}
```

### Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Waiting in queue |
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

1. **Event-Driven Loading** - Watchdog detects file changes instantly (no polling)
2. **Per-Source Queues** - Each Task Source Directory has its own queue
3. **Sequential Within Source** - Prevents file conflict race conditions
4. **Parallel Across Sources** - Different sources can execute simultaneously
5. **Background Processing** - Daemon runs independently with watchdog
6. **Status on Request** - Only check progress when user asks
7. **Auto-Archive** - Completed specs moved to `tasks/task-archive/`

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

### No tasks loaded

```bash
task-queue load --task-source-dir tasks/task-documents --project-workspace /home/admin/workspaces/datachat --source-id main
# Output: No tasks to load.

# Check Task Source Directory
ls tasks/task-documents/task-*.md
# Ensure task-YYYYMMDD-HHMMSS-*.md files exist
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
# Check result JSON
cat tasks/task-queue/task-{id}.json

# Check detailed worker report
ls tasks/task-reports/task-{id}/
cat tasks/task-reports/task-{id}/audit-report-*.md
```
