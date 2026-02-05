# Task System Guide

Complete guide to the asynchronous task execution system (task-queue) with event-driven watchdog monitoring and parallel worker execution.

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
# 1. Use task-documents skill to create a task specification
# This creates: tasks/task-documents/task-YYYYMMDD-HHMMSS-{description}.md

# 2. Register Task Source Directory (one-time setup)
task-queue register --task-source-dir tasks/task-documents --project-workspace /home/admin/workspaces/datachat --source-id main

# 3. Task executes in background using Claude Agent SDK
# (Watchdog monitors directory, daemon processes tasks automatically)

# 4. Check results
task-queue status

# 5. View completed tasks
ls tasks/task-archive/
```

### Common Commands

```bash
# Check daemon status
task-queue status

# Register a Task Source Directory (one-time setup)
task-queue register --task-source-dir tasks/task-documents --project-workspace /home/admin/workspaces/datachat --source-id main

# List Task Source Directories
task-queue list-sources

# Remove a Task Source Directory
task-queue unregister --source-id main

# Run interactively (for testing)
task-queue run --cycles 1

# View live logs
journalctl --user -u task-queue -f
```

---

## System Overview

The Task System is an asynchronous, event-driven task execution architecture that:

- **Generates** task specifications via `task-documents` skill
- **Monitors** Task Source Directories via watchdog (event-driven, no polling)
- **Executes** tasks using parallel worker threads (one per Task Source Directory)
- **Processes** tasks sequentially within each source (no conflicts)
- **Tracks** state via directory structure (no state file)
- **Archives** completed tasks automatically
- **Moves** failed tasks to failed directory

**Key Benefits:**
- Directory-based state (no complex state file synchronization)
- Event-driven monitoring (no polling delay)
- Parallel execution across sources (multiple workers)
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
│ Step 3: Register Task Source Directory (one-time setup)                  │
│                                                                          │
│   task-queue register --task-source-dir <dir>                          │
│                      --project-workspace <dir>                          │
│                      --source-id <id>                                   │
│                                                                          │
│   Note: This registers the directory for watchdog monitoring.           │
│   Tasks are auto-loaded when files appear (no manual loading needed).   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 4: task-queue Daemon with Parallel Workers                         │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │              Watchdog (Event-Driven Monitoring)                  │   │
│   │                                                                 │   │
│   │   File Created → Watchdog Event → Wake Worker Thread           │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│   │ Source A Worker │  │ Source B Worker │  │ Source C Worker │     │
│   │   (Thread 1)     │  │   (Thread 2)     │  │   (Thread 3)     │     │
│   │                 │  │                 │  │                 │     │
│   │ task-a1 (pending)│  │ task-b1 (running)│  │ task-c1 (pending)│     │
│   │ task-a2 (pending)│  │ task-b2 (pending)│  │ task-c2 (pending)│     │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│           │                   │                   │                     │
│           ▼                   ▼                   ▼                     │
│   Sequential One       Sequential One       Sequential One                         │
│   at a Time           at a Time           at a Time                               │
│                                                                          │
│   All workers run in PARALLEL (different sources)                         │
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
│ Step 6: Task State via Directory Structure                                │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ Directory-Based State (No state.json file)                      │   │
│   │                                                                 │   │
│   │ tasks/task-documents/   ← Pending tasks                           │   │
│   │   ├── task-001.md                                               │   │
│   │   ├── .task-001.running  ← Execution marker                      │   │
│   │   └── task-002.md                                               │   │
│   │                                                                 │   │
│   │ tasks/task-archive/     ← Completed tasks (auto-moved)           │   │
│   │ tasks/task-failed/     ← Failed tasks (auto-moved)               │   │
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
│   │   ├── .task-20260205-100000-fix-auth-timeout.running  # Marker for running tasks
│   │   └── task-20260205-100500-add-feature.md
│   ├── task-archive/               # Completed specs (auto-moved)
│   │   ├── task-20260205-090000-previous-task.md
│   │   └── task-20260205-093000-completed-task.md
│   ├── task-failed/               # Failed specs (auto-moved)
│   │   └── task-20260205-080000-failed-task.md
│   └── task-reports/               # Worker execution reports (created by task-worker skill)
│       └── task-{timestamp}-{description}/
│           ├── workflow-result.json
│           ├── audit-report-iteration-1.md
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
└── config.json.lock               # Lock file for config access
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
- Watchdog auto-integration (daemon detects new files)

### 3. task-queue

**Purpose:** Coordinate task execution with watchdog and CLI commands

**Workflow:**
1. Register Task Source Directory via CLI
2. Watchdog monitors for file changes
3. Worker threads process tasks (one per source)
4. Check status via CLI
5. Completed tasks auto-archive

**Key Commands:**
```bash
# Register Task Source Directory
task-queue register --task-source-dir <dir> --project-workspace <dir> --source-id <id>

# List sources
task-queue list-sources

# Remove source
task-queue unregister --source-id <id>

# Check status
task-queue status

# Run interactively
task-queue run --cycles 1
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
4. Remove all files from subdirectories
5. Verify cleanup complete

**Official Directories Cleaned:**
- `tasks/task-archive/` - Archived task specifications
- `tasks/task-failed/` - Failed task specifications
- `tasks/task-reports/` - Worker execution reports
- `tasks/task-planning/` - Planning documents
- `tasks/task-documents/` - Task specifications

**Preserved:**
- All subdirectories (empty, ready for new tasks)

**Called by:** User or AI when needing a clean slate for new task work

---

## Execution Model

### Directory-Based State (v2.0)

The task-queue now uses **directory-based state** with these rules:

| Rule | Description |
|------|-------------|
| **Same source** | Sequential FIFO execution (one at a time) |
| **Different sources** | Parallel execution (can run simultaneously) |
| **State tracking** | Directory structure (no state.json file) |
| **Running marker** | `.task-XXX.running` file indicates task in progress |

### Visual Example

```
Source A Worker:         Source B Worker:         Source C Worker:
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ Thread 1         │      │ Thread 2         │      │ Thread 3         │
│                  │      │                  │      │                  │
│ Scan task-a1     │      │ Scan task-b1     │      │ Scan task-c1     │
│ Execute          │      │ Execute          │      │ Execute          │
│ Archive          │      │ Archive          │      │ Archive          │
│ Scan task-a2     │      │ Scan task-b2     │      │ Scan task-c2     │
└──────────────────┘      └──────────────────┘      └──────────────────┘
      │                        │                        │
      ▼                        ▼                        ▼
Sequential One           Sequential One            Sequential One
at a Time               at a Time               at a Time

All run in PARALLEL (different sources)
```

### Task States

```
┌─────────────────────────────────────────────────────────────────┐
│ Task Lifecycle                                                       │
│                                                                     │
│  task-documents/          Running             Archive/Failed       │
│  ┌─────────────┐          ┌─────────┐          ┌─────────────┐    │
│  │ task-001.md │ ─create──▶│.running │──done───▶│task-001.md │    │
│  │ (pending)  │          │ marker  │          │(completed) │    │
│  └─────────────┘          └─────────┘          └─────────────┘    │
│                                                                     │
│  On failure → task-failed/task-001.md                              │
└─────────────────────────────────────────────────────────────────┘
```

### Loading Methods

| Method | When to Use |
|--------|-------------|
| **Watchdog (auto)** | Production, continuous operation - daemon wakes when files appear |
| **Register command** | Initial setup, adding new sources |

### Within Each Source

Tasks within the same Task Source Directory execute sequentially:

```
tasks/task-documents/:
├── task-001.md ──→ [Worker picks] ──→ [.task-001.running] ──→ [Executing] ──→ Archive
├── task-002.md ──→ [Waiting] ──────────→ [Next cycle] ──────────────────→ Archive
└── task-003.md ──→ [Waiting] ──────────→ [Waiting] ─────────────────────→ ...
```

---

## CLI Commands

The `task-queue` CLI provides these commands:

### Configuration

```bash
# Specify custom config file
task-queue --config /path/to/config.json <command>
```

**Note:** Configuration is auto-created on first use. No manual initialization needed.

### Task Source Directory Management

```bash
# Register a Task Source Directory (one-time setup)
# This adds the directory to config for watchdog monitoring
task-queue register --task-source-dir <path> --project-workspace <path> --source-id <id>

# List registered Task Source Directories
task-queue list-sources

# Remove a Task Source Directory from monitoring
task-queue unregister --source-id <id>
```

### Monitoring

```bash
# Show system status
task-queue status
```

### Interactive Mode

```bash
# Run interactively (for testing)
task-queue run [--cycles N]

# Cycles: 0 = infinite, N = specific number
```

### View Results

```bash
# View completed tasks
ls tasks/task-archive/

# View failed tasks
ls tasks/task-failed/

# View task reports
ls tasks/task-reports/task-{timestamp}-{description}/
```

---

## Service Management

The task-queue daemon runs as a systemd user service with watchdog monitoring.

```bash
# Start service
systemctl --user start task-queue.service

# Stop service
systemctl --user stop task-queue.service

# Restart service
systemctl --user restart task-queue.service

# Check status
systemctl --user status task-queue.service

# Enable at login
systemctl --user enable task-queue.service

# View live logs
journalctl --user -u task-queue.service -f

# View last 100 log lines
journalctl --user -u task-queue.service -n 100
```

---

## Troubleshooting

### Service won't start

**Symptom:** `systemctl --user status task-queue.service` shows "failed" or "inactive"

**Solutions:**

1. **Check the logs:**
   ```bash
   journalctl --user -u task-queue.service -n 50
   ```

2. **Verify directory structure:**
   ```bash
   ls -la tasks/task-documents/
   ls -la tasks/task-archive/
   ls -la tasks/task-failed/
   ```

3. **Verify Python environment:**
   ```bash
   source /home/admin/workspaces/datachat/.venv/bin/activate
   python -m task_queue.cli status
   ```

4. **Check config file:**
   ```bash
   cat ~/.config/task-queue/config.json
   ```

### Tasks not being processed

**Symptom:** `task-queue status` shows pending tasks but they don't execute

**Solutions:**

1. **Verify task files exist:**
   ```bash
   ls tasks/task-documents/task-*.md
   ```

2. **Check naming pattern:** Task files must match `task-YYYYMMDD-HHMMSS-*.md`

3. **Check service is running:**
   ```bash
   systemctl --user status task-queue.service
   ```

4. **Check for stuck running markers:**
   ```bash
   ls tasks/task-documents/.task-*.running
   # Note: The system auto-detects and cleans stale markers by checking process IDs
   # Manual removal should rarely be necessary
   ```

### Task execution errors

**Symptom:** Task moves to failed directory

**Solutions:**

1. **View failed task:**
   ```bash
   cat tasks/task-failed/task-{id}.md
   cat tasks/task-failed/task-{id}.error.*
   ```

2. **Check detailed worker report:**
   ```bash
   ls tasks/task-reports/task-{id}/
   cat tasks/task-reports/task-{id}/audit-report-*.md
   ```

3. **Verify project context:** Task should execute with correct working directory (Project Workspace)

### Watchdog not detecting files

**Symptom:** Creating task files doesn't trigger execution

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
   journalctl --user -u task-queue.service -n 50 | grep -i watchdog
   ```

### Tasks not archiving

**Symptom:** Completed specs remain in `task-documents/`

**Cause:** Archive path may be incorrect

**Solution:** Verify archive path exists:
```bash
ls tasks/task-archive/
ls tasks/task-failed/
```

---

## Key Design Principles

1. **Conversation Continuity** - Tasks run in background, user keeps chatting
2. **Event-Driven Loading** - Watchdog detects file changes instantly (no polling)
3. **Directory-Based State** - File system is the source of truth (no state file)
4. **Parallel Execution** - Multiple workers run simultaneously (one per source)
5. **Sequential Within Source** - Prevents file conflict race conditions
6. **Direct Generation** - Task specifications generated directly as `.md` files
7. **Auto-Iteration** - Worker-auditor loop until quality threshold met
8. **Project Context** - Each task runs with correct `cwd` (Project Workspace)
9. **Graceful Shutdown** - All workers stop cleanly on SIGTERM
10. **Auto-Cleanup** - Stale running markers automatically detected and removed via process ID checking

---

## Related Modules

### task-queue Module

**Location:** `/home/admin/workspaces/task-queue/` (separate workspace)

**Version:** 2.0 (Directory-Based State with Parallel Workers)

**Installation:**
```bash
# Module runs as Python module from datachat venv
source /home/admin/workspaces/datachat/.venv/bin/activate
export PYTHONPATH=/home/admin/workspaces/task-queue:$PYTHONPATH
python -m task_queue.cli <command>
```

**Components:**
- **daemon.py**: Background daemon with parallel worker threads
- **task_runner.py**: Core task execution logic
- **watchdog.py**: Event-driven file system monitoring
- **executor.py**: Executes tasks via Claude Agent SDK
- **scanner.py**: Scans for task document files
- **cli.py**: CLI commands
- **models.py**: Pydantic data models (v2.0)
- **config.py**: Configuration management
- **file_utils.py**: Atomic file operations and file locking

**Service:** `~/.config/systemd/user/task-queue.service`

### Key Changes in v2.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| **State** | queue_state.json file | Directory-based state |
| **Polling** | 10-second intervals | Event-driven (threading.Event) |
| **Execution** | Single-threaded sequential | Parallel workers, sequential per source |
| **Architecture** | Monitor + Processor + Coordinator | Daemon with worker threads |
| **Tracking** | In-memory queue state | `.running` marker files |
| **Archive** | task-archive/ only | task-archive/ + task-failed/ |
| **Commands** | set-project, add-doc, reload | register, unregister, list-sources, status |
| **Terminology** | Spec Directory, Project Path | Task Source Directory, Project Workspace |
