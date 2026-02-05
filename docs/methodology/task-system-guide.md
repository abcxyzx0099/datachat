# Task System Guide

Complete guide to the asynchronous task execution system (task-queue) with event-driven watchdog monitoring and per-source queue architecture.

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Architecture Diagram](#architecture-diagram)
4. [Directory Structure](#directory-structure)
5. [Task Document Format](#task-document-format)
6. [Skills Reference](#skills-reference)
7. [Execution Model](#execution-model)
8. [CLI Commands](#cli-commands)
9. [Service Management](#service-management)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Create and Execute a Task

```bash
# 1. Use task-documents to create a task specification
# This creates: tasks/task-documents/task-YYYYMMDD-HHMMSS-{description}.md

# 2. Load tasks using CLI
task-queue load --task-source-dir tasks/task-documents --project-workspace /home/admin/workspaces/datachat --source-id main

# 3. Task executes in background using Claude Agent SDK
# (Watchdog auto-loads new files, daemon processes them)

# 4. Check results
cat tasks/task-queue/task-{timestamp}-{description}.json

# 5. View detailed worker report
ls tasks/task-reports/task-{timestamp}-{description}/
```

### Common Commands

```bash
# Check daemon status
task-queue status

# Load tasks from Task Source Directory
task-queue load --task-source-dir tasks/task-documents --project-workspace /home/admin/workspaces/datachat --source-id main

# Reload (force re-scan) a Task Source Directory
task-queue reload --task-source-dir main --project-workspace /home/admin/workspaces/datachat

# View queue status
task-queue queue

# List Task Source Directories
task-queue list-sources

# View live logs
journalctl --user -u task-queue -f

# Check specific task result
cat tasks/task-queue/task-{timestamp}-{description}.json
```

---

## System Overview

The Task System is an asynchronous, event-driven task execution architecture that:

- **Generates** task specifications via `task-documents` skill
- **Auto-loads** tasks via watchdog when files are created/modified
- **Queues** tasks per-source with round-robin execution
- **Executes** tasks using Claude Agent SDK in isolated background sessions
- **Reports** results to two separate output locations
- **Archives** completed task specifications automatically

**Key Benefits:**
- Event-driven loading (no polling delay)
- Per-source queues (parallel execution across sources)
- Sequential execution within each source (no conflicts)
- Continue conversation while tasks execute independently

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
│   task-documents skill                                   │
│   → tasks/task-documents/task-{timestamp}-{description}.md        │
│                                                                          │
│   Naming: task-YYYYMMDD-HHMMSS-{kebab-description}.md                   │
│   Example: task-20260205-100000-fix-auth-timeout.md                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 3: Watchdog Auto-Load OR Manual Load                                │
│                                                                          │
│   Option A: Watchdog (Automatic)                                        │
│   ┌───────────────────────────────────────────────────────────────┐  │
│   │  File Created/Modified → Watchdog Event → Auto-Load Task     │  │
│   └───────────────────────────────────────────────────────────────┘  │
│                                                                          │
│   Option B: Manual Load                                                  │
│   ┌───────────────────────────────────────────────────────────────┐  │
│   │  task-queue load --task-source-dir <dir>                      │  │
│   │                  --project-workspace <dir>                       │  │
│   │                  --source-id <id>                               │  │
│   └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 4: task-queue Daemon with Per-Source Queues (Background Process)   │
│                                                                          │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│   │ Source A Queue  │  │ Source B Queue  │  │ Source C Queue  │     │
│   │                 │  │                 │  │                 │     │
│   │ task-a1 (pending)│  │ task-b1 (running)│  │ task-c1 (pending)│     │
│   │ task-a2 (pending)│  │ task-b2 (pending)│  │ task-c2 (pending)│     │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│           │                   │                   │                     │
│           ▼                   ▼                   ▼                     │
│   Sequential One       Sequential One       Sequential One                        │
│   at a Time           at a Time           at a Time                               │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │         Source Coordinator (Round-Robin Scheduling)          │   │
│   │                                                         │   │
│   │   A-1 → B-1 → C-1 → A-2 → C-2 → ... (fair scheduling)    │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  TaskExecutor (task_queue/executor.py)                          │   │
│   │                                                                  │   │
│   │  options = ClaudeAgentOptions(                                  │   │
│   │      cwd=str(project_workspace),    # Project context           │   │
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
│   │ Location: tasks/task-queue/{task_id}.json     │   │
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
│   │ Location: tasks/task-reports/{task_id}/                  │   │
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

### Project Directory Structure (under your project root)

```
{project-workspace}/
├── tasks/
│   ├── task-planning/              # Task planning documents
│   │   └── {descriptive-name}.md
│   ├── task-documents/             # Input: Task specifications (Task Source Directory)
│   │   ├── task-20260205-100000-fix-auth-timeout.md
│   │   └── task-20260205-100500-add-feature.md
│   ├── task-queue/                 # Execution tracking JSONs (flat)
│   │   ├── task-20260205-100000-fix-auth-timeout.json
│   │   └── task-20260205-100500-add-feature.json
│   ├── task-archive/               # Completed specs (auto-moved)
│   │   ├── task-20260205-100000-fix-auth-timeout.md
│   │   └── task-20260205-100500-add-feature.md
│   └── task-reports/               # Worker execution reports (detailed)
│       └── task-{timestamp}-{description}/
│           ├── workflow-result.json
│           ├── audit-report-iteration-1.md
│           ├── audit-report-iteration-2.md
│           └── implementation-summary.md
└── .claude/
    └── skills/
        ├── task-planning/
        ├── task-documents/
        ├── task-queue/
        ├── task-worker/
        └── task-cleanup/
```

### Config Directory Structure (under `~/.config/`)

```
~/.config/task-queue/
├── config.json                     # Queue configuration (v2.0)
├── config.json.lock               # Lock file for config access
└── state/
    ├── queue_state.json           # Queue state v2.0 (per-source queues)
    └── queue_state.json.lock      # Lock file for state access
```

---

## Task Document Format

### Naming Convention

| Component | Format | Example |
|-----------|--------|---------|
| **Prefix** | `task-` | `task-` |
| **Timestamp** | `YYYYMMDD-HHMMSS` | `20260205-100000` |
| **Separator** | `-` | `-` |
| **Description** | kebab-case | `fix-auth-timeout` |
| **Extension** | `.md` | `.md` |

**Full Example:** `task-20260205-100000-fix-auth-timeout.md`

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

### 2. task-documents

**Purpose:** Generate task specification documents from planning or conversation

**Two Scenarios:**

| Scenario | Input | Output |
|----------|-------|--------|
| **Scenario 1** | Conversation context | Single task specification |
| **Scenario 2** | Planning document | Multiple task specifications (bulk) |

**Output:** `tasks/task-documents/task-{timestamp}-{description}.md`

**Key Features:**
- Direct `.md` generation
- Watchdog auto-integration (daemon auto-loads new files)
- Manual loading also available via CLI

### 3. task-queue

**Purpose:** Coordinate task execution with watchdog and CLI commands

**Workflow:**
1. Watchdog auto-loads Task Documents when files are created/modified
2. Or manual load via `task-queue load` command
3. Per-source queues with round-robin coordinator
4. Monitor queue status (`task-queue queue`)
5. Display results (check `tasks/task-queue/`)

**Key Commands:**
```bash
# Load from Task Source Directory
task-queue load --task-source-dir <dir> --project-workspace <dir> --source-id <id>

# Reload (force re-scan)
task-queue reload --task-source-dir <id-or-path> --project-workspace <dir>

# Unload (remove all tasks from source)
task-queue unload --source-id <id>

# List sources
task-queue list-sources

# Check status/queue
task-queue status
task-queue queue
```

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
- `tasks/task-queue/` - Result JSON files
- `tasks/task-reports/` - Worker execution reports
- `tasks/task-planning/` - Planning documents
- `tasks/task-documents/` - Task specifications

**Preserved:**
- `docs/methodology/task-system-guide.md` - Documentation file
- All subdirectories (empty, ready for new tasks)

**Called by:** User or AI when needing a clean slate for new task work

---

## Execution Model

### Per-Source Architecture (v2.0)

The task-queue now uses **per-source queues** with these rules:

| Rule | Description |
|------|-------------|
| **Same source** | Sequential FIFO execution (one at a time) |
| **Different sources** | Parallel execution (can run simultaneously) |
| **Scheduling** | Round-robin coordinator for fair scheduling |

### Visual Example

```
Source A (tasks/a/):    Source B (tasks/b/):    Source C (tasks/c/):
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│ Queue (FIFO) │        │ Queue (FIFO) │        │ Queue (FIFO) │
│              │        │              │        │              │
│ task-a1      │        │ task-b1      │        │ task-c1      │
│ task-a2      │        │ task-b2      │        │ task-c2      │
└──────────────┘        └──────────────┘        └──────────────┘
      │                       │                       │
      ▼                       ▼                       ▼
Sequential One            Sequential One            Sequential One
at a Time               at a Time               at a Time

Round-Robin Coordinator:
A-1 → Switch to B → B-1 → Switch to C → C-1 → Switch to A → A-2 → ...
```

### Loading Methods

| Method | When to Use |
|--------|-------------|
| **Watchdog (auto)** | Production, continuous operation - tasks auto-load when files are created |
| **Manual Load** | One-off processing, testing, specific files |

### Within Each Source

Tasks within the same Task Source Directory still execute sequentially to prevent file conflicts:

```
tasks/task-documents/:
├── task-1.md ────→ [Load] ────→ [Queue] ────→ [Executing] ────→ Done
├── task-2.md ────→ [Load] ────→ [Waiting] ──→ [Next] ────────→ Done
└── task-3.md ────→ [Load] ────→ [Waiting] ──→ [Waiting] ──────→ ...
```

---

## CLI Commands

The `task-queue` CLI provides these commands:

### Task Operations

```bash
# Load tasks from Task Source Directory
task-queue load --task-source-dir <path> --project-workspace <path> --source-id <id>

# Load a single Task Document
task-queue load --task-source-dir tasks/task-documents/task-001.md --project-workspace /home/admin/workspaces/datachat --source-id main

# Force re-scan a Task Source Directory
task-queue reload --task-source-dir <source-id-or-path> --project-workspace <path>

# Remove ALL tasks from a Task Source Directory
task-queue unload --source-id <source-id>

# Process pending tasks
task-queue process [--max-tasks N]
```

### Monitoring

```bash
# Show system status
task-queue status [-v]

# Show queue status
task-queue queue

# List Task Source Directories
task-queue list-sources
```

### Interactive Mode

```bash
# Run monitor interactively
task-queue run [--cycles N]

# Cycles: 0 = infinite, N = specific number
```

### View Results

```bash
# View task results
cat tasks/task-queue/task-{timestamp}-{description}.json

# View task execution logs (if available)
cat tasks/task-queue/logs/task-{timestamp}-{description}.log
```

---

## Service Management

The task-queue daemon runs as a systemd user service with watchdog monitoring.

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
   ls -la tasks/task-documents/
   ls -la tasks/task-queue/
   ```

3. **Verify Python environment:**
   ```bash
   cd /home/admin/workspaces/task-queue
   pip install -e .
   ```

4. **Check config file:**
   ```bash
   cat ~/.config/task-queue/config.json
   ```

### Tasks not being loaded

**Symptom:** `task-queue load` shows no tasks

**Solutions:**

1. **Verify task files exist:**
   ```bash
   ls tasks/task-documents/task-*.md
   ```

2. **Check naming pattern:** Task files must match `task-YYYYMMDD-HHMMSS-*.md`

3. **Check service is running:**
   ```bash
   systemctl --user status task-queue
   ```

4. **Check if watchdog is working:**
   ```bash
   # Create a test file
   touch tasks/task-documents/task-$(date +%Y%m%d-%H%M%S)-test.md

   # Check logs for watchdog event
   journalctl --user -u task-queue -f
   ```

### Task execution errors

**Symptom:** Task completes with "failed" status

**Solutions:**

1. **View error details:**
   ```bash
   cat tasks/task-queue/task-{id}.json
   ```

2. **Check detailed worker report:**
   ```bash
   ls tasks/task-reports/task-{id}/
   cat tasks/task-reports/task-{id}/audit-report-*.md
   ```

3. **Verify project context:** Task should execute with correct working directory (Project Workspace)

### Watchdog not detecting files

**Symptom:** Creating task files doesn't auto-load them

**Solutions:**

1. **Check watchdog is enabled in config:**
   ```bash
   cat ~/.config/task-queue/config.json | grep watch_enabled
   ```

2. **Verify Task Source Directory is configured:**
   ```bash
   task-queue list-sources
   ```

3. **Check daemon logs for watchdog errors:**
   ```bash
   journalctl --user -u task-queue -n 50 | grep -i watchdog
   ```

### Tasks not archiving

**Symptom:** Completed specs remain in `task-documents/`

**Cause:** Archive path may be incorrect

**Solution:** Verify archive path points to correct location:
```bash
ls tasks/task-archive/
```

---

## Key Design Principles

1. **Conversation Continuity** - Tasks run in background, user keeps chatting
2. **Event-Driven Loading** - Watchdog detects file changes instantly (no polling)
3. **Per-Source Architecture** - Each Task Source Directory has its own queue
4. **Sequential Within Source** - Prevents file conflict race conditions
5. **Parallel Across Sources** - Different sources can execute simultaneously
6. **Direct Generation** - Task specifications generated directly as `.md` files
7. **Traceability** - Full stdout/stderr captured in results JSON
8. **Auto-Iteration** - Worker-auditor loop until quality threshold met
9. **Project Context** - Each task runs with correct `cwd` (Project Workspace)

---

## Related Modules

### task-queue Module

**Location:** `/home/admin/workspaces/task-queue/` (separate workspace)

**Version:** 2.0 (Per-Source Queues with Watchdog)

**Installation:**
```bash
# Install in datachat venv
cd /home/admin/workspaces/datachat
source .venv/bin/activate
pip install -e /home/admin/workspaces/task-queue
```

**Components:**
- **watchdog.py**: Event-driven file system monitoring
- **coordinator.py**: Round-robin source coordinator
- **daemon.py**: Background daemon with watchdog
- **executor.py**: Executes tasks via Claude Agent SDK
- **processor.py**: Per-source queue management
- **scanner.py**: Scans for task document files
- **cli.py**: CLI commands
- **monitor.py**: Main queue orchestration
- **models.py**: Pydantic data models (v2.0)
- **config.py**: Configuration management
- **atomic.py**: Atomic file operations

**Service:** `~/.config/systemd/user/task-queue.service`

### Key Changes in v2.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| **Loading** | Manual only | Watchdog + Manual |
| **Polling** | 10-second intervals | Event-driven |
| **Queue** | Single global queue | Per-source queues |
| **Execution** | Sequential only | Sequential per source, parallel across sources |
| **Commands** | set-project, add-doc, etc. | load, reload, unload, list-sources |
| **State** | Single queue | Per-source with coordinator |
| **Terminology** | Spec Directory, Project Path | Task Source Directory, Project Workspace |
