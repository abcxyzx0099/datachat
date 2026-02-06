---
name: task-init
description: "Initializes the task system by creating the directory structure and registering Task Source Directories with the task-queue module. One-time setup that configures ad-hoc and planned task queues for parallel execution."
---

# Task System Initialization

Initializes the task system with separate queues for ad-hoc and planned tasks.

## Overview

This skill performs one-time setup of the task system by:

1. **Creating directory structure** for ad-hoc and planned tasks
2. **Registering Task Source Directories** with task-queue
3. **Verifying setup** with status check

The task system supports two independent queues that execute in parallel:

| Queue | Purpose | Source |
|-------|---------|--------|
| **ad-hoc** | Quick tasks from conversation | Spontaneous user requests |
| **planned** | Organized tasks from planning docs | `task-planning` output |

---

## When to Use

| Scenario | When |
|----------|------|
| **First-time setup** | New project or fresh workspace |
| **Re-configuration** | Adding or re-registering task sources |
| **Verification** | Checking if task system is properly configured |

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

## Step-by-Step Procedure

### Step 1: Verify Prerequisites

```bash
# Check if .venv exists
ls -d /home/admin/workspaces/datachat/.venv

# Check if task-queue module is accessible
source /home/admin/workspaces/datachat/.venv/bin/activate
export PYTHONPATH=/home/admin/workspaces/task-queue:$PYTHONPATH
python -m task_queue.cli --help
```

### Step 2: Create Directory Structure

```bash
# Create ad-hoc task directories
mkdir -p /home/admin/workspaces/datachat/tasks/ad-hoc/{task-staging,task-documents,task-archive,task-failed,task-queue,task-reports}

# Create planned task directories
mkdir -p /home/admin/workspaces/datachat/tasks/planned/{task-staging,task-documents,task-archive,task-failed,task-queue,task-reports}
```

### Step 3: Register Task Source Directories

```bash
# Activate Python environment
source /home/admin/workspaces/datachat/.venv/bin/activate
export PYTHONPATH=/home/admin/workspaces/task-queue:$PYTHONPATH

# Register ad-hoc queue
python -m task_queue.cli register \
    --task-source-dir /home/admin/workspaces/datachat/tasks/ad-hoc/task-documents \
    --project-workspace /home/admin/workspaces/datachat \
    --source-id ad-hoc

# Register planned queue
python -m task_queue.cli register \
    --task-source-dir /home/admin/workspaces/datachat/tasks/planned/task-documents \
    --project-workspace /home/admin/workspaces/datachat \
    --source-id planned
```

### Step 4: Verify Registration

```bash
# List registered sources
python -m task_queue.cli list-sources

# Check daemon status
python -m task_queue.cli status
```

**Expected output:**
```
Registered Task Source Directories:
  Source ID: ad-hoc
    Task Source Dir: /home/admin/workspaces/datachat/tasks/ad-hoc/task-documents
    Project Workspace: /home/admin/workspaces/datachat

  Source ID: planned
    Task Source Dir: /home/admin/workspaces/datachat/tasks/planned/task-documents
    Project Workspace: /home/admin/workspaces/datachat
```

---

## Usage After Initialization

Once initialized, tasks are generated using the `task-documents` skill:

| Scenario | Skill Usage | Target Directory |
|----------|-------------|------------------|
| **Ad-hoc task** | `task-documents` from conversation | `tasks/ad-hoc/task-documents/` |
| **Planned task** | `task-documents` from planning doc | `tasks/planned/task-documents/` |

---

## CLI Commands Reference

| Command | Purpose |
|---------|---------|
| `mkdir -p tasks/{ad-hoc,planned}/{task-staging,task-documents,...}` | Create directory structure |
| `python -m task_queue.cli register --source-id <id>` | Register a Task Source Directory |
| `python -m task_queue.cli list-sources` | List registered sources |
| `python -m task_queue.cli status` | Check system status |
| `systemctl --user start task-queue.service` | Start the daemon |
| `journalctl --user -u task-queue.service -f` | View live logs |

---

## Troubleshooting

### Registration Fails

**Symptom:** `Error: Task source directory already registered`

**Solution:**
```bash
# List existing sources
python -m task_queue.cli list-sources

# Unregister if needed
python -m task_queue.cli unregister --source-id ad-hoc
python -m task_queue.cli unregister --source-id planned

# Re-register
python -m task_queue.cli register --source-id ad-hoc ...
```

### Directories Already Exist

**Symptom:** `mkdir: cannot create directory: File exists`

**Solution:** This is normal. Existing directories will be used. No action needed.

### Module Not Found

**Symptom:** `ModuleNotFoundError: No module named 'task_queue'`

**Solution:**
```bash
export PYTHONPATH=/home/admin/workspaces/task-queue:$PYTHONPATH
```

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

- **One-time setup:** This skill is typically run once per workspace
- **Re-run safe:** Can be safely re-run if configuration needs verification
- **Parallel execution:** Both queues process independently via separate worker threads
- **Project workspace:** Always use `/home/admin/workspaces/datachat` for this project
