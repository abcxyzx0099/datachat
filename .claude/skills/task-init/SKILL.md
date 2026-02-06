---
name: task-init
description: "Initializes the task system by creating the directory structure and registering Task Source Directories with the task-queue module. One-time setup that configures ad-hoc and planned task queues for parallel execution."
---

# Task System Initialization

Initializes the task system with separate queues for ad-hoc and planned tasks.

## Overview

This skill performs one-time setup of the task system using three CLI commands:

| Command | Purpose | Usage |
|---------|---------|-------|
| **init** | Quick setup - creates directories and registers both queues | First-time setup |
| **register** | Advanced - register a single Task Source Directory | Custom configurations |
| **unregister** | Remove a Task Source Directory from monitoring | Reconfiguration |

The task system supports two independent queues that execute in parallel:

| Queue | Purpose | Source |
|-------|---------|--------|
| **ad-hoc** | Quick tasks from conversation | Spontaneous user requests |
| **planned** | Organized tasks from planning docs | `task-planning` output |

---

## When to Use

| Scenario | Command |
|----------|---------|
| **First-time setup** | `task-queue init` (recommended) |
| **Re-configuration** | `task-queue init --force` or `register`/`unregister` |
| **Add custom queue** | `task-queue register` |
| **Remove queue** | `task-queue unregister` |
| **Verification** | `task-queue list-sources` |

---

## Directory Structure

```
tasks/
├── ad-hoc/                              # Ad-hoc task queue
│   ├── task-staging/                    # Staging area (atomic writes)
│   ├── task-documents/                  # Task Source Directory (watchdog monitors)
│   ├── task-archive/                    # Completed task specs
│   ├── task-failed/                    # Failed task specs
│   ├── task-queue/                     # JSON result files
│   └── task-reports/                   # Worker execution reports
│
└── planned/                             # Planned task queue
    ├── task-staging/                    # Staging area (atomic writes)
    ├── task-documents/                  # Task Source Directory (watchdog monitors)
    ├── task-archive/                    # Completed task specs
    ├── task-failed/                    # Failed task specs
    ├── task-queue/                     # JSON result files
    └── task-reports/                   # Worker execution reports
```

---

## Command Reference

### 1. init - Quick Setup

**Recommended for most use cases.** Initializes from current directory.

```bash
# From project directory
cd /home/admin/workspaces/datachat
source .venv/bin/activate
export PYTHONPATH=/home/admin/workspaces/task-queue:$PYTHONPATH

# Initialize (creates directories, registers both queues)
python -m task_queue.cli init

# Options
python -m task_queue.cli init --force           # Re-initialize completely
python -m task_queue.cli init --skip-existing   # Skip already registered queues
python -m task_queue.cli init --restart-daemon  # Restart daemon after init
```

**What it does:**
- Uses current directory as Project Workspace
- Creates all directory structures for both queues
- Registers `ad-hoc` and `planned` Task Source Directories
- Saves configuration
- Shows verification summary

---

### 2. register - Advanced Configuration

**Use for custom queue configurations.** Register a single Task Source Directory.

```bash
# Activate environment
source /home/admin/workspaces/datachat/.venv/bin/activate
export PYTHONPATH=/home/admin/workspaces/task-queue:$PYTHONPATH

# Register a queue
python -m task_queue.cli register \
    --task-source-dir /path/to/task-documents \
    --project-workspace /home/admin/workspaces/datachat \
    --source-id my-queue

# Register ad-hoc queue (manual setup)
python -m task_queue.cli register \
    --task-source-dir /home/admin/workspaces/datachat/tasks/ad-hoc/task-documents \
    --project-workspace /home/admin/workspaces/datachat \
    --source-id ad-hoc

# Register planned queue (manual setup)
python -m task_queue.cli register \
    --task-source-dir /home/admin/workspaces/datachat/tasks/planned/task-documents \
    --project-workspace /home/admin/workspaces/datachat \
    --source-id planned
```

**Required Arguments:**
| Argument | Description |
|----------|-------------|
| `--task-source-dir` | Path to Task Source Directory (contains task-*.md files) |
| `--project-workspace` | Path to project root directory |
| `--source-id` | Unique identifier for this queue |

---

### 3. unregister - Remove Queue

**Use to remove a queue from monitoring.**

```bash
# Unregister a queue
python -m task_queue.cli unregister --source-id my-queue

# Unregister ad-hoc queue
python -m task_queue.cli unregister --source-id ad-hoc

# Unregister planned queue
python -m task_queue.cli unregister --source-id planned
```

---

## Other Useful Commands

```bash
# List registered Task Source Directories
python -m task_queue.cli list-sources

# Check system status
python -m task_queue.cli status

# Run interactively (for testing)
python -m task_queue.cli run --cycles 1

# Start daemon
systemctl --user start task-queue.service

# View live logs
journalctl --user -u task-queue.service -f
```

---

## Quick Start Examples

### Example 1: New Project (Recommended)

```bash
cd /home/admin/workspaces/datachat
source .venv/bin/activate
export PYTHONPATH=/home/admin/workspaces/task-queue:$PYTHONPATH

# One command to set up everything
python -m task_queue.cli init

# Verify
python -m task_queue.cli list-sources
```

### Example 2: Custom Queue Setup

```bash
# Create custom queue directories
mkdir -p tasks/custom/{task-staging,task-documents,task-archive,task-failed,task-queue,task-reports}

# Register custom queue
python -m task_queue.cli register \
    --task-source-dir /home/admin/workspaces/datachat/tasks/custom/task-documents \
    --project-workspace /home/admin/workspaces/datachat \
    --source-id custom

# Verify
python -m task_queue.cli list-sources
```

### Example 3: Remove and Re-register

```bash
# Unregister existing queue
python -m task_queue.cli unregister --source-id ad-hoc

# Re-register with different path
python -m task_queue.cli register \
    --task-source-dir /new/path/task-documents \
    --project-workspace /home/admin/workspaces/datachat \
    --source-id ad-hoc
```

---

## Usage After Initialization

Once initialized, tasks are generated using the `task-documents` skill:

| Scenario | Skill Usage | Target Directory |
|----------|-------------|------------------|
| **Ad-hoc task** | `task-documents` from conversation | `tasks/ad-hoc/task-documents/` |
| **Planned task** | `task-documents` from planning doc | `tasks/planned/task-documents/` |

---

## Troubleshooting

### Init Detects Existing Setup

**Symptom:** "Task system appears to be already initialized"

**Solutions:**
```bash
# Option 1: Use --skip-existing to add missing queues only
python -m task_queue.cli init --skip-existing

# Option 2: Use --force to completely re-initialize
python -m task_queue.cli init --force

# Option 3: Use register/unregister for specific changes
python -m task_queue.cli unregister --source-id ad-hoc
python -m task_queue.cli register --source-id ad-hoc ...
```

### Registration Fails

**Symptom:** "Task source directory already registered"

**Solution:**
```bash
# List existing sources
python -m task_queue.cli list-sources

# Unregister first, then re-register
python -m task_queue.cli unregister --source-id my-queue
python -m task_queue.cli register --source-id my-queue ...
```

### Module Not Found

**Symptom:** `ModuleNotFoundError: No module named 'task_queue'`

**Solution:**
```bash
export PYTHONPATH=/home/admin/workspaces/task-queue:$PYTHONPATH
```

### Directories Already Exist

**Symptom:** Directories present before running init

**Solution:** This is normal. Existing directories will be used. Use `--force` to re-register.

---

## Completion Checklist

- [ ] Directory structure created for ad-hoc and planned queues
- [ ] ad-hoc Task Source Directory registered
- [ ] planned Task Source Directory registered
- [ ] Registration verified with `list-sources`
- [ ] Status check shows both sources
- [ ] task-queue daemon is running (if applicable)

---

## Related Skills

- **task-planning**: Generates planning documents for organized task lists
- **task-documents**: Generates task specifications to ad-hoc or planned directories
- **task-queue**: Manages task execution and monitoring
- **task-cleanup**: Cleans up task directories while preserving structure

---

## Notes

- **Init is recommended:** Use `task-queue init` for most setups
- **Register for custom:** Use `register` for custom queue configurations
- **Unregister to remove:** Use `unregister` to remove queues from monitoring
- **Project workspace:** Always use `/home/admin/workspaces/datachat` for this project
- **Parallel execution:** Both queues process independently via separate worker threads
- **Idempotent:** Commands can be safely re-run
