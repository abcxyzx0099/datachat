---
name: task-init
description: "Initializes the task system by creating the directory structure and adding Task Source Directories with the task-monitor module. One-time setup that configures ad-hoc and planned task queues for parallel execution."
---

# Task System Initialization

Initializes the task system with separate queues for ad-hoc and planned tasks.

## Overview

This skill performs one-time setup of the task system using the init command or manual source management:

| Command | Purpose | Usage |
|---------|---------|-------|
| **init** | Quick setup - creates directories and adds both queues | First-time setup |
| **sources add** | Advanced - add a single Task Source Directory | Custom configurations |
| **sources rm** | Remove a Task Source Directory from monitoring | Reconfiguration |
| **sources list** | List added Task Source Directories | Verification |

The task system supports two independent queues that execute in parallel:

| Queue | Purpose | Source |
|-------|---------|--------|
| **ad-hoc** | Quick tasks from conversation | Spontaneous user requests |
| **planned** | Organized tasks from planning docs | `task-planning` output |

---

## When to Use

| Scenario | Command |
|----------|---------|
| **First-time setup** | `task-monitor init` (recommended) |
| **Re-configuration** | `task-monitor init --force` or `sources add`/`sources rm` |
| **Add custom queue** | `task-monitor sources add` |
| **Remove queue** | `task-monitor sources rm` |
| **Verification** | `task-monitor sources list` |

---

## Directory Structure

```
tasks/
├── ad-hoc/                              # Ad-hoc task queue (Task Source Directory)
│   ├── staging/                    # Staging area (atomic writes)
│   ├── pending/                  # Watchdog monitors this subdirectory
│   ├── completed/                 # Completed task specs
│   ├── failed/                    # Failed task specs
│   ├── results/                   # JSON result files
│   └── reports/                   # Worker execution reports
│
└── planned/                             # Planned task queue (Task Source Directory)
    ├── staging/                    # Staging area (atomic writes)
    ├── pending/                  # Watchdog monitors this subdirectory
    ├── completed/                 # Completed task specs
    ├── failed/                    # Failed task specs
    ├── results/                   # JSON result files
    ├── reports/                   # Worker execution reports
    └── planning/                  # Planning documents (task-planning output)
```

---

## Command Reference

### 1. init - Quick Setup

**Recommended for most use cases.** Initializes from current directory.

```bash
# From project directory
cd /home/admin/workspaces/datachat
source .venv/bin/activate

# Initialize (creates directories, adds both queues)
task-monitor init

# Options
task-monitor init --force           # Re-initialize completely
task-monitor init --skip-existing   # Skip already added queues
task-monitor init --restart-daemon  # Restart daemon after init
```

**What it does:**
- Uses current directory as Project Workspace
- Creates all directory structures for both queues
- Adds `ad-hoc` and `planned` Task Source Directories
- Saves configuration
- Shows verification summary

---

### 2. sources add - Advanced Configuration

**Use for custom queue configurations.** Add a single Task Source Directory (parent directory).

```bash
# Activate environment
source /home/admin/workspaces/datachat/.venv/bin/activate

# Add a custom queue
task-monitor sources add /path/to/queue \
    --id my-queue \
    --project-workspace /home/admin/workspaces/datachat \
    --description "My custom queue"

# Add ad-hoc queue (manual setup)
task-monitor sources add \
    /home/admin/workspaces/datachat/tasks/ad-hoc \
    --id ad-hoc \
    --project-workspace /home/admin/workspaces/datachat

# Add planned queue (manual setup)
task-monitor sources add \
    /home/admin/workspaces/datachat/tasks/planned \
    --id planned \
    --project-workspace /home/admin/workspaces/datachat
```

**Required Arguments:**
| Argument | Description |
|----------|-------------|
| Positional | Path to Task Source Directory (parent queue directory with pending/ subdirectory) |
| `--id` | Unique identifier for this queue |
| `--project-workspace` | Path to project root directory |
| `--description` | Description of this queue (optional) |

---

### 3. sources rm - Remove Queue

**Use to remove a queue from monitoring.**

```bash
# Remove a queue
task-monitor sources rm --source-id my-queue

# Remove ad-hoc queue
task-monitor sources rm --source-id ad-hoc

# Remove planned queue
task-monitor sources rm --source-id planned
```

---

## Other Useful Commands

```bash
# List added Task Source Directories
task-monitor sources list

# Check system status
task-monitor status

# Show detailed status (with running tasks)
task-monitor status --detailed

# Run interactively (for testing)
task-monitor run --cycles 1

# Start daemon
systemctl --user start task-monitor.service

# View live logs
task-monitor logs --follow
# Or with journalctl
journalctl --user -u task-monitor.service -f
```

---

## Quick Start Examples

### Example 1: New Project (Recommended)

```bash
cd /home/admin/workspaces/datachat
source .venv/bin/activate

# One command to set up everything
task-monitor init

# Verify
task-monitor sources list
```

### Example 2: Custom Queue Setup

```bash
# Create custom queue directories
mkdir -p tasks/custom/{staging,pending,completed,failed,results,reports}

# Add custom queue
task-monitor sources add \
    /home/admin/workspaces/datachat/tasks/custom/pending \
    --id custom \
    --project-workspace /home/admin/workspaces/datachat \
    --description "Custom queue"

# Verify
task-monitor sources list
```

---

## Usage After Initialization

Once initialized, tasks are generated using the `task-documents` skill:

| Scenario | Skill Usage | Target Directory |
|----------|-------------|------------------|
| **Ad-hoc task** | `task-documents` from conversation | `tasks/ad-hoc/pending/` |
| **Planned task** | `task-documents` from planning doc | `tasks/planned/pending/` |

---

## Troubleshooting

### Init Detects Existing Setup

**Symptom:** "Task system appears to be already initialized"

**Solutions:**
```bash
# Option 1: Use --skip-existing to add missing queues only
task-monitor init --skip-existing

# Option 2: Use --force to completely re-initialize
task-monitor init --force
```

### Command Not Found

**Symptom:** `task-monitor: command not found`

**Solution:**
```bash
# The wrapper script uses the PYTHONPATH to find task-monitor module
# The task-monitor command should be available from ~/.local/bin/task-monitor
# which sets PYTHONPATH automatically
```

### Directories Already Exist

**Symptom:** Directories present before running init

**Solution:** This is normal. Existing directories will be used. Use `--force` to re-initialize completely.

---

## Completion Checklist

- [ ] Directory structure created for ad-hoc and planned queues
- [ ] ad-hoc Task Source Directory added
- [ ] planned Task Source Directory added
- [ ] Source addition verified with `sources list`
- [ ] Status check shows both sources
- [ ] task-monitor daemon is running (if applicable)

---

## Related Skills

- **task-planning**: Generates planning documents for organized task lists
- **task-documents**: Generates task specifications to ad-hoc or planned directories
- **task-monitor**: Coordinates task execution and monitors sources
- **task-execution**: Executes tasks using two-agent workflow
- **task-cleanup**: Cleans up task directories while preserving structure

---

## Notes

- **Init is recommended:** Use `task-monitor init` for most setups
- **sources add for custom:** Use `task-monitor sources add` to add Task Source Directories
- **sources rm to remove:** Use `task-monitor sources rm` to remove queues from monitoring
- **Project workspace:** Always use `/home/admin/workspaces/datachat` for this project
- **Parallel execution:** Both queues process independently via separate worker threads
- **Idempotent:** Commands can be safely re-run
