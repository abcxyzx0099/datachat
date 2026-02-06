---
name: task-init
description: "Initializes the task system by creating the directory structure and registering Task Source Directories with the task-queue module. One-time setup that configures ad-hoc and planned task queues for parallel execution."
---

# Task System Initialization

Initializes the task system with separate queues for ad-hoc and planned tasks.

## Overview

This skill performs one-time setup of the task system using the init command or manual source registration:

| Command | Purpose | Usage |
|---------|---------|-------|
| **init** | Quick setup - creates directories and registers both queues | First-time setup |
| **sources add** | Advanced - register a single Task Source Directory | Custom configurations |
| **sources rm** | Remove a Task Source Directory from monitoring | Reconfiguration |
| **sources list** | List registered Task Source Directories | Verification |

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
| **Re-configuration** | `task-queue init --force` or `sources add`/`sources rm` |
| **Add custom queue** | `task-queue sources add` |
| **Remove queue** | `task-queue sources rm` |
| **Verification** | `task-queue sources list` |

---

## Directory Structure

```
tasks/
├── ad-hoc/                              # Ad-hoc task queue
│   ├── task-staging/                    # Staging area (atomic writes)
│   ├── task-documents/                  # Task Source Directory (watchdog monitors)
│   ├── task-archive/                    # Completed task specs
│   ├── task-failed/                     # Failed task specs
│   ├── task-queue/                      # JSON result files
│   └── task-reports/                    # Worker execution reports
│
└── planned/                             # Planned task queue
    ├── task-staging/                    # Staging area (atomic writes)
    ├── task-documents/                  # Task Source Directory (watchdog monitors)
    ├── task-archive/                    # Completed task specs
    ├── task-failed/                     # Failed task specs
    ├── task-queue/                      # JSON result files
    └── task-reports/                    # Worker execution reports
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

### 2. sources add - Advanced Configuration

**Use for custom queue configurations.** Register a single Task Source Directory.

```bash
# Activate environment
source /home/admin/workspaces/datachat/.venv/bin/activate
export PYTHONPATH=/home/admin/workspaces/task-queue:$PYTHONPATH

# Register a queue
python -m task_queue.cli sources add /path/to/task-documents \
    --id my-queue \
    --project-workspace /home/admin/workspaces/datachat \
    --description "My custom queue"

# Register ad-hoc queue (manual setup)
python -m task_queue.cli sources add \
    /home/admin/workspaces/datachat/tasks/ad-hoc/task-documents \
    --id ad-hoc \
    --project-workspace /home/admin/workspaces/datachat

# Register planned queue (manual setup)
python -m task_queue.cli sources add \
    /home/admin/workspaces/datachat/tasks/planned/task-documents \
    --id planned \
    --project-workspace /home/admin/workspaces/datachat
```

**Required Arguments:**
| Argument | Description |
|----------|-------------|
| Positional | Path to Task Source Directory (contains task-*.md files) |
| `--id` | Unique identifier for this queue |
| `--project-workspace` | Path to project root directory |
| `--description` | Description of this queue (optional) |

---

### 3. sources rm - Remove Queue

**Use to remove a queue from monitoring.**

```bash
# Remove a queue
python -m task_queue.cli sources rm --source-id my-queue

# Remove ad-hoc queue
python -m task_queue.cli sources rm --source-id ad-hoc

# Remove planned queue
python -m task_queue.cli sources rm --source-id planned
```

---

## Other Useful Commands

```bash
# List registered Task Source Directories
python -m task_queue.cli sources list

# Check system status
python -m task_queue.cli status

# Show detailed status (with running tasks)
python -m task_queue.cli status --detailed

# Run interactively (for testing)
python -m task_queue.cli run --cycles 1

# Start daemon
systemctl --user start task-queue.service

# View live logs
python -m task_queue.cli logs --follow
# Or with journalctl
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
python -m task_queue.cli sources list
```

### Example 2: Custom Queue Setup

```bash
# Create custom queue directories
mkdir -p tasks/custom/{task-staging,task-documents,task-archive,task-failed,task-queue,task-reports}

# Register custom queue
python -m task_queue.cli sources add \
    /home/admin/workspaces/datachat/tasks/custom/task-documents \
    --id custom \
    --project-workspace /home/admin/workspaces/datachat \
    --description "Custom queue"

# Verify
python -m task_queue.cli sources list
```

### Example 3: Remove and Re-register

```bash
# Remove existing queue
python -m task_queue.cli sources rm --source-id ad-hoc

# Re-register with different path
python -m task_queue.cli sources add \
    /new/path/task-documents \
    --id ad-hoc \
    --project-workspace /home/admin/workspaces/datachat
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

# Option 3: Use sources rm/add for specific changes
python -m task_queue.cli sources rm --source-id ad-hoc
python -m task_queue.cli sources add /path/to/task-documents --id ad-hoc --project-workspace /home/admin/workspaces/datachat
```

### Registration Fails

**Symptom:** "Task source directory already registered"

**Solution:**
```bash
# List existing sources
python -m task_queue.cli sources list

# Remove first, then re-add
python -m task_queue.cli sources rm --source-id my-queue
python -m task_queue.cli sources add /path/to/task-documents --id my-queue --project-workspace /home/admin/workspaces/datachat
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
- [ ] Registration verified with `sources list`
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
- **sources add for custom:** Use `sources add` for custom queue configurations
- **sources rm to remove:** Use `sources rm` to remove queues from monitoring
- **Project workspace:** Always use `/home/admin/workspaces/datachat` for this project
- **Parallel execution:** Both queues process independently via separate worker threads
- **Idempotent:** Commands can be safely re-run
