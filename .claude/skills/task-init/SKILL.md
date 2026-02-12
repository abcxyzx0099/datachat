---
name: task-init
description: "Initializes the task system by creating the directory structure, adding Task Source Directories, installing the task-monitor CLI, and ensuring the task-monitor service is configured and running. One-time setup that configures ad-hoc and planned task queues for parallel execution."
---

# Task System Initialization

Initializes the task system with separate queues for ad-hoc and planned tasks, installs the CLI, configures the service, and verifies everything is running.

## Overview

This skill performs one-time setup of the task system using the init command or manual queue management, and verifies the systemd service is operational:

| Command | Purpose | Usage |
|---------|---------|-------|
| **init** | Quick setup - creates directories, adds both queues, ensures service running | First-time setup |
| **service-setup** | Verifies/configures systemd service and starts daemon | Service management |
| **queues add** | Advanced - add a single Task Source Directory (queue) | Custom configurations |
| **queues rm** | Remove a Task Source Directory (queue) from monitoring | Reconfiguration |
| **queues list** | List added Task Source Directories (queues) | Verification |

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
| **Re-configuration** | `task-monitor init --force` or `queues add`/`queues rm` |
| **Add custom queue** | `task-monitor queues add` |
| **Remove queue** | `task-monitor queues rm` |
| **Verification** | `task-monitor queues list` |

---

## Directory Structure

```
task-monitor/
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

## Reference Documents

Detailed setup instructions are in separate reference documents:

| Document | Purpose |
|----------|---------|
| **[CLI Setup](reference/cli-setup.md)** | Install and configure the `task-monitor` CLI command |
| **[Service Setup](reference/service-setup.md)** | Configure and manage the task-monitor systemd service |

---

## Command Reference

### 1. init - Quick Setup

**Recommended for most use cases.** Initializes from current directory.

```bash
# From project directory
cd /home/admin/workspaces/datachat

# Initialize (creates directories, adds both queues)
task-monitor init

# Options
task-monitor init --force           # Re-initialize completely
task-monitor init --skip-existing   # Skip already added queues
```

**What it does:**
- Uses current directory as Project Workspace
- Creates all directory structures for both queues
- Adds `ad-hoc` and `planned` Task Source Directories
- Saves configuration
- Shows verification summary

---

### 2. CLI Installation

**Install the `task-monitor` CLI command.** See [CLI Setup](reference/cli-setup.md) for detailed instructions.

```bash
# Quick install (editable mode)
cd /home/admin/workspaces/task-monitor
.venv/bin/pip install -e . --break-system-packages

# Verify installation
.venv/bin/task-monitor status

# Or install globally with pipx (production)
pipx install /home/admin/workspaces/task-monitor
```

---

### 3. Service Setup

**Configure and start the task-monitor systemd service.** See [Service Setup](reference/service-setup.md) for detailed instructions.

```bash
# Quick status check
systemctl --user status task-monitor.service

# Start if not running
systemctl --user start task-monitor.service

# Enable auto-start at login
systemctl --user enable task-monitor.service
```

---

### 4. queues add - Advanced Configuration

**Use for custom queue configurations.** Add a single Task Source Directory (parent directory).

```bash
# Activate environment
source /home/admin/workspaces/datachat/.venv/bin/activate

# Add a custom queue
task-monitor queues add /path/to/queue \
    --id my-queue \
    --project-workspace /home/admin/workspaces/datachat \
    --description "My custom queue"

# Add ad-hoc queue (manual setup)
task-monitor queues add \
    /home/admin/workspaces/datachat/task-monitor/ad-hoc \
    --id ad-hoc \
    --project-workspace /home/admin/workspaces/datachat

# Add planned queue (manual setup)
task-monitor queues add \
    /home/admin/workspaces/datachat/task-monitor/planned \
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

### 5. queues rm - Remove Queue

**Use to remove a queue from monitoring.**

```bash
# Remove a queue
task-monitor queues rm my-queue

# Remove ad-hoc queue
task-monitor queues rm ad-hoc

# Remove planned queue
task-monitor queues rm planned
```

---

## Other Useful Commands

```bash
# List added Task Source Directories (queues)
task-monitor queues list

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

### Example 1: Complete First-Time Setup

```bash
cd /home/admin/workspaces/datachat

# 1. Install CLI
cd /home/admin/workspaces/task-monitor
.venv/bin/pip install -e . --break-system-packages

# 2. Initialize task system (creates directories, adds queues)
cd /home/admin/workspaces/datachat
.venv/bin/task-monitor init

# 3. Verify service is running
systemctl --user status task-monitor.service

# 4. Start service if needed
systemctl --user start task-monitor.service

# 5. Enable auto-start at login
systemctl --user enable task-monitor.service

# 6. Verify everything
.venv/bin/task-monitor status
.venv/bin/task-monitor queues list
```

**For detailed setup instructions, see:**
- [CLI Setup](reference/cli-setup.md)
- [Service Setup](reference/service-setup.md)

### Example 2: Custom Queue Setup

```bash
# Create custom queue directories
mkdir -p task-monitor/custom/{staging,pending,completed,failed,results,reports}

# Add custom queue
task-monitor queues add \
    /home/admin/workspaces/datachat/task-monitor/custom \
    --id custom \
    --project-workspace /home/admin/workspaces/datachat \
    --description "Custom queue"

# Verify
task-monitor queues list
```

---

## Usage After Initialization

Once initialized, tasks are generated using the `task-documents` skill:

| Scenario | Skill Usage | Target Directory |
|----------|-------------|------------------|
| **Ad-hoc task** | `task-documents` from conversation | `task-monitor/ad-hoc/pending/` |
| **Planned task** | `task-documents` from planning doc | `task-monitor/planned/pending/` |

---

## Troubleshooting

### CLI Not Working

**See:** [CLI Setup](reference/cli-setup.md#troubleshooting)

### Service Not Running

**See:** [Service Setup](reference/service-setup.md#troubleshooting)

### Service File Missing

**See:** [Service Setup](reference/service-setup.md#service-file-missing)

### Service Crashes Repeatedly

**See:** [Service Setup](reference/service-setup.md#service-crashes-repeatedly)

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
- [ ] Queue addition verified with `queues list`
- [ ] Status check shows both queues
- [ ] **task-monitor.service file exists** (`~/.config/systemd/user/task-monitor.service`)
- [ ] **Service is enabled** for auto-start at login
- [ ] **Service is running** (active)
- [ ] **Service logs show clean startup** (no errors)

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
- **queues add for custom:** Use `task-monitor queues add` to add Task Source Directories
- **queues rm to remove:** Use `task-monitor queues rm` to remove queues from monitoring
- **Project workspace:** Always use `/home/admin/workspaces/datachat` for this project
- **Parallel execution:** Both queues process independently via separate worker threads
- **Idempotent:** Commands can be safely re-run
