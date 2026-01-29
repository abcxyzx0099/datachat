---
name: task-monitor-system
description: "Create and configure the multi-project task monitoring system with watchdog file monitoring and Claude Agent SDK integration. Use when: setting up a new task monitor system; installing from scratch; understanding system architecture; troubleshooting service issues; configuring the monitor; registering new projects. For detailed architecture, see [architecture.md](references/architecture.md). For troubleshooting, see [troubleshooting.md](references/troubleshooting.md)."
---

# Multi-Project Task Monitor System

## Quick Overview

Single service that monitors multiple projects, watching each project's `/tasks/` directory and executing tasks **sequentially within each project** (but **parallel across projects**).

## Execution Model

```
Project A (sequential) ──┐
                         ├─→ PARALLEL ──→ Tasks execute independently
Project B (sequential) ──┘
```

- **Within project**: Sequential FIFO queue (one task at a time)
- **Across projects**: Parallel execution (projects run independently)

---

## Creating the Task Monitor System

### Quick Install

The install script is included in this skill at [references/install-service.sh](references/install-service.sh).

```bash
# Run the install script
sudo bash /opt/task-monitor/install-service.sh
```

This will:
1. Create virtual environment at `/opt/task-monitor/.venv/`
2. Install dependencies (claude-agent-sdk, watchdog, pydantic)
3. Create `pyproject.toml` for CLI installation
4. Install CLI command via `pip install --user`
5. Create systemd service
6. Create management CLI (`task-monitor-control`)
7. Start the service

### Manual Installation

If you prefer to install manually:

```bash
# 1. Create virtual environment
sudo python3 -m venv /opt/task-monitor/.venv

# 2. Install dependencies
sudo /opt/task-monitor/.venv/bin/pip install claude-agent-sdk watchdog pydantic

# 3. Create pyproject.toml (see references/install-service.sh for content)

# 4. Install CLI
pip install --user --break-system-packages /opt/task-monitor

# 5. Create systemd service (see references/install-service.sh for content)

# 6. Start service
sudo systemctl enable task-monitor
sudo systemctl start task-monitor
```

### Verify Installation

```bash
# Check service status
sudo systemctl status task-monitor

# Test CLI
task-monitor --help

# List projects (empty initially)
task-monitor-control list
```

---

## Task Naming Convention

**Format:** `task-<description>-YYYYMMDD-HHMMSS.md`

**Example:** `task-system-verification-20250129-143000.md`

- `task-` - Fixed prefix
- `<description>` - Short, kebab-case description
- `<timestamp>` - ISO format with single dash (YYYYMMDD-HHMMSS)
- `.md` - Markdown document

**Pattern (glob):** `task-*-????????-??????.md`

## Key Paths

| Purpose | Path |
|---------|------|
| Install script | `.claude/skills/task-monitor-system/references/install-service.sh` |
| System service | `/etc/systemd/system/task-monitor.service` |
| Monitor daemon | `/opt/task-monitor/` (system-level) |
| Configuration | `~/.config/task-monitor/` |
| CLI command | `~/.local/bin/task-monitor` (installed via `pip install --user`) |
| CLI source | `/opt/task-monitor/cli.py` (with `main()` entry point) |
| Package config | `/opt/task-monitor/pyproject.toml` (defines `[project.scripts]`) |
| Package location | `~/.local/lib/python3.13/site-packages/` (modules: cli.py, models.py, etc.) |

## Project Structure (Each Project)

```
{project-root}/
├── tasks/          # Task documents (watched by monitor)
├── results/        # Execution results (JSON)
├── state/          # Queue state per project
├── logs/           # Monitor logs per project
└── .claude/
    └── skills/     # Project-specific skills
```

## Quick Commands

```bash
# Service management
sudo systemctl status task-monitor       # Check status
sudo systemctl restart task-monitor      # Restart service

# Project management
task-monitor-control list                              # List all projects
task-monitor-control register /path/to/project          # Register new project
task-monitor-control register /path/to/project --name myproject  # Custom name
task-monitor-control unregister project-name            # Remove project
task-monitor-control disable project-name               # Temporarily disable
task-monitor-control enable project-name                # Re-enable
task-monitor-control restart                            # Apply registry changes

# Query tasks (per project)
task-monitor queue                                      # Show queue status (uses default project)
task-monitor -p /path/to/project queue                  # Show queue for specific project
task-monitor task-id                                    # Show task status
task-monitor --help                                     # Show all options
```

## Systemd Service

**File:** `/etc/systemd/system/task-monitor.service`

```ini
[Unit]
Description=Multi-Project Task Monitor Daemon
After=network.target

[Service]
Type=simple
User=admin
Environment="PATH=/opt/task-monitor/.venv/bin:/usr/bin"
Environment="PYTHONPATH=/opt/task-monitor"
EnvironmentFile=/home/admin/.config/task-monitor/.env
ExecStart=/opt/task-monitor/.venv/bin/python /opt/task-monitor/monitor_daemon.py
Restart=always
RestartSec=10
```

**Single service** monitoring all registered projects. Uses dedicated virtual environment at `/opt/task-monitor/.venv/`.

## Workflow

```
1. Register project(s) → ~/.config/task-monitor/registered.json
                          ↓
2. Start service → task-monitor.service
                          ↓
3. For each project:
   - Watchdog monitors {project}/tasks/
   - Tasks queued in project-specific FIFO queue
   - Sequential execution within project
   - Results saved to {project}/results/
```

## Directory Structure

```
/etc/systemd/system/
└── task-monitor.service           # Single service for all projects

/opt/task-monitor/                 # System-level infrastructure
├── .venv/                         # Dedicated virtual environment (self-contained)
│   ├── bin/
│   │   ├── python → python3       # Python interpreter for service
│   │   └── ...
│   └── lib/
│       └── python3.13/
│           └── site-packages/
│               ├── claude_agent_sdk/
│               ├── watchdog/
│               └── pydantic/
├── monitor_daemon.py              # Multi-project monitor daemon
├── task_executor.py               # Task executor (with project cwd)
├── models.py                      # Data models
├── cli.py                         # Status CLI source (with main() entry point)
├── pyproject.toml                 # Package config (defines [project.scripts])
└── install-service.sh             # Installation script

~/.config/task-monitor/            # User configuration
├── .env                           # API credentials
└── registered.json                # Project registry

~/.local/
├── bin/
│   └── task-monitor               # CLI wrapper (installed via pip install --user)
└── lib/python3.13/site-packages/
    ├── cli.py                     # CLI module (with main() entry point)
    ├── models.py                  # Data models
    ├── monitor_daemon.py          # Monitor daemon (for reference)
    ├── task_executor.py           # Task executor (for reference)
    └── task_monitor-1.0.0.dist-info/  # Package metadata

/usr/local/bin/
└── task-monitor-control           # Management CLI

{project-root}/                    # Per-project (can be multiple)
├── tasks/                         # Task documents
├── results/                       # Execution results
├── state/                         # Queue state
└── logs/                          # Log files
```

## Project Registry

**Location:** `~/.config/task-monitor/registered.json`

```json
{
  "projects": {
    "datachat": {
      "path": "/home/admin/workspaces/datachat",
      "enabled": true,
      "registered_at": "2026-01-29T12:43:00"
    },
    "project-b": {
      "path": "/home/admin/workspaces/project-b",
      "enabled": true,
      "registered_at": "2026-01-29T13:00:00"
    }
  }
}
```

## Registering a New Codebase/Project

### Basic Registration

```bash
# Register a new project (uses directory name as project name)
task-monitor-control register /home/admin/workspaces/myproject
```

This will:
1. Create required directories (`tasks/`, `results/`, `state/`, `logs/`)
2. Add project to registry
3. Automatically restart the task monitor service
4. Start watching `{project}/tasks/` for new task files

### Registration with Custom Name

```bash
# Register with a custom project name
task-monitor-control register /home/admin/workspaces/myproject --name myproject
```

Use custom names when:
- Directory name is not descriptive
- You want a shorter/alias name
- Multiple projects have similar directory names

### What Happens During Registration

```
1. Verify project path exists
         ↓
2. Create required directories:
   - {project}/tasks/       (task documents)
   - {project}/results/     (execution results)
   - {project}/state/       (queue state)
   - {project}/logs/        (monitor logs)
         ↓
3. Add to ~/.config/task-monitor/registered.json
         ↓
4. Restart task-monitor.service
         ↓
5. Service creates:
   - Watchdog observer for {project}/tasks/
   - Project-specific queue
   - Project-specific executor (with correct cwd)
```

### Verify Registration

```bash
# List all registered projects
task-monitor-control list

# Check service logs
sudo journalctl -u task-monitor | grep "Observer started"

# Verify project structure
ls -la /home/admin/workspaces/myproject/tasks/
ls -la /home/admin/workspaces/myproject/results/
ls -la /home/admin/workspaces/myproject/state/
```

## Enabling/Disabling Projects

### Disable a Project (Temporarily)

```bash
# Disable monitoring for a project (keeps registration)
task-monitor-control disable project-name

# Service restarts automatically
# Project's observer is stopped
# Project's queue processor is stopped
```

**Use cases:**
- Temporarily stop task processing for a project
- Debug issues without unregistering
- Pause monitoring during maintenance

### Enable a Project

```bash
# Re-enable monitoring for a disabled project
task-monitor-control enable project-name

# Service restarts automatically
# Project's observer is started
# Project's queue processor resumes
```

### Disable vs Unregister

| Operation | Registry | Configuration | Use Case |
|-----------|----------|---------------|----------|
| `disable` | Kept | `enabled: false` | Temporary pause |
| `unregister` | Removed | Entry deleted | Permanent removal |

### Check Project Status

```bash
# List projects with status
task-monitor-control list

# Output shows enabled/disabled status:
#   datachat
#     Path: /home/admin/workspaces/datachat
#     Status: ✓ enabled
#
#   project-b
#     Path: /home/admin/workspaces/project-b
#     Status: ✗ disabled
```

### Batch Operations

```bash
# Register multiple projects without auto-restart
task-monitor-control register /path/to/project-a --no-restart
task-monitor-control register /path/to/project-b --no-restart
task-monitor-control register /path/to/project-c --no-restart
# Then restart once
task-monitor-control restart
```

## Detailed Information

- **Full Architecture**: [architecture.md](references/architecture.md) - System layout, multi-project design, file descriptions
- **Troubleshooting**: [troubleshooting.md](references/troubleshooting.md) - Common issues and solutions
- **Install Script**: [scripts/install-service.sh](scripts/install-service.sh) - Complete installation script
- **Source Code**: All Python modules included in `scripts/`:
  - [scripts/monitor_daemon.py](scripts/monitor_daemon.py) - Multi-project watchdog daemon
  - [scripts/task_executor.py](scripts/task_executor.py) - Task executor with Claude Agent SDK
  - [scripts/models.py](scripts/models.py) - Pydantic data models
  - [scripts/cli.py](scripts/cli.py) - Command-line interface

## Recreating the System from Scratch

If the task monitor system is completely deleted, you can recreate it using only this skill:

```bash
# 1. Create the system directory
sudo mkdir -p /opt/task-monitor

# 2. Copy source files from this skill's scripts/
sudo cp .claude/skills/task-monitor-system/scripts/*.py /opt/task-monitor/
sudo cp .claude/skills/task-monitor-system/scripts/install-service.sh /opt/task-monitor/

# 3. Run the install script
sudo bash /opt/task-monitor/install-service.sh

# 4. Register your project
task-monitor-control register /home/admin/workspaces/datachat
```

## Dependencies

The task monitor uses a **dedicated virtual environment** at `/opt/task-monitor/.venv/` for independence from project-specific environments.

**Installed dependencies (in venv):**
```
claude-agent-sdk    # Claude Agent SDK
watchdog>=5.0.0     # File system monitoring
pydantic>=2.0.0     # Data validation
```

**CLI Installation (pip install --user):**

The CLI is installed via `pyproject.toml` using setuptools entry points:

```toml
[project.scripts]
task-monitor = "cli:main"
```

**To install/reinstall the CLI:**
```bash
# Install to user site-packages (requires --break-system-packages on Debian)
pip install --user --break-system-packages /opt/task-monitor

# Or using a temp directory to avoid permission issues
TEMP_DIR=$(mktemp -d) && cp -r /opt/task-monitor/* "$TEMP_DIR/" && \
pip install --user --break-system-packages "$TEMP_DIR" && rm -rf "$TEMP_DIR"
```

This creates:
- `~/.local/bin/task-monitor` - Native wrapper script
- `~/.local/lib/python3.13/site-packages/cli.py` - CLI module (with main())
- `~/.local/lib/python3.13/site-packages/models.py` - Data models
- `~/.local/lib/python3.13/site-packages/monitor_daemon.py` - Monitor daemon
- `~/.local/lib/python3.13/site-packages/task_executor.py` - Task executor

## Environment Variables

**Location:** `~/.config/task-monitor/.env`

```bash
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
ANTHROPIC_MODEL=glm-4.7
ANTHROPIC_AUTH_TOKEN=your_token_here
```

The systemd service loads these via `EnvironmentFile`.

## Key Design Principles

1. **Single Service**: One `task-monitor.service` for all projects
2. **Dedicated Virtual Environment**: Self-contained venv at `/opt/task-monitor/.venv/` for independence
3. **Per-Project Isolation**: Each project has its own queue, executor, and watchdog observer
4. **Sequential Within Project**: Tasks in same project execute one at a time (FIFO)
5. **Parallel Across Projects**: Different projects execute simultaneously
6. **Project-Specific CWD**: Each task executes with its project root as working directory
7. **Registration-Based**: Projects registered via CLI, service reloads automatically

## Related Skills

- `task-document-generator`: Creates task documents with correct naming pattern
- `task-coordination`: Executes tasks with worker-auditor workflow
