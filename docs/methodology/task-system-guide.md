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
8. [Result Tracking](#result-tracking)
9. [CLI Commands](#cli-commands)
10. [Service Management](#service-management)
11. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Initial Setup (One-Time)

```bash
# 1. Initialize the task system with ad-hoc and planned queues
# This creates the directory structure and registers Task Source Directories
# (Run the task-init skill for complete setup)

# 2. Register ad-hoc queue
python -m task_queue.cli register \
    --task-source-dir /home/admin/workspaces/datachat/tasks/ad-hoc/task-documents \
    --project-workspace /home/admin/workspaces/datachat \
    --source-id ad-hoc

# 3. Register planned queue
python -m task_queue.cli register \
    --task-source-dir /home/admin/workspaces/datachat/tasks/planned/task-documents \
    --project-workspace /home/admin/workspaces/datachat \
    --source-id planned
```

### Create and Execute a Task

```bash
# 1. Use task-documents skill to create a task specification
#    - Ad-hoc tasks: goes to tasks/ad-hoc/task-documents/
#    - Planned tasks: goes to tasks/planned/task-documents/

# 2. Task executes in background using Claude Agent SDK
#    (Watchdog monitors directories, daemon processes tasks automatically)

# 3. Check results
python -m task_queue.cli status

# 4. View completed tasks and result files
ls tasks/ad-hoc/task-archive/       # or tasks/planned/task-archive/
ls tasks/ad-hoc/task-queue/         # or tasks/planned/task-queue/
cat tasks/ad-hoc/task-queue/task-{id}.json
```

### Common Commands

```bash
# Check daemon status
python -m task_queue.cli status

# List Task Source Directories
python -m task_queue.cli list-sources

# Remove a Task Source Directory
python -m task_queue.cli unregister --source-id ad-hoc
python -m task_queue.cli unregister --source-id planned

# Run interactively (for testing)
python -m task_queue.cli run --cycles 1

# View live logs
journalctl --user -u task-queue -f
```

---

## System Overview

The Task System is an asynchronous, event-driven task execution architecture with **two independent queues**:

### Two Queue System

| Queue | Purpose | Source |
|-------|---------|--------|
| **ad-hoc** | Quick, spontaneous tasks | Conversation context |
| **planned** | Organized, sequential tasks | Planning documents |

### System Capabilities

- **Generates** task specifications via `task-documents` skill (separate queues)
- **Monitors** Task Source Directories via watchdog (event-driven, no polling)
- **Executes** tasks using parallel worker threads (one per Task Source Directory)
- **Processes** tasks sequentially within each source (no conflicts)
- **Tracks** state via directory structure (no state file)
- **Saves** JSON result files with execution metadata, cost, and usage
- **Archives** completed tasks automatically
- **Moves** failed tasks to failed directory

**Key Benefits:**
- Separation of ad-hoc and planned tasks
- Directory-based state (no complex state file synchronization)
- Event-driven monitoring (no polling delay)
- Parallel execution across queues (multiple workers)
- Sequential execution within each queue (no conflicts)
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
│ Step 1: Task Planning (Optional - for planned queue)                    │
│                                                                          │
│   task-planning skill → tasks/task-planning/{descriptive-name}.md       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 2: Task Specification Generation                                   │
│                                                                          │
│   task-documents skill                                                  │
│                                                                          │
│   Ad-hoc path (from conversation):                                     │
│     → tasks/ad-hoc/task-staging/... (write first)                       │
│     → tasks/ad-hoc/task-documents/... (atomic move)                     │
│                                                                          │
│   Planned path (from planning):                                         │
│     → tasks/planned/task-staging/... (write first)                       │
│     → tasks/planned/task-documents/... (atomic move)                     │
│                                                                          │
│   Naming: task-YYYYMMDD-HHMMSS-{kebab-description}.md                   │
│   Example: task-20260205-100000-fix-auth-timeout.md                     │
│                                                                          │
│   Staging pattern: Write complete file, then atomic move triggers       │
│   watchdog detection. This prevents processing incomplete files.        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 3: Register Task Source Directories (one-time setup)               │
│                                                                          │
│   Run task-init skill OR manually register:                             │
│                                                                          │
│   python -m task_queue.cli register --task-source-dir <dir>            │
│                          --project-workspace <dir>                      │
│                          --source-id <id>                               │
│                                                                          │
│   Source IDs: ad-hoc, planned                                            │
│                                                                          │
│   Note: Watchdog monitors each queue's task-documents/ directory.       │
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
│   ┌─────────────────┐              ┌─────────────────┐                  │
│   │ Ad-hoc Worker   │              │ Planned Worker  │                  │
│   │   (Thread 1)     │              │   (Thread 2)     │                  │
│   │                 │              │                 │                  │
│   │ task-a1 (pending)│              │ task-p1 (running)│                  │
│   │ task-a2 (pending)│              │ task-p2 (pending)│                  │
│   └─────────────────┘              └─────────────────┘                  │
│           │                                  │                           │
│           ▼                                  ▼                           │
│   Sequential One                      Sequential One                     │
│   at a Time                          at a Time                           │
│                                                                          │
│   Both workers run in PARALLEL (different sources)                         │
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
│   │ tasks/ad-hoc/task-documents/   ← Pending ad-hoc tasks             │   │
│   │ tasks/planned/task-documents/  ← Pending planned tasks            │   │
│   │   ├── task-001.md                                               │   │
│   │   ├── .task-001.running  ← Execution marker                      │   │
│   │   └── task-002.md                                               │   │
│   │                                                                 │   │
│   │ tasks/ad-hoc/task-archive/     ← Completed ad-hoc tasks           │   │
│   │ tasks/planned/task-archive/    ← Completed planned tasks          │   │
│   │ tasks/ad-hoc/task-failed/     ← Failed ad-hoc tasks              │   │
│   │ tasks/planned/task-failed/    ← Failed planned tasks             │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 7: JSON Result File Creation                                        │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ tasks/ad-hoc/task-queue/task-{id}.json                          │   │
│   │ tasks/planned/task-queue/task-{id}.json                         │   │
│   │                                                                 │   │
│   │ {                                                              │   │
│   │   "success": true,                                             │   │
│   │   "task_id": "task-20260206-105319",                           │   │
│   │   "started_at": "2026-02-06T10:56:17.747530",                   │   │
│   │   "completed_at": "2026-02-06T10:56:45.316864",                 │   │
│   │   "duration_ms": 8829,                                         │   │
│   │   "duration_api_ms": 7785,                                     │   │
│   │   "total_cost_usd": 0.176559,                                  │   │
│   │   "usage": {                                                   │   │
│   │     "input_tokens": 25836,                                     │   │
│   │     "output_tokens": 267,                                      │   │
│   │     "cache_read_input_tokens": 81408                           │   │
│   │   },                                                           │   │
│   │   "session_id": "4e23bdf6-95b2-4856-ad69-5187d539b87a",         │   │
│   │   "num_turns": 4,                                              │   │
│   │   "output": "...",                                             │   │
│   │   "error": ""                                                  │   │
│   │ }                                                              │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

### Project Directory Structure (under your project root)

```
{project-workspace}/
├── tasks/
│   ├── ad-hoc/                            # Ad-hoc task queue
│   │   ├── task-staging/                  # Staging area (atomic writes)
│   │   ├── task-documents/                # Task Source Directory (watchdog monitors)
│   │   │   ├── task-20260205-100000-fix-bug.md
│   │   │   ├── .task-20260205-100000-fix-bug.running  # Marker for running
│   │   │   └── task-20260205-100500-add-feature.md
│   │   ├── task-archive/                  # Completed specs (auto-moved)
│   │   │   ├── task-20260205-090000-previous-task.md
│   │   │   └── task-20260205-093000-completed-task.md
│   │   ├── task-failed/                  # Failed specs (auto-moved)
│   │   │   └── task-20260205-080000-failed-task.md
│   │   ├── task-queue/                   # JSON result files with SDK metadata
│   │   │   └── task-{id}.json            # Execution result: duration, cost, usage
│   │   └── task-reports/                 # Worker execution reports
│   │       └── task-{timestamp}-{description}/
│   │           ├── workflow-result.json
│   │           ├── audit-report-iteration-1.md
│   │           └── implementation-summary.md
│   │
│   ├── planned/                           # Planned task queue
│   │   ├── task-staging/                  # Staging area (atomic writes)
│   │   ├── task-documents/                # Task Source Directory (watchdog monitors)
│   │   │   ├── task-20260205-110000-01-feature.md
│   │   │   ├── task-20260205-110001-02-refactor.md
│   │   │   └── task-20260205-110002-03-tests.md
│   │   ├── task-archive/                  # Completed specs (auto-moved)
│   │   ├── task-failed/                  # Failed specs (auto-moved)
│   │   ├── task-queue/                   # JSON result files with SDK metadata
│   │   └── task-reports/                 # Worker execution reports
│   │
│   └── task-planning/                     # Task planning documents
│       └── {descriptive-name}.md
│
└── .claude/
    └── skills/
        ├── task-init/                     # Initialize task system
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

**For multiple tasks from planning:** `task-20260205-100000-01-first-task.md`

### Document Template

```markdown
# Task: [One-line summary]

**Status**: pending

---

## Task
[Clear one-line description of what needs to be done]

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

### 1. task-init

**Purpose:** Initializes the task system with ad-hoc and planned queues

**Actions:**
- Creates directory structure for both queues
- Registers Task Source Directories with task-queue
- Verifies setup

**Use when:** First-time setup or re-configuration

### 2. task-planning

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

### 3. task-documents

**Purpose:** Generate task specification documents from planning or conversation

**Two Queues:**

| Scenario | Input | Output | Queue |
|----------|-------|--------|-------|
| **Ad-hoc** | Conversation context | Single task specification | ad-hoc |
| **Planned** | Planning document | Multiple task specifications | planned |

**Output:**
- Ad-hoc: `tasks/ad-hoc/task-documents/task-{timestamp}-{description}.md`
- Planned: `tasks/planned/task-documents/task-{timestamp}-{description}.md`

**Key Features:**
- Staging pattern (write to task-staging/ first, then atomic move)
- Watchdog auto-integration (daemon detects new files)

### 4. task-queue

**Purpose:** Coordinate task execution with watchdog and CLI commands

**Workflow:**
1. Register Task Source Directories via CLI
2. Watchdog monitors for file changes
3. Worker threads process tasks (one per source)
4. Check status via CLI
5. Completed tasks auto-archive

**Key Commands:**
```bash
# Register Task Source Directory
python -m task_queue.cli register --task-source-dir <dir> --project-workspace <dir> --source-id <id>

# List sources
python -m task_queue.cli list-sources

# Remove source
python -m task_queue.cli unregister --source-id <id>

# Check status
python -m task_queue.cli status

# Run interactively
python -m task_queue.cli run --cycles 1
```

### 5. task-worker

**Purpose:** Execute tasks with worker-auditor workflow

**Workflow:**
1. Implementation Agent executes task
2. Auditor Agent reviews output
3. Automatic iteration based on feedback (max 3x)
4. Quality gate: stops when threshold met

**Called by:** task-queue module (via Claude Agent SDK)

### 6. task-cleanup

**Purpose:** Clean up the tasks directory by removing all materials while preserving directory structure

**Workflow:**
1. Verify tasks directory exists
2. Show current contents and count files to be removed
3. Confirm with user before proceeding
4. Remove all files from subdirectories (both ad-hoc and planned queues)
5. Verify cleanup complete

**Official Directories Cleaned:**
- `tasks/ad-hoc/*` - All ad-hoc subdirectories
- `tasks/planned/*` - All planned subdirectories
- `tasks/task-planning/` - Planning documents

**Preserved:**
- All subdirectories (empty, ready for new tasks)

---

## Execution Model

### Directory-Based State (v2.0)

The task-queue uses **directory-based state** with these rules:

| Rule | Description |
|------|-------------|
| **Same source** | Sequential FIFO execution (one at a time) |
| **Different sources** | Parallel execution (can run simultaneously) |
| **State tracking** | Directory structure (no state.json file) |
| **Running marker** | `.task-XXX.running` file indicates task in progress |

### Visual Example

```
Ad-hoc Worker:           Planned Worker:
┌──────────────────┐      ┌──────────────────┐
│ Thread 1          │      │ Thread 2          │
│                   │      │                   │
│ Scan ad-hoc-1     │      │ Scan planned-1    │
│ Execute           │      │ Execute           │
│ Archive           │      │ Archive           │
│ Scan ad-hoc-2     │      │ Scan planned-2    │
└──────────────────┘      └──────────────────┘
      │                         │
      ▼                         ▼
Sequential One            Sequential One
at a Time                at a Time

Both run in PARALLEL (different sources)
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

---

## Result Tracking

### JSON Result Files

After each task execution, a JSON result file is automatically created at:

```
tasks/ad-hoc/task-queue/{task_id}.json
tasks/planned/task-queue/{task_id}.json
```

### Result File Structure

```json
{
  "success": true,
  "output": "Task execution output from Claude...",
  "error": "",
  "task_id": "task-20260206-105319",
  "duration_ms": 8829,
  "duration_api_ms": 7785,
  "total_cost_usd": 0.176559,
  "usage": {
    "input_tokens": 25836,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 81408,
    "output_tokens": 267,
    "server_tool_use": {
      "web_search_requests": 0,
      "web_fetch_requests": 0
    },
    "service_tier": "standard"
  },
  "session_id": "4e23bdf6-95b2-4856-ad69-5187d539b87a",
  "num_turns": 4,
  "started_at": "2026-02-06T10:56:17.747530",
  "completed_at": "2026-02-06T10:56:45.316864"
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether task completed successfully |
| `output` | string | Full text output from Claude Agent SDK |
| `error` | string | Error message if task failed |
| `task_id` | string | Task identifier |
| `duration_ms` | integer | Total execution time in milliseconds |
| `duration_api_ms` | integer | API call duration only (milliseconds) |
| `total_cost_usd` | float | Cost in USD for this execution |
| `usage` | object | Token usage statistics |
| `session_id` | string | Session identifier for tracing |
| `num_turns` | integer | Number of conversation turns |
| `started_at` | string | ISO 8601 start timestamp |
| `completed_at` | string | ISO 8601 completion timestamp |

### Viewing Results

```bash
# List all result files
ls tasks/ad-hoc/task-queue/
ls tasks/planned/task-queue/

# View specific result
cat tasks/ad-hoc/task-queue/task-{id}.json

# View with pretty formatting
cat tasks/ad-hoc/task-queue/task-{id}.json | jq .

# Check recent results
ls -lt tasks/ad-hoc/task-queue/ | head -10
```

---

## CLI Commands

The `task-queue` CLI provides these commands:

### Configuration

```bash
# Specify custom config file
python -m task_queue.cli --config /path/to/config.json <command>
```

**Note:** Configuration is auto-created on first use. No manual initialization needed.

### Task Source Directory Management

```bash
# Register a Task Source Directory (one-time setup)
python -m task_queue.cli register --task-source-dir <path> --project-workspace <path> --source-id <id>

# Example: Register ad-hoc queue
python -m task_queue.cli register \
    --task-source-dir /home/admin/workspaces/datachat/tasks/ad-hoc/task-documents \
    --project-workspace /home/admin/workspaces/datachat \
    --source-id ad-hoc

# Example: Register planned queue
python -m task_queue.cli register \
    --task-source-dir /home/admin/workspaces/datachat/tasks/planned/task-documents \
    --project-workspace /home/admin/workspaces/datachat \
    --source-id planned

# List registered Task Source Directories
python -m task_queue.cli list-sources

# Remove a Task Source Directory from monitoring
python -m task_queue.cli unregister --source-id <id>
```

### Monitoring

```bash
# Show system status
python -m task_queue.cli status
```

### Interactive Mode

```bash
# Run interactively (for testing)
python -m task_queue.cli run [--cycles N]

# Cycles: 0 = infinite, N = specific number
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
   ls -la tasks/ad-hoc/task-documents/
   ls -la tasks/planned/task-documents/
   ls -la tasks/ad-hoc/task-archive/
   ls -la tasks/planned/task-archive/
   ```

3. **Verify Python environment:**
   ```bash
   source /home/admin/workspaces/datachat/.venv/bin/activate
   export PYTHONPATH=/home/admin/workspaces/task-queue:$PYTHONPATH
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
   ls tasks/ad-hoc/task-documents/task-*.md
   ls tasks/planned/task-documents/task-*.md
   ```

2. **Check naming pattern:** Task files must match `task-YYYYMMDD-HHMMSS-*.md`

3. **Check service is running:**
   ```bash
   systemctl --user status task-queue.service
   ```

4. **Check for stuck running markers:**
   ```bash
   ls tasks/ad-hoc/task-documents/.task-*.running
   ls tasks/planned/task-documents/.task-*.running
   ```

### Task execution errors

**Symptom:** Task moves to failed directory

**Solutions:**

1. **View failed task:**
   ```bash
   cat tasks/ad-hoc/task-failed/task-{id}.md
   cat tasks/planned/task-failed/task-{id}.md
   ```

2. **Check detailed worker report:**
   ```bash
   ls tasks/ad-hoc/task-reports/task-{id}/
   ls tasks/planned/task-reports/task-{id}/
   cat tasks/ad-hoc/task-reports/task-{id}/audit-report-*.md
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
   python -m task_queue.cli list-sources
   ```

3. **Check daemon logs for watchdog errors:**
   ```bash
   journalctl --user -u task-queue.service -n 50 | grep -i watchdog
   ```

---

## Key Design Principles

1. **Conversation Continuity** - Tasks run in background, user keeps chatting
2. **Event-Driven Loading** - Watchdog detects file changes instantly (no polling)
3. **Directory-Based State** - File system is the source of truth (no state file)
4. **Parallel Execution** - Multiple workers run simultaneously (one per source)
5. **Sequential Within Source** - Prevents file conflict race conditions
6. **Staging Pattern** - Write to staging first, then atomic move (prevents incomplete file processing)
7. **Two Queue System** - Ad-hoc and planned tasks are separated
8. **Auto-Iteration** - Worker-auditor loop until quality threshold met
9. **Project Context** - Each task runs with correct `cwd` (Project Workspace)
10. **Graceful Shutdown** - All workers stop cleanly on SIGTERM
11. **Result Tracking** - JSON result files capture execution metadata, cost, and usage

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
- **executor.py**: Executes tasks via Claude Agent SDK, saves JSON result files
- **scanner.py**: Scans for task document files
- **cli.py**: CLI commands
- **models.py**: Pydantic data models (v2.0)
- **config.py**: Configuration management
- **file_utils.py**: Atomic file operations and file locking

**Service:** `~/.config/systemd/user/task-queue.service`
